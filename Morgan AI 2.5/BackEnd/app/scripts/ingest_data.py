"""
Processes and stores all knowledge base documents into Pinecone vector database
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService
from app.services.langchain_service import PineconeService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KnowledgeBaseIngestor:
    """Ingest Morgan State CS knowledge base data into Pinecone vector database"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.pinecone_service = PineconeService()
        self.langchain_service = PineconeService()
        self.knowledge_base_dir = settings.KNOWLEDGE_BASE_DIR
        self.processed_dir = settings.PROCESSED_DIR
        
        # Track processing statistics
        self.stats = {
            "files_processed": 0,
            "documents_created": 0,
            "chunks_generated": 0,
            "vectors_stored": 0,
            "errors": []
        }
    
    async def load_json_files(self) -> List[Dict[str, Any]]:
        """Recursively load and process all JSON files from knowledge base and subfolders"""
        documents = []
        json_files = list(self.knowledge_base_dir.rglob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files to process (recursive)")
        for json_file in json_files:
            try:
                logger.info(f"Processing {json_file}")
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Convert JSON to structured text based on file type
                name = json_file.name
                if "courses" in name:
                    content = self._process_courses_json(data)
                elif "prerequisites" in name:
                    content = self._process_prerequisites_json(data)
                elif "faculty" in name:
                    content = self._process_faculty_json(data)
                elif "deadlines" in name:
                    content = self._process_deadlines_json(data)
                elif "advising" in name:
                    content = self._process_advising_json(data)
                else:
                    content = self._json_to_text(data)
                doc = {
                    "content": content,
                    "metadata": {
                        "source": str(json_file),
                        "type": json_file.stem,
                        "category": self._categorize_file(json_file.stem),
                        "document_id": self._generate_document_id(json_file.stem),
                        "file_size": json_file.stat().st_size,
                        "last_modified": datetime.fromtimestamp(json_file.stat().st_mtime).isoformat(),
                        "content_length": len(content),
                        "ingested_at": datetime.utcnow().isoformat()
                    }
                }
                documents.append(doc)
                self.stats["files_processed"] += 1
                logger.info(f"Successfully loaded {json_file} ({len(content)} characters)")
            except json.JSONDecodeError as e:
                error_msg = f"JSON decode error in {json_file}: {str(e)}"
                logger.error(error_msg)
                self.stats["errors"].append(error_msg)
            except Exception as e:
                error_msg = f"Error loading {json_file}: {str(e)}"
                logger.error(error_msg)
                self.stats["errors"].append(error_msg)
        return documents
    
    async def load_text_files(self) -> List[Dict[str, Any]]:
        """Recursively load and process text files from knowledge base and subfolders"""
        documents = []
        text_files = list(self.knowledge_base_dir.rglob("*.txt"))
        logger.info(f"Found {len(text_files)} text files to process (recursive)")
        for text_file in text_files:
            try:
                logger.info(f"Processing {text_file}")
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if text_file.name == "training_data.txt":
                    content = self._enhance_training_data(content)
                doc = {
                    "content": content,
                    "metadata": {
                        "source": str(text_file),
                        "type": "general_knowledge" if text_file.name == "training_data.txt" else "text",
                        "category": "overview",
                        "document_id": self._generate_document_id(text_file.stem),
                        "file_size": text_file.stat().st_size,
                        "last_modified": datetime.fromtimestamp(text_file.stat().st_mtime).isoformat(),
                        "content_length": len(content),
                        "ingested_at": datetime.utcnow().isoformat()
                    }
                }
                documents.append(doc)
                self.stats["files_processed"] += 1
                logger.info(f"Successfully loaded {text_file} ({len(content)} characters)")
            except Exception as e:
                error_msg = f"Error loading {text_file}: {str(e)}"
                logger.error(error_msg)
                self.stats["errors"].append(error_msg)
        return documents
    
    def _process_courses_json(self, data: Dict) -> str:
        """Process courses.json into structured text"""
        text = "MORGAN STATE UNIVERSITY COMPUTER SCIENCE COURSES\n\n"
        
        if "courses" in data:
            for course in data["courses"]:
                text += f"\nCourse Code: {course.get('course_code', 'N/A')}\n"
                text += f"Title: {course.get('title', 'N/A')}\n"
                text += f"Credits: {course.get('credits', 'N/A')}\n"
                text += f"Description: {course.get('description', 'N/A')}\n"
                text += f"Prerequisites: {', '.join(course.get('prerequisites', ['None']))}\n"
                text += f"Offered: {', '.join(course.get('offered', ['TBA']))}\n"
                text += f"Level: {course.get('level', 'N/A')}\n"
                text += f"Category: {course.get('category', 'N/A')}\n"
                text += "-" * 50 + "\n"
        
        return text
    
    def _process_prerequisites_json(self, data: Dict) -> str:
        """Process prerequisites.json into structured text"""
        text = "COURSE PREREQUISITES AND REQUIREMENTS\n\n"
        
        if "course_prerequisites" in data:
            for course_code, info in data["course_prerequisites"].items():
                text += f"\n{course_code}: {info.get('course_name', 'N/A')}\n"
                text += f"Credits: {info.get('credits', 'N/A')}\n"
                text += f"Prerequisites: {', '.join(info.get('prerequisites', ['None']))}\n"
                text += f"Corequisites: {', '.join(info.get('corequisites', ['None']))}\n"
                text += f"Description: {info.get('description', 'N/A')}\n"
                text += "-" * 50 + "\n"
        
        return text
    
    def _process_faculty_json(self, data: Dict) -> str:
        """Process faculty_staff.json into structured text"""
        text = "MORGAN STATE CS DEPARTMENT FACULTY AND STAFF\n\n"
        
        if "department_chair" in data:
            chair = data["department_chair"]
            text += f"Department Chair: {chair.get('name', 'N/A')}\n"
            text += f"Title: {chair.get('title', 'N/A')}\n"
            text += f"Office: {chair.get('office', 'N/A')}\n"
            text += f"Email: {chair.get('email', 'N/A')}\n"
            text += f"Phone: {chair.get('phone', 'N/A')}\n\n"
        
        if "full_time_faculty" in data:
            text += "FACULTY MEMBERS:\n"
            for faculty in data["full_time_faculty"]:
                text += f"\n{faculty.get('name', 'N/A')}\n"
                text += f"Title: {faculty.get('title', 'N/A')}\n"
                text += f"Office: {faculty.get('office', 'N/A')}\n"
                text += f"Email: {faculty.get('email', 'N/A')}\n"
                text += f"Office Hours: {faculty.get('office_hours', 'N/A')}\n"
                text += f"Research: {', '.join(faculty.get('research_interests', []))}\n"
                text += "-" * 30 + "\n"
        
        return text
    
    def _process_deadlines_json(self, data: Dict) -> str:
        """Process deadlines.json into structured text"""
        text = "IMPORTANT ACADEMIC DEADLINES\n\n"
        
        if "fall_2024" in data:
            text += "FALL 2024 SEMESTER:\n"
            fall = data["fall_2024"]
            if "registration" in fall:
                for key, value in fall["registration"].items():
                    text += f"{key.replace('_', ' ').title()}: {value}\n"
            if "semester_dates" in fall:
                text += "\nImportant Dates:\n"
                for key, value in fall["semester_dates"].items():
                    text += f"{key.replace('_', ' ').title()}: {value}\n"
        
        if "spring_2025" in data:
            text += "\nSPRING 2025 SEMESTER:\n"
            spring = data["spring_2025"]
            if "registration" in spring:
                for key, value in spring["registration"].items():
                    text += f"{key.replace('_', ' ').title()}: {value}\n"
            if "semester_dates" in spring:
                text += "\nImportant Dates:\n"
                for key, value in spring["semester_dates"].items():
                    text += f"{key.replace('_', ' ').title()}: {value}\n"
        
        return text
    
    def _process_advising_json(self, data: Dict) -> str:
        """Process advising_info.json into structured text"""
        text = "ACADEMIC ADVISING INFORMATION\n\n"
        
        if "academic_advisors" in data:
            advisors = data["academic_advisors"]
            if "freshmen_sophomores" in advisors:
                fresh = advisors["freshmen_sophomores"]
                if "primary_advisor" in fresh:
                    advisor = fresh["primary_advisor"]
                    text += f"Freshman/Sophomore Advisor: {advisor.get('name', 'N/A')}\n"
                    text += f"Office: {advisor.get('office', 'N/A')}\n"
                    text += f"Email: {advisor.get('email', 'N/A')}\n"
                    text += f"Phone: {advisor.get('phone', 'N/A')}\n\n"
        
        if "enrollment_pin_system" in data:
            pin_info = data["enrollment_pin_system"]
            text += "ENROLLMENT PIN SYSTEM:\n"
            text += f"Purpose: {pin_info.get('purpose', 'N/A')}\n"
            if "how_it_works" in pin_info:
                text += "How it works:\n"
                for item in pin_info["how_it_works"]:
                    text += f"- {item}\n"
        
        return text
    
    def _enhance_training_data(self, content: str) -> str:
        """Enhance the training_data.txt with additional context"""
        enhanced = "MORGAN STATE UNIVERSITY COMPUTER SCIENCE DEPARTMENT\n"
        enhanced += "COMPREHENSIVE KNOWLEDGE BASE\n"
        enhanced += "=" * 60 + "\n\n"
        enhanced += content
        enhanced += "\n\n" + "=" * 60
        enhanced += "\nLast Updated: " + datetime.utcnow().strftime("%Y-%m-%d")
        return enhanced
    
    def _json_to_text(self, data: Any, indent: int = 0) -> str:
        """Convert JSON data to readable text format"""
        text = ""
        indent_str = "  " * indent
        
        if isinstance(data, dict):
            for key, value in data.items():
                # Format key as readable text
                formatted_key = key.replace('_', ' ').title()
                
                if isinstance(value, (dict, list)):
                    text += f"\n{indent_str}{formatted_key}:\n"
                    text += self._json_to_text(value, indent + 1)
                else:
                    text += f"{indent_str}{formatted_key}: {value}\n"
                    
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    text += self._json_to_text(item, indent)
                else:
                    text += f"{indent_str}- {item}\n"
        else:
            text += f"{indent_str}{str(data)}\n"
        
        return text
    
    def _categorize_file(self, filename: str) -> str:
        """Categorize file based on filename for better organization"""
        categories = {
            "advising": ["advising", "advisor"],
            "courses": ["courses", "prerequisites", "programs"],
            "registration": ["registration", "deadlines", "forms"],
            "career": ["career", "internship", "organizations", "career_prep"],
            "resources": ["tech", "tutoring", "locations", "tech_resources"],
            "people": ["faculty", "staff", "contact", "faculty_staff", "contact_info"]
        }
        
        filename_lower = filename.lower()
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    return category
        
        return "general"
    
    def _generate_document_id(self, content: str) -> str:
        """Generate a unique document ID"""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    async def save_processing_log(self, result: Dict[str, Any]):
        """Save detailed processing log"""
        log_file = self.processed_dir / f"ingestion_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(log_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"Processing log saved to {log_file}")
        except Exception as e:
            logger.error(f"Failed to save processing log: {str(e)}")
    
    async def validate_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate documents before processing"""
        valid_documents = []
        
        for doc in documents:
            if not doc.get("content"):
                logger.warning(f"Skipping document with empty content: {doc.get('metadata', {}).get('source')}")
                continue
            
            if len(doc["content"]) < 10:
                logger.warning(f"Skipping document with minimal content: {doc.get('metadata', {}).get('source')}")
                continue
            
            valid_documents.append(doc)
            self.stats["documents_created"] += 1
        
        logger.info(f"Validated {len(valid_documents)}/{len(documents)} documents")
        return valid_documents
    
    async def ingest_all(self, clear_existing: bool = True):
        """Main ingestion process - ingest all knowledge base data"""
        start_time = datetime.now()
        
        try:
            logger.info("=" * 60)
            logger.info("Morgan State CS Knowledge Base Ingestion Starting...")
            logger.info(f"Knowledge base directory: {self.knowledge_base_dir}")
            logger.info("=" * 60)
            
            # Initialize Pinecone
            logger.info("Initializing Pinecone connection...")
            await self.pinecone_service.initialize()
            
            # Clear existing data if requested
            if clear_existing:
                logger.info("Clearing existing vectors from Pinecone...")
                await self.pinecone_service.delete_vectors(delete_all=True)
                await asyncio.sleep(2)  # Wait for deletion to propagate
            
            # Load all documents
            logger.info("\nLoading knowledge base files...")
            json_docs = await self.load_json_files()
            text_docs = await self.load_text_files()
            all_docs = json_docs + text_docs
            
            logger.info(f"\nTotal files loaded: {len(all_docs)}")
            
            # Validate documents
            valid_docs = await self.validate_documents(all_docs)
            
            if not valid_docs:
                logger.error("No valid documents to process!")
                return {"success": False, "error": "No valid documents"}
            
            # Process documents through LangChain
            logger.info("\nProcessing documents and generating embeddings...")
            logger.info("This may take several minutes...")
            
            result = await self.langchain_service.process_documents(valid_docs)
            
            # Update statistics
            self.stats["chunks_generated"] = result.get("total_chunks", 0)
            self.stats["vectors_stored"] = result.get("vectors_stored", 0)
            
            # Get final Pinecone statistics
            final_stats = await self.pinecone_service.get_stats()
            
            # Prepare comprehensive result
            final_result = {
                "success": True,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "statistics": self.stats,
                "pinecone_stats": final_stats,
                "categories_processed": list(set(doc["metadata"]["category"] for doc in valid_docs))
            }
            
            # Save processing log
            await self.save_processing_log(final_result)
            
            # Print summary
            logger.info("\n" + "=" * 60)
            logger.info("INGESTION COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"Duration: {final_result['duration_seconds']:.2f} seconds")
            logger.info(f"Files Processed: {self.stats['files_processed']}")
            logger.info(f"Documents Created: {self.stats['documents_created']}")
            logger.info(f"Chunks Generated: {self.stats['chunks_generated']}")
            logger.info(f"Vectors Stored: {self.stats['vectors_stored']}")
            logger.info(f"Total Vectors in Index: {final_stats.get('total_vector_count', 0)}")
            
            if self.stats["errors"]:
                logger.warning(f"Errors encountered: {len(self.stats['errors'])}")
                for error in self.stats["errors"]:
                    logger.warning(f"  - {error}")
            
            logger.info("=" * 60)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Ingestion failed with error: {str(e)}")
            error_result = {
                "success": False,
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "statistics": self.stats
            }
            await self.save_processing_log(error_result)
            raise

async def main():
    """Main entry point for the ingestion script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ingest Morgan State CS knowledge base into Pinecone",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ingest_data.py                    # Full ingestion (clears existing data)
  python ingest_data.py --no-clear         # Append mode (keeps existing data)
  python ingest_data.py --test             # Test mode (processes but doesn't save)
        """
    )
    
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Don't clear existing vectors (append mode)"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode - validate files without ingesting"
    )
    
    args = parser.parse_args()
    
    try:
        ingestor = KnowledgeBaseIngestor()
        
        if args.test:
            logger.info("Running in TEST mode - validating files only...")
            json_docs = await ingestor.load_json_files()
            text_docs = await ingestor.load_text_files()
            all_docs = json_docs + text_docs
            valid_docs = await ingestor.validate_documents(all_docs)
            
            print(f"\nTest Results:")
            print(f"  Files found: {ingestor.stats['files_processed']}")
            print(f"  Valid documents: {len(valid_docs)}")
            print(f"  Errors: {len(ingestor.stats['errors'])}")
            
            if ingestor.stats['errors']:
                print("\nErrors encountered:")
                for error in ingestor.stats['errors']:
                    print(f"  - {error}")
        else:
            result = await ingestor.ingest_all(clear_existing=not args.no_clear)
            
            if result["success"]:
                print("\n✓ Ingestion successful!")
                print(f"  Processed {result['statistics']['files_processed']} files")
                print(f"  Created {result['statistics']['vectors_stored']} vectors")
                print(f"  View logs in: {settings.PROCESSED_DIR}")
            else:
                print(f"\n✗ Ingestion failed: {result.get('error')}")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n\nIngestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())