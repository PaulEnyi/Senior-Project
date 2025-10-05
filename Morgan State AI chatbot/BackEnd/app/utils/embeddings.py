import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from sentence_transformers import SentenceTransformer
import asyncio
from functools import lru_cache
import hashlib
import json

from ..core.config import settings
from ..core.exceptions import OpenAIServiceException

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Utility class for generating and managing text embeddings"""
    
    def __init__(self):
        self.openai_model = settings.OPENAI_EMBEDDING_MODEL
        self.dimension = 1536  # OpenAI ada-002 dimension
        self.cache = {}  # Simple in-memory cache
        self.max_cache_size = 1000
        
        # Initialize local embedding model as fallback
        self.local_model = None
        self._initialize_local_model()
    
    def _initialize_local_model(self):
        """Initialize local sentence transformer as backup"""
        try:
            self.local_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Local embedding model initialized as fallback")
        except Exception as e:
            logger.warning(f"Could not initialize local embedding model: {str(e)}")
    
    def _get_cache_key(self, text: str, model: str) -> str:
        """Generate cache key for text embedding"""
        content = f"{text}:{model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _manage_cache_size(self):
        """Keep cache size under limit"""
        if len(self.cache) > self.max_cache_size:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self.cache.keys())[:100]
            for key in keys_to_remove:
                del self.cache[key]
    
    async def generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        try:
            from ..services.openai_service import OpenAIService
            
            # Check cache first
            cache_key = self._get_cache_key(text, self.openai_model)
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            openai_service = OpenAIService()
            embedding = await openai_service.generate_single_embedding(text)
            
            # Cache the result
            self.cache[cache_key] = embedding
            self._manage_cache_size()
            
            return embedding
            
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {str(e)}")
            raise OpenAIServiceException(f"Failed to generate OpenAI embedding: {str(e)}")
    
    def generate_local_embedding(self, text: str) -> List[float]:
        """Generate embedding using local model"""
        try:
            if self.local_model is None:
                raise Exception("Local embedding model not available")
            
            # Check cache first
            cache_key = self._get_cache_key(text, "local")
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            embedding = self.local_model.encode(text, convert_to_tensor=False)
            embedding_list = embedding.tolist()
            
            # Cache the result
            self.cache[cache_key] = embedding_list
            self._manage_cache_size()
            
            return embedding_list
            
        except Exception as e:
            logger.error(f"Local embedding generation failed: {str(e)}")
            raise Exception(f"Failed to generate local embedding: {str(e)}")
    
    async def generate_embedding_with_fallback(self, text: str, prefer_openai: bool = True) -> Tuple[List[float], str]:
        """Generate embedding with fallback strategy"""
        if prefer_openai:
            try:
                embedding = await self.generate_openai_embedding(text)
                return embedding, "openai"
            except Exception as e:
                logger.warning(f"OpenAI embedding failed, falling back to local: {str(e)}")
                try:
                    embedding = self.generate_local_embedding(text)
                    return embedding, "local"
                except Exception as e2:
                    logger.error(f"Both embedding methods failed: OpenAI: {str(e)}, Local: {str(e2)}")
                    raise Exception("All embedding generation methods failed")
        else:
            try:
                embedding = self.generate_local_embedding(text)
                return embedding, "local"
            except Exception as e:
                logger.warning(f"Local embedding failed, trying OpenAI: {str(e)}")
                try:
                    embedding = await self.generate_openai_embedding(text)
                    return embedding, "openai"
                except Exception as e2:
                    logger.error(f"Both embedding methods failed: Local: {str(e)}, OpenAI: {str(e2)}")
                    raise Exception("All embedding generation methods failed")
    
    async def generate_batch_embeddings(
        self, 
        texts: List[str], 
        batch_size: int = 20,
        prefer_openai: bool = True
    ) -> List[Tuple[List[float], str]]:
        """Generate embeddings for multiple texts in batches"""
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = []
            
            for text in batch:
                try:
                    embedding, method = await self.generate_embedding_with_fallback(
                        text, prefer_openai
                    )
                    batch_results.append((embedding, method))
                except Exception as e:
                    logger.error(f"Failed to generate embedding for text: {text[:50]}... Error: {str(e)}")
                    # Use zero vector as fallback
                    zero_embedding = [0.0] * (self.dimension if prefer_openai else 384)
                    batch_results.append((zero_embedding, "error"))
            
            results.extend(batch_results)
            
            # Small delay between batches to avoid rate limiting
            if i + batch_size < len(texts):
                await asyncio.sleep(0.1)
        
        logger.info(f"Generated {len(results)} embeddings for batch of {len(texts)} texts")
        return results
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            return 0.0
    
    def find_most_similar(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """Find most similar embeddings to query"""
        try:
            similarities = []
            
            for i, candidate in enumerate(candidate_embeddings):
                similarity = self.calculate_similarity(query_embedding, candidate)
                similarities.append((i, similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            return []
    
    def normalize_embedding(self, embedding: List[float]) -> List[float]:
        """Normalize embedding to unit length"""
        try:
            vec = np.array(embedding)
            norm = np.linalg.norm(vec)
            
            if norm == 0:
                return embedding
            
            normalized = vec / norm
            return normalized.tolist()
            
        except Exception as e:
            logger.error(f"Embedding normalization failed: {str(e)}")
            return embedding
    
    def get_embedding_stats(self, embeddings: List[List[float]]) -> Dict[str, Any]:
        """Calculate statistics for a set of embeddings"""
        try:
            if not embeddings:
                return {"count": 0}
            
            embeddings_array = np.array(embeddings)
            
            stats = {
                "count": len(embeddings),
                "dimension": len(embeddings[0]),
                "mean_norm": float(np.mean([np.linalg.norm(emb) for emb in embeddings])),
                "std_norm": float(np.std([np.linalg.norm(emb) for emb in embeddings])),
                "mean_values": np.mean(embeddings_array, axis=0).tolist()[:10],  # First 10 dims
                "std_values": np.std(embeddings_array, axis=0).tolist()[:10]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Embedding stats calculation failed: {str(e)}")
            return {"count": len(embeddings), "error": str(e)}
    
    def save_embeddings_to_file(self, embeddings: List[List[float]], filepath: str):
        """Save embeddings to numpy file"""
        try:
            embeddings_array = np.array(embeddings)
            np.save(filepath, embeddings_array)
            logger.info(f"Saved {len(embeddings)} embeddings to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save embeddings: {str(e)}")
            raise e
    
    def load_embeddings_from_file(self, filepath: str) -> List[List[float]]:
        """Load embeddings from numpy file"""
        try:
            embeddings_array = np.load(filepath)
            embeddings = embeddings_array.tolist()
            logger.info(f"Loaded {len(embeddings)} embeddings from {filepath}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to load embeddings: {str(e)}")
            raise e
    
    def clear_cache(self):
        """Clear the embedding cache"""
        self.cache.clear()
        logger.info("Embedding cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the embedding cache"""
        return {
            "cache_size": len(self.cache),
            "max_cache_size": self.max_cache_size,
            "cache_keys": list(self.cache.keys())[:10]  # First 10 keys for debugging
        }

# Global instance
embedding_generator = EmbeddingGenerator()