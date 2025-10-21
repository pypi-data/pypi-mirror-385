"""
Server Startup Initialization for ISA Model

Handles automatic initialization of:
- Database migrations
- Model registry population
- Embedding generation
- System validation
"""

import logging
import asyncio
from typing import Dict, Any
import json
import os

from ...core.config.config_manager import ConfigManager
from ...core.models.model_repo import ModelRegistry
from ...core.types import ModelType, ModelCapability

logger = logging.getLogger(__name__)

class StartupInitializer:
    """Handles server startup initialization"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self._embedding_service = None
        self._model_registry = None
        
    async def initialize_system(self):
        """Run complete system initialization"""
        print("🚀 Starting ISA Model system initialization...")

        try:
            # 1. Populate model registry
            await self._populate_models()

            # 2. Generate embeddings
            await self._generate_embeddings()

            # 3. Validate system
            await self._validate_system()

            print("✅ System initialization completed successfully!")

        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            raise
    
    async def _populate_models(self):
        """Populate model registry with all configured models"""
        print("📚 Populating model registry...")
        
        try:
            registry = ModelRegistry()
            self._model_registry = registry  # Track for cleanup
            
            # Check if models are already populated to avoid unnecessary database operations
            try:
                stats = registry.get_stats()
                if stats and stats.get('total_models', 0) > 0:
                    print(f"✅ Model registry already populated: {stats['total_models']} models")
                    return
            except Exception as e:
                print(f"⚠️ Could not check existing models, proceeding with population: {e}")
            
            # Get all configured models
            all_models = self.config_manager.model_definitions
            
            if not all_models:
                print("⚠️ No models configured in providers")
                return
            
            registered_count = 0
            
            for model_id, model_data in all_models.items():
                try:
                    # Skip individual model check to avoid multiple database queries
                    # We already checked if any models exist above
                    
                    # Map model type
                    model_type_str = model_data.get('type', 'llm')
                    model_type = self._map_model_type(model_type_str)
                    
                    # Map capabilities
                    capabilities = self._map_capabilities(model_data.get('capabilities', []))
                    
                    # Get provider
                    provider = model_data.get('provider', 'unknown')
                    
                    # Register the model
                    success = registry.register_model(
                        model_id=model_id,
                        model_type=model_type,
                        capabilities=capabilities,
                        metadata=model_data,
                        provider=provider
                    )
                    
                    if success:
                        registered_count += 1
                    else:
                        logger.warning(f"Failed to register {model_id}")
                        
                except Exception as e:
                    logger.error(f"Error registering {model_id}: {e}")
                    continue
            
            print(f"✅ Model registry populated: {registered_count}/{len(all_models)} models")
            
        except Exception as e:
            logger.error(f"❌ Model population error: {e}")
            raise
    
    async def _generate_embeddings(self):
        """Generate embeddings for all registered models using OpenAI embedding service"""
        print("🧠 Generating model embeddings...")
        
        try:
            # Initialize embedding service
            from ...inference.ai_factory import AIFactory
            factory = AIFactory.get_instance()
            embedding_service = factory.get_embed("text-embedding-3-small", "openai")
            self._embedding_service = embedding_service  # Track for cleanup
            
            if not embedding_service:
                print("⚠️ Could not initialize embedding service, skipping embedding generation")
                return
            
            # Get all registered models
            registry = ModelRegistry()
            models = registry.list_models()
            
            if not models:
                print("⚠️ No models found in registry")
                return
            
            # Check existing embeddings using Supabase client
            supabase_client = registry.supabase_client
            existing_result = supabase_client.table("model_embeddings").select("model_id").execute()
            existing_embeddings = {row['model_id'] for row in existing_result.data}
            
            processed = 0
            
            for model_id, model_data in models.items():
                try:
                    # Skip if embedding already exists
                    if model_id in existing_embeddings:
                        continue
                    
                    provider = model_data.get('provider', 'unknown')
                    model_type = model_data.get('type', 'llm')
                    metadata = model_data.get('metadata', {})
                    
                    # Create searchable text from model information (same logic as intelligent_model_selector)
                    description = metadata.get('description', '')
                    specialized_tasks = metadata.get('specialized_tasks', [])
                    
                    # Combine all text for embedding
                    search_text = f"{model_id} {provider} model. "
                    if description:
                        search_text += f"{description} "
                    if specialized_tasks:
                        search_text += f"Specialized for: {', '.join(specialized_tasks)}"
                    
                    # Generate embedding using OpenAI service
                    embedding = await embedding_service.create_text_embedding(search_text)
                    
                    # Store embedding in database
                    embedding_data = {
                        'model_id': model_id,
                        'provider': provider,
                        'description': search_text,
                        'embedding': embedding
                    }
                    
                    result = supabase_client.table('model_embeddings').insert(embedding_data).execute()
                    
                    if result.data:
                        processed += 1
                    else:
                        logger.warning(f"Failed to store embedding for {model_id}")
                    
                except Exception as e:
                    logger.error(f"Error creating embedding for {model_id}: {e}")
                    continue
            
            print(f"✅ Generated {processed}/{len(models)} new embeddings")
            
            # Close embedding service
            await embedding_service.close()
            
        except Exception as e:
            logger.error(f"❌ Embedding generation error: {e}")
            raise
    
    async def _validate_system(self):
        """Validate system is working correctly"""
        print("🔍 Validating system...")
        
        try:
            registry = ModelRegistry()
            stats = registry.get_stats()
            
            print(f"📊 System validation results:")
            print(f"   Models: {stats['total_models']}")
            print(f"   By type: {stats['models_by_type']}")
            print(f"   By capability: {stats['models_by_capability']}")
            
            if stats['total_models'] == 0:
                raise Exception("No models found in registry")
            
            # Initialize and test intelligent selector
            try:
                from ...core.services.intelligent_model_selector import get_model_selector
                selector = await get_model_selector()
                
                # Test basic functionality
                available_models = await selector.get_available_models()
                print(f"   Available models for selection: {len(available_models)}")
                
            except Exception as e:
                logger.warning(f"⚠️ Intelligent selector initialization failed: {e}")
            
            print("✅ System validation completed")
            
        except Exception as e:
            logger.error(f"❌ System validation error: {e}")
            raise
    
    def _map_model_type(self, model_type_str: str) -> ModelType:
        """Map string model type to enum"""
        mapping = {
            'llm': ModelType.LLM,
            'embedding': ModelType.EMBEDDING,
            'rerank': ModelType.RERANK,
            'image': ModelType.IMAGE,
            'audio': ModelType.AUDIO,
            'video': ModelType.VIDEO,
            'vision': ModelType.VISION,
            'omni': ModelType.LLM  # Omni models are treated as LLM for now
        }
        return mapping.get(model_type_str.lower(), ModelType.LLM)
    
    def _map_capabilities(self, capabilities_list: list) -> list:
        """Map capability strings to enums"""
        mapping = {
            'text_generation': ModelCapability.TEXT_GENERATION,
            'chat': ModelCapability.CHAT,
            'embedding': ModelCapability.EMBEDDING,
            'reranking': ModelCapability.RERANKING,
            'reasoning': ModelCapability.REASONING,
            'image_generation': ModelCapability.IMAGE_GENERATION,
            'image_analysis': ModelCapability.IMAGE_ANALYSIS,
            'audio_transcription': ModelCapability.AUDIO_TRANSCRIPTION,
            'audio_realtime': ModelCapability.AUDIO_REALTIME,
            'speech_to_text': ModelCapability.SPEECH_TO_TEXT,
            'text_to_speech': ModelCapability.TEXT_TO_SPEECH,
            'conversation': ModelCapability.CONVERSATION,
            'image_understanding': ModelCapability.IMAGE_UNDERSTANDING,
            'ui_detection': ModelCapability.UI_DETECTION,
            'ocr': ModelCapability.OCR,
            'table_detection': ModelCapability.TABLE_DETECTION,
            'table_structure_recognition': ModelCapability.TABLE_STRUCTURE_RECOGNITION
        }
        
        result = []
        for cap in capabilities_list:
            if cap in mapping:
                result.append(mapping[cap])
            else:
                # Log unmapped capabilities for debugging
                logger.warning(f"Unknown capability '{cap}' - skipping")
        
        # Default to text generation if no capabilities
        if not result:
            result = [ModelCapability.TEXT_GENERATION]
            
        return result
    
    async def cleanup(self):
        """Clean up startup resources"""
        logger.info("🧹 Starting startup initializer cleanup...")
        
        try:
            # Clean up any persistent connections or resources
            # Most cleanup is handled by individual services, but we can do some general cleanup here
            
            # If we have any cached embedding services, clean them up
            if hasattr(self, '_embedding_service') and self._embedding_service:
                try:
                    await self._embedding_service.close()
                    logger.info("✅ Embedding service closed")
                except Exception as e:
                    logger.error(f"❌ Error closing embedding service: {e}")
            
            # Clean up model registry connections if needed
            if hasattr(self, '_model_registry'):
                try:
                    # ModelRegistry doesn't need explicit cleanup currently
                    # but this is where we'd add it if needed
                    pass
                except Exception as e:
                    logger.error(f"❌ Error cleaning up model registry: {e}")
            
            logger.info("✅ Startup initializer cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Error during startup cleanup: {e}")


# Global initializer instance
startup_initializer = StartupInitializer()

async def run_startup_initialization():
    """Main startup initialization function"""
    await startup_initializer.initialize_system()