import asyncio
import logging
import sys
sys.path.append('..')

from app.core.config import settings
from app.services.pinecone_service import PineconeService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_pinecone():
    """Initialize Pinecone index for the chatbot"""
    try:
        logger.info("Setting up Pinecone index...")
        
        # Initialize Pinecone service
        pinecone_service = PineconeService()
        await pinecone_service.initialize()
        
        # Get index stats
        stats = await pinecone_service.get_stats()
        logger.info(f"Pinecone index stats: {stats}")
        
        logger.info("Pinecone setup complete!")
        return True
        
    except Exception as e:
        logger.error(f"Pinecone setup failed: {str(e)}")
        return False

async def verify_setup():
    """Verify that Pinecone is properly configured"""
    try:
        logger.info("Verifying Pinecone setup...")
        
        pinecone_service = PineconeService()
        await pinecone_service.initialize()
        
        # Test query
        test_embedding = [0.1] * 1536  # Dummy embedding
        results = await pinecone_service.query_vectors(
            query_embedding=test_embedding,
            top_k=1
        )
        
        logger.info(f"Test query successful. Index is operational.")
        return True
        
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Pinecone for Morgan Chatbot")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify existing setup"
    )
    
    args = parser.parse_args()
    
    if args.verify:
        success = asyncio.run(verify_setup())
    else:
        success = asyncio.run(setup_pinecone())
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()