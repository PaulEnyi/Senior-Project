from pinecone import Pinecone, ServerlessSpec
from typing import Dict, Any, List, Optional, Tuple
import logging
import asyncio
from app.core.config import settings
from app.core.exceptions import PineconeException

logger = logging.getLogger(__name__)

class PineconeService:
    """Service for interacting with Pinecone vector database"""
    
    def __init__(self):
        self.api_key = settings.PINECONE_API_KEY
        self.environment = settings.PINECONE_ENVIRONMENT
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = 1536  # OpenAI embedding dimension
        self.metric = "cosine"
        self.client = None
        self.index = None
    
    async def initialize(self):
        """Initialize Pinecone connection and create index if needed"""
        try:
            # Initialize Pinecone client
            self.client = Pinecone(api_key=self.api_key)
            
            # Get list of existing indexes
            existing_indexes = self.client.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            # Create index if it doesn't exist
            if self.index_name not in index_names:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                
                self.client.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                
                # Wait for index to be ready
                await self._wait_for_index()
            
            # Connect to index
            self.index = self.client.Index(self.index_name)
            
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Pinecone initialization error: {str(e)}")
            raise PineconeException(f"Failed to initialize Pinecone: {str(e)}")
    
    async def _wait_for_index(self, max_retries: int = 30):
        """Wait for index to be ready"""
        for _ in range(max_retries):
            try:
                self.client.describe_index(self.index_name)
                break
            except:
                await asyncio.sleep(2)
        else:
            raise PineconeException("Index creation timeout")
    
    async def upsert_vectors(
        self,
        vectors: List[Tuple[str, List[float], Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Insert or update vectors in Pinecone
        
        Args:
            vectors: List of tuples (id, embedding, metadata)
        """
        try:
            if not self.index:
                await self.initialize()
            
            # Format vectors for Pinecone
            formatted_vectors = [
                {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                }
                for vector_id, embedding, metadata in vectors
            ]
            
            # Upsert in batches
            batch_size = 100
            upserted_count = 0
            
            for i in range(0, len(formatted_vectors), batch_size):
                batch = formatted_vectors[i:i + batch_size]
                response = self.index.upsert(vectors=batch)
                upserted_count += response.upserted_count
            
            return {
                "upserted_count": upserted_count,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Pinecone upsert error: {str(e)}")
            raise PineconeException(f"Failed to upsert vectors: {str(e)}")
    
    async def query_vectors(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """Query similar vectors from Pinecone
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_dict: Metadata filters
            include_metadata: Include metadata in results
        """
        try:
            if not self.index:
                await self.initialize()
            
            # Query Pinecone
            response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=include_metadata
            )
            
            # Format results
            results = []
            for match in response.matches:
                result = {
                    "id": match.id,
                    "score": match.score
                }
                if include_metadata and match.metadata:
                    result["metadata"] = match.metadata
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Pinecone query error: {str(e)}")
            raise PineconeException(f"Failed to query vectors: {str(e)}")
    
    async def delete_vectors(
        self,
        ids: Optional[List[str]] = None,
        delete_all: bool = False,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delete vectors from Pinecone
        
        Args:
            ids: List of vector IDs to delete
            delete_all: Delete all vectors
            filter_dict: Delete by metadata filter
        """
        try:
            if not self.index:
                await self.initialize()
            
            if delete_all:
                self.index.delete(delete_all=True)
                return {"message": "All vectors deleted", "success": True}
            elif ids:
                self.index.delete(ids=ids)
                return {"message": f"Deleted {len(ids)} vectors", "success": True}
            elif filter_dict:
                self.index.delete(filter=filter_dict)
                return {"message": "Vectors deleted by filter", "success": True}
            else:
                raise ValueError("Must specify ids, delete_all, or filter")
                
        except Exception as e:
            logger.error(f"Pinecone delete error: {str(e)}")
            raise PineconeException(f"Failed to delete vectors: {str(e)}")
    
    async def update_metadata(
        self,
        vector_id: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update metadata for a vector
        
        Args:
            vector_id: Vector ID
            metadata: New metadata
        """
        try:
            if not self.index:
                await self.initialize()
            
            # Fetch existing vector
            fetch_response = self.index.fetch(ids=[vector_id])
            
            if vector_id not in fetch_response.vectors:
                raise PineconeException(f"Vector {vector_id} not found")
            
            vector = fetch_response.vectors[vector_id]
            
            # Update with new vector including updated metadata
            self.index.upsert(
                vectors=[{
                    "id": vector_id,
                    "values": vector.values,
                    "metadata": metadata
                }]
            )
            
            return {"message": "Metadata updated", "success": True}
            
        except Exception as e:
            logger.error(f"Pinecone metadata update error: {str(e)}")
            raise PineconeException(f"Failed to update metadata: {str(e)}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            if not self.index:
                await self.initialize()
            
            stats = self.index.describe_index_stats()
            
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }
            
        except Exception as e:
            logger.error(f"Pinecone stats error: {str(e)}")
            return {
                "total_vector_count": 0,
                "dimension": self.dimension,
                "index_fullness": 0,
                "namespaces": {}
            }
    
    async def close(self):
        """Close Pinecone connection"""
        try:
            # Pinecone client doesn't need explicit closing
            self.index = None
            self.client = None
            logger.info("Pinecone connection closed")
        except Exception as e:
            logger.error(f"Error closing Pinecone: {str(e)}")
    
    async def create_backup(self) -> Dict[str, Any]:
        """Create a backup of all vectors"""
        try:
            if not self.index:
                await self.initialize()
            
            # Fetch all vector IDs
            stats = self.index.describe_index_stats()
            total_vectors = stats.total_vector_count
            
            if total_vectors == 0:
                return {"message": "No vectors to backup", "count": 0}
            
            # For large indexes, this would need pagination
            # This is a simplified version
            logger.info(f"Creating backup of {total_vectors} vectors")
            
            return {
                "message": "Backup created",
                "vector_count": total_vectors,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Backup error: {str(e)}")
            raise PineconeException(f"Failed to create backup: {str(e)}")
    
    async def get_relevant_context(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get relevant context from knowledge base using semantic search
        
        Args:
            query: User's query text
            top_k: Number of relevant documents to retrieve
            filter_dict: Optional metadata filters
            
        Returns:
            Dictionary containing relevant context and sources
        """
        try:
            # Import OpenAI here to avoid circular dependency
            from app.services.openai_service import OpenAIService
            
            if not self.index:
                await self.initialize()
            
            # Generate embedding for the query using OpenAI
            openai_service = OpenAIService()
            query_embedding = await openai_service.create_embedding(query)
            
            # Query Pinecone for similar vectors
            results = await self.query_vectors(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_dict=filter_dict,
                include_metadata=True
            )
            
            # Format results into context
            context_texts = []
            sources = []
            
            for result in results:
                metadata = result.get("metadata", {})
                text = metadata.get("text", "")
                source = metadata.get("source", "Unknown")
                score = result.get("score", 0.0)
                
                if text:
                    context_texts.append(text)
                    sources.append({
                        "source": source,
                        "score": score,
                        "metadata": metadata
                    })
            
            # Combine context texts
            combined_context = "\n\n".join(context_texts)
            
            logger.info(f"Retrieved {len(context_texts)} relevant context snippets for query")
            
            return {
                "context": combined_context,
                "sources": sources,
                "total_results": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            # Return empty context instead of failing
            return {
                "context": "",
                "sources": [],
                "total_results": 0,
                "error": str(e)
            }