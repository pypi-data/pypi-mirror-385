#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Deployment Billing Tracker - Specialized billing for deployment and training operations

Extends the core ModelBillingTracker with deployment-specific metrics:
- GPU runtime hours
- Instance type costs
- Training epochs/steps billing
- Deployment lifecycle costs
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
import json
import logging
from enum import Enum
from .model_billing_tracker import ModelBillingTracker, ModelUsageRecord, ModelOperationType

logger = logging.getLogger(__name__)

class DeploymentProvider(Enum):
    """Deployment providers"""
    MODAL = "modal"
    TRITON_LOCAL = "triton_local"
    TRITON_CLOUD = "triton_cloud"
    RUNPOD = "runpod"
    LAMBDA_LABS = "lambda_labs"
    COREWEAVE = "coreweave"

class GPUType(Enum):
    """GPU types for cost calculation"""
    RTX_4090 = "rtx_4090"
    RTX_A6000 = "rtx_a6000"
    A100_40GB = "a100_40gb"
    A100_80GB = "a100_80gb"
    H100 = "h100"
    T4 = "t4"
    V100 = "v100"

@dataclass
class DeploymentUsageRecord(ModelUsageRecord):
    """Extended usage record for deployment operations"""
    # GPU/Infrastructure metrics
    gpu_type: Optional[str] = None
    gpu_count: Optional[int] = None
    runtime_hours: Optional[float] = None
    cpu_cores: Optional[int] = None
    memory_gb: Optional[int] = None
    
    # Training-specific metrics
    training_epochs: Optional[int] = None
    training_steps: Optional[int] = None
    dataset_size: Optional[int] = None
    
    # Deployment-specific metrics
    deployment_duration_hours: Optional[float] = None
    requests_served: Optional[int] = None
    avg_latency_ms: Optional[float] = None
    
    # Infrastructure costs
    compute_cost_usd: Optional[float] = None
    storage_cost_usd: Optional[float] = None
    network_cost_usd: Optional[float] = None

