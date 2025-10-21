#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Model Billing Tracker - Core billing and usage tracking for model lifecycle management

This module tracks model usage, costs, and billing across all lifecycle stages:
- Training costs
- Evaluation costs  
- Deployment costs
- Inference costs

Integrates with ModelRegistry to store billing data in Supabase.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import json
import logging
from pathlib import Path
from enum import Enum
import os

logger = logging.getLogger(__name__)

class ModelOperationType(Enum):
    """Types of model operations that incur costs"""
    TRAINING = "training"
    EVALUATION = "evaluation"
    DEPLOYMENT = "deployment"
    INFERENCE = "inference"
    STORAGE = "storage"

class ServiceType(Enum):
    """Types of AI services"""
    LLM = "llm"
    EMBEDDING = "embedding"
    VISION = "vision"
    IMAGE_GENERATION = "image_generation"
    AUDIO_STT = "audio_stt"
    AUDIO_TTS = "audio_tts"
    AUDIO_REALTIME = "audio_realtime"

@dataclass
class ModelUsageRecord:
    """Record of model usage across its lifecycle"""
    timestamp: str
    model_id: str
    operation_type: str  # ModelOperationType
    provider: str
    service_type: str   # ServiceType
    operation: str      # Specific operation (e.g., 'chat', 'train', 'deploy')
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    input_units: Optional[float] = None  # For non-token based services
    output_units: Optional[float] = None
    cost_usd: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelUsageRecord':
        """Create from dictionary, filtering out database-specific fields"""
        # Filter out database fields that aren't part of the ModelUsageRecord
        filtered_data = {
            k: v for k, v in data.items() 
            if k in ['timestamp', 'model_id', 'operation_type', 'provider', 'service_type', 
                    'operation', 'input_tokens', 'output_tokens', 'total_tokens', 
                    'input_units', 'output_units', 'cost_usd', 'metadata']
        }
        return cls(**filtered_data)

