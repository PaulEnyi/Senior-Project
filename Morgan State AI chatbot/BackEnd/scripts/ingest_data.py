import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.langchain_service import LangChainRAGService
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataIngestionManager:
    """Manages the ingestion of Morgan State CS knowledge base data"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.pinecone_service = PineconeService()
        self.rag_service = LangChainRAGService()
        self.knowledge_base_path = Path(settings.KNOWLEDGE_BASE_PATH)
        self.processed_path = Path("data/processed")
        self.processed_path.mkdir(exist_ok=True, parents=True)
    
    async def ingest_all_data(self):
        """Main function to ingest all knowledge base data"""
        try:
            logger.info("✓ Starting Morgan AI knowledge base ingestion...")
            
            # Step 1: Load and process all JSON files
            all_documents = await self.load_all_knowledge_files()
            logger.info(f"✓ Loaded {len(all_documents)} documents from knowledge base")
            
            # Step 2: Clear existing Pinecone index
            logger.info("  Clearing existing Pinecone index...")
            await self.pinecone_service.clear_index()
            
            # Step 3: Generate embeddings for all documents
            logger.info("✓ Generating embeddings...")
            embeddings = await self.generate_embeddings(all_documents)
            
            # Step 4: Upload to Pinecone
            logger.info("  Uploading to Pinecone...")
            await self.pinecone_service.upsert_documents(all_documents, embeddings)
            
            # Step 5: Save metadata
            await self.save_processing_metadata(all_documents, embeddings)
            
            # Step 6: Verify ingestion
            stats = await self.pinecone_service.get_index_stats()
            logger.info(f"✓ Ingestion complete! Vector count: {stats.get('total_vectors', 0)}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Ingestion failed: {str(e)}")
            logger.exception("Full error details:")
            raise e
    
    async def load_all_knowledge_files(self):
        """Load all JSON knowledge files and convert to document format"""
        all_documents = []
        
        # Process training_data.txt first
        training_file = self.knowledge_base_path / "training_data.txt"
        if training_file.exists():
            logger.info(f"Processing {training_file.name}...")
            with open(training_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Split into sections for better embeddings
                sections = self.split_training_data(content)
                for i, section in enumerate(sections):
                    doc = {
                        'id': f"training_data_{i}",
                        'content': section,
                        'category': 'training_data',
                        'source': 'training_data.txt',
                        'title': f'Training Data Section {i+1}',
                        'last_updated': datetime.utcnow().isoformat()
                    }
                    all_documents.append(doc)
            logger.info(f"  Created {len(sections)} sections from training data")
        
        # Process all JSON files in subdirectories
        json_files = [
            # Department info
            ('department_info/faculty_staff.json', 'faculty_staff'),
            ('department_info/locations.json', 'locations'),
            ('department_info/contact_info.json', 'contact_info'),
            
            # Academics
            ('academics/courses.json', 'courses'),
            ('academics/programs.json', 'programs'),
            ('academics/prerequisites.json', 'prerequisites'),
            ('academics/advising_info.json', 'advising'),
            
            # Student resources
            ('student_resources/tutoring.json', 'tutoring'),
            ('student_resources/organizations.json', 'organizations'),
            ('student_resources/career_prep.json', 'career_prep'),
            ('student_resources/tech_resources.json', 'tech_resources'),
            
            # Administrative
            ('administrative/registration.json', 'registration'),
            ('administrative/deadlines.json', 'deadlines'),
            ('administrative/forms.json', 'forms')
        ]
        
        for file_path, category in json_files:
            full_path = self.knowledge_base_path / file_path
            if full_path.exists():
                docs = await self.process_json_file(full_path, category)
                all_documents.extend(docs)
                logger.info(f"✓ Processed {file_path}: {len(docs)} documents")
            else:
                logger.warning(f"  File not found: {file_path}")
        
        return all_documents
    
    def split_training_data(self, content, max_chunk_size=1000):
        """Split training data into manageable chunks"""
        # Split by headers (##) first
        sections = []
        current_section = ""
        
        for line in content.split('\n'):
            if line.startswith('##') and current_section:
                # Save previous section
                if len(current_section) > 50:  # Minimum chunk size
                    sections.append(current_section.strip())
                current_section = line + '\n'
            else:
                current_section += line + '\n'
            
            # If section gets too large, split it
            if len(current_section) > max_chunk_size:
                sections.append(current_section.strip())
                current_section = ""
        
        # Add final section
        if current_section.strip():
            sections.append(current_section.strip())
        
        return sections if sections else [content]
    
    async def process_json_file(self, file_path, category):
        """Process a single JSON file and convert to documents"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            file_name = file_path.name
            
            if isinstance(data, dict):
                # Handle dictionary data
                for key, value in data.items():
                    doc_content = self.format_content(key, value)
                    doc = {
                        'id': f"{category}_{key.lower().replace(' ', '_')}",
                        'content': doc_content,
                        'category': category,
                        'source': file_name,
                        'title': key.replace('_', ' ').title(),
                        'last_updated': datetime.utcnow().isoformat()
                    }
                    documents.append(doc)
            
            elif isinstance(data, list):
                # Handle list data
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        doc_content = self.format_dict_content(item)
                        title = item.get('name', item.get('title', f'{category.title()} {i+1}'))
                    else:
                        doc_content = str(item)
                        title = f'{category.title()} {i+1}'
                    
                    doc = {
                        'id': f"{category}_{i}",
                        'content': doc_content,
                        'category': category,
                        'source': file_name,
                        'title': title,
                        'last_updated': datetime.utcnow().isoformat()
                    }
                    documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return []
    
    def format_content(self, key, value):
        """Format key-value content for embedding"""
        if isinstance(value, dict):
            return f"{key}:\n{self.format_dict_content(value)}"
        elif isinstance(value, list):
            items = '\n'.join([f"• {item}" for item in value])  # FIXED: proper bullet
            return f"{key}:\n{items}"
        else:
            return f"{key}: {value}"
    
    def format_dict_content(self, data):
        """Format dictionary content for embedding"""
        formatted_parts = []
        for key, value in data.items():
            if isinstance(value, list):
                items = ', '.join(map(str, value))
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {items}")
            elif isinstance(value, dict):
                sub_content = self.format_dict_content(value)
                formatted_parts.append(f"{key.replace('_', ' ').title()}:\n{sub_content}")
            else:
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return '\n'.join(formatted_parts)
    
    async def generate_embeddings(self, documents):
        """Generate embeddings for all documents"""
        texts = [doc['content'] for doc in documents]
        batch_size = 50  # Process in batches to avoid rate limits
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(texts)-1)//batch_size + 1
            logger.info(f"  Processing embedding batch {batch_num}/{total_batches}")
            
            try:
                batch_embeddings = await self.openai_service.generate_embeddings(batch)
                all_embeddings.extend(batch_embeddings)
                
                # Small delay to respect rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {batch_num}: {str(e)}")
                raise e
        
        return all_embeddings
    
    async def save_processing_metadata(self, documents, embeddings):
        """Save metadata about the processing"""
        metadata = {
            'processed_at': datetime.utcnow().isoformat(),
            'total_documents': len(documents),
            'total_embeddings': len(embeddings),
            'categories': list(set(doc['category'] for doc in documents)),
            'sources': list(set(doc['source'] for doc in documents)),
            'embedding_model': settings.OPENAI_EMBEDDING_MODEL,
            'embedding_dimension': 1536
        }
        
        # Save processing metadata
        metadata_file = self.processed_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save document index for reference
        doc_index = [
            {
                'id': doc['id'],
                'title': doc['title'],
                'category': doc['category'],
                'source': doc['source']
            }
            for doc in documents
        ]
        
        index_file = self.processed_path / "document_index.json"
        with open(index_file, 'w') as f:
            json.dump(doc_index, f, indent=2)
        
        logger.info(f"✓ Saved metadata to {metadata_file}")
        logger.info(f"✓ Saved document index to {index_file}")

async def main():
    """Main ingestion function"""
    print("\nMorgan AI Knowledge Base Ingestion")
    print("=" * 40)
    print()
    
    try:
        manager = DataIngestionManager()
        await manager.ingest_all_data()
        
        print("\n" + "="*60)
        print("✓ Morgan AI knowledge base ingestion completed successfully!")
        print("\nYou can now start the chatbot and it will have access to")
        print("all the Morgan State CS data.")
        print("\nNext steps:")
        print("1. Start the backend: python -m app.main")
        print("2. Start the frontend: npm run dev")
        print("3. Test the chatbot with queries")
        print("="*60)
        return 0
        
    except Exception as e:
        print(f"\n✗ Ingestion failed: {str(e)}")
        print("Check the logs above for details.")
        return 1

if __name__ == "__main__":
    # Run the ingestion
    exit_code = asyncio.run(main())
    sys.exit(exit_code)