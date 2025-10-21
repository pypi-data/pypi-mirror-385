"""
ISA Embedding & Reranking Service

Jina-based embedding and reranking service using SOTA Transformer models
- Reranking: Jina Reranker v2 (Transformer architecture)  
- Languages: 100+ supported
"""

import modal
import time
import json
import os
import logging
from typing import Dict, List, Optional, Any

# Define Modal application
app = modal.App("isa-embed-rerank")

# Define Modal container image
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        "torch>=2.0.0",
        "transformers>=4.35.0",
        "sentence-transformers>=2.2.2",
        "huggingface_hub",
        "accelerate",
        "numpy>=1.24.3",
        "httpx>=0.26.0",
        "requests",
        "pydantic>=2.0.0",
        "python-dotenv",
        "einops",  # Required for Jina Reranker v2
    ])
    .env({
        "TRANSFORMERS_CACHE": "/models",
        "TORCH_HOME": "/models/torch",
        "HF_HOME": "/models",
    })
)

# Jina Reranking Service - Optimized for T4 GPU
@app.cls(
    gpu="T4",           # T4 4GB GPU for Jina Reranker
    image=image,
    memory=8192,        # 8GB RAM
    timeout=1800,       # 30 minutes
    scaledown_window=60,    # 1 minute idle timeout
    min_containers=0,   # Scale to zero
    max_containers=10,  # Support up to 10 concurrent containers
)
class ISAEmbedRerankService:
    """
    ISA Jina Reranker v2 Service
    
    Transformer-based SOTA reranking model:
    - Model: jinaai/jina-reranker-v2-base-multilingual
    - Architecture: Transformer (Cross-encoder)
    - Languages: 100+ supported
    - Performance: 2024 best-in-class reranker
    """
        
    @modal.enter()
    def load_models(self):
        """Load Jina Reranker v2 model"""
        print("Loading Jina Reranker v2...")
        start_time = time.time()
        
        # Initialize instance variables
        self.reranker_model = None
        self.logger = logging.getLogger(__name__)
        self.request_count = 0
        self.total_processing_time = 0.0
        
        try:
            from transformers import AutoModelForSequenceClassification
            
            # Load Jina Reranker v2 (SOTA 2024 Transformer)
            print("Loading Jina Reranker v2 (Transformer-based)...")
            self.reranker_model = AutoModelForSequenceClassification.from_pretrained(
                'jinaai/jina-reranker-v2-base-multilingual',
                torch_dtype="auto",
                trust_remote_code=True
            )
            
            load_time = time.time() - start_time
            print(f"Jina Reranker v2 loaded successfully in {load_time:.2f}s")
            
            # Model loading status
            self.models_loaded = True
            
        except Exception as e:
            print(f"Model loading failed: {e}")
            import traceback
            traceback.print_exc()
            self.models_loaded = False
    
    @modal.method()
    def rerank_documents(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
        return_documents: bool = True
    ) -> Dict[str, Any]:
        """
        Rerank documents using Jina Reranker v2
        
        Args:
            query: Query text
            documents: List of documents to rerank
            top_k: Return top k results
            return_documents: Whether to return document content
            
        Returns:
            Reranking results
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Validate model loading status
            if not self.models_loaded or not self.reranker_model:
                raise RuntimeError("Jina Reranker v2 model not loaded")
            
            # Prepare reranking input (query-document pairs)
            query_doc_pairs = [[query, doc] for doc in documents]
            
            # Execute reranking (Jina Reranker v2 API)
            scores = self.reranker_model.compute_score(query_doc_pairs, max_length=1024)
            
            # Ensure scores is numpy array/list
            if hasattr(scores, 'cpu'):
                scores = scores.cpu().numpy()
            elif hasattr(scores, 'tolist'):
                scores = scores.tolist()
            elif not isinstance(scores, (list, tuple)):
                scores = [scores]
            
            # Create results list
            results = []
            for i, (doc, score) in enumerate(zip(documents, scores)):
                result_item = {
                    'index': i,
                    'relevance_score': float(score),
                }
                if return_documents:
                    result_item['document'] = doc
                results.append(result_item)
            
            # Sort by score (descending)
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Apply top_k limit
            if top_k is not None:
                results = results[:top_k]
            
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            # Calculate cost (T4 GPU: ~$0.40/hour)
            gpu_cost = (processing_time / 3600) * 0.40
            
            result = {
                'success': True,
                'service': 'isa-embed-rerank',
                'operation': 'reranking',
                'provider': 'ISA',
                'results': results,
                'query': query,
                'model': 'jina-reranker-v2-base-multilingual',
                'architecture': 'Transformer',
                'num_documents': len(documents),
                'returned_count': len(results),
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"rerank_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round(gpu_cost, 6),
                    'gpu_type': 'T4'
                },
                'model_info': {
                    'model_name': 'jina-reranker-v2-base-multilingual',
                    'provider': 'ISA',
                    'architecture': 'Transformer',
                    'gpu': 'T4',
                    'languages_supported': '100+',
                    'top_k': top_k,
                    'container_id': os.environ.get('MODAL_TASK_ID', 'unknown')
                }
            }
            
            # Output JSON results
            print("=== JSON_RESULT_START ===")
            print(json.dumps(result, default=str))
            print("=== JSON_RESULT_END ===")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_result = {
                'success': False,
                'service': 'isa-embed-rerank',
                'operation': 'reranking',
                'provider': 'ISA', 
                'error': str(e),
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"rerank_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round((processing_time / 3600) * 0.40, 6),
                    'gpu_type': 'T4'
                }
            }
            
            print("=== JSON_RESULT_START ===")
            print(json.dumps(error_result, default=str))
            print("=== JSON_RESULT_END ===")
            
            return error_result
    
    @modal.method()
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'isa-embed-rerank',
            'provider': 'ISA',
            'models_loaded': self.models_loaded,
            'model': 'jina-reranker-v2-base-multilingual',
            'architecture': 'Transformer',
            'timestamp': time.time(),
            'gpu': 'T4',
            'memory_usage': '8GB',
            'request_count': self.request_count,
            'languages_supported': '100+'
        }

# Deployment functions
@app.function()
def deploy_info():
    """Deployment information"""
    return {
        'service': 'isa-embed-rerank',
        'version': '1.0.0',
        'description': 'ISA Jina Reranker v2 service - SOTA 2024 Transformer-based reranking',
        'model': 'jina-reranker-v2-base-multilingual',
        'architecture': 'Transformer',
        'gpu': 'T4',
        'languages': '100+',
        'deployment_time': time.time()
    }

@app.function()
def register_service():
    """Register service to model repository"""
    try:
        from isa_model.core.models.model_repo import ModelRepository
        
        repo = ModelRepository()
        
        # Register reranking service
        repo.register_model({
            'model_id': 'isa-jina-reranker-v2-service',
            'model_type': 'reranking',
            'provider': 'isa',
            'endpoint': 'https://isa-embed-rerank.modal.run',
            'capabilities': ['reranking', 'document_ranking'],
            'pricing': {'gpu_type': 'T4', 'cost_per_hour': 0.40},
            'metadata': {
                'model': 'jina-reranker-v2-base-multilingual',
                'architecture': 'Transformer',
                'languages': '100+',
                'sota_2024': True
            }
        })
        
        print("Jina Reranker v2 service registered successfully")
        return {'status': 'registered'}
        
    except Exception as e:
        print(f"Service registration failed: {e}")
        return {'status': 'failed', 'error': str(e)}

if __name__ == "__main__":
    print("ISA Jina Reranker v2 Service - Modal Deployment")
    print("Deploy with: modal deploy isa_embed_rerank_service.py")
    print()
    print("Model: jina-reranker-v2-base-multilingual")
    print("Architecture: Transformer (Cross-encoder)")
    print("Languages: 100+ supported")
    print("GPU: T4 (cost-effective)")
    print()
    print("Usage:")
    print("service.rerank_documents('query', ['doc1', 'doc2', 'doc3'], top_k=5)")