"""
LLM Services - Business logic services for Language Models
"""

# Import LLM services here when created
from .ollama_llm_service import OllamaLLMService
from .openai_llm_service import OpenAILLMService
from .yyds_llm_service import YydsLLMService
from .huggingface_llm_service import ISALLMService, HuggingFaceLLMService, HuggingFaceInferenceService
# LocalLLMService requires torch (local mode only) - import explicitly when needed
# from .local_llm_service import LocalLLMService, create_local_llm_service

__all__ = [
    "OllamaLLMService",
    "OpenAILLMService",
    "YydsLLMService",
    "ISALLMService",
    "HuggingFaceLLMService",
    "HuggingFaceInferenceService",
    # "LocalLLMService",  # Requires isa_model[local]
    # "create_local_llm_service"
] 