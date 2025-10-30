"""
Test RAG retrieval from Pinecone
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.services.langchain_service import PineconeService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_rag():
    """Test retrieving relevant context"""
    try:
        logger.info("Testing RAG retrieval...")
        
        pinecone_service = PineconeService()
        await pinecone_service.initialize()
        
        # Test query
        query = "Who are the faculty members in Computer Science?"
        
        logger.info(f"Query: {query}")
        logger.info("Getting relevant context...")
        
        result = await pinecone_service.get_relevant_context(query, top_k=3)
        
        logger.info(f"\n{'='*80}")
        logger.info("RESULTS:")
        logger.info(f"{'='*80}")
        logger.info(f"Total results: {result.get('total_results', 0)}")
        logger.info(f"\nContext:\n{result.get('context', 'No context found')[:500]}...")
        logger.info(f"\n{'='*80}")
        logger.info(f"Sources: {len(result.get('sources', []))}")
        
        for i, source in enumerate(result.get('sources', [])[:3]):
            logger.info(f"\nSource {i+1}:")
            logger.info(f"  Score: {source.get('score', 0):.4f}")
            logger.info(f"  Text: {source.get('metadata', {}).get('text', '')[:200]}...")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_rag())
