"""
Health Check Routes

System health and status endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import time
import psutil
from typing import Dict, Any

# Optional torch import - only available in local mode
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    version: str
    uptime: float
    system: Dict[str, Any]

@router.get("", response_model=HealthResponse)
@router.get("/", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Basic health check endpoint
    Responds to both /health and /health/
    """
    # Check if startup failed
    startup_failed = getattr(request.app.state, 'startup_failed', False)
    startup_error = getattr(request.app.state, 'startup_error', None)
    
    status = "degraded" if startup_failed else "healthy"
    
    system_info = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "gpu_available": torch.cuda.is_available() if TORCH_AVAILABLE else False,
        "gpu_count": torch.cuda.device_count() if (TORCH_AVAILABLE and torch.cuda.is_available()) else 0
    }
    
    if startup_failed:
        system_info["startup_error"] = startup_error
        system_info["warning"] = "Server started with initialization errors"
    
    return HealthResponse(
        status=status,
        timestamp=time.time(),
        version="1.0.0",
        uptime=time.time(),  # Simplified uptime
        system=system_info
    )

@router.get("/detailed")
async def detailed_health():
    """
    Detailed health check with system information
    """
    gpu_info = []
    if TORCH_AVAILABLE and torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            gpu_info.append({
                "device": i,
                "name": torch.cuda.get_device_name(i),
                "memory_allocated": torch.cuda.memory_allocated(i),
                "memory_cached": torch.cuda.memory_reserved(i)
            })
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "system": {
            "cpu": {
                "percent": psutil.cpu_percent(),
                "count": psutil.cpu_count()
            },
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "available": psutil.virtual_memory().available,
                "total": psutil.virtual_memory().total
            },
            "gpu": {
                "available": torch.cuda.is_available() if TORCH_AVAILABLE else False,
                "devices": gpu_info
            }
        }
    }

@router.get("/ready")
async def readiness_probe():
    """
    Kubernetes readiness probe endpoint
    """
    # Add model loading checks here
    return {"status": "ready", "timestamp": time.time()}