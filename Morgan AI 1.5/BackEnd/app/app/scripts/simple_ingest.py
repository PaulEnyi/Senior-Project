"""
Simple script to ingest knowledge base data into Pinecone
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.openai_service import OpenAIService
from app.services.langchain_service import PineconeService as LangchainPineconeService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def ingest_training_data():
    """Ingest the training_data.txt file into Pinecone"""
    try:
        logger.info("Starting knowledge base ingestion...")
        
        # Initialize services
        openai_service = OpenAIService()
        pinecone_service = LangchainPineconeService()
        
        # Initialize Pinecone connection
        await pinecone_service.initialize()
        logger.info("✓ Pinecone initialized")
        
        # Read training data
        training_file = Path("/app/app/data/knowledge_base/training_data.txt")
        if not training_file.exists():
            logger.error(f"Training file not found: {training_file}")
            return
        
        logger.info(f"Reading {training_file}...")
        with open(training_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"Read {len(content)} characters")
        
        # Split content into chunks (by sections or paragraphs)
        chunks = []
        current_chunk = []
        current_size = 0
        max_chunk_size = 1000  # characters
        
        for line in content.split('\n'):
            line_size = len(line)
            
            # If adding this line would exceed max size, save current chunk
            if current_size + line_size > max_chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        # Add last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Process each chunk
        vectors_to_upsert = []
        
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            
            # Generate embedding
            logger.info(f"Processing chunk {i+1}/{len(chunks)}...")
            embedding = await openai_service.generate_embedding(chunk)
            
            # Create vector with metadata
            vector = (
                f"chunk_{i}",
                embedding,
                {
                    "text": chunk,
                    "source": "training_data.txt",
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            )
            vectors_to_upsert.append(vector)
        
        logger.info(f"Generated {len(vectors_to_upsert)} vectors")
        
        # Upsert to Pinecone
        if vectors_to_upsert:
            logger.info("Upserting vectors to Pinecone...")
            result = await pinecone_service.upsert_vectors(vectors_to_upsert)
            logger.info(f"✓ Upserted {result.get('upserted_count', 0)} vectors")
        
        # Get stats
        stats = await pinecone_service.get_stats()
        logger.info(f"✓ Total vectors in index: {stats.get('total_vector_count', 0)}")
        
        logger.info("✓ Ingestion complete!")
        
    except Exception as e:
        logger.error(f"✗ Ingestion failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(ingest_training_data())
