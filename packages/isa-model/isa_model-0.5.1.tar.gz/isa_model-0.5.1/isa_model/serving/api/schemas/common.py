"""
Common API Schemas

Base schemas used across different endpoints
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional
import time

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool
    timestamp: float = time.time()
    
class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    
class HealthStatus(BaseModel):
    """Health status model"""
    status: str
    timestamp: float
    version: str
    
class SystemInfo(BaseModel):
    """System information model"""
    cpu_percent: float
    memory_percent: float
    gpu_available: bool
    gpu_count: int