class ModelBillingTracker:
    """
    Core billing tracker for model lifecycle management
    
    Integrates with ModelRegistry to store billing data in Supabase.
    Provides unified cost tracking across training, evaluation, deployment, and inference.
    """
    
    def __init__(self, model_registry=None, storage_path: Optional[str] = None):
        """
        Initialize model billing tracker
        
        Args:
            model_registry: ModelRegistry instance for database storage
            storage_path: Fallback local storage path
        """
        self.model_registry = model_registry
        
        # Fallback to local storage if no registry provided
        if storage_path is None:
            project_root = Path(__file__).parent.parent.parent.parent  # Go up one more level to reach project root
            self.storage_path = project_root / "model_billing_data.json"
        else:
            self.storage_path = Path(storage_path)
            
        self.usage_records: List[ModelUsageRecord] = []
        self.session_start = datetime.now(timezone.utc).isoformat()
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load existing billing data from registry or local storage"""
        try:
            if self.model_registry and hasattr(self.model_registry, 'supabase_client'):
                # Load from Supabase
                self._load_from_supabase()
            else:
                # Load from local storage
                self._load_from_local()
        except Exception as e:
            logger.warning(f"Could not load billing data: {e}")
            self.usage_records = []
    
    def _load_from_supabase(self):
        """Load billing data from Supabase - disabled as model_usage table removed"""
        # Model usage table has been removed, so no data to load
        self.usage_records = []
        logger.info("Model usage tracking disabled - no billing records to load from Supabase")
    
    def _load_from_local(self):
        """Load billing data from local JSON file"""
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.usage_records = [
                    ModelUsageRecord.from_dict(record) 
                    for record in data.get('usage_records', [])
                ]
            logger.info(f"Loaded {len(self.usage_records)} billing records from local storage")
    
    def _save_data(self):
        """Save billing data to registry or local storage"""
        try:
            if self.model_registry and hasattr(self.model_registry, 'supabase_client'):
                self._save_to_supabase()
            else:
                self._save_to_local()
        except Exception as e:
            logger.error(f"Could not save billing data: {e}")
    
    def _save_to_supabase(self):
        """Save billing data to Supabase"""
        # Disabled to prevent model_usage table writes
        # try:
        #     if not self.model_registry or not hasattr(self.model_registry, 'supabase_client'):
        #         logger.warning("No Supabase client available for billing data saving")
        #         return
        #     
        #     if not self.usage_records:
        #         logger.debug("No usage records to save")
        #         return
        #     
        #     # Convert usage records to dict format for Supabase
        #     records_to_save = []
        #     for record in self.usage_records:
        #         record_dict = record.to_dict()
        #         # Ensure all required fields are present and properly formatted
        #         record_dict['created_at'] = record_dict.get('timestamp')
        #         records_to_save.append(record_dict)
        #     
        #     # Insert records into model_usage table (simple insert, let DB handle duplicates)
        #     result = self.model_registry.supabase_client.table('model_usage').insert(
        #         records_to_save
        #     ).execute()
        #     
        #     if result.data:
        #         logger.info(f"Successfully saved {len(result.data)} billing records to Supabase")
        #     else:
        #         logger.warning("No records were saved to Supabase")
        #         
        # except Exception as e:
        #     logger.error(f"Failed to save billing data to Supabase: {e}")
        #     # Fallback to local storage on Supabase failure
        #     logger.info("Falling back to local storage for billing data")
        #     self._save_to_local()
        pass
    
    def _save_to_local(self):
        """Save billing data to local JSON file"""
        # Disabled to prevent automatic file creation
        # self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        # 
        # data = {
        #     "session_start": self.session_start,
        #     "last_updated": datetime.now(timezone.utc).isoformat(),
        #     "usage_records": [record.to_dict() for record in self.usage_records]
        # }
        # 
        # with open(self.storage_path, 'w') as f:
        #     json.dump(data, f, indent=2)
        pass
    
    def track_model_usage(
        self,
        model_id: str,
        operation_type: Union[str, ModelOperationType],
        provider: str,
        service_type: Union[str, ServiceType],
        operation: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        input_units: Optional[float] = None,
        output_units: Optional[float] = None,
        cost_usd: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ModelUsageRecord:
        """
        Track model usage across its lifecycle
        
        Args:
            model_id: Unique model identifier
            operation_type: Type of operation (training, evaluation, deployment, inference)
            provider: Provider name (openai, replicate, etc.)
            service_type: Type of service
            operation: Specific operation performed
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            input_units: Input units for non-token services
            output_units: Output units for non-token services
            cost_usd: Cost in USD for this operation
            metadata: Additional metadata
            
        Returns:
            ModelUsageRecord object
        """
        # Convert enums to strings
        if isinstance(operation_type, ModelOperationType):
            operation_type = operation_type.value
        if isinstance(service_type, ServiceType):
            service_type = service_type.value
        
        # Calculate total tokens
        total_tokens = None
        if input_tokens is not None or output_tokens is not None:
            total_tokens = (input_tokens or 0) + (output_tokens or 0)
        
        # Use provided cost_usd or calculate it
        if cost_usd is None:
            cost_usd = self._calculate_cost(
                provider, model_id, operation_type,
                input_tokens, output_tokens, input_units, output_units
            )
        
        # Create usage record
        record = ModelUsageRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            model_id=model_id,
            operation_type=operation_type,
            provider=provider,
            service_type=service_type,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_units=input_units,
            output_units=output_units,
            cost_usd=cost_usd,
            metadata=metadata or {}
        )
        
        # Add to records and save
        self.usage_records.append(record)
        self._save_data()
        
        logger.info(f"Tracked model usage: {model_id} - {operation_type} - ${cost_usd:.6f}")
        return record
    
    def _calculate_cost(
        self,
        provider: str,
        model_id: str,
        operation_type: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        input_units: Optional[float] = None,
        output_units: Optional[float] = None
    ) -> float:
        """Calculate cost for model usage"""
        try:
            # Import here to avoid circular imports
            from .model_manager import ModelManager
            
            # Create ModelManager instance to get pricing
            model_manager = ModelManager()
            
            # Use the centralized pricing calculation
            if input_tokens is not None and output_tokens is not None:
                return model_manager.calculate_cost(provider, model_id, input_tokens, output_tokens)
            
            # Fallback for non-token based services
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating cost for model {model_id}: {e}")
            return 0.0
    
    def get_model_usage_summary(self, model_id: str) -> Dict[str, Any]:
        """Get usage summary for a specific model"""
        model_records = [
            record for record in self.usage_records
            if record.model_id == model_id
        ]
        
        return self._generate_summary(model_records, f"Model {model_id} Usage")
    
    def get_operation_summary(self, operation_type: Union[str, ModelOperationType]) -> Dict[str, Any]:
        """Get usage summary for a specific operation type"""
        if isinstance(operation_type, ModelOperationType):
            operation_type = operation_type.value
            
        operation_records = [
            record for record in self.usage_records
            if record.operation_type == operation_type
        ]
        
        return self._generate_summary(operation_records, f"{operation_type.title()} Operations")
    
    def get_provider_summary(self, provider: str) -> Dict[str, Any]:
        """Get usage summary for a specific provider"""
        provider_records = [
            record for record in self.usage_records
            if record.provider == provider
        ]
        
        return self._generate_summary(provider_records, f"{provider.title()} Usage")
    
    def _generate_summary(self, records: List[ModelUsageRecord], title: str) -> Dict[str, Any]:
        """Generate usage summary from records"""
        if not records:
            return {
                "title": title,
                "total_cost": 0.0,
                "total_requests": 0,
                "operations": {},
                "models": {},
                "providers": {}
            }
        
        total_cost = sum(record.cost_usd or 0 for record in records)
        total_requests = len(records)
        
        # Group by operation type
        operations = {}
        for record in records:
            if record.operation_type not in operations:
                operations[record.operation_type] = {
                    "cost": 0.0,
                    "requests": 0
                }
            operations[record.operation_type]["cost"] += record.cost_usd or 0
            operations[record.operation_type]["requests"] += 1
        
        # Group by model
        models = {}
        for record in records:
            if record.model_id not in models:
                models[record.model_id] = {
                    "cost": 0.0,
                    "requests": 0,
                    "total_tokens": 0
                }
            models[record.model_id]["cost"] += record.cost_usd or 0
            models[record.model_id]["requests"] += 1
            if record.total_tokens:
                models[record.model_id]["total_tokens"] += record.total_tokens
        
        # Group by provider
        providers = {}
        for record in records:
            if record.provider not in providers:
                providers[record.provider] = {
                    "cost": 0.0,
                    "requests": 0
                }
            providers[record.provider]["cost"] += record.cost_usd or 0
            providers[record.provider]["requests"] += 1
        
        return {
            "title": title,
            "total_cost": round(total_cost, 6),
            "total_requests": total_requests,
            "operations": operations,
            "models": models,
            "providers": providers,
            "period": {
                "start": records[0].timestamp if records else None,
                "end": records[-1].timestamp if records else None
            }
        }
    
    def print_model_summary(self, model_id: str):
        """Print usage summary for a specific model"""
        summary = self.get_model_usage_summary(model_id)
        
        print(f"\n🤖 {summary['title']} Summary")
        print("=" * 50)
        print(f"💵 Total Cost: ${summary['total_cost']:.6f}")
        print(f"📊 Total Operations: {summary['total_requests']}")
        
        if summary['operations']:
            print("\n📈 By Operation Type:")
            for operation, data in summary['operations'].items():
                print(f"  {operation}: ${data['cost']:.6f} ({data['requests']} operations)")
        
        if summary['providers']:
            print("\n🔧 By Provider:")
            for provider, data in summary['providers'].items():
                print(f"  {provider}: ${data['cost']:.6f} ({data['requests']} requests)")

# Global model billing tracker instance
_global_model_tracker: Optional[ModelBillingTracker] = None

def get_model_billing_tracker() -> ModelBillingTracker:
    """Get the global model billing tracker instance"""
    global _global_model_tracker
    if _global_model_tracker is None:
        # Try to get ModelRegistry instance
        try:
            from .model_repo import ModelRegistry
            registry = ModelRegistry()
            _global_model_tracker = ModelBillingTracker(model_registry=registry)
        except Exception:
            _global_model_tracker = ModelBillingTracker()
    return _global_model_tracker

def track_model_usage(**kwargs) -> ModelUsageRecord:
    """Convenience function to track model usage"""
    return get_model_billing_tracker().track_model_usage(**kwargs)

def print_model_billing_summary(model_id: str = None, operation_type: str = None):
    """Convenience function to print billing summary"""
    tracker = get_model_billing_tracker()
    if model_id:
        tracker.print_model_summary(model_id)
    elif operation_type:
        summary = tracker.get_operation_summary(operation_type)
        print(f"\n💰 {summary['title']} Summary")
        print("=" * 50)
        print(f"💵 Total Cost: ${summary['total_cost']:.6f}")
        print(f"📊 Total Operations: {summary['total_requests']}")