"""
Triton deployment configuration

Configuration classes for Triton Inference Server deployment with TensorRT-LLM backend.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from pathlib import Path


class TritonServiceType(Enum):
    """Triton service types"""
    LLM = "llm"
    VISION = "vision"
    EMBEDDING = "embedding"


class TritonBackend(Enum):
    """Triton backends"""
    TENSORRT_LLM = "tensorrtllm"
    PYTHON = "python"
    ONNX = "onnxruntime"
    PYTORCH = "pytorch"


@dataclass
class TritonConfig:
    """Configuration for Triton Inference Server deployment"""
    
    # Service identification
    service_name: str
    service_type: TritonServiceType
    model_id: str
    
    # Model configuration
    model_name: str
    model_version: str = "1"
    backend: TritonBackend = TritonBackend.TENSORRT_LLM
    
    # Model paths
    model_repository: str = "/models"
    hf_model_path: str = "/workspace/hf_model"
    engine_output_path: str = "/workspace/engines"
    
    # Performance settings
    max_batch_size: int = 8
    max_sequence_length: int = 2048
    instance_group_count: int = 1
    instance_group_kind: str = "KIND_GPU"
    
    # TensorRT-LLM specific
    use_tensorrt: bool = True
    tensorrt_precision: str = "float16"  # float16, int8, int4
    use_inflight_batching: bool = True
    enable_streaming: bool = True
    
    # Container configuration
    gpu_type: str = "nvidia"
    gpu_count: int = 1
    memory_gb: int = 32
    container_image: str = "nvcr.io/nvidia/tritonserver:23.10-trtllm-python-py3"
    
    # Network configuration
    http_port: int = 8000
    grpc_port: int = 8001
    metrics_port: int = 8002
    
    # Build configuration
    build_container_image: str = "nvcr.io/nvidia/tensorrtllm/tensorrt-llm:latest"
    build_options: Dict[str, Any] = field(default_factory=lambda: {
        "gemm_plugin": "float16",
        "gpt_attention_plugin": "float16",
        "paged_kv_cache": True,
        "remove_input_padding": True
    })
    
    # Environment variables
    environment: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "service_name": self.service_name,
            "service_type": self.service_type.value,
            "model_id": self.model_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "backend": self.backend.value,
            "model_repository": self.model_repository,
            "hf_model_path": self.hf_model_path,
            "engine_output_path": self.engine_output_path,
            "max_batch_size": self.max_batch_size,
            "max_sequence_length": self.max_sequence_length,
            "instance_group_count": self.instance_group_count,
            "instance_group_kind": self.instance_group_kind,
            "use_tensorrt": self.use_tensorrt,
            "tensorrt_precision": self.tensorrt_precision,
            "use_inflight_batching": self.use_inflight_batching,
            "enable_streaming": self.enable_streaming,
            "gpu_type": self.gpu_type,
            "gpu_count": self.gpu_count,
            "memory_gb": self.memory_gb,
            "container_image": self.container_image,
            "http_port": self.http_port,
            "grpc_port": self.grpc_port,
            "metrics_port": self.metrics_port,
            "build_container_image": self.build_container_image,
            "build_options": self.build_options,
            "environment": self.environment
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TritonConfig":
        """Create from dictionary"""
        return cls(
            service_name=data["service_name"],
            service_type=TritonServiceType(data["service_type"]),
            model_id=data["model_id"],
            model_name=data["model_name"],
            model_version=data.get("model_version", "1"),
            backend=TritonBackend(data.get("backend", "tensorrtllm")),
            model_repository=data.get("model_repository", "/models"),
            hf_model_path=data.get("hf_model_path", "/workspace/hf_model"),
            engine_output_path=data.get("engine_output_path", "/workspace/engines"),
            max_batch_size=data.get("max_batch_size", 8),
            max_sequence_length=data.get("max_sequence_length", 2048),
            instance_group_count=data.get("instance_group_count", 1),
            instance_group_kind=data.get("instance_group_kind", "KIND_GPU"),
            use_tensorrt=data.get("use_tensorrt", True),
            tensorrt_precision=data.get("tensorrt_precision", "float16"),
            use_inflight_batching=data.get("use_inflight_batching", True),
            enable_streaming=data.get("enable_streaming", True),
            gpu_type=data.get("gpu_type", "nvidia"),
            gpu_count=data.get("gpu_count", 1),
            memory_gb=data.get("memory_gb", 32),
            container_image=data.get("container_image", "nvcr.io/nvidia/tritonserver:23.10-trtllm-python-py3"),
            http_port=data.get("http_port", 8000),
            grpc_port=data.get("grpc_port", 8001),
            metrics_port=data.get("metrics_port", 8002),
            build_container_image=data.get("build_container_image", "nvcr.io/nvidia/tensorrtllm/tensorrt-llm:latest"),
            build_options=data.get("build_options", {
                "gemm_plugin": "float16",
                "gpt_attention_plugin": "float16",
                "paged_kv_cache": True,
                "remove_input_padding": True
            }),
            environment=data.get("environment", {})
        )


# Predefined configurations for common use cases
def create_llm_triton_config(service_name: str, model_id: str, 
                           precision: str = "float16",
                           max_batch_size: int = 8) -> TritonConfig:
    """Create configuration for LLM service with TensorRT-LLM"""
    return TritonConfig(
        service_name=service_name,
        service_type=TritonServiceType.LLM,
        model_id=model_id,
        model_name=service_name.replace("-", "_"),
        tensorrt_precision=precision,
        max_batch_size=max_batch_size,
        memory_gb=32 if precision == "float16" else 24,
        use_inflight_batching=True,
        enable_streaming=True
    )


def create_vision_triton_config(service_name: str, model_id: str) -> TritonConfig:
    """Create configuration for vision service"""
    return TritonConfig(
        service_name=service_name,
        service_type=TritonServiceType.VISION,
        model_id=model_id,
        model_name=service_name.replace("-", "_"),
        backend=TritonBackend.PYTHON,
        use_tensorrt=False,
        memory_gb=16,
        max_batch_size=16
    )


def create_embedding_triton_config(service_name: str, model_id: str) -> TritonConfig:
    """Create configuration for embedding service"""
    return TritonConfig(
        service_name=service_name,
        service_type=TritonServiceType.EMBEDDING,
        model_id=model_id,
        model_name=service_name.replace("-", "_"),
        backend=TritonBackend.PYTHON,
        use_tensorrt=False,
        memory_gb=8,
        max_batch_size=32
    )