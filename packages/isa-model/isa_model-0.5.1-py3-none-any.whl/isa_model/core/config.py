"""
Centralized Configuration Management for ISA Model SDK

This module provides unified configuration management across all modules:
- Environment variable loading
- Provider API key management  
- Global settings and defaults
- Configuration validation
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
import yaml
import json
from dotenv import load_dotenv

from .types import Provider, DeploymentPlatform

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for a single provider"""
    name: str
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    organization: Optional[str] = None
    rate_limit_rpm: Optional[int] = None
    rate_limit_tpm: Optional[int] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeploymentConfig:
    """Configuration for deployment platforms"""
    platform: DeploymentPlatform
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    default_gpu: str = "T4"
    default_memory_mb: int = 16384
    auto_scaling: bool = True
    scale_to_zero: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class LocalGPUGlobalConfig:
    """Global configuration for local GPU deployment"""
    enable_local_gpu: bool = True
    auto_detect_gpu: bool = True
    workspace_dir: str = "./local_deployments"
    preferred_backend: str = "api"  # cloud api only
    
    # Default resource settings
    default_gpu_memory_fraction: float = 0.9
    default_max_batch_size: int = 8
    default_max_model_len: int = 2048
    default_precision: str = "float16"
    
    # Health monitoring
    health_check_interval: int = 30  # seconds
    auto_restart_unhealthy: bool = True
    max_consecutive_failures: int = 3
    
    # Service limits
    max_concurrent_services: int = 3
    max_services_per_gpu: int = 2
    
    # Performance settings
    enable_model_compilation: bool = True
    enable_memory_optimization: bool = True
    cleanup_on_shutdown: bool = True


@dataclass
class GlobalConfig:
    """Global configuration settings"""
    # Storage settings
    default_storage_backend: str = "local"
    storage_path: str = "./isa_model_data"
    cache_dir: str = "./isa_model_cache"
    
    # Database settings
    use_supabase: bool = False
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    sqlite_path: str = "./isa_model.db"
    
    # Billing settings
    track_costs: bool = True
    cost_alerts_enabled: bool = True
    monthly_budget_usd: Optional[float] = None
    
    # Health monitoring
    health_check_interval: int = 300  # 5 minutes
    health_check_timeout: int = 30    # 30 seconds
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Model caching
    enable_model_cache: bool = True
    cache_size_gb: int = 50
    cache_cleanup_interval: int = 3600  # 1 hour
    
    # Local GPU settings
    enable_local_gpu: bool = True
    local_gpu_memory_fraction: float = 0.9
    local_workspace_dir: str = "./local_deployments"
    auto_detect_gpu: bool = True
    preferred_local_backend: str = "api"  # cloud api only
    
    # Local service defaults
    local_health_check_interval: int = 30  # seconds
    local_auto_restart_unhealthy: bool = True
    local_max_concurrent_services: int = 3


