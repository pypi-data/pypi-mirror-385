import logging
import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from isa_model.inference.services.embedding.base_embed_service import BaseEmbedService

logger = logging.getLogger(__name__)

class OpenAIEmbedService(BaseEmbedService):
    """
    OpenAI embedding service using text-embedding-3-small as default.
    Provides high-quality embeddings for production use.
    """
    
    def __init__(self, provider_name: str, model_name: str = "text-embedding-3-small", **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        # Get configuration from centralized config manager
        provider_config = self.get_provider_config()
        
        # Initialize AsyncOpenAI client with provider configuration
        try:
            if not provider_config.get("api_key"):
                raise ValueError("OpenAI API key not found in provider configuration")
            
            self.client = AsyncOpenAI(
                api_key=provider_config["api_key"],
                base_url=provider_config.get("base_url", "https://api.openai.com/v1"),
                organization=provider_config.get("organization")
            )
            
            logger.info(f"Initialized OpenAIEmbedService with model '{self.model_name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ValueError(f"Failed to initialize OpenAI client. Check your API key configuration: {e}") from e
        
        # Model-specific configurations
        self.dimensions = provider_config.get('dimensions', None)  # Optional dimension reduction
        self.encoding_format = provider_config.get('encoding_format', 'float')
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def create_text_embedding(self, text: str, **kwargs) -> List[float]:
        """Create embedding for single text"""
        try:
            # Extract user_id from kwargs for billing
            self._current_user_id = kwargs.get('user_id')
            kwargs = {
                "model": self.model_name,
                "input": text,
                "encoding_format": self.encoding_format
            }
            
            # Add dimensions parameter if specified (for text-embedding-3-small/large)
            if self.dimensions and "text-embedding-3" in self.model_name:
                kwargs["dimensions"] = self.dimensions
            
            response = await self.client.embeddings.create(**kwargs)
            
            # Track usage for billing
            usage = getattr(response, 'usage', None)
            if usage and self._current_user_id:
                total_tokens = getattr(usage, 'total_tokens', 0)
                await self._publish_billing_event(
                    user_id=self._current_user_id,
                    service_type="embedding",
                    operation="create_text_embedding",
                    input_tokens=total_tokens,
                    output_tokens=0,
                    metadata={
                        "model": self.model_name,
                        "dimensions": self.dimensions,
                        "text_length": len(text)
                    }
                )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error creating text embedding: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def create_text_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        if not texts:
            return []

        try:
            # Extract user_id from kwargs for billing
            self._current_user_id = kwargs.get('user_id')
            kwargs = {
                "model": self.model_name,
                "input": texts,
                "encoding_format": self.encoding_format
            }
            
            # Add dimensions parameter if specified
            if self.dimensions and "text-embedding-3" in self.model_name:
                kwargs["dimensions"] = self.dimensions
            
            response = await self.client.embeddings.create(**kwargs)
            
            # Track usage for billing
            usage = getattr(response, 'usage', None)
            if usage and self._current_user_id:
                total_tokens = getattr(usage, 'total_tokens', 0)
                await self._publish_billing_event(
                    user_id=self._current_user_id,
                    service_type="embedding",
                    operation="create_text_embeddings",
                    input_tokens=total_tokens,
                    output_tokens=0,
                    metadata={
                        "model": self.model_name,
                        "dimensions": self.dimensions,
                        "batch_size": len(texts),
                        "total_text_length": sum(len(t) for t in texts)
                    }
                )
            
            return [data.embedding for data in response.data]
            
        except Exception as e:
            logger.error(f"Error creating text embeddings: {e}")
            raise

    async def invoke(
        self,
        input_data: Optional[str] = None,
        task: Optional[str] = None,
        **kwargs
    ) -> List[float]:
        """
        Unified invoke method for embedding service.
        Follows pattern: text → vector embedding
        """
        if input_data is None:
            raise ValueError("Text input is required for embedding generation")

        # Embedding service generates vector from text
        return await self.create_text_embedding(text=input_data, **kwargs)

    async def create_chunks(self, text: str, metadata: Optional[Dict] = None, chunk_size: int = 400, overlap: int = 50, **kwargs) -> List[Dict]:
        """Create text chunks with embeddings"""
        # Use provided chunk_size and overlap, or defaults optimized for OpenAI models
        
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
        
        return chunks
    
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        import math
        
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = math.sqrt(sum(a * a for a in embedding1))
        norm2 = math.sqrt(sum(b * b for b in embedding2))
        
        if norm1 * norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    async def find_similar_texts(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find most similar texts based on embeddings"""
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
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service"""
        if self.dimensions:
            return self.dimensions
        
        # Default dimensions for OpenAI models
        model_dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        
        return model_dimensions.get(self.model_name, 1536)
    
    def get_max_input_length(self) -> int:
        """Get maximum input text length supported"""
        # OpenAI embedding models support up to 8192 tokens
        return 8192
    
    async def close(self):
        """Cleanup resources"""
        await self.client.close()
        logger.info("OpenAIEmbedService client has been closed.")
