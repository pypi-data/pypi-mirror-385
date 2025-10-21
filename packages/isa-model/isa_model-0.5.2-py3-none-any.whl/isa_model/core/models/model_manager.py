from typing import Dict, Optional, List, Any
import logging
from pathlib import Path
from datetime import datetime
from .model_storage import ModelStorage, LocalModelStorage
from .model_repo import ModelRegistry, ModelType, ModelCapability
from .model_billing_tracker import ModelBillingTracker, ModelOperationType
from .model_statistics_tracker import ModelStatisticsTracker
from ..config import ConfigManager

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Model lifecycle management service
    
    Handles the complete model lifecycle:
    - Model registration and metadata management
    - Model downloads, versions, and caching  
    - Cost tracking and billing across all operations
    - Integration with model training, evaluation, and deployment
    """
    
    
    def __init__(self, 
                 storage: Optional[ModelStorage] = None,
                 registry: Optional[ModelRegistry] = None,
                 billing_tracker: Optional[ModelBillingTracker] = None,
                 statistics_tracker: Optional[ModelStatisticsTracker] = None,
                 config_manager: Optional[ConfigManager] = None):
        self.storage = storage or LocalModelStorage()
        self.registry = registry or ModelRegistry()
        self.billing_tracker = billing_tracker or ModelBillingTracker(model_registry=self.registry)
        self.statistics_tracker = statistics_tracker or ModelStatisticsTracker(model_registry=self.registry)
        self.config_manager = config_manager or ConfigManager()
    
    def get_model_pricing(self, provider: str, model_name: str) -> Dict[str, float]:
        """获取模型定价信息（从数据库）"""
        try:
            if not self.registry or not hasattr(self.registry, 'supabase_client'):
                logger.warning("No database connection for pricing lookup")
                return {"input": 0.0, "output": 0.0}
            
            # 查询统一定价表
            result = self.registry.supabase_client.table('current_model_pricing').select('*').eq(
                'model_id', model_name
            ).eq('provider', provider).execute()
            
            if result.data and len(result.data) > 0:
                pricing = result.data[0]
                
                # 根据定价模型转换为统一格式
                pricing_model = pricing.get('pricing_model')
                unit_size = pricing.get('unit_size', 1)
                
                if pricing_model == 'per_token':
                    # 转换为每个 token 的成本
                    input_cost = float(pricing.get('input_cost_per_unit', 0)) * unit_size
                    output_cost = float(pricing.get('output_cost_per_unit', 0)) * unit_size
                elif pricing_model in ['per_character', 'per_minute', 'per_request']:
                    # 这些按原始单位计费
                    input_cost = float(pricing.get('input_cost_per_unit', 0))
                    output_cost = float(pricing.get('output_cost_per_unit', 0))
                    # 如果有基础请求费用，加到 input 成本中
                    if pricing.get('base_cost_per_request', 0) > 0:
                        input_cost += float(pricing.get('base_cost_per_request', 0))
                else:
                    input_cost = output_cost = 0.0
                
                return {"input": input_cost, "output": output_cost}
                
        except Exception as e:
            logger.warning(f"Failed to get pricing for {provider}/{model_name}: {e}")
        
        return {"input": 0.0, "output": 0.0}
    
    def calculate_cost(self, provider: str, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """计算请求成本"""
        pricing = self.get_model_pricing(provider, model_name)
        if pricing["input"] > 0:
            return (input_tokens + output_tokens) * pricing["input"] / 1000.0
        return 0.0
    
    def get_cheapest_model(self, provider: str, model_type: str = "llm") -> Optional[str]:
        """获取最便宜的模型"""
        try:
            models = self.config_manager.get_models_by_provider(provider)
            cheapest_model = None
            lowest_cost = float('inf')
            
            for model in models:
                if model.get("model_type") == model_type:
                    pricing = self.get_model_pricing(provider, model["model_id"])
                    if pricing["input"] > 0 and pricing["input"] < lowest_cost:
                        lowest_cost = pricing["input"]
                        cheapest_model = model["model_id"]
            
            return cheapest_model
        except Exception as e:
            logger.warning(f"Failed to find cheapest model for {provider}: {e}")
            return None

    # Local model download functionality removed - use cloud API services only
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all downloaded models with their metadata"""
        models = await self.storage.list_models()
        return [
            {
                "model_id": model_id,
                **metadata,
                **(self.registry.get_model_info(model_id) or {})
            }
            for model_id, metadata in models.items()
        ]
    
    async def remove_model(self, model_id: str) -> bool:
        """Remove a model and its metadata"""
        try:
            # Remove from storage
            storage_success = await self.storage.delete_model(model_id)
            
            # Unregister from registry
            registry_success = self.registry.unregister_model(model_id)
            
            return storage_success and registry_success
            
        except Exception as e:
            logger.error(f"Failed to remove model {model_id}: {e}")
            return False
    
    async def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        storage_info = await self.storage.get_metadata(model_id)
        registry_info = self.registry.get_model_info(model_id)
        
        if not storage_info and not registry_info:
            return None
            
        return {
            **(storage_info or {}),
            **(registry_info or {})
        }
    
    async def update_model(self, 
                          model_id: str, 
                          repo_id: str,
                          model_type: ModelType,
                          capabilities: List[ModelCapability],
                          revision: Optional[str] = None) -> bool:
        """Update a model to a new version"""
        try:
            return bool(await self.get_model(
                model_id=model_id,
                repo_id=repo_id,
                model_type=model_type,
                capabilities=capabilities,
                revision=revision,
                force_download=True
            ))
        except Exception as e:
            logger.error(f"Failed to update model {model_id}: {e}")
            return False 
    
    # === MODEL LIFECYCLE MANAGEMENT ===
    
    async def register_model_for_lifecycle(
        self,
        model_id: str,
        model_type: ModelType,
        capabilities: List[ModelCapability],
        provider: str = "custom",
        provider_model_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a model for lifecycle management
        
        Args:
            model_id: Unique identifier for the model
            model_type: Type of model (LLM, embedding, etc.)
            capabilities: List of model capabilities
            provider: Provider name for billing
            provider_model_name: Provider-specific model name for pricing
            metadata: Additional metadata
            
        Returns:
            True if registration successful
        """
        try:
            # Prepare metadata with billing info
            full_metadata = metadata or {}
            full_metadata.update({
                "provider": provider,
                "provider_model_name": provider_model_name or model_id,
                "registered_for_lifecycle": True,
                "lifecycle_stage": "registered"
            })
            
            # Register in model registry
            success = self.registry.register_model(
                model_id=model_id,
                model_type=model_type,
                capabilities=capabilities,
                metadata=full_metadata
            )
            
            if success:
                # Track registration operation
                self.billing_tracker.track_model_usage(
                    model_id=model_id,
                    operation_type=ModelOperationType.STORAGE,
                    provider=provider,
                    service_type="model_management",
                    operation="register_model",
                    metadata={"stage": "registration"}
                )
                
                logger.info(f"Successfully registered model {model_id} for lifecycle management")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to register model {model_id} for lifecycle: {e}")
            return False
    
    def track_model_usage(
        self,
        model_id: str,
        operation_type: ModelOperationType,
        provider: str,
        service_type: str,
        operation: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        input_units: Optional[float] = None,
        output_units: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Track model usage and costs
        
        This method should be called by:
        - Training services when training a model
        - Evaluation services when evaluating a model  
        - Deployment services when deploying a model
        - Inference services when using a model for inference
        """
        return self.billing_tracker.track_model_usage(
            model_id=model_id,
            operation_type=operation_type,
            provider=provider,
            service_type=service_type,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_units=input_units,
            output_units=output_units,
            metadata=metadata
        )
    
    async def update_model_stage(
        self,
        model_id: str,
        new_stage: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update model lifecycle stage
        
        Args:
            model_id: Model identifier
            new_stage: New lifecycle stage (training, evaluation, deployment, production, retired)
            metadata: Additional metadata for this stage
            
        Returns:
            True if update successful
        """
        try:
            # Get current model info
            model_info = self.registry.get_model_info(model_id)
            if not model_info:
                logger.error(f"Model {model_id} not found in registry")
                return False
            
            # Update metadata with new stage
            current_metadata = model_info.get("metadata", {})
            current_metadata.update({
                "lifecycle_stage": new_stage,
                "stage_updated_at": str(datetime.now()),
                **(metadata or {})
            })
            
            # Update in registry
            success = self.registry.register_model(
                model_id=model_id,
                model_type=ModelType(model_info["type"]),
                capabilities=[ModelCapability(cap) for cap in model_info["capabilities"]],
                metadata=current_metadata
            )
            
            if success:
                logger.info(f"Updated model {model_id} to stage: {new_stage}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update model {model_id} stage: {e}")
            return False
    
    def get_model_lifecycle_summary(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete lifecycle summary for a model including costs
        
        Returns:
            Dictionary with model info, lifecycle stage, and billing summary
        """
        try:
            # Get model info from registry
            model_info = self.registry.get_model_info(model_id)
            if not model_info:
                return None
            
            # Get billing summary from tracker
            billing_summary = self.billing_tracker.get_model_usage_summary(model_id)
            
            return {
                "model_id": model_id,
                "model_info": model_info,
                "billing_summary": billing_summary,
                "current_stage": model_info.get("metadata", {}).get("lifecycle_stage", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Failed to get lifecycle summary for {model_id}: {e}")
            return None
    
    def list_models_by_stage(self, stage: str) -> List[Dict[str, Any]]:
        """
        List all models in a specific lifecycle stage
        
        Args:
            stage: Lifecycle stage to filter by
            
        Returns:
            List of model dictionaries
        """
        try:
            all_models = self.registry.list_models()
            stage_models = []
            
            for model_id, model_info in all_models.items():
                current_stage = model_info.get("metadata", {}).get("lifecycle_stage")
                if current_stage == stage:
                    stage_models.append({
                        "model_id": model_id,
                        **model_info
                    })
            
            return stage_models
            
        except Exception as e:
            logger.error(f"Failed to list models by stage {stage}: {e}")
            return []
    
    def get_billing_summary_by_operation(self, operation_type: ModelOperationType) -> Dict[str, Any]:
        """Get billing summary for a specific operation type"""
        return self.billing_tracker.get_operation_summary(operation_type)
    
    def print_model_costs(self, model_id: str):
        """Print cost summary for a specific model"""
        self.billing_tracker.print_model_summary(model_id)