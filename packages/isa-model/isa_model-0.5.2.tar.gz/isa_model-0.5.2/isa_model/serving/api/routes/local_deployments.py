"""
Local GPU deployments API routes

Endpoints for managing local GPU model deployments.
"""

import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from ....deployment.core.deployment_manager import DeploymentManager
from ....deployment.local.config import (
    LocalGPUConfig, LocalServiceType, LocalBackend,
    create_vllm_config, create_tensorrt_config, create_transformers_config
)
from ...middleware.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/local", tags=["local-deployments"])


# Request/Response Models
class LocalDeployRequest(BaseModel):
    """Local deployment request"""
    service_name: str = Field(..., description="Unique service name")
    model_id: str = Field(..., description="HuggingFace model ID")
    backend: str = Field("transformers", description="Inference backend (vllm, tensorrt_llm, transformers)")
    service_type: str = Field("llm", description="Service type (llm, vision, audio, embedding)")
    
    # Model configuration
    model_precision: str = Field("float16", description="Model precision")
    max_model_len: int = Field(2048, description="Maximum sequence length")
    max_batch_size: int = Field(8, description="Maximum batch size")
    
    # GPU settings
    gpu_id: Optional[int] = Field(None, description="Specific GPU ID to use")
    gpu_memory_utilization: float = Field(0.9, description="GPU memory utilization fraction")
    
    # Performance settings
    tensor_parallel_size: int = Field(1, description="Tensor parallel size")
    enable_chunked_prefill: bool = Field(True, description="Enable chunked prefill")
    enable_prefix_caching: bool = Field(True, description="Enable prefix caching")
    
    # Quantization
    quantization: Optional[str] = Field(None, description="Quantization method (int8, int4, awq, gptq)")
    
    # Advanced settings
    trust_remote_code: bool = Field(False, description="Trust remote code in model")
    revision: Optional[str] = Field(None, description="Model revision")
    
    # Backend-specific settings
    vllm_args: Dict[str, Any] = Field(default_factory=dict, description="Additional vLLM arguments")
    tensorrt_args: Dict[str, Any] = Field(default_factory=dict, description="Additional TensorRT arguments")
    transformers_args: Dict[str, Any] = Field(default_factory=dict, description="Additional Transformers arguments")


class LocalServiceInfo(BaseModel):
    """Local service information"""
    service_name: str
    model_id: str
    backend: str
    service_type: str
    status: str
    healthy: bool
    response_time_ms: Optional[float] = None
    error_count: int = 0
    uptime_seconds: Optional[float] = None
    deployed_at: Optional[str] = None


class GenerateRequest(BaseModel):
    """Text generation request"""
    prompt: str = Field(..., description="Input prompt")
    max_tokens: int = Field(512, description="Maximum tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature")
    top_p: float = Field(0.9, description="Top-p sampling")
    top_k: int = Field(50, description="Top-k sampling")
    stream: bool = Field(False, description="Stream response")


class ChatCompletionRequest(BaseModel):
    """Chat completion request"""
    messages: List[Dict[str, str]] = Field(..., description="Chat messages")
    max_tokens: int = Field(512, description="Maximum tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature")
    top_p: float = Field(0.9, description="Top-p sampling")
    stream: bool = Field(False, description="Stream response")


# Dependency injection
async def get_deployment_manager() -> DeploymentManager:
    """Get deployment manager instance"""
    return DeploymentManager()


@router.get("/status", summary="Get local GPU system status")
async def get_local_status(
    manager: DeploymentManager = Depends(get_deployment_manager)
):
    """Get overall local GPU system status including available resources"""
    try:
        status = await manager.get_local_system_status()
        return {"success": True, "status": status}
    except Exception as e:
        logger.error(f"Failed to get local status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy", summary="Deploy model to local GPU")
async def deploy_local_service(
    request: LocalDeployRequest,
    background_tasks: BackgroundTasks,
    manager: DeploymentManager = Depends(get_deployment_manager),
    current_user: Optional[Dict] = Depends(get_current_user)
):
    """Deploy a model service to local GPU"""
    try:
        # Convert request to configuration
        config = LocalGPUConfig(
            service_name=request.service_name,
            service_type=LocalServiceType(request.service_type),
            model_id=request.model_id,
            backend=LocalBackend(request.backend),
            model_precision=request.model_precision,
            max_model_len=request.max_model_len,
            max_batch_size=request.max_batch_size,
            gpu_id=request.gpu_id,
            gpu_memory_utilization=request.gpu_memory_utilization,
            tensor_parallel_size=request.tensor_parallel_size,
            enable_chunked_prefill=request.enable_chunked_prefill,
            enable_prefix_caching=request.enable_prefix_caching,
            quantization=request.quantization,
            trust_remote_code=request.trust_remote_code,
            revision=request.revision,
            vllm_args=request.vllm_args,
            tensorrt_args=request.tensorrt_args,
            transformers_args=request.transformers_args
        )
        
        # Deploy service
        result = await manager.deploy_to_local(config)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Service {request.service_name} deployed successfully",
                "deployment": result
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Deployment failed"))
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {e}")
    except Exception as e:
        logger.error(f"Local deployment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services", summary="List local GPU services")
async def list_local_services(
    manager: DeploymentManager = Depends(get_deployment_manager)
) -> Dict[str, Any]:
    """List all deployed local GPU services"""
    try:
        services = await manager.list_local_services()
        return {
            "success": True,
            "services": services,
            "count": len(services)
        }
    except Exception as e:
        logger.error(f"Failed to list local services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{service_name}", summary="Get local service information")
