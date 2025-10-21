from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional
from isa_model.inference.services.base_service import BaseService

class BaseEmbedService(BaseService):
    """Base class for embedding services with unified task dispatch"""
    
    async def invoke(
        self, 
        input_data: Union[str, List[str]],
        task: Optional[str] = None,
        **kwargs
    ) -> Union[List[float], List[List[float]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        统一的任务分发方法 - Base类提供通用实现
        
        Args:
            input_data: 输入数据，可以是:
                - str: 单个文本
                - List[str]: 多个文本（批量处理）
            task: 任务类型，支持多种embedding任务
            **kwargs: 任务特定的附加参数
            
        Returns:
            Various types depending on task
        """
        task = task or "embed"
        
        # ==================== 嵌入生成类任务 ====================
        if task == "embed":
            if isinstance(input_data, list):
                return await self.create_text_embeddings(input_data)
            else:
                return await self.create_text_embedding(input_data)
        elif task == "embed_batch":
            if not isinstance(input_data, list):
                input_data = [input_data]
            return await self.create_text_embeddings(input_data)
        elif task in ["chunk", "chunk_and_embed"]:
            if isinstance(input_data, list):
                raise ValueError("chunk task requires single text input")
            return await self.create_chunks(input_data, **kwargs)
        elif task == "similarity":
            # Support both text-based and embedding-based similarity
            candidates = kwargs.get("candidates")
            embedding1 = kwargs.get("embedding1")
            embedding2 = kwargs.get("embedding2")
            
            if candidates:
                # Text-based similarity - compute embeddings first
                if isinstance(input_data, list):
                    raise ValueError("similarity task with candidates requires single query text")
                # Remove candidates from kwargs to avoid duplicate parameter
                similarity_kwargs = {k: v for k, v in kwargs.items() if k != 'candidates'}
                return await self._text_similarity_search(input_data, candidates, **similarity_kwargs)
            elif embedding1 and embedding2:
                # Direct embedding similarity
                similarity = await self.compute_similarity(embedding1, embedding2)
                return {"similarity": similarity}
            else:
                raise ValueError("similarity task requires either 'candidates' parameter or both 'embedding1' and 'embedding2' parameters")
        elif task == "find_similar":
            query_embedding = kwargs.get("query_embedding")
            candidate_embeddings = kwargs.get("candidate_embeddings")
            if not query_embedding or not candidate_embeddings:
                raise ValueError("find_similar task requires query_embedding and candidate_embeddings parameters")
            return await self.find_similar_texts(
                query_embedding, 
                candidate_embeddings, 
                kwargs.get("top_k", 5)
            )
        
        # ==================== 重排序类任务 ====================
        elif task in ["rerank", "rerank_documents", "document_ranking"]:
            query = kwargs.get("query") or input_data
            documents = kwargs.get("documents")
            if not documents:
                raise ValueError("rerank task requires documents parameter")
            if isinstance(query, list):
                raise ValueError("rerank task requires single query string")
            return await self.rerank_documents(
                query=query,
                documents=documents,
                top_k=kwargs.get("top_k"),
                return_documents=kwargs.get("return_documents", True)
            )
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support task: {task}")
    
    def get_supported_tasks(self) -> List[str]:
        """
        获取支持的任务列表
        
        Returns:
            List of supported task names
        """
        return ["embed", "embed_batch", "chunk", "chunk_and_embed", "similarity", "find_similar", "rerank", "rerank_documents", "document_ranking"]
    
    async def _text_similarity_search(self, query_text: str, candidates: List[str], **kwargs) -> Dict[str, Any]:
        """
        Helper method for text-based similarity search
        
        Args:
            query_text: Query text
            candidates: List of candidate texts
            **kwargs: Additional parameters (top_k, threshold, etc.)
            
        Returns:
            Dictionary containing similar documents with scores
        """
        # Get embeddings for query and candidates
        query_embedding = await self.create_text_embedding(query_text)
        candidate_embeddings = await self.create_text_embeddings(candidates)
        
        # Find similar texts
        similar_results = await self.find_similar_texts(
            query_embedding, 
            candidate_embeddings, 
            kwargs.get("top_k", len(candidates))
        )
        
        # Apply threshold if specified
        threshold = kwargs.get("threshold")
        if threshold is not None:
            similar_results = [r for r in similar_results if r["similarity"] >= threshold]
        
        # Convert to expected format with text content
        similar_documents = []
        for result in similar_results:
            similar_documents.append({
                "text": candidates[result["index"]],
                "similarity": result["similarity"],
                "index": result["index"]
            })
        
        return {
            "similar_documents": similar_documents,
            "query": query_text,
            "total_candidates": len(candidates),
            "returned_count": len(similar_documents)
        }
    
    @abstractmethod
    async def create_text_embedding(self, text: str) -> List[float]:
        """
        Create embedding for single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of float values representing the embedding vector
        """
        pass
    
    @abstractmethod
    async def create_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors, one for each input text
        """
        pass
    
    @abstractmethod
    async def create_chunks(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Create text chunks with embeddings
        
        Args:
            text: Input text to chunk and embed
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of dictionaries containing:
            - text: The chunk text
            - embedding: The embedding vector
            - metadata: Associated metadata
            - start_index: Start position in original text
            - end_index: End position in original text
        """
        pass
    
    @abstractmethod
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (typically cosine similarity, range -1 to 1)
        """
        pass
    
    @abstractmethod
    async def find_similar_texts(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find most similar texts based on embeddings
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            top_k: Number of top similar results to return
            
        Returns:
            List of dictionaries containing:
            - index: Index in candidate_embeddings
            - similarity: Similarity score
        """
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this service
        
        Returns:
            Integer dimension of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_max_input_length(self) -> int:
        """
        Get maximum input text length supported
        
        Returns:
            Maximum number of characters/tokens supported
        """
        pass
    
    async def rerank_documents(
        self, 
        query: str, 
        documents: List[str], 
        top_k: Optional[int] = None,
        return_documents: bool = True
    ) -> Dict[str, Any]:
        """
        Rerank documents based on relevance to query
        
        Default implementation returns NotImplementedError.
        Override in subclasses that support reranking.
        
        Args:
            query: Search query string
            documents: List of documents to rerank
            top_k: Number of top results to return (None = all)
            return_documents: Whether to include document text in results
            
        Returns:
            Dictionary containing:
            - success: Boolean success status
            - results: List of ranked documents with scores
            - metadata: Additional information (model, timing, etc.)
        """
        return {
            'success': False,
            'error': f'Reranking not supported by {self.__class__.__name__}',
            'provider': getattr(self, 'provider_name', 'unknown'),
            'service': getattr(self, 'model_name', 'unknown')
        }
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass
