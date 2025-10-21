"""
Services - Service implementations for different model types

File: isa_model/inference/services/__init__.py
This module contains service implementations for different AI model types.
"""

from .base_service import BaseService, BaseEmbeddingService
from .llm.base_llm_service import BaseLLMService

__all__ = [
    "BaseService",
    "BaseLLMService", 
    "BaseEmbeddingService"
] 