class ConfigManager:
    """
    Centralized configuration manager for the entire ISA Model SDK.
    
    Features:
    - Loads configuration from .env files, YAML files, and environment variables
    - Manages provider API keys and settings
    - Handles deployment platform configurations
    - Provides unified access to all settings
    
    Example:
        ```python
        from isa_model.core.config import ConfigManager
        
        config = ConfigManager()
        
        # Get provider configuration
        openai_config = config.get_provider_config(Provider.OPENAI)
        
        # Get deployment configuration
        modal_config = config.get_deployment_config(DeploymentPlatform.MODAL)
        
        # Check if provider is enabled
        if config.is_provider_enabled(Provider.OPENAI):
            print("OpenAI is configured and enabled")
        ```
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager"""
        if not self._initialized:
            self.global_config = GlobalConfig()
            self.local_gpu_config = LocalGPUGlobalConfig()
            self.provider_configs: Dict[str, ProviderConfig] = {}
            self.deployment_configs: Dict[str, DeploymentConfig] = {}
            
            self._load_configuration()
            ConfigManager._initialized = True
    
    def _load_configuration(self):
        """Load configuration from various sources"""
        # 1. Load environment variables
        self._load_env_files()
        
        # 2. Load from YAML config file if exists
        self._load_yaml_config()
        
        # 3. Load provider configurations
        self._load_provider_configs()
        
        # 4. Load deployment configurations
        self._load_deployment_configs()
        
        # 5. Validate configuration
        self._validate_configuration()
        
        logger.info("Configuration loaded successfully")
    
    def _load_env_files(self):
        """Load environment variables from .env files"""
        # Load from project root
        project_root = self._find_project_root()
        env_files = [
            project_root / ".env",
            project_root / ".env.local",
            project_root / "deployment" / "dev" / ".env",
            Path.cwd() / ".env",
        ]
        
        for env_file in env_files:
            if env_file.exists():
                load_dotenv(env_file)
                logger.debug(f"Loaded environment from {env_file}")
    
    def _find_project_root(self) -> Path:
        """Find the project root directory"""
        current = Path(__file__).parent
        while current != current.parent:
            if (current / "pyproject.toml").exists() or (current / "setup.py").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _load_yaml_config(self):
        """Load configuration from YAML file"""
        config_files = [
            Path.cwd() / "isa_model_config.yaml",
            Path.cwd() / "config.yaml",
            self._find_project_root() / "isa_model_config.yaml",
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        yaml_config = yaml.safe_load(f)
                    
                    self._apply_yaml_config(yaml_config)
                    logger.info(f"Loaded YAML configuration from {config_file}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load YAML config from {config_file}: {e}")
    
    def _apply_yaml_config(self, yaml_config: Dict[str, Any]):
        """Apply YAML configuration to global settings"""
        if "global" in yaml_config:
            global_settings = yaml_config["global"]
            for key, value in global_settings.items():
                if hasattr(self.global_config, key):
                    setattr(self.global_config, key, value)
        
        # Load database configuration from environment
        # Check multiple possible environment variable names for compatibility
        supabase_url = os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_LOCAL_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_LOCAL_ANON_KEY")
        
        if supabase_url and supabase_key:
            self.global_config.use_supabase = True
            self.global_config.supabase_url = supabase_url
            self.global_config.supabase_key = supabase_key
            logger.debug(f"Supabase configured: URL={supabase_url[:30]}...")
        else:
            # Check if explicitly disabled
            use_supabase_env = os.getenv("ISA_USE_SUPABASE", "").lower()
            if use_supabase_env == "false":
                self.global_config.use_supabase = False
            logger.debug("Supabase not configured, using default storage")
        
        # Load local GPU configuration
        local_gpu_settings = {
            "enable_local_gpu": os.getenv("ISA_ENABLE_LOCAL_GPU", "true").lower() == "true",
            "auto_detect_gpu": os.getenv("ISA_AUTO_DETECT_GPU", "true").lower() == "true",
            "workspace_dir": os.getenv("ISA_LOCAL_WORKSPACE_DIR", "./local_deployments"),
            "preferred_backend": os.getenv("ISA_PREFERRED_LOCAL_BACKEND", "api"),
            "default_gpu_memory_fraction": float(os.getenv("ISA_GPU_MEMORY_FRACTION", "0.9")),
            "health_check_interval": int(os.getenv("ISA_LOCAL_HEALTH_CHECK_INTERVAL", "30")),
            "max_concurrent_services": int(os.getenv("ISA_MAX_CONCURRENT_SERVICES", "3")),
        }
        
        for key, value in local_gpu_settings.items():
            if hasattr(self.local_gpu_config, key):
                setattr(self.local_gpu_config, key, value)
    
    def _load_provider_configs(self):
        """Load provider configurations from environment"""
        
        # Define provider environment variable patterns
        provider_env_mapping = {
            Provider.OPENAI: {
                "api_key": ["OPENAI_API_KEY"],
                "organization": ["OPENAI_ORG_ID", "OPENAI_ORGANIZATION"],
                "api_base_url": ["OPENAI_API_BASE", "OPENAI_BASE_URL"],
            },
            Provider.REPLICATE: {
                "api_key": ["REPLICATE_API_TOKEN", "REPLICATE_API_KEY"],
            },
            Provider.ANTHROPIC: {
                "api_key": ["ANTHROPIC_API_KEY"],
            },
            Provider.GOOGLE: {
                "api_key": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
            },
            Provider.YYDS: {
                "api_key": ["YYDS_API_KEY"],
                "api_base_url": ["YYDS_API_BASE", "YYDS_BASE_URL"],
            },
        }
        
        for provider, env_vars in provider_env_mapping.items():
            config = ProviderConfig(name=provider.value)
            
            # Load API key
            for env_var in env_vars.get("api_key", []):
                if os.getenv(env_var):
                    config.api_key = os.getenv(env_var)
                    break
            
            # Load other settings
            for setting, env_var_list in env_vars.items():
                if setting == "api_key":
                    continue
                for env_var in env_var_list:
                    if os.getenv(env_var):
                        setattr(config, setting, os.getenv(env_var))
                        break
            
            # Check if provider is enabled
            config.enabled = bool(config.api_key)
            
            self.provider_configs[provider.value] = config
    
    def _load_deployment_configs(self):
        """Load deployment platform configurations"""
        
        deployment_env_mapping = {
            DeploymentPlatform.MODAL: {
                "api_key": ["MODAL_TOKEN"],
                "endpoint": ["MODAL_ENDPOINT"],
            },
            DeploymentPlatform.RUNPOD: {
                "api_key": ["RUNPOD_API_KEY"],
                "endpoint": ["RUNPOD_ENDPOINT"],
            },
            DeploymentPlatform.KUBERNETES: {
                "endpoint": ["K8S_ENDPOINT", "KUBERNETES_ENDPOINT"],
                "api_key": ["K8S_TOKEN", "KUBERNETES_TOKEN"],
            },
        }
        
        for platform, env_vars in deployment_env_mapping.items():
            config = DeploymentConfig(platform=platform)
            
            # Load settings from environment
            for setting, env_var_list in env_vars.items():
                for env_var in env_var_list:
                    if os.getenv(env_var):
                        setattr(config, setting, os.getenv(env_var))
                        break
            
            self.deployment_configs[platform.value] = config
    
    def _validate_configuration(self):
        """Validate loaded configuration"""
        warnings = []
        
        # Check if any providers are configured
        enabled_providers = [p for p in self.provider_configs.values() if p.enabled]
        if not enabled_providers:
            warnings.append("No providers are configured with API keys")
        
        # Check storage path accessibility
        storage_path = Path(self.global_config.storage_path)
        try:
            storage_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            warnings.append(f"Storage path not accessible: {e}")
        
        # Check database configuration
        if self.global_config.use_supabase:
            if not self.global_config.supabase_url or not self.global_config.supabase_key:
                warnings.append("Supabase is enabled but URL/key not configured")
        
        for warning in warnings:
            logger.warning(f"Configuration warning: {warning}")
    
    # Public API methods
    
    def get_provider_config(self, provider: Provider) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider"""
        return self.provider_configs.get(provider.value)
    
    def get_deployment_config(self, platform: DeploymentPlatform) -> Optional[DeploymentConfig]:
        """Get configuration for a specific deployment platform"""
        return self.deployment_configs.get(platform.value)
    
    def get_local_gpu_config(self) -> LocalGPUGlobalConfig:
        """Get local GPU global configuration"""
        return self.local_gpu_config
    
    def is_local_gpu_enabled(self) -> bool:
        """Check if local GPU deployment is enabled and available"""
        if not self.local_gpu_config.enable_local_gpu:
            return False
        
        try:
            from ..utils.gpu_utils import check_cuda_availability
            return check_cuda_availability()
        except ImportError:
            return False
    
    def is_provider_enabled(self, provider: Provider) -> bool:
        """Check if a provider is enabled and configured"""
        config = self.get_provider_config(provider)
        return config is not None and config.enabled and config.api_key is not None
    
    def get_enabled_providers(self) -> List[Provider]:
        """Get list of all enabled providers"""
        enabled = []
        for provider_str, config in self.provider_configs.items():
            if config.enabled:
                try:
                    enabled.append(Provider(provider_str))
                except ValueError:
                    continue
        return enabled
    
    def get_provider_api_key(self, provider: Provider) -> Optional[str]:
        """Get API key for a specific provider"""
        config = self.get_provider_config(provider)
        return config.api_key if config else None
    
    def get_global_config(self) -> GlobalConfig:
        """Get global configuration"""
        return self.global_config
    
    def update_provider_config(self, provider: Provider, **kwargs):
        """Update provider configuration"""
        if provider.value not in self.provider_configs:
            self.provider_configs[provider.value] = ProviderConfig(name=provider.value)
        
        config = self.provider_configs[provider.value]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    def save_config(self, config_file: Optional[Path] = None):
        """Save current configuration to YAML file"""
        if config_file is None:
            config_file = Path.cwd() / "isa_model_config.yaml"
        
        config_data = {
            "global": {
                "default_storage_backend": self.global_config.default_storage_backend,
                "storage_path": self.global_config.storage_path,
                "cache_dir": self.global_config.cache_dir,
                "use_supabase": self.global_config.use_supabase,
                "track_costs": self.global_config.track_costs,
                "health_check_interval": self.global_config.health_check_interval,
                "log_level": self.global_config.log_level,
            },
            "providers": {},
            "deployments": {}
        }
        
        # Add provider configs (without API keys for security)
        for provider_name, config in self.provider_configs.items():
            config_data["providers"][provider_name] = {
                "enabled": config.enabled,
                "rate_limit_rpm": config.rate_limit_rpm,
                "rate_limit_tpm": config.rate_limit_tpm,
                "metadata": config.metadata,
            }
        
        # Add deployment configs (without API keys)
        for platform_name, config in self.deployment_configs.items():
            config_data["deployments"][platform_name] = {
                "default_gpu": config.default_gpu,
                "default_memory_mb": config.default_memory_mb,
                "auto_scaling": config.auto_scaling,
                "scale_to_zero": config.scale_to_zero,
                "metadata": config.metadata,
            }
        
        try:
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            logger.info(f"Configuration saved to {config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        enabled_providers = [p.name for p in self.provider_configs.values() if p.enabled]
        configured_deployments = [p.platform.value for p in self.deployment_configs.values() if p.api_key]
        
        return {
            "enabled_providers": enabled_providers,
            "configured_deployments": configured_deployments,
            "storage_backend": self.global_config.default_storage_backend,
            "database": "supabase" if self.global_config.use_supabase else "sqlite",
            "cost_tracking": self.global_config.track_costs,
            "model_caching": self.global_config.enable_model_cache,
        }


# Global configuration instance
config_manager = ConfigManager()

# Convenience functions
def get_provider_config(provider: Provider) -> Optional[ProviderConfig]:
    """Get provider configuration"""
    return config_manager.get_provider_config(provider)

def get_deployment_config(platform: DeploymentPlatform) -> Optional[DeploymentConfig]:
    """Get deployment platform configuration"""
    return config_manager.get_deployment_config(platform)

def is_provider_enabled(provider: Provider) -> bool:
    """Check if provider is enabled"""
    return config_manager.is_provider_enabled(provider)

def get_api_key(provider: Provider) -> Optional[str]:
    """Get API key for provider"""
    return config_manager.get_provider_api_key(provider)