#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Resilient Embedding Service - Provides fallback mechanisms for embedding operations
Automatically handles OpenAI API failures with local embedding alternatives
"""

import logging
import random
import numpy as np
from typing import List, Dict, Any, Optional, Union
from openai import APIConnectionError, APITimeoutError, RateLimitError, AuthenticationError

from isa_model.inference.services.embedding.openai_embed_service import OpenAIEmbedService
from isa_model.inference.services.embedding.base_embed_service import BaseEmbedService

logger = logging.getLogger(__name__)

class ResilientEmbedService(BaseEmbedService):
    """
    Resilient embedding service with automatic fallback mechanisms
    
    When OpenAI service fails, automatically falls back to:
    1. Simple TF-IDF based embeddings
    2. Random embeddings (for testing/demo purposes)
    """
    
    def __init__(self, provider_name: str = "openai", model_name: str = "text-embedding-3-small", **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        # Try to initialize OpenAI service
        self.primary_service = None
        self.fallback_mode = False
        
        try:
            self.primary_service = OpenAIEmbedService(provider_name, model_name, **kwargs)
            logger.info("✅ Primary OpenAI embedding service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI service, starting in fallback mode: {e}")
            self.fallback_mode = True
        
        # Initialize TF-IDF vectorizer for fallback
        self._init_fallback_vectorizer()
    
    def _init_fallback_vectorizer(self):
        """Initialize TF-IDF vectorizer for fallback embeddings"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            # Use a simple TF-IDF vectorizer with limited features
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1536,  # Match OpenAI dimensions
                stop_words='english',
                ngram_range=(1, 2),
                lowercase=True,
                strip_accents='unicode'
            )
            
            # Pre-fit with some common words to ensure consistency
            common_words = [
                "hello world", "machine learning", "artificial intelligence",
                "data science", "natural language processing", "computer vision",
                "deep learning", "neural networks", "text analysis",
                "information retrieval", "semantic search", "embeddings"
            ]
            self.tfidf_vectorizer.fit(common_words)
            self.tfidf_available = True
            logger.info("✅ TF-IDF fallback vectorizer initialized")
            
        except ImportError:
            logger.warning("scikit-learn not available, using random embeddings as fallback")
            self.tfidf_available = False
    
    def _generate_fallback_embedding(self, text: str, dimension: int = 1536) -> List[float]:
        """Generate fallback embedding for a single text"""
        
        if self.tfidf_available and hasattr(self, 'tfidf_vectorizer'):
            try:
                # Use TF-IDF for more meaningful embeddings
                tfidf_vector = self.tfidf_vectorizer.transform([text]).toarray()[0]
                
                # Pad or truncate to desired dimension
                if len(tfidf_vector) < dimension:
                    padding = [0.0] * (dimension - len(tfidf_vector))
                    tfidf_vector = np.concatenate([tfidf_vector, padding])
                elif len(tfidf_vector) > dimension:
                    tfidf_vector = tfidf_vector[:dimension]
                
                # Normalize to unit vector
                norm = np.linalg.norm(tfidf_vector)
                if norm > 0:
                    tfidf_vector = tfidf_vector / norm
                
                return tfidf_vector.tolist()
                
            except Exception as e:
                logger.warning(f"TF-IDF fallback failed: {e}, using random embedding")
        
        # Random embedding as last resort (normalized)
        random.seed(hash(text) % (2**32))  # Deterministic based on text
        embedding = [random.gauss(0, 1) for _ in range(dimension)]
        
        # Normalize to unit vector
        norm = np.sqrt(sum(x*x for x in embedding))
        if norm > 0:
            embedding = [x/norm for x in embedding]
        
        return embedding
    
    async def create_text_embedding(self, text: str) -> List[float]:
        """Create embedding for single text with fallback"""
        
        # Try primary service first if available
        if not self.fallback_mode and self.primary_service:
            try:
                result = await self.primary_service.create_text_embedding(text)
                logger.debug("✅ Used primary OpenAI service")
                return result
                
            except (APIConnectionError, APITimeoutError) as e:
                logger.warning(f"OpenAI connection issue, switching to fallback: {e}")
                self.fallback_mode = True
            except RateLimitError as e:
                logger.warning(f"OpenAI rate limit hit, using fallback: {e}")
            except AuthenticationError as e:
                logger.error(f"OpenAI authentication failed, switching to fallback: {e}")
                self.fallback_mode = True
            except Exception as e:
                logger.warning(f"OpenAI service error, using fallback: {e}")
        
        # Use fallback embedding
        logger.info(f"Using fallback embedding for text: {text[:50]}...")
        return self._generate_fallback_embedding(text)
    
    async def create_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts with fallback"""
        if not texts:
            return []
        
        # Try primary service first if available
        if not self.fallback_mode and self.primary_service:
            try:
                result = await self.primary_service.create_text_embeddings(texts)
                logger.debug(f"✅ Used primary OpenAI service for {len(texts)} texts")
                return result
                
            except (APIConnectionError, APITimeoutError) as e:
                logger.warning(f"OpenAI connection issue, switching to fallback: {e}")
                self.fallback_mode = True
            except RateLimitError as e:
                logger.warning(f"OpenAI rate limit hit, using fallback: {e}")
            except AuthenticationError as e:
                logger.error(f"OpenAI authentication failed, switching to fallback: {e}")
                self.fallback_mode = True
            except Exception as e:
                logger.warning(f"OpenAI service error, using fallback: {e}")
        
        # Use fallback embeddings
        logger.info(f"Using fallback embeddings for {len(texts)} texts")
        return [self._generate_fallback_embedding(text) for text in texts]
    
    async def create_chunks(self, text: str, metadata: Optional[Dict] = None, 
                          chunk_size: int = 400, overlap: int = 50, **kwargs) -> List[Dict]:
        """Create text chunks with embeddings (with fallback)"""
        words = text.split()
        if not words:
            return []
        
        chunks = []
        chunk_texts = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            chunk_texts.append(chunk_text)
            
            chunks.append({
                "text": chunk_text,
                "start_index": i,
                "end_index": min(i + chunk_size, len(words)),
                "metadata": metadata or {}
            })
        
        # Get embeddings for all chunks
        embeddings = await self.create_text_embeddings(chunk_texts)
        
        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding
            chunk["fallback_used"] = self.fallback_mode
        
        return chunks
    
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        import math
        
        try:
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            norm1 = math.sqrt(sum(a * a for a in embedding1))
            norm2 = math.sqrt(sum(b * b for b in embedding2))
            
            if norm1 * norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    async def find_similar_texts(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find most similar texts based on embeddings"""
        try:
            similarities = []
            
            for i, candidate in enumerate(candidate_embeddings):
                similarity = await self.compute_similarity(query_embedding, candidate)
                similarities.append({
                    "index": i, 
                    "similarity": similarity
                })
            
            # Sort by similarity in descending order and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar texts: {e}")
            return []
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service"""
        return 1536  # Standard dimension for consistency
    
    def get_max_input_length(self) -> int:
        """Get maximum input text length supported"""
        return 8192
    
    def is_fallback_mode(self) -> bool:
        """Check if service is running in fallback mode"""
        return self.fallback_mode
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status and capabilities"""
        return {
            "primary_service_available": not self.fallback_mode and self.primary_service is not None,
            "fallback_mode": self.fallback_mode,
            "tfidf_available": self.tfidf_available,
            "provider": self.provider_name,
            "model": self.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "max_input_length": self.get_max_input_length()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check with detailed status"""
        status = self.get_service_status()
        
        # Test embedding generation
        try:
            test_embedding = await self.create_text_embedding("test")
            status["embedding_test"] = {
                "success": True,
                "dimension": len(test_embedding),
                "fallback_used": self.fallback_mode
            }
        except Exception as e:
            status["embedding_test"] = {
                "success": False,
                "error": str(e)
            }
        
        return status
    
    async def close(self):
        """Cleanup resources"""
        if self.primary_service:
            await self.primary_service.close()
        logger.info("ResilientEmbedService has been closed.")