import logging
import httpx
import asyncio
from typing import List, Dict, Any, Optional

from isa_model.inference.services.embedding.base_embed_service import BaseEmbedService
from isa_model.core.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class OllamaEmbedService(BaseEmbedService):
    """
    Ollama embedding service with unified architecture.
    Uses direct HTTP client communication with Ollama API.
    """
    
    def __init__(self, provider_name: str, model_name: str = "bge-m3", **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        # Get configuration from centralized config manager
        provider_config = self.get_provider_config()
        
        # Initialize HTTP client with provider configuration
        try:
            config_manager = ConfigManager()
            # Use Consul discovery with fallback
            default_base_url = config_manager.get_ollama_url()
            
            if "base_url" in provider_config:
                base_url = provider_config["base_url"]
            else:
                host = provider_config.get("host", "localhost")
                port = provider_config.get("port", 11434)
                base_url = provider_config.get("base_url", f"http://{host}:{port}")
                
            # Use config manager default (Consul discovery) if still not set
            if base_url == f"http://localhost:11434":
                base_url = default_base_url
            
            self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
            
            logger.info(f"Initialized OllamaEmbedService with model '{self.model_name}' at {base_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            raise ValueError(f"Failed to initialize Ollama client: {e}") from e
    
    async def create_text_embedding(self, text: str, **kwargs) -> List[float]:
        """Create embedding for single text"""
        try:
            # Extract user_id from kwargs for billing
            self._current_user_id = kwargs.get('user_id')
            payload = {
                "model": self.model_name,
                "prompt": text
            }
            
            response = await self.client.post("/api/embeddings", json=payload)
            response.raise_for_status()
            
            result = response.json()
            embedding = result["embedding"]
            
            # Track usage for billing (estimate token usage for Ollama)
            if self._current_user_id:
                estimated_tokens = len(text.split()) * 1.3  # Rough estimation
                await self._publish_billing_event(
                    user_id=self._current_user_id,
                    service_type="embedding",
                    operation="create_text_embedding",
                    input_tokens=int(estimated_tokens),
                    output_tokens=0,
                    metadata={
                        "model": self.model_name,
                        "text_length": len(text),
                        "estimated_tokens": int(estimated_tokens)
                    }
                )
            
            return embedding
            
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating text embedding: {e}")
            raise
    
    async def create_text_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Create embeddings for multiple texts concurrently"""
        if not texts:
            return []

        # Extract user_id from kwargs for billing
        self._current_user_id = kwargs.get('user_id')

        tasks = [self.create_text_embedding(text, **kwargs) for text in texts]
        embeddings = await asyncio.gather(*tasks)

        # Track batch usage for billing
        if self._current_user_id:
            total_estimated_tokens = sum(len(text.split()) * 1.3 for text in texts)
            await self._publish_billing_event(
                user_id=self._current_user_id,
                service_type="embedding",
                operation="create_text_embeddings",
                input_tokens=int(total_estimated_tokens),
                output_tokens=0,
                metadata={
                    "model": self.model_name,
                    "batch_size": len(texts),
                    "total_text_length": sum(len(t) for t in texts),
                    "estimated_tokens": int(total_estimated_tokens)
                }
            )
        
        return embeddings

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

    async def create_chunks(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """Create text chunks with embeddings"""
        chunk_size = 200  # words
        overlap = 50     # word overlap between chunks
        
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
        # Model-specific dimensions
        model_dimensions = {
            "bge-m3": 1024,
            "bge-large": 1024,
            "all-minilm": 384,
            "nomic-embed-text": 768
        }
        return model_dimensions.get(self.model_name, 1024)
    
    def get_max_input_length(self) -> int:
        """Get maximum input text length supported"""
        # Most Ollama embedding models support up to 8192 tokens
        return 8192

    async def close(self):
        """Cleanup resources"""
        await self.client.aclose()
        logger.info("OllamaEmbedService client has been closed.")