async def get_local_service(
    service_name: str,
    manager: DeploymentManager = Depends(get_deployment_manager)
):
    """Get detailed information about a specific local service"""
    try:
        service_info = await manager.get_local_service_info(service_name)
        
        if service_info is None:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        return {
            "success": True,
            "service": service_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get service info for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/services/{service_name}", summary="Undeploy local service")
async def undeploy_local_service(
    service_name: str,
    manager: DeploymentManager = Depends(get_deployment_manager),
    current_user: Optional[Dict] = Depends(get_current_user)
):
    """Stop and remove a deployed local service"""
    try:
        result = await manager.undeploy_local_service(service_name)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Service {service_name} undeployed successfully"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Undeploy failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to undeploy service {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/services/{service_name}/generate", summary="Generate text using local service")
async def generate_text(
    service_name: str,
    request: GenerateRequest,
    manager: DeploymentManager = Depends(get_deployment_manager)
):
    """Generate text using a deployed local service"""
    try:
        # Get the local provider and call generate_text
        local_provider = manager.local_provider
        
        result = await local_provider.generate_text(
            service_name=service_name,
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            stream=request.stream
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Generation failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text generation failed for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/services/{service_name}/chat/completions", summary="Chat completion using local service")
async def chat_completion(
    service_name: str,
    request: ChatCompletionRequest,
    manager: DeploymentManager = Depends(get_deployment_manager)
):
    """Generate chat completion using a deployed local service"""
    try:
        # Get the local provider and call chat_completion
        local_provider = manager.local_provider
        
        result = await local_provider.chat_completion(
            service_name=service_name,
            messages=request.messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stream=request.stream
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Chat completion failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat completion failed for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backends", summary="List available local backends")
async def list_backends():
    """List available local inference backends"""
    backends = []
    
    # Check backend availability
    try:
        import vllm
        backends.append({
            "name": "vllm",
            "description": "High-performance LLM inference server",
            "available": True,
            "features": ["high_throughput", "dynamic_batching", "prefix_caching"]
        })
    except ImportError:
        backends.append({
            "name": "vllm",
            "description": "High-performance LLM inference server",
            "available": False,
            "install_command": "pip install vllm"
        })
    
    try:
        import tensorrt_llm
        backends.append({
            "name": "tensorrt_llm",
            "description": "NVIDIA TensorRT-LLM for maximum optimization",
            "available": True,
            "features": ["maximum_performance", "tensorrt_optimization", "cuda_acceleration"]
        })
    except ImportError:
        backends.append({
            "name": "tensorrt_llm",
            "description": "NVIDIA TensorRT-LLM for maximum optimization",
            "available": False,
            "install_command": "pip install tensorrt-llm"
        })
    
    try:
        import transformers
        backends.append({
            "name": "transformers",
            "description": "HuggingFace Transformers for universal compatibility",
            "available": True,
            "features": ["universal_compatibility", "all_model_types", "quantization_support"]
        })
    except ImportError:
        backends.append({
            "name": "transformers",
            "description": "HuggingFace Transformers for universal compatibility",
            "available": False,
            "install_command": "pip install transformers"
        })
    
    return {
        "success": True,
        "backends": backends
    }


@router.get("/gpu-info", summary="Get GPU information")
async def get_gpu_info():
    """Get detailed information about available GPUs"""
    try:
        from ....utils.gpu_utils import get_gpu_manager
        
        gpu_manager = get_gpu_manager()
        system_info = gpu_manager.get_system_info()
        
        return {
            "success": True,
            "gpu_info": system_info
        }
    except Exception as e:
        logger.error(f"Failed to get GPU info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estimate-memory", summary="Estimate model memory requirements")
async def estimate_memory(
    model_id: str,
    precision: str = "float16"
):
    """Estimate memory requirements for a model"""
    try:
        from ....utils.gpu_utils import estimate_model_memory
        
        memory_mb = estimate_model_memory(model_id, precision)
        memory_gb = memory_mb / 1024
        
        return {
            "success": True,
            "model_id": model_id,
            "precision": precision,
            "estimated_memory_mb": memory_mb,
            "estimated_memory_gb": round(memory_gb, 2)
        }
    except Exception as e:
        logger.error(f"Failed to estimate memory for {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets", summary="Get deployment configuration presets")
async def get_deployment_presets():
    """Get predefined deployment configuration presets"""
    presets = {
        "vllm_small": {
            "name": "vLLM - Small Model",
            "description": "Optimized for models up to 7B parameters",
            "backend": "vllm",
            "max_model_len": 2048,
            "max_batch_size": 16,
            "gpu_memory_utilization": 0.9,
            "enable_chunked_prefill": True,
            "enable_prefix_caching": True
        },
        "vllm_large": {
            "name": "vLLM - Large Model", 
            "description": "Optimized for models 13B+ parameters",
            "backend": "vllm",
            "max_model_len": 4096,
            "max_batch_size": 8,
            "gpu_memory_utilization": 0.95,
            "tensor_parallel_size": 2,
            "enable_chunked_prefill": True,
            "enable_prefix_caching": True
        },
        "tensorrt_performance": {
            "name": "TensorRT-LLM - Maximum Performance",
            "description": "Maximum optimization with TensorRT",
            "backend": "tensorrt_llm",
            "model_precision": "float16",
            "max_batch_size": 16,
            "tensorrt_args": {
                "enable_kv_cache_reuse": True,
                "use_gpt_attention_plugin": True,
                "remove_input_padding": True
            }
        },
        "transformers_compatible": {
            "name": "Transformers - Universal",
            "description": "Maximum compatibility with all models",
            "backend": "transformers", 
            "model_precision": "float16",
            "max_batch_size": 4,
            "gpu_memory_utilization": 0.8,
            "transformers_args": {
                "device_map": "auto",
                "torch_dtype": "auto",
                "low_cpu_mem_usage": True
            }
        }
    }
    
    return {
        "success": True,
        "presets": presets
    }