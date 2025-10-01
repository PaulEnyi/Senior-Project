import pinecone
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional, Tuple
import logging
import json
import uuid
from ..core.config import settings
from ..core.exceptions import PineconeServiceException

logger = logging.getLogger(__name__)

class PineconeService:
    """Service for handling Pinecone vector database operations"""
    
    def __init__(self):
        self.client = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = 1536  # OpenAI ada-002 embedding dimension
        self.index = None
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize Pinecone index"""
        try:
            # Check if index exists
            if self.index_name not in [index.name for index in self.client.list_indexes()]:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.client.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.PINECONE_ENVIRONMENT
                    )
                )
            
            self.index = self.client.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {str(e)}")
            raise PineconeServiceException(f"Failed to initialize Pinecone: {str(e)}")
    
    async def test_connection(self) -> bool:
        """Test Pinecone connection"""
        try:
            stats = self.index.describe_index_stats()
            logger.info(f"Pinecone connection successful. Index stats: {stats}")
            return True
        except Exception as e:
            logger.error(f"Pinecone connection failed: {str(e)}")
            raise PineconeServiceException(f"Failed to connect to Pinecone: {str(e)}")
    
    async def upsert_documents(
        self, 
        documents: List[Dict[str, Any]], 
        embeddings: List[List[float]],
        batch_size: int = 100
    ) -> bool:
        """Upsert documents with their embeddings to Pinecone"""
        try:
            if len(documents) != len(embeddings):
                raise ValueError("Number of documents must match number of embeddings")
            
            # Prepare vectors for upsert
            vectors = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                vector_id = doc.get('id', str(uuid.uuid4()))
                
                # Prepare metadata (Pinecone has limitations on metadata)
                metadata = {
                    'content': doc.get('content', '')[:40000],  # Limit content length
                    'category': doc.get('category', 'general'),
                    'source': doc.get('source', 'unknown'),
                    'title': doc.get('title', '')[:1000],  # Limit title length
                    'last_updated': doc.get('last_updated', ''),
                }
                
                # Remove empty values to save space
                metadata = {k: v for k, v in metadata.items() if v}
                
                vectors.append({
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata
                })
            
            # Upsert in batches
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
                logger.info(f"Upserted batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1}")
            
            logger.info(f"Successfully upserted {len(vectors)} documents to Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert documents: {str(e)}")
            raise PineconeServiceException(f"Failed to upsert documents: {str(e)}")
    
    async def similarity_search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity"""
        try:
            # Prepare filter
            filter_dict = {}
            if category_filter:
                filter_dict['category'] = {'$eq': category_filter}
            
            # Perform search
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )
            
            # Format results
            results = []
            for match in search_results.matches:
                result = {
                    'id': match.id,
                    'score': float(match.score),
                    'content': match.metadata.get('content', ''),
                    'category': match.metadata.get('category', 'general'),
                    'source': match.metadata.get('source', 'unknown'),
                    'title': match.metadata.get('title', ''),
                    'last_updated': match.metadata.get('last_updated', '')
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {str(e)}")
            raise PineconeServiceException(f"Failed to search documents: {str(e)}")
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents by their IDs"""
        try:
            self.index.delete(ids=document_ids)
            logger.info(f"Deleted {len(document_ids)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {str(e)}")
            raise PineconeServiceException(f"Failed to delete documents: {str(e)}")
    
    async def clear_index(self) -> bool:
        """Clear all documents from the index"""
        try:
            self.index.delete(delete_all=True)
            logger.info("Cleared all documents from Pinecone index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear index: {str(e)}")
            raise PineconeServiceException(f"Failed to clear index: {str(e)}")
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness,
                'namespaces': dict(stats.namespaces) if stats.namespaces else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            raise PineconeServiceException(f"Failed to get index stats: {str(e)}")
    
    async def search_by_text_query(
        self, 
        query: str, 
        openai_service,  # Import here to avoid circular imports
        top_k: int = 5,
        category_filter: Optional[str] = None,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search documents by text query (generates embedding first)"""
        try:
            # Generate embedding for the query
            query_embedding = await openai_service.generate_single_embedding(query)
            
            # Perform similarity search
            results = await self.similarity_search(
                query_embedding=query_embedding,
                top_k=top_k,
                category_filter=category_filter
            )
            
            # Filter by similarity threshold
            filtered_results = [
                result for result in results 
                if result['score'] >= similarity_threshold
            ]
            
            logger.info(f"Found {len(filtered_results)} documents above threshold {similarity_threshold}")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Failed to search by text query: {str(e)}")
            raise PineconeServiceException(f"Failed to search by text: {str(e)}")
    
    async def batch_search(
        self, 
        queries: List[str], 
        openai_service,
        top_k: int = 5
    ) -> List[List[Dict[str, Any]]]:
        """Perform batch search for multiple queries"""
        try:
            # Generate embeddings for all queries
            query_embeddings = await openai_service.generate_embeddings(queries)
            
            # Perform searches
            all_results = []
            for i, embedding in enumerate(query_embeddings):
                results = await self.similarity_search(
                    query_embedding=embedding,
                    top_k=top_k
                )
                all_results.append(results)
                logger.debug(f"Batch search {i+1}/{len(queries)} completed")
            
            return all_results
            
        except Exception as e:
            logger.error(f"Failed to perform batch search: {str(e)}")
            raise PineconeServiceException(f"Failed to perform batch search: {str(e)}")
    
    def get_categories(self) -> List[str]:
        """Get list of available document categories"""
        # This would ideally be cached or stored separately
        # For now, return the expected categories for Morgan State CS
        return [
            'department_info',
            'faculty_staff', 
            'academics',
            'courses',
            'programs',
            'student_resources',
            'organizations',
            'career_prep',
            'administrative',
            'registration',
            'advising',
            'general'
        ]