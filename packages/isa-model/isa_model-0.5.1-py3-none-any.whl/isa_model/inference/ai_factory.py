#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simplified AI Factory for creating inference services
Uses the new unified service architecture with centralized managers
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
import logging
from isa_model.inference.services.base_service import BaseService
from isa_model.core.models.model_manager import ModelManager
from isa_model.core.config import ConfigManager

if TYPE_CHECKING:
    from isa_model.inference.services.audio.base_stt_service import BaseSTTService
    from isa_model.inference.services.audio.base_tts_service import BaseTTSService
    from isa_model.inference.services.vision.base_vision_service import BaseVisionService
    from isa_model.inference.services.img.base_image_gen_service import BaseImageGenService

logger = logging.getLogger(__name__)

class AIFactory:
    """
    Modernized AI Factory using centralized ModelManager and ConfigManager
    Provides unified interface with only 6 core methods: get_llm, get_vision, get_img, get_stt, get_tts, get_embed
    """
    
    _instance = None
    _is_initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the AI Factory."""
        # Check if this specific instance has been initialized (not class-level flag)
        if not hasattr(self, 'model_manager'):
            # Use centralized managers
            self.model_manager = ModelManager()
            self.config_manager = ConfigManager()
            self._cached_services: Dict[str, BaseService] = {}

            logger.info("AI Factory initialized with centralized ModelManager and ConfigManager")
            AIFactory._is_initialized = True
    
    # Core service methods using centralized architecture
    def get_llm(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None) -> BaseService:
        """
        Get a LLM service instance with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: OpenAI="gpt-4.1-mini", Ollama="llama3.2:3b", YYDS="claude-sonnet-4-20250514", Cerebras="gpt-oss-120b", ISA="isa-llm-service")
            provider: Provider name (defaults to 'openai' for production, 'ollama' for dev, 'cerebras' for ultra-fast inference, 'isa' for custom models, 'huggingface' for HF models)
            config: Optional configuration dictionary
            
        Returns:
            LLM service instance
        """
        # Set defaults based on provider
        if provider == "openai":
            final_model_name = model_name or "gpt-4.1-mini"
            final_provider = provider
        elif provider == "ollama":
            final_model_name = model_name or "llama3.2:3b-instruct-fp16"
            final_provider = provider
        elif provider == "yyds":
            final_model_name = model_name or "claude-sonnet-4-20250514"
            final_provider = provider
        elif provider == "cerebras":
            final_model_name = model_name or "gpt-oss-120b"
            final_provider = provider
        elif provider == "isa":
            final_model_name = model_name or "isa-llm-service"
            final_provider = provider
        elif provider == "huggingface":
            final_model_name = model_name or "xenobordom/dialogpt-isa-trained-1755493402"
            final_provider = provider
        else:
            # Default provider selection - OpenAI with cheapest model
            final_provider = provider or "openai"
            if final_provider == "openai":
                final_model_name = model_name or "gpt-4.1-mini"
            elif final_provider == "ollama":
                final_model_name = model_name or "llama3.2:3b-instruct-fp16"
            elif final_provider == "cerebras":
                final_model_name = model_name or "gpt-oss-120b"
            elif final_provider == "isa":
                final_model_name = model_name or "isa-llm-service"
            elif final_provider == "huggingface":
                final_model_name = model_name or "xenobordom/dialogpt-isa-trained-1755493402"
            else:
                final_model_name = model_name or "gpt-4.1-mini"
        
        # Create service using new centralized approach
        try:
            if final_provider == "openai":
                from isa_model.inference.services.llm.openai_llm_service import OpenAILLMService
                return OpenAILLMService(provider_name=final_provider, model_name=final_model_name, 
                                      model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "ollama":
                from isa_model.inference.services.llm.ollama_llm_service import OllamaLLMService
                return OllamaLLMService(provider_name=final_provider, model_name=final_model_name,
                                      model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "yyds":
                from isa_model.inference.services.llm.yyds_llm_service import YydsLLMService
                return YydsLLMService(provider_name=final_provider, model_name=final_model_name,
                                    model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "cerebras":
                from isa_model.inference.services.llm.cerebras_llm_service import CerebrasLLMService
                return CerebrasLLMService(provider_name=final_provider, model_name=final_model_name,
                                        model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "isa":
                from isa_model.inference.services.llm.huggingface_llm_service import ISALLMService
                return ISALLMService(provider_name=final_provider, model_name=final_model_name,
                                   model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "huggingface":
                from isa_model.inference.services.llm.huggingface_llm_service import ISALLMService
                return ISALLMService(provider_name="isa", model_name=final_model_name,
                                   model_manager=self.model_manager, config_manager=self.config_manager)
            else:
                raise ValueError(f"Unsupported LLM provider: {final_provider}")
        except Exception as e:
            logger.error(f"Failed to create LLM service: {e}")
            raise
    
    def get_vision(
        self,
        model_name: Optional[str] = None,
        provider: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> 'BaseVisionService':
        """
        Get vision service with automatic defaults
        
        Args:
            model_name: Model name. Special names:
                       - "hybrid": Unified UI/Document analysis service (RECOMMENDED)
                       - "isa_vision_table": Table extraction service
                       - "isa_vision_ui": UI detection service  
                       - "isa_vision_doc": Document analysis service
                       - Default: "gpt-4.1-mini"
            provider: Provider name (auto-detected for ISA services)
            config: Optional configuration override
            
        Returns:
            Vision service instance
        """
        # Handle special vision services  
        if model_name == "hybrid":
            # Hybrid vision service has been deprecated, use OpenAI as fallback
            logger.warning("HybridVisionService is deprecated, using OpenAI vision service as fallback")
            final_provider = "openai"
            final_model_name = "gpt-4.1-nano"
        
        elif model_name in ["isa_vision_table", "isa_vision_ui", "isa_vision_doc"]:
            try:
                from isa_model.deployment.modal.services.vision.simple_auto_deploy_vision_service import SimpleAutoDeployVisionService
                logger.info(f"Creating auto-deploy service wrapper for {model_name}")
                return SimpleAutoDeployVisionService(model_name, config)
            except Exception as e:
                logger.error(f"Failed to create ISA vision service: {e}")
                # Fallback to ISA service
                logger.warning(f"Auto-deploy service failed, using ISA vision service as fallback")
                final_provider = "isa"
                final_model_name = "isa-omniparser-ui-detection"
        
        # Set defaults for regular services
        elif provider == "openai":
            final_model_name = model_name or "gpt-4.1-mini"
            final_provider = provider
        elif provider == "ollama":
            final_model_name = model_name or "llama3.2-vision:latest"
            final_provider = provider
        elif provider == "replicate":
            final_model_name = model_name or "meta/llama-2-70b-chat"
            final_provider = provider
        elif provider == "isa":
            final_model_name = model_name or "isa-omniparser-ui-detection"
            final_provider = provider
        elif provider == "yyds":
            final_model_name = model_name or "gpt-4o-mini"
            final_provider = provider
        else:
            # Default provider selection
            final_provider = provider or "openai"
            if final_provider == "openai":
                final_model_name = model_name or "gpt-4.1-mini"
            elif final_provider == "ollama":
                final_model_name = model_name or "llama3.2-vision:latest"
            elif final_provider == "isa":
                final_model_name = model_name or "isa-omniparser-ui-detection"
            elif final_provider == "yyds":
                final_model_name = model_name or "gpt-4o-mini"
            else:
                final_model_name = model_name or "gpt-4.1-mini"
        
        # Create service using new centralized approach
        try:
            if final_provider == "openai":
                from isa_model.inference.services.vision.openai_vision_service import OpenAIVisionService
                return OpenAIVisionService(provider_name=final_provider, model_name=final_model_name,
                                         model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "replicate":
                from isa_model.inference.services.vision.replicate_vision_service import ReplicateVisionService
                return ReplicateVisionService(provider_name=final_provider, model_name=final_model_name,
                                            model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "isa":
                from isa_model.inference.services.vision.isa_vision_service import ISAVisionService
                logger.info(f"Creating ISA Vision Service with model: {final_model_name}")
                return ISAVisionService()
            elif final_provider == "yyds":
                from isa_model.inference.services.vision.yyds_vision_service import YydsVisionService
                logger.info(f"Creating YYDS Vision Service with model: {final_model_name}")
                return YydsVisionService(provider_name=final_provider, model_name=final_model_name,
                                        model_manager=self.model_manager, config_manager=self.config_manager)
            else:
                raise ValueError(f"Unsupported vision provider: {final_provider}")
        except Exception as e:
            logger.error(f"Failed to create vision service: {e}")
            raise
    
    def get_img(self, type: str = "t2i", model_name: Optional[str] = None, provider: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None) -> 'BaseImageGenService':
        """
        Get an image generation service with type-specific defaults
        
        Args:
            type: Image generation type:
                  - "t2i" (text-to-image): Uses flux-schnell ($3 per 1000 images)
                  - "i2i" (image-to-image): Uses flux-kontext-pro ($0.04 per image)
            model_name: Optional model name override
            provider: Provider name (defaults to 'replicate')
            config: Optional configuration dictionary
            
        Returns:
            Image generation service instance
            
        Usage:
            # Text-to-image (default)
            img_service = AIFactory().get_img()
            img_service = AIFactory().get_img(type="t2i")
            
            # Image-to-image
            img_service = AIFactory().get_img(type="i2i")
            
            # Custom model
            img_service = AIFactory().get_img(type="t2i", model_name="custom-model")
        """
        # Set defaults based on type
        final_provider = provider or "replicate"
        
        if type == "t2i":
            # Text-to-image: flux-schnell
            final_model_name = model_name or "black-forest-labs/flux-schnell"
        elif type == "i2i":
            # Image-to-image: flux-kontext-pro
            final_model_name = model_name or "black-forest-labs/flux-kontext-pro"
        else:
            raise ValueError(f"Unknown image generation type: {type}. Use 't2i' or 'i2i'")
        
        # Create service using new centralized architecture
        try:
            if final_provider == "replicate":
                from isa_model.inference.services.img.replicate_image_gen_service import ReplicateImageGenService
                return ReplicateImageGenService(provider_name=final_provider, model_name=final_model_name,
                                              model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "openai":
                from isa_model.inference.services.img.services.openai_dalle_service import OpenAIDALLEService
                return OpenAIDALLEService(provider_name=final_provider, model_name=final_model_name,
                                        model_manager=self.model_manager, config_manager=self.config_manager)
            else:
                raise ValueError(f"Unsupported image generation provider: {final_provider}")
        except Exception as e:
            logger.error(f"Failed to create image generation service: {e}")
            raise

    def get_stt(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None) -> 'BaseSTTService':
        """
        Get Speech-to-Text service with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: "whisper-1")
            provider: Provider name (defaults to 'openai')
            config: Optional configuration dictionary
            
        Returns:
            STT service instance
        """
        # Set defaults
        final_provider = provider or "openai"
        final_model_name = model_name or "whisper-1"
        
        # Create service using new centralized approach
        try:
            if final_provider == "openai":
                from isa_model.inference.services.audio.openai_stt_service import OpenAISTTService
                return OpenAISTTService(provider_name=final_provider, model_name=final_model_name,
                                      model_manager=self.model_manager, config_manager=self.config_manager)
            else:
                raise ValueError(f"Unsupported STT provider: {final_provider}")
        except Exception as e:
            logger.error(f"Failed to create STT service: {e}")
            raise

    def get_tts(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None) -> 'BaseTTSService':
        """
        Get Text-to-Speech service with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: Replicate="kokoro-82m", OpenAI="tts-1")
            provider: Provider name (defaults to 'replicate' for production, 'openai' for dev)
            config: Optional configuration dictionary
            
        Returns:
            TTS service instance
        """
        # Set defaults based on provider
        if provider == "replicate":
            final_model_name = model_name or "kokoro-82m"
            final_provider = provider
        elif provider == "openai":
            final_model_name = model_name or "tts-1"
            final_provider = provider
        else:
            # Default provider selection
            final_provider = provider or "replicate"
            if final_provider == "replicate":
                final_model_name = model_name or "kokoro-82m"
            else:
                final_model_name = model_name or "tts-1"
        
        # Create service using new centralized approach
        try:
            if final_provider == "replicate":
                from isa_model.inference.services.audio.replicate_tts_service import ReplicateTTSService
                # Use full model name for Replicate
                if final_model_name == "kokoro-82m":
                    final_model_name = "jaaari/kokoro-82m:f559560eb822dc509045f3921a1921234918b91739db4bf3daab2169b71c7a13"
                return ReplicateTTSService(provider_name=final_provider, model_name=final_model_name,
                                         model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "openai":
                from isa_model.inference.services.audio.openai_tts_service import OpenAITTSService
                return OpenAITTSService(provider_name=final_provider, model_name=final_model_name,
                                      model_manager=self.model_manager, config_manager=self.config_manager)
            else:
                raise ValueError(f"Unsupported TTS provider: {final_provider}")
        except Exception as e:
            logger.error(f"Failed to create TTS service: {e}")
            raise
    
    def get_realtime(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                     config: Optional[Dict[str, Any]] = None) -> BaseService:
        """
        Get realtime audio service with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: OpenAI="gpt-4o-realtime-preview-2024-10-01")
            provider: Provider name (defaults to 'openai')
            config: Optional configuration dictionary
            
        Returns:
            Realtime service instance
        """
        # Set defaults based on provider
        if provider == "openai":
            final_model_name = model_name or "gpt-4o-realtime-preview-2024-10-01"
            final_provider = provider
        else:
            # Default provider selection - only OpenAI supports realtime currently
            final_provider = provider or "openai"
            final_model_name = model_name or "gpt-4o-realtime-preview-2024-10-01"
        
        # Create service using new centralized approach
        try:
            if final_provider == "openai":
                from isa_model.inference.services.audio.openai_realtime_service import OpenAIRealtimeService
                return OpenAIRealtimeService(provider_name=final_provider, model_name=final_model_name,
                                           model_manager=self.model_manager, config_manager=self.config_manager)
            else:
                raise ValueError(f"Unsupported realtime provider: {final_provider}")
        except Exception as e:
            logger.error(f"Failed to create realtime service: {e}")
            raise
    
    def get_embed(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                     config: Optional[Dict[str, Any]] = None) -> BaseService:
        """
        Get embedding service with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: OpenAI="text-embedding-3-small", Ollama="bge-m3")
            provider: Provider name (defaults to 'openai' for production)
            config: Optional configuration dictionary
            
        Returns:
            Embedding service instance
        """
        # Set defaults based on provider
        if provider == "openai":
            final_model_name = model_name or "text-embedding-3-small"
            final_provider = provider
        elif provider == "ollama":
            final_model_name = model_name or "bge-m3"
            final_provider = provider
        else:
            # Default provider selection
            final_provider = provider or "openai"
            if final_provider == "openai":
                final_model_name = model_name or "text-embedding-3-small"
            else:
                final_model_name = model_name or "bge-m3"
        
        # Create service using new centralized approach
        # Create cache key
        cache_key = f"embed_{final_provider}_{final_model_name}"
        
        # Check cache first
        if cache_key in self._cached_services:
            logger.debug(f"Using cached embedding service: {cache_key}")
            return self._cached_services[cache_key]
        
        try:
            if final_provider == "openai":
                # Use resilient embedding service for OpenAI (with fallback)
                from isa_model.inference.services.embedding.resilient_embed_service import ResilientEmbedService
                service = ResilientEmbedService(provider_name=final_provider, model_name=final_model_name,
                                              model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "ollama":
                from isa_model.inference.services.embedding.ollama_embed_service import OllamaEmbedService
                service = OllamaEmbedService(provider_name=final_provider, model_name=final_model_name,
                                           model_manager=self.model_manager, config_manager=self.config_manager)
            elif final_provider == "isa":
                from isa_model.inference.services.embedding.isa_embed_service import ISAEmbedService
                service = ISAEmbedService()  # ISA service doesn't use model_manager/config_manager yet
            else:
                raise ValueError(f"Unsupported embedding provider: {final_provider}")
            
            # Cache the service
            self._cached_services[cache_key] = service
            logger.debug(f"Created and cached embedding service: {cache_key}")
            return service
            
        except Exception as e:
            logger.error(f"Failed to create embedding service: {e}")
            # As a last resort, try the resilient service
            try:
                logger.info("Attempting to create resilient embedding service as fallback")
                from isa_model.inference.services.embedding.resilient_embed_service import ResilientEmbedService
                service = ResilientEmbedService(provider_name="openai", model_name="text-embedding-3-small",
                                              model_manager=self.model_manager, config_manager=self.config_manager)
                self._cached_services[cache_key] = service
                logger.info("Successfully created fallback embedding service")
                return service
            except Exception as fallback_error:
                logger.error(f"Even fallback embedding service failed: {fallback_error}")
                # Create a more informative error
                error_details = {
                    "primary_error": str(e),
                    "fallback_error": str(fallback_error),
                    "provider": final_provider,
                    "model": final_model_name,
                    "suggestions": [
                        "检查OpenAI API密钥配置",
                        "确认网络连接正常",
                        "尝试使用其他嵌入提供商如ollama"
                    ]
                }
                raise ValueError(f"嵌入服务创建失败: {str(e)}。详细信息: {error_details}")

    def clear_cache(self):
        """Clear the service cache"""
        self._cached_services.clear()
        logger.info("Service cache cleared")
    
    @classmethod
    def get_instance(cls) -> 'AIFactory':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    # Modal service deployment methods for AutoDeployVisionService
    def _get_modal_app_name(self, model_name: str) -> str:
        """Get Modal app name for a given model"""
        app_mapping = {
            "isa_vision_table": "qwen-vision-table",
            "isa_vision_ui": "isa-vision-ui", 
            "isa_vision_doc": "isa-vision-doc"
        }
        return app_mapping.get(model_name, f"unknown-{model_name}")
    
    def _check_modal_service_availability(self, app_name: str) -> bool:
        """Check if Modal service is available and running"""
        try:
            import modal
            # Try to lookup the app
            app = modal.App.lookup(app_name)
            return True
        except Exception as e:
            logger.debug(f"Modal service {app_name} not available: {e}")
            return False
    
    def _auto_deploy_modal_service(self, model_name: str) -> bool:
        """Auto-deploy Modal service for given model"""
        try:
            import subprocess
            import os
            from pathlib import Path
            
            # Get the Modal service file path
            service_files = {
                "isa_vision_table": "isa_vision_table_service.py",
                "isa_vision_ui": "isa_vision_ui_service.py", 
                "isa_vision_doc": "isa_vision_doc_service.py"
            }
            
            if model_name not in service_files:
                logger.error(f"No Modal service file found for {model_name}")
                return False
            
            # Get the service file path
            service_file = service_files[model_name]
            modal_dir = Path(__file__).parent.parent / "deployment" / "cloud" / "modal"
            service_path = modal_dir / service_file
            
            if not service_path.exists():
                logger.error(f"Modal service file not found: {service_path}")
                return False
            
            logger.info(f"Deploying Modal service: {service_file}")
            
            # Run modal deploy command
            result = subprocess.run(
                ["modal", "deploy", str(service_path)],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                cwd=str(modal_dir)
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully deployed {model_name} Modal service")
                return True
            else:
                logger.error(f"Failed to deploy {model_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Deployment timeout for {model_name}")
            return False
        except Exception as e:
            logger.error(f"Exception during {model_name} deployment: {e}")
            return False
    
    def _shutdown_modal_service(self, model_name: str):
        """Shutdown Modal service (optional - Modal handles auto-scaling)"""
        # Modal services auto-scale to zero, so explicit shutdown isn't required
        # This method is here for compatibility with AutoDeployVisionService
        logger.info(f"Modal service {model_name} will auto-scale to zero when idle")
        pass
    
    async def cleanup(self):
        """Clean up all cached services and resources"""
        logger.info("🧹 Starting AIFactory cleanup...")
        
        cleanup_tasks = []
        for service_key, service in self._cached_services.items():
            try:
                if hasattr(service, 'close') and callable(service.close):
                    cleanup_tasks.append(service.close())
                    logger.debug(f"Scheduled cleanup for service: {service_key}")
            except Exception as e:
                logger.error(f"Error scheduling cleanup for service {service_key}: {e}")
        
        # Wait for all cleanup tasks to complete
        if cleanup_tasks:
            import asyncio
            try:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
                logger.info(f"✅ Cleaned up {len(cleanup_tasks)} services")
            except Exception as e:
                logger.error(f"❌ Error during service cleanup: {e}")
        
        # Clear the cached services
        self._cached_services.clear()
        
        # Clean up model manager if it has cleanup method
        if hasattr(self.model_manager, 'cleanup') and callable(self.model_manager.cleanup):
            try:
                await self.model_manager.cleanup()
                logger.info("✅ Model manager cleaned up")
            except Exception as e:
                logger.error(f"❌ Error cleaning up model manager: {e}")
        
        logger.info("✅ AIFactory cleanup completed")
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (useful for testing)"""
        cls._instance = None
        cls._is_initialized = False