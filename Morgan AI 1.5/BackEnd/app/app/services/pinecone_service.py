from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PineconeService:
    """Service for managing Pinecone vector database operations"""
    
    def __init__(self):
        """Initialize Pinecone client with API key"""
        try:
            # NEW API (pinecone-client 5.0+)
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.index_name = settings.PINECONE_INDEX_NAME
            self.dimension = 1536  # OpenAI text-embedding-ada-002 dimension
            
            # Initialize or connect to index
            self._ensure_index_exists()
            self.index = self.pc.Index(self.index_name)
            
            logger.info(f"✓ Pinecone initialized successfully with index: {self.index_name}")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Pinecone: {str(e)}")
            raise
    
    def _ensure_index_exists(self):
        """Create index if it doesn't exist"""
        try:
            # Get list of existing indexes
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                
                # Create index with serverless spec
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'  # Change to your preferred region
                    )
                )
                logger.info(f"✓ Index '{self.index_name}' created successfully")
            else:
                logger.info(f"✓ Index '{self.index_name}' already exists")
                
        except Exception as e:
            logger.error(f"✗ Error ensuring index exists: {str(e)}")
            raise
    
    def upsert_vectors(
        self,
        vectors: List[tuple],
        namespace: str = "morgan-cs-dept"
    ) -> Dict[str, Any]:
        """
        Upsert vectors into Pinecone index
        
        Args:
            vectors: List of (id, embedding, metadata) tuples
            namespace: Namespace for organizing vectors
            
        Returns:
            Response from Pinecone upsert operation
        """
        try:
            # Format vectors for Pinecone
            formatted_vectors = [
                {
                    "id": vec_id,
                    "values": embedding,
                    "metadata": metadata
                }
                for vec_id, embedding, metadata in vectors
            ]
            
            # Upsert in batches of 100
            batch_size = 100
            total_upserted = 0
            
            for i in range(0, len(formatted_vectors), batch_size):
                batch = formatted_vectors[i:i + batch_size]
                response = self.index.upsert(
                    vectors=batch,
                    namespace=namespace
                )
                total_upserted += len(batch)
                logger.info(f"Upserted batch {i//batch_size + 1}: {len(batch)} vectors")
            
            logger.info(f"✓ Total vectors upserted: {total_upserted}")
            return {"upserted_count": total_upserted}
            
        except Exception as e:
            logger.error(f"✗ Error upserting vectors: {str(e)}")
            raise
    
    def query_vectors(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        namespace: str = "morgan-cs-dept",
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query similar vectors from Pinecone
        
        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            namespace: Namespace to query
            filter: Metadata filter (optional)
            
        Returns:
            List of matching results with scores and metadata
        """
        try:
            response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=True
            )
            
            results = []
            for match in response.matches:
                results.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            logger.info(f"✓ Query returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"✗ Error querying vectors: {str(e)}")
            raise
    
    def delete_vectors(
        self,
        ids: Optional[List[str]] = None,
        delete_all: bool = False,
        namespace: str = "morgan-cs-dept"
    ) -> Dict[str, Any]:
        """
        Delete vectors from index
        
        Args:
            ids: List of vector IDs to delete
            delete_all: If True, delete all vectors in namespace
            namespace: Namespace to delete from
            
        Returns:
            Deletion response
        """
        try:
            if delete_all:
                self.index.delete(delete_all=True, namespace=namespace)
                logger.info(f"✓ Deleted all vectors from namespace: {namespace}")
                return {"deleted": "all"}
            elif ids:
                self.index.delete(ids=ids, namespace=namespace)
                logger.info(f"✓ Deleted {len(ids)} vectors")
                return {"deleted_count": len(ids)}
            else:
                logger.warning("No vectors specified for deletion")
                return {"deleted_count": 0}
                
        except Exception as e:
            logger.error(f"✗ Error deleting vectors: {str(e)}")
            raise
    
    def get_index_stats(self, namespace: str = "morgan-cs-dept") -> Dict[str, Any]:
        """
        Get statistics about the index
        
        Args:
            namespace: Namespace to get stats for
            
        Returns:
            Index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            
            # Extract namespace-specific stats if available
            namespace_stats = None
            if hasattr(stats, 'namespaces') and namespace in stats.namespaces:
                namespace_stats = stats.namespaces[namespace]
            
            result = {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespace_stats": namespace_stats
            }
            
            logger.info(f"✓ Retrieved index stats: {result}")
            return result
            
        except Exception as e:
            logger.error(f"✗ Error getting index stats: {str(e)}")
            raise
    
    def list_indexes(self) -> List[str]:
        """List all available indexes"""
        try:
            indexes = [index.name for index in self.pc.list_indexes()]
            logger.info(f"✓ Found {len(indexes)} indexes")
            return indexes
        except Exception as e:
            logger.error(f"✗ Error listing indexes: {str(e)}")
            raise


# Singleton instance
_pinecone_service = None


def get_pinecone_service() -> PineconeService:
    """Get or create PineconeService singleton"""
    global _pinecone_service
    if _pinecone_service is None:
        _pinecone_service = PineconeService()
    return _pinecone_service


# Example usage
if __name__ == "__main__":
    # Test the service
    service = get_pinecone_service()
    
    # Get index stats
    stats = service.get_index_stats()
    print(f"Index Stats: {stats}")
    
    # List all indexes
    indexes = service.list_indexes()
    print(f"Available Indexes: {indexes}")
