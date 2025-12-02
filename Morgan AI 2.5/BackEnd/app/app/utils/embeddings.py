"""
Functions for generating, processing, and manipulating text embeddings

"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
import hashlib
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class EmbeddingUtils:
    """Utility functions for embedding operations"""
    
    @staticmethod
    def normalize_embedding(embedding: List[float]) -> List[float]:
        """Normalize an embedding vector to unit length"""
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return (np.array(embedding) / norm).tolist()
    
    @staticmethod
    def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Reshape for sklearn
            e1 = np.array(embedding1).reshape(1, -1)
            e2 = np.array(embedding2).reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(e1, e2)[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    @staticmethod
    def batch_similarities(
        query_embedding: List[float],
        embeddings: List[List[float]]
    ) -> List[float]:
        """Calculate similarities for a batch of embeddings"""
        try:
            query = np.array(query_embedding).reshape(1, -1)
            batch = np.array(embeddings)
            
            similarities = cosine_similarity(query, batch)[0]
            return similarities.tolist()
            
        except Exception as e:
            logger.error(f"Error in batch similarity calculation: {str(e)}")
            return []
    
    @staticmethod
    def average_embeddings(embeddings: List[List[float]]) -> List[float]:
        """Calculate the average of multiple embeddings"""
        if not embeddings:
            return []
        
        try:
            avg = np.mean(embeddings, axis=0)
            return avg.tolist()
            
        except Exception as e:
            logger.error(f"Error averaging embeddings: {str(e)}")
            return embeddings[0] if embeddings else []
    
    @staticmethod
    def weighted_average_embeddings(
        embeddings: List[List[float]],
        weights: List[float]
    ) -> List[float]:
        """Calculate weighted average of embeddings"""
        if not embeddings or not weights:
            return []
        
        if len(embeddings) != len(weights):
            logger.warning("Embeddings and weights length mismatch")
            return EmbeddingUtils.average_embeddings(embeddings)
        
        try:
            # Normalize weights
            weights = np.array(weights)
            weights = weights / weights.sum()
            
            # Calculate weighted average
            weighted_avg = np.average(embeddings, axis=0, weights=weights)
            return weighted_avg.tolist()
            
        except Exception as e:
            logger.error(f"Error in weighted average: {str(e)}")
            return embeddings[0] if embeddings else []
    
    @staticmethod
    def find_most_similar(
        query_embedding: List[float],
        embeddings: List[Tuple[str, List[float]]],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Tuple[str, float]]:
        """Find most similar embeddings from a collection"""
        results = []
        
        for id, embedding in embeddings:
            similarity = EmbeddingUtils.calculate_similarity(query_embedding, embedding)
            if similarity >= threshold:
                results.append((id, similarity))
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
    
    @staticmethod
    def cluster_embeddings(
        embeddings: List[List[float]],
        n_clusters: int = 5
    ) -> Dict[int, List[int]]:
        """Simple clustering of embeddings using k-means"""
        try:
            from sklearn.cluster import KMeans
            
            if len(embeddings) < n_clusters:
                n_clusters = len(embeddings)
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(embeddings)
            
            # Group indices by cluster
            clusters = {}
            for idx, label in enumerate(labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(idx)
            
            return clusters
            
        except ImportError:
            logger.warning("sklearn not available for clustering")
            return {0: list(range(len(embeddings)))}
        except Exception as e:
            logger.error(f"Clustering error: {str(e)}")
            return {0: list(range(len(embeddings)))}
    
    @staticmethod
    def generate_embedding_id(text: str) -> str:
        """Generate a unique ID for an embedding based on text content"""
        return hashlib.md5(text.encode()).hexdigest()[:16]
    
    @staticmethod
    def validate_embedding(embedding: List[float], expected_dim: int = 1536) -> bool:
        """Validate an embedding vector"""
        if not embedding:
            return False
        
        if len(embedding) != expected_dim:
            logger.warning(f"Embedding dimension mismatch: {len(embedding)} != {expected_dim}")
            return False
        
        if not all(isinstance(x, (int, float)) for x in embedding):
            logger.warning("Embedding contains non-numeric values")
            return False
        
        if all(x == 0 for x in embedding):
            logger.warning("Embedding is all zeros")
            return False
        
        return True
    
    @staticmethod
    def compress_embedding(
        embedding: List[float],
        precision: int = 4
    ) -> str:
        """Compress embedding for storage"""
        try:
            # Round to specified precision
            compressed = [round(x, precision) for x in embedding]
            
            # Convert to JSON string
            return json.dumps(compressed)
            
        except Exception as e:
            logger.error(f"Error compressing embedding: {str(e)}")
            return json.dumps(embedding)
    
    @staticmethod
    def decompress_embedding(compressed: str) -> List[float]:
        """Decompress stored embedding"""
        try:
            return json.loads(compressed)
        except Exception as e:
            logger.error(f"Error decompressing embedding: {str(e)}")
            return []
    
    @staticmethod
    def reduce_dimensionality(
        embeddings: List[List[float]],
        target_dim: int = 256
    ) -> List[List[float]]:
        """Reduce embedding dimensionality using PCA"""
        try:
            from sklearn.decomposition import PCA
            
            if len(embeddings) < target_dim:
                logger.warning(f"Not enough samples for PCA reduction to {target_dim}")
                return embeddings
            
            pca = PCA(n_components=target_dim)
            reduced = pca.fit_transform(embeddings)
            
            logger.info(f"Reduced embeddings from {len(embeddings[0])} to {target_dim} dimensions")
            logger.info(f"Explained variance ratio: {sum(pca.explained_variance_ratio_):.2f}")
            
            return reduced.tolist()
            
        except ImportError:
            logger.warning("sklearn not available for PCA")
            return embeddings
        except Exception as e:
            logger.error(f"Dimensionality reduction error: {str(e)}")
            return embeddings
    
    @staticmethod
    def create_embedding_metadata(
        text: str,
        embedding: List[float],
        source: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create metadata for an embedding"""
        return {
            "id": EmbeddingUtils.generate_embedding_id(text),
            "text_length": len(text),
            "embedding_dim": len(embedding),
            "embedding_norm": float(np.linalg.norm(embedding)),
            "source": source,
            "created_at": datetime.utcnow().isoformat(),
            **kwargs
        }

class EmbeddingCache:
    """Simple in-memory cache for embeddings"""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}
        self.created_at = {}
    
    def get(self, key: str) -> Optional[List[float]]:
        """Get embedding from cache"""
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        return None
    
    def set(self, key: str, embedding: List[float]):
        """Store embedding in cache"""
        # Check cache size
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        self.cache[key] = embedding
        self.access_count[key] = 0
        self.created_at[key] = datetime.utcnow()
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if not self.cache:
            return
        
        # Find LRU item
        lru_key = min(self.access_count.keys(), key=lambda k: self.access_count[k])
        
        # Remove from cache
        del self.cache[lru_key]
        del self.access_count[lru_key]
        del self.created_at[lru_key]
    
    def clear(self):
        """Clear the cache"""
        self.cache.clear()
        self.access_count.clear()
        self.created_at.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "total_accesses": sum(self.access_count.values()),
            "avg_accesses": np.mean(list(self.access_count.values())) if self.access_count else 0
        }
