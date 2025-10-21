"""
GPU detection and resource management utilities

Provides functions for detecting and managing local GPU resources.
"""

import os
import logging
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import platform

logger = logging.getLogger(__name__)


@dataclass
class GPUInfo:
    """GPU information structure"""
    gpu_id: int
    name: str
    memory_total: int  # MB
    memory_free: int   # MB  
    memory_used: int   # MB
    utilization: float  # %
    temperature: Optional[int] = None  # Celsius
    power_draw: Optional[float] = None  # Watts
    driver_version: Optional[str] = None
    cuda_version: Optional[str] = None


class GPUManager:
    """Local GPU resource manager"""
    
    def __init__(self):
        self.gpus: List[GPUInfo] = []
        self.cuda_available = False
        self.nvidia_smi_available = False
        self._initialize()
    
    def _initialize(self):
        """Initialize GPU detection"""
        self.cuda_available = self._check_cuda_availability()
        self.nvidia_smi_available = self._check_nvidia_smi()
        
        if self.nvidia_smi_available:
            self.gpus = self._detect_nvidia_gpus()
        elif self.cuda_available:
            self.gpus = self._detect_cuda_gpus_fallback()
        else:
            logger.warning("No CUDA-capable GPUs detected")
    
    def _check_cuda_availability(self) -> bool:
        """Check if CUDA is available through PyTorch"""
        try:
            import torch
            available = torch.cuda.is_available()
            if available:
                logger.info(f"CUDA detected: {torch.cuda.device_count()} devices")
                logger.info(f"CUDA version: {torch.version.cuda}")
            return available
        except ImportError:
            logger.warning("PyTorch not available for CUDA detection")
            return False
        except Exception as e:
            logger.warning(f"CUDA detection failed: {e}")
            return False
    
    def _check_nvidia_smi(self) -> bool:
        """Check if nvidia-smi is available"""
        try:
            result = subprocess.run(['nvidia-smi', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def _detect_nvidia_gpus(self) -> List[GPUInfo]:
        """Detect GPUs using nvidia-smi"""
        gpus = []
        
        try:
            # Get GPU information using nvidia-smi
            cmd = [
                'nvidia-smi', 
                '--query-gpu=index,name,memory.total,memory.free,memory.used,utilization.gpu,temperature.gpu,power.draw,driver_version',
                '--format=csv,noheader,nounits'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 7:
                            gpu_info = GPUInfo(
                                gpu_id=int(parts[0]),
                                name=parts[1],
                                memory_total=int(parts[2]),
                                memory_free=int(parts[3]), 
                                memory_used=int(parts[4]),
                                utilization=float(parts[5]),
                                temperature=int(parts[6]) if parts[6] != '[Not Supported]' else None,
                                power_draw=float(parts[7]) if len(parts) > 7 and parts[7] != '[Not Supported]' else None,
                                driver_version=parts[8] if len(parts) > 8 else None
                            )
                            gpus.append(gpu_info)
            
            # Get CUDA version
            try:
                cuda_result = subprocess.run(['nvcc', '--version'], 
                                           capture_output=True, text=True, timeout=5)
                if cuda_result.returncode == 0:
                    for line in cuda_result.stdout.split('\n'):
                        if 'release' in line.lower():
                            cuda_version = line.split()[-1].rstrip(',')
                            for gpu in gpus:
                                gpu.cuda_version = cuda_version
                            break
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
                
        except Exception as e:
            logger.error(f"Failed to detect GPUs with nvidia-smi: {e}")
        
        return gpus
    
    def _detect_cuda_gpus_fallback(self) -> List[GPUInfo]:
        """Fallback GPU detection using PyTorch"""
        gpus = []
        
        try:
            import torch
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    
                    # Get memory info
                    torch.cuda.set_device(i)
                    memory_total = torch.cuda.get_device_properties(i).total_memory // (1024**2)  # MB
                    memory_free = (torch.cuda.get_device_properties(i).total_memory - torch.cuda.memory_allocated(i)) // (1024**2)
                    memory_used = torch.cuda.memory_allocated(i) // (1024**2)
                    
                    gpu_info = GPUInfo(
                        gpu_id=i,
                        name=props.name,
                        memory_total=memory_total,
                        memory_free=memory_free,
                        memory_used=memory_used,
                        utilization=0.0,  # Cannot get utilization without nvidia-smi
                        cuda_version=torch.version.cuda
                    )
                    gpus.append(gpu_info)
                    
        except Exception as e:
            logger.error(f"Failed to detect GPUs with PyTorch: {e}")
            
        return gpus
    
    def get_gpu_info(self, gpu_id: Optional[int] = None) -> Optional[GPUInfo]:
        """Get information for a specific GPU or best available GPU"""
        if not self.gpus:
            return None
            
        if gpu_id is not None:
            for gpu in self.gpus:
                if gpu.gpu_id == gpu_id:
                    return gpu
            return None
        
        # Return GPU with most free memory
        return max(self.gpus, key=lambda x: x.memory_free)
    
    def get_best_gpu(self, min_memory_mb: int = 1024) -> Optional[GPUInfo]:
        """Get the best available GPU for model deployment"""
        available_gpus = [gpu for gpu in self.gpus if gpu.memory_free >= min_memory_mb]
        
        if not available_gpus:
            return None
        
        # Sort by free memory (descending) and utilization (ascending)
        return sorted(available_gpus, 
                     key=lambda x: (-x.memory_free, x.utilization))[0]
    
    def estimate_model_memory(self, model_id: str, precision: str = "float16") -> int:
        """Estimate memory requirements for a model in MB"""
        # Simple estimation based on model name and precision
        memory_multipliers = {
            "float32": 4,
            "float16": 2, 
            "int8": 1,
            "int4": 0.5
        }
        
        multiplier = memory_multipliers.get(precision, 2)
        
        # Rough parameter estimates based on model names
        if "7b" in model_id.lower():
            params = 7_000_000_000
        elif "13b" in model_id.lower():
            params = 13_000_000_000
        elif "70b" in model_id.lower():
            params = 70_000_000_000
        elif "large" in model_id.lower():
            params = 1_000_000_000
        elif "medium" in model_id.lower():
            params = 350_000_000
        elif "small" in model_id.lower():
            params = 125_000_000
        else:
            params = 500_000_000  # Default estimate
        
        # Memory = parameters * bytes_per_param + overhead
        estimated_mb = int((params * multiplier + 1024**3) / (1024**2))  # +1GB overhead
        
        return estimated_mb
    
    def check_gpu_compatibility(self, model_id: str, precision: str = "float16") -> Tuple[bool, List[str]]:
        """Check if local GPUs can handle the model"""
        warnings = []
        
        if not self.gpus:
            return False, ["No CUDA-capable GPUs detected"]
        
        estimated_memory = self.estimate_model_memory(model_id, precision)
        best_gpu = self.get_best_gpu(estimated_memory)
        
        if not best_gpu:
            warnings.append(f"Insufficient GPU memory. Required: {estimated_memory}MB, Available: {max(gpu.memory_free for gpu in self.gpus)}MB")
            return False, warnings
        
        # Check compute capability for advanced features
        if precision in ["int8", "int4"]:
            warnings.append("Quantized precision may require specific GPU compute capability")
        
        return True, warnings
    
    def refresh(self):
        """Refresh GPU information"""
        if self.nvidia_smi_available:
            self.gpus = self._detect_nvidia_gpus()
        elif self.cuda_available:
            self.gpus = self._detect_cuda_gpus_fallback()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        info = {
            "platform": platform.system(),
            "architecture": platform.machine(),
            "cuda_available": self.cuda_available,
            "nvidia_smi_available": self.nvidia_smi_available,
            "gpu_count": len(self.gpus),
            "gpus": [
                {
                    "id": gpu.gpu_id,
                    "name": gpu.name,
                    "memory_total_mb": gpu.memory_total,
                    "memory_free_mb": gpu.memory_free,
                    "memory_used_mb": gpu.memory_used,
                    "utilization_percent": gpu.utilization,
                    "temperature_c": gpu.temperature,
                    "power_draw_w": gpu.power_draw,
                    "driver_version": gpu.driver_version,
                    "cuda_version": gpu.cuda_version
                }
                for gpu in self.gpus
            ]
        }
        
        # Add Python environment info
        try:
            import torch
            info["torch_version"] = torch.__version__
            info["torch_cuda_version"] = torch.version.cuda
        except ImportError:
            pass
            
        return info


# Global GPU manager instance
_gpu_manager = None

def get_gpu_manager() -> GPUManager:
    """Get global GPU manager instance"""
    global _gpu_manager
    if _gpu_manager is None:
        _gpu_manager = GPUManager()
    return _gpu_manager


def detect_gpus() -> List[GPUInfo]:
    """Convenience function to detect GPUs"""
    return get_gpu_manager().gpus


def get_best_gpu(min_memory_mb: int = 1024) -> Optional[GPUInfo]:
    """Convenience function to get best available GPU"""
    return get_gpu_manager().get_best_gpu(min_memory_mb)


def check_cuda_availability() -> bool:
    """Check if CUDA is available"""
    return get_gpu_manager().cuda_available


def estimate_model_memory(model_id: str, precision: str = "float16") -> int:
    """Estimate model memory requirements"""
    return get_gpu_manager().estimate_model_memory(model_id, precision)