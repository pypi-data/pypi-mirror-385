"""
Dependency management and checking utilities for ISA Model.

This module provides utilities for checking optional dependencies
and providing clear error messages when dependencies are missing.
"""

import importlib.util
import logging
from typing import Dict, List, Optional, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


class DependencyChecker:
    """Utility class for checking and managing optional dependencies."""
    
    # Cache for dependency availability
    _cache: Dict[str, bool] = {}
    
    # Dependency groups with their packages
    DEPENDENCY_GROUPS = {
        # LLM Services
        "openai": ["openai"],
        "cerebras": ["cerebras.cloud.sdk"],
        "local_llm": ["torch", "transformers", "accelerate"],
        "vllm": ["vllm"],
        
        # Vision Services
        "vision_torch": ["torch", "torchvision", "PIL"],
        "vision_tf": ["tensorflow", "keras"],
        "vision_transformers": ["transformers", "PIL"],
        
        # Audio Services
        "audio": ["librosa", "soundfile", "numba"],
        "openai_audio": ["openai"],
        
        # Image Generation
        "replicate": ["replicate"],
        "image_gen": ["PIL", "requests"],
        
        # Training
        "training_torch": ["torch", "datasets", "peft", "trl"],
        "training_tf": ["tensorflow", "keras"],
        
        # Deployment
        "modal": ["modal"],
        "docker": ["docker"],
        "kubernetes": ["kubernetes"],
        
        # Storage
        "s3": ["boto3"],
        "gcs": ["google.cloud.storage"],
        "minio": ["minio"],
        
        # Monitoring
        "mlflow": ["mlflow"],
        "wandb": ["wandb"],
        "influxdb": ["influxdb_client"],
        "loki": ["python_logging_loki"],
    }
    
    @classmethod
    def check_dependency(cls, package: str) -> bool:
        """
        Check if a single package is available.
        
        Args:
            package: Package name to check (e.g., 'torch', 'openai')
            
        Returns:
            True if package is available, False otherwise
        """
        if package in cls._cache:
            return cls._cache[package]
        
        spec = importlib.util.find_spec(package.split('.')[0])
        available = spec is not None
        cls._cache[package] = available
        
        if not available:
            logger.debug(f"Package '{package}' is not available")
        
        return available
    
    @classmethod
    def check_dependencies(cls, packages: List[str]) -> Tuple[bool, List[str]]:
        """
        Check if multiple packages are available.
        
        Args:
            packages: List of package names to check
            
        Returns:
            Tuple of (all_available, missing_packages)
        """
        missing = []
        for package in packages:
            if not cls.check_dependency(package):
                missing.append(package)
        
        return len(missing) == 0, missing
    
    @classmethod
    def check_group(cls, group: str) -> Tuple[bool, List[str]]:
        """
        Check if all packages in a dependency group are available.
        
        Args:
            group: Name of the dependency group
            
        Returns:
            Tuple of (all_available, missing_packages)
        """
        if group not in cls.DEPENDENCY_GROUPS:
            raise ValueError(f"Unknown dependency group: {group}")
        
        packages = cls.DEPENDENCY_GROUPS[group]
        return cls.check_dependencies(packages)
    
    @classmethod
    def get_install_command(cls, group: Optional[str] = None, packages: Optional[List[str]] = None) -> str:
        """
        Get the pip install command for missing dependencies.
        
        Args:
            group: Dependency group name
            packages: List of package names
            
        Returns:
            Pip install command string
        """
        if group:
            # Map groups to pyproject.toml extras
            extras_map = {
                "openai": "cloud",
                "cerebras": "cloud",
                "local_llm": "local",
                "vision_torch": "vision",
                "vision_tf": "vision",
                "audio": "audio",
                "training_torch": "training",
                "modal": "cloud",
                "mlflow": "monitoring",
            }
            
            if group in extras_map:
                return f"pip install 'isa-model[{extras_map[group]}]'"
        
        if packages:
            return f"pip install {' '.join(packages)}"
        
        return "pip install isa-model[all]"
    
    @classmethod
    def require_dependencies(cls, packages: List[str] = None, group: str = None, 
                           message: str = None):
        """
        Decorator to check dependencies before running a function.
        
        Args:
            packages: List of required packages
            group: Dependency group name
            message: Custom error message
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if group:
                    available, missing = cls.check_group(group)
                elif packages:
                    available, missing = cls.check_dependencies(packages)
                else:
                    raise ValueError("Either packages or group must be specified")
                
                if not available:
                    error_msg = message or f"Missing required dependencies: {', '.join(missing)}"
                    install_cmd = cls.get_install_command(group=group, packages=missing)
                    raise ImportError(f"{error_msg}\nInstall with: {install_cmd}")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator


# Convenience functions for checking common dependencies
def is_torch_available() -> bool:
    """Check if PyTorch is available."""
    return DependencyChecker.check_dependency("torch")


def is_tensorflow_available() -> bool:
    """Check if TensorFlow is available."""
    return DependencyChecker.check_dependency("tensorflow")


def is_transformers_available() -> bool:
    """Check if Transformers is available."""
    return DependencyChecker.check_dependency("transformers")


def is_openai_available() -> bool:
    """Check if OpenAI SDK is available."""
    return DependencyChecker.check_dependency("openai")


def is_replicate_available() -> bool:
    """Check if Replicate SDK is available."""
    return DependencyChecker.check_dependency("replicate")


def is_modal_available() -> bool:
    """Check if Modal SDK is available."""
    return DependencyChecker.check_dependency("modal")


def is_cerebras_available() -> bool:
    """Check if Cerebras SDK is available."""
    return DependencyChecker.check_dependency("cerebras")


# Conditional imports with proper error handling
def import_torch():
    """Import PyTorch with proper error handling."""
    if not is_torch_available():
        raise ImportError(
            "PyTorch is not installed. "
            "Install with: pip install 'isa-model[local]' or pip install torch"
        )
    import torch
    return torch


def import_transformers():
    """Import Transformers with proper error handling."""
    if not is_transformers_available():
        raise ImportError(
            "Transformers is not installed. "
            "Install with: pip install 'isa-model[local]' or pip install transformers"
        )
    import transformers
    return transformers


def import_openai():
    """Import OpenAI with proper error handling."""
    if not is_openai_available():
        raise ImportError(
            "OpenAI SDK is not installed. "
            "Install with: pip install 'isa-model[cloud]' or pip install openai"
        )
    import openai
    return openai


def import_replicate():
    """Import Replicate with proper error handling."""
    if not is_replicate_available():
        raise ImportError(
            "Replicate SDK is not installed. "
            "Install with: pip install 'isa-model[cloud]' or pip install replicate"
        )
    import replicate
    return replicate


def import_cerebras():
    """Import Cerebras with proper error handling."""
    if not is_cerebras_available():
        raise ImportError(
            "Cerebras SDK is not installed. "
            "Install with: pip install cerebras-cloud-sdk"
        )
    from cerebras.cloud.sdk import Cerebras
    return Cerebras


# Lazy loading utilities
class LazyImport:
    """Lazy import wrapper for optional dependencies."""
    
    def __init__(self, module_name: str, package_name: str = None, 
                 install_hint: str = None):
        """
        Initialize lazy import wrapper.
        
        Args:
            module_name: Full module name to import
            package_name: Package name to check (defaults to module_name)
            install_hint: Custom installation hint
        """
        self.module_name = module_name
        self.package_name = package_name or module_name.split('.')[0]
        self.install_hint = install_hint
        self._module = None
    
    def __getattr__(self, name):
        """Lazy load the module when accessed."""
        if self._module is None:
            if not DependencyChecker.check_dependency(self.package_name):
                hint = self.install_hint or f"pip install {self.package_name}"
                raise ImportError(
                    f"{self.module_name} is not installed. Install with: {hint}"
                )
            
            import importlib
            self._module = importlib.import_module(self.module_name)
        
        return getattr(self._module, name)
    
    def __call__(self, *args, **kwargs):
        """Support direct calling for classes."""
        if self._module is None:
            self.__getattr__('__call__')  # Trigger lazy loading
        return self._module(*args, **kwargs)