"""
Simple script to ingest knowledge base into Pinecone
"""
import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.openai_service import OpenAIService
from app.services.pinecone_service import get_pinecone_service

async def main():
    print("=== Morgan AI Knowledge Base Simple Ingestion ===\n")
    
    # Initialize services
    openai_service = OpenAIService()
    pinecone_service = get_pinecone_service()
    
    # Load all knowledge base files
    knowledge_base_dir = Path("data/knowledge_base")
    all_files = list(knowledge_base_dir.rglob("*.json")) + list(knowledge_base_dir.rglob("*.txt"))
    
    print(f"Found {len(all_files)} files to process\n")
    
    vectors_to_upsert = []
    
    for file_path in all_files:
        print(f"Processing: {file_path.name}")
        
        try:
            # Read file content
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Convert JSON to text
                content = json.dumps(data, indent=2)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Skip empty content
            if not content or len(content.strip()) < 10:
                print(f"  Skipped (empty or too short)")
                continue
            
            # Generate embedding
            embedding = await openai_service.generate_embedding(content)
            
            # Create vector ID and metadata
            vector_id = f"{file_path.stem}_{hash(content) % 10000}"
            metadata = {
                "text": content[:2000],  # Store first 2000 chars in metadata
                "source": str(file_path),
                "type": file_path.stem,
                "file_type": file_path.suffix
            }
            
            vectors_to_upsert.append((vector_id, embedding, metadata))
            print(f"  ✓ Generated embedding ({len(content)} chars)")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Upsert to Pinecone
    if vectors_to_upsert:
        print(f"\nUpserting {len(vectors_to_upsert)} vectors to Pinecone...")
        result = pinecone_service.upsert_vectors(vectors_to_upsert)
        print(f"✓ Upserted {result['upserted_count']} vectors")
        
        # Get stats
        stats = pinecone_service.get_index_stats()
        print(f"\nIndex Stats:")
        print(f"  Total vectors: {stats['total_vector_count']}")
        print(f"  Dimension: {stats['dimension']}")
    else:
        print("\n✗ No vectors to upsert")
    
    print("\n=== Ingestion Complete ===")

if __name__ == "__main__":
    asyncio.run(main())
