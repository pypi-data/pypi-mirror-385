"""
Modal deployment configuration

Simplified configuration for Modal-specific deployments.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class ModalServiceType(Enum):
    """Modal service types"""
    LLM = "llm"
    VISION = "vision"
    AUDIO = "audio"
    EMBEDDING = "embedding"
    VIDEO = "video"


@dataclass
class ModalConfig:
    """Configuration for Modal deployment"""
    
    # Service identification
    service_name: str
    service_type: ModalServiceType
    model_id: str
    
    # Modal-specific settings
    image_tag: str = "latest"
    cpu_cores: int = 2
    memory_gb: int = 8
    gpu_type: Optional[str] = None  # e.g., "A10G", "T4", "A100"
    timeout_seconds: int = 300
    
    # Scaling configuration
    min_instances: int = 0
    max_instances: int = 10
    concurrency_limit: int = 1
    
    # Environment variables
    environment: Dict[str, str] = field(default_factory=dict)
    
    # Service-specific configuration
    service_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "service_name": self.service_name,
            "service_type": self.service_type.value,
            "model_id": self.model_id,
            "image_tag": self.image_tag,
            "cpu_cores": self.cpu_cores,
            "memory_gb": self.memory_gb,
            "gpu_type": self.gpu_type,
            "timeout_seconds": self.timeout_seconds,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "concurrency_limit": self.concurrency_limit,
            "environment": self.environment,
            "service_config": self.service_config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModalConfig":
        """Create from dictionary"""
        return cls(
            service_name=data["service_name"],
            service_type=ModalServiceType(data["service_type"]),
            model_id=data["model_id"],
            image_tag=data.get("image_tag", "latest"),
            cpu_cores=data.get("cpu_cores", 2),
            memory_gb=data.get("memory_gb", 8),
            gpu_type=data.get("gpu_type"),
            timeout_seconds=data.get("timeout_seconds", 300),
            min_instances=data.get("min_instances", 0),
            max_instances=data.get("max_instances", 10),
            concurrency_limit=data.get("concurrency_limit", 1),
            environment=data.get("environment", {}),
            service_config=data.get("service_config", {})
        )


# Predefined configurations for common service types
def create_llm_config(service_name: str, model_id: str, gpu_type: str = "A10G") -> ModalConfig:
    """Create configuration for LLM service"""
    return ModalConfig(
        service_name=service_name,
        service_type=ModalServiceType.LLM,
        model_id=model_id,
        gpu_type=gpu_type,
        memory_gb=16,
        timeout_seconds=600,
        max_instances=5
    )


def create_vision_config(service_name: str, model_id: str, gpu_type: str = "T4") -> ModalConfig:
    """Create configuration for vision service"""
    return ModalConfig(
        service_name=service_name,
        service_type=ModalServiceType.VISION,
        model_id=model_id,
        gpu_type=gpu_type,
        memory_gb=12,
        timeout_seconds=300,
        max_instances=10
    )


def create_audio_config(service_name: str, model_id: str, gpu_type: str = "T4") -> ModalConfig:
    """Create configuration for audio service"""
    return ModalConfig(
        service_name=service_name,
        service_type=ModalServiceType.AUDIO,
        model_id=model_id,
        gpu_type=gpu_type,
        memory_gb=8,
        timeout_seconds=300,
        max_instances=8
    )


def create_embedding_config(service_name: str, model_id: str, gpu_type: str = "T4") -> ModalConfig:
    """Create configuration for embedding service"""
    return ModalConfig(
        service_name=service_name,
        service_type=ModalServiceType.EMBEDDING,
        model_id=model_id,
        gpu_type=gpu_type,
        memory_gb=6,
        timeout_seconds=120,
        max_instances=15
    )