class DeploymentBillingTracker(ModelBillingTracker):
    """
    Specialized billing tracker for deployment and training operations
    
    Extends ModelBillingTracker with deployment-specific cost calculations
    and metrics tracking for GPU-based operations.
    """
    
    def __init__(self, model_registry=None, storage_path: Optional[str] = None):
        super().__init__(model_registry, storage_path)
        
        # Load pricing data for deployment providers
        self.pricing_data = self._load_deployment_pricing()
    
    def _load_deployment_pricing(self) -> Dict[str, Dict[str, float]]:
        """Load pricing data for different deployment providers and GPU types"""
        return {
            "modal": {
                "t4": 0.50,      # $/hour
                "rtx_4090": 0.80,
                "a100_40gb": 2.50,
                "a100_80gb": 4.00,
                "h100": 8.00,
                "base_compute": 0.10  # $/hour base compute
            },
            "triton_local": {
                "electricity": 0.12,  # $/kWh
                "gpu_tdp": {
                    "rtx_4090": 450,   # Watts
                    "a100_40gb": 400,
                    "a100_80gb": 400,
                    "h100": 700
                }
            },
            "runpod": {
                "rtx_4090": 0.44,
                "rtx_a6000": 0.79,
                "a100_40gb": 1.69,
                "a100_80gb": 2.89,
                "h100": 4.89
            },
            "lambda_labs": {
                "rtx_4090": 0.50,
                "a100_40gb": 1.50,
                "a100_80gb": 2.50,
                "h100": 4.50
            },
            "coreweave": {
                "rtx_4090": 0.57,
                "a100_40gb": 2.06,
                "a100_80gb": 2.23,
                "h100": 4.76
            }
        }
    
    def track_deployment_usage(
        self,
        model_id: str,
        provider: Union[str, DeploymentProvider],
        operation_type: Union[str, ModelOperationType],
        service_type: str,
        operation: str,
        
        # GPU/Infrastructure metrics
        gpu_type: Optional[Union[str, GPUType]] = None,
        gpu_count: Optional[int] = None,
        runtime_hours: Optional[float] = None,
        cpu_cores: Optional[int] = None,
        memory_gb: Optional[int] = None,
        
        # Training-specific
        training_epochs: Optional[int] = None,
        training_steps: Optional[int] = None,
        dataset_size: Optional[int] = None,
        
        # Deployment-specific
        deployment_duration_hours: Optional[float] = None,
        requests_served: Optional[int] = None,
        avg_latency_ms: Optional[float] = None,
        
        # Standard billing
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        cost_usd: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DeploymentUsageRecord:
        """
        Track deployment/training usage with specialized metrics
        
        Args:
            model_id: Model identifier
            provider: Deployment provider
            operation_type: Type of operation (training, deployment, inference)
            service_type: Service type (llm, vision, etc.)
            operation: Specific operation
            gpu_type: Type of GPU used
            gpu_count: Number of GPUs
            runtime_hours: Hours of runtime
            training_epochs: Number of training epochs
            deployment_duration_hours: Hours deployment was active
            ... (other parameters as documented)
            
        Returns:
            DeploymentUsageRecord with calculated costs
        """
        # Convert enums to strings
        if isinstance(provider, DeploymentProvider):
            provider = provider.value
        if isinstance(operation_type, ModelOperationType):
            operation_type = operation_type.value
        if isinstance(gpu_type, GPUType):
            gpu_type = gpu_type.value
        
        # Calculate deployment-specific costs
        if cost_usd is None:
            cost_breakdown = self._calculate_deployment_cost(
                provider, gpu_type, gpu_count, runtime_hours,
                deployment_duration_hours, training_epochs, training_steps
            )
            cost_usd = cost_breakdown["total_cost"]
            compute_cost = cost_breakdown["compute_cost"]
            storage_cost = cost_breakdown["storage_cost"]
            network_cost = cost_breakdown["network_cost"]
        else:
            compute_cost = cost_usd  # If provided, assume it's compute cost
            storage_cost = 0.0
            network_cost = 0.0
        
        # Create deployment usage record
        record = DeploymentUsageRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            model_id=model_id,
            operation_type=operation_type,
            provider=provider,
            service_type=service_type,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=(input_tokens or 0) + (output_tokens or 0) if input_tokens or output_tokens else None,
            cost_usd=cost_usd,
            metadata=metadata or {},
            
            # Deployment-specific fields
            gpu_type=gpu_type,
            gpu_count=gpu_count,
            runtime_hours=runtime_hours,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            training_epochs=training_epochs,
            training_steps=training_steps,
            dataset_size=dataset_size,
            deployment_duration_hours=deployment_duration_hours,
            requests_served=requests_served,
            avg_latency_ms=avg_latency_ms,
            compute_cost_usd=compute_cost,
            storage_cost_usd=storage_cost,
            network_cost_usd=network_cost
        )
        
        # Add to records and save
        self.usage_records.append(record)
        self._save_data()
        
        logger.info(f"Tracked deployment usage: {model_id} - {provider} - {gpu_type} - ${cost_usd:.4f}")
        return record
    
    def _calculate_deployment_cost(
        self,
        provider: str,
        gpu_type: Optional[str],
        gpu_count: Optional[int],
        runtime_hours: Optional[float],
        deployment_duration_hours: Optional[float],
        training_epochs: Optional[int],
        training_steps: Optional[int]
    ) -> Dict[str, float]:
        """Calculate deployment costs based on provider and usage"""
        
        gpu_count = gpu_count or 1
        runtime_hours = runtime_hours or deployment_duration_hours or 1.0
        
        compute_cost = 0.0
        storage_cost = 0.0
        network_cost = 0.0
        
        try:
            if provider in self.pricing_data:
                pricing = self.pricing_data[provider]
                
                if provider == "modal":
                    # Modal pricing: per-GPU hourly rate
                    if gpu_type and gpu_type in pricing:
                        compute_cost = pricing[gpu_type] * gpu_count * runtime_hours
                    else:
                        compute_cost = pricing.get("base_compute", 0.10) * runtime_hours
                
                elif provider == "triton_local":
                    # Local deployment: electricity costs
                    if gpu_type and gpu_type in pricing["gpu_tdp"]:
                        power_watts = pricing["gpu_tdp"][gpu_type] * gpu_count
                        kwh_used = (power_watts / 1000) * runtime_hours
                        compute_cost = kwh_used * pricing["electricity"]
                
                elif provider in ["runpod", "lambda_labs", "coreweave"]:
                    # Cloud GPU providers: per-GPU hourly rates
                    if gpu_type and gpu_type in pricing:
                        compute_cost = pricing[gpu_type] * gpu_count * runtime_hours
                
                # Add storage costs (simplified)
                storage_cost = runtime_hours * 0.01  # $0.01/hour for storage
                
                # Add network costs for training (data transfer)
                if training_epochs and training_epochs > 0:
                    network_cost = training_epochs * 0.05  # $0.05 per epoch for data
            
        except Exception as e:
            logger.error(f"Error calculating deployment cost: {e}")
            compute_cost = 0.0
        
        total_cost = compute_cost + storage_cost + network_cost
        
        return {
            "total_cost": round(total_cost, 6),
            "compute_cost": round(compute_cost, 6),
            "storage_cost": round(storage_cost, 6),
            "network_cost": round(network_cost, 6)
        }
    
    def estimate_deployment_cost(
        self,
        provider: str,
        gpu_type: str,
        gpu_count: int = 1,
        estimated_hours: float = 1.0,
        operation_type: str = "deployment"
    ) -> Dict[str, float]:
        """
        Estimate deployment costs before starting deployment
        
        Args:
            provider: Deployment provider
            gpu_type: GPU type to use
            gpu_count: Number of GPUs
            estimated_hours: Estimated runtime hours
            operation_type: Type of operation
            
        Returns:
            Cost breakdown dictionary
        """
        return self._calculate_deployment_cost(
            provider, gpu_type, gpu_count, estimated_hours,
            estimated_hours, None, None
        )
    
    def get_deployment_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        provider: Optional[str] = None,
        gpu_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get deployment cost summary with filters"""
        
        # Filter records
        filtered_records = []
        for record in self.usage_records:
            # Check if it's a deployment record
            if not isinstance(record, DeploymentUsageRecord):
                continue
            
            # Apply filters
            if start_date and datetime.fromisoformat(record.timestamp.replace('Z', '+00:00')) < start_date:
                continue
            if end_date and datetime.fromisoformat(record.timestamp.replace('Z', '+00:00')) > end_date:
                continue
            if provider and record.provider != provider:
                continue
            if gpu_type and record.gpu_type != gpu_type:
                continue
                
            filtered_records.append(record)
        
        if not filtered_records:
            return {
                "total_cost": 0.0,
                "total_gpu_hours": 0.0,
                "deployments": 0,
                "by_provider": {},
                "by_gpu_type": {},
                "by_operation": {}
            }
        
        # Calculate summary
        total_cost = sum(record.cost_usd or 0 for record in filtered_records)
        total_gpu_hours = sum((record.runtime_hours or 0) * (record.gpu_count or 1) for record in filtered_records)
        total_deployments = len(filtered_records)
        
        # Group by provider
        by_provider = {}
        for record in filtered_records:
            if record.provider not in by_provider:
                by_provider[record.provider] = {"cost": 0.0, "gpu_hours": 0.0, "count": 0}
            by_provider[record.provider]["cost"] += record.cost_usd or 0
            by_provider[record.provider]["gpu_hours"] += (record.runtime_hours or 0) * (record.gpu_count or 1)
            by_provider[record.provider]["count"] += 1
        
        # Group by GPU type
        by_gpu_type = {}
        for record in filtered_records:
            gpu = record.gpu_type or "unknown"
            if gpu not in by_gpu_type:
                by_gpu_type[gpu] = {"cost": 0.0, "gpu_hours": 0.0, "count": 0}
            by_gpu_type[gpu]["cost"] += record.cost_usd or 0
            by_gpu_type[gpu]["gpu_hours"] += (record.runtime_hours or 0) * (record.gpu_count or 1)
            by_gpu_type[gpu]["count"] += 1
        
        # Group by operation
        by_operation = {}
        for record in filtered_records:
            op = record.operation_type
            if op not in by_operation:
                by_operation[op] = {"cost": 0.0, "gpu_hours": 0.0, "count": 0}
            by_operation[op]["cost"] += record.cost_usd or 0
            by_operation[op]["gpu_hours"] += (record.runtime_hours or 0) * (record.gpu_count or 1)
            by_operation[op]["count"] += 1
        
        return {
            "total_cost": round(total_cost, 6),
            "total_gpu_hours": round(total_gpu_hours, 2),
            "deployments": total_deployments,
            "avg_cost_per_deployment": round(total_cost / total_deployments, 6) if total_deployments > 0 else 0,
            "avg_cost_per_gpu_hour": round(total_cost / total_gpu_hours, 6) if total_gpu_hours > 0 else 0,
            "by_provider": by_provider,
            "by_gpu_type": by_gpu_type,
            "by_operation": by_operation,
            "period": {
                "start": filtered_records[0].timestamp if filtered_records else None,
                "end": filtered_records[-1].timestamp if filtered_records else None
            }
        }

# Global deployment billing tracker instance
_global_deployment_tracker: Optional[DeploymentBillingTracker] = None

def get_deployment_billing_tracker() -> DeploymentBillingTracker:
    """Get the global deployment billing tracker instance"""
    global _global_deployment_tracker
    if _global_deployment_tracker is None:
        try:
            from .model_repo import ModelRegistry
            registry = ModelRegistry()
            _global_deployment_tracker = DeploymentBillingTracker(model_registry=registry)
        except Exception:
            _global_deployment_tracker = DeploymentBillingTracker()
    return _global_deployment_tracker

def track_deployment_usage(**kwargs) -> DeploymentUsageRecord:
    """Convenience function to track deployment usage"""
    return get_deployment_billing_tracker().track_deployment_usage(**kwargs)

def estimate_deployment_cost(**kwargs) -> Dict[str, float]:
    """Convenience function to estimate deployment cost"""
    return get_deployment_billing_tracker().estimate_deployment_cost(**kwargs)