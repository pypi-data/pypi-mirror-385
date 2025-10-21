"""
Unified Configuration Manager for ISA Model Core

Centralizes all configuration management:
- Environment settings (dev, prod, etc.)
- Provider API keys and configurations  
- Database setup and initialization
- Model definitions and capabilities
- Deployment platform settings
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv

from ..types import Provider, DeploymentPlatform

logger = logging.getLogger(__name__)

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class ProviderConfig:
    """Configuration for a provider"""
    name: str
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    organization: Optional[str] = None
    rate_limit_rpm: Optional[int] = None
    rate_limit_tpm: Optional[int] = None
    enabled: bool = True
    models: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConsulConfig:
    """Consul service discovery configuration"""
    enabled: bool = True
    host: str = "localhost"
    port: int = 8500
    timeout: int = 10
    
@dataclass
class ServiceConfig:
    """Service endpoint configuration with Consul discovery support"""
    # Enable Consul discovery
    use_consul_discovery: bool = True
    
    # Fallback URLs when Consul is unavailable
    mcp_base_url: str = "http://localhost:8081"
    ollama_base_url: str = "http://localhost:11434"
    influxdb_url: str = "http://localhost:8086"
    loki_url: str = "http://localhost:3100"
    minio_endpoint: str = "localhost:9000"
    redis_url: str = "redis://localhost:6379"
    api_port: int = 8000
    redis_port: int = 6379
    
    # Consul service names for discovery
    mcp_service_name: str = "mcp"
    ollama_service_name: str = "ollama"
    influxdb_service_name: str = "influxdb"
    loki_service_name: str = "loki"
    minio_service_name: str = "minio"
    redis_service_name: str = "redis"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    use_supabase: bool = True
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_schema: Optional[str] = None
    fallback_to_sqlite: bool = False
    sqlite_path: str = "./isa_model.db"
    default_database_url: str = "postgresql://postgres:postgres@127.0.0.1:54322/postgres?options=-c%20search_path%3Ddev"
    connection_pool_size: int = 10
    max_retries: int = 3

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    platform: str = "local"
    auto_scaling: bool = False
    scale_to_zero: bool = False
    default_gpu: str = "cpu"
    default_memory_mb: int = 8192
    keep_warm: int = 0
    timeout_seconds: int = 300

@dataclass
class APIConfig:
    """API configuration"""
    rate_limit_rpm: int = 100
    max_file_size_mb: int = 20
    cache_ttl_seconds: int = 3600
    enable_auth: bool = False
    cors_origins: List[str] = field(default_factory=lambda: ["*"])

@dataclass
class ServingConfig:
    """Serving configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    log_level: str = "info"

@dataclass
class BillingConfig:
    """Billing and cost tracking configuration"""
    track_costs: bool = True
    cost_alerts_enabled: bool = True
    monthly_budget_usd: Optional[float] = None

@dataclass
class HealthConfig:
    """Health monitoring configuration"""
    check_interval_seconds: int = 300
    timeout_seconds: int = 30
    enabled: bool = True

@dataclass
class CacheConfig:
    """Model caching configuration"""
    enabled: bool = True
    size_gb: int = 50
    cleanup_interval_seconds: int = 3600

@dataclass
class GlobalConfig:
    """Complete global configuration"""
    environment: Environment
    debug: bool = False
    
    # Component configurations
    consul: ConsulConfig = field(default_factory=ConsulConfig)
    services: ServiceConfig = field(default_factory=ServiceConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    deployment: DeploymentConfig = field(default_factory=DeploymentConfig)
    api: APIConfig = field(default_factory=APIConfig)
    serving: ServingConfig = field(default_factory=ServingConfig)
    billing: BillingConfig = field(default_factory=BillingConfig)
    health: HealthConfig = field(default_factory=HealthConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)

class ConfigManager:
    """
    Unified Configuration Manager for ISA Model Core
    
    Manages all configuration from a centralized location:
    - Environment-specific settings
    - Provider configurations
    - Database and deployment settings
    - Model definitions
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.config_dir = Path(__file__).parent
            self.global_config: Optional[GlobalConfig] = None
            self.provider_configs: Dict[str, ProviderConfig] = {}
            self.model_definitions: Dict[str, Dict[str, Any]] = {}
            self._consul_discovery = None
            
            self._load_configuration()
            self._initialize_consul_discovery()
            ConfigManager._initialized = True
    
    def _load_configuration(self):
        """Load all configuration from files and environment"""
        # 0. Load environment variables from .env files
        self._load_env_files()
        
        # 1. Determine environment
        env_name = os.getenv("ISA_ENV", "development")
        try:
            environment = Environment(env_name)
        except ValueError:
            logger.warning(f"Unknown environment '{env_name}', defaulting to development")
            environment = Environment.DEVELOPMENT
        
        # 2. Load environment-specific config
        self._load_environment_config(environment)
        
        # 3. Load provider configurations
        self._load_provider_configs()
        
        # 4. Load deployment configurations
        self._load_deployment_configs()
        
        # 5. Load model definitions
        self._load_model_definitions()
        
        # 6. Apply environment variable overrides
        self._apply_env_overrides()
        
        logger.info(f"Configuration loaded for environment: {environment}")
    
    def _load_env_files(self):
        """Load environment variables from deployment environment files"""
        # Load from deployment environment directories only
        project_root = self._find_project_root()
        
        # Check environment-specific deployment directories
        env_files = [
            project_root / "deployment" / "dev" / ".env",
            project_root / "deployment" / "staging" / "env" / ".env.staging", 
            project_root / "deployment" / "production" / "env" / ".env.production",
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
    
    def _load_environment_config(self, environment: Environment):
        """Load environment-specific configuration"""
        env_file = self.config_dir / "environments" / f"{environment.value}.yaml"
        
        if not env_file.exists():
            logger.warning(f"Environment config not found: {env_file}")
            self.global_config = GlobalConfig(environment=environment)
            return
        
        try:
            with open(env_file, 'r') as f:
                env_data = yaml.safe_load(f)
            
            # Build configuration from YAML
            self.global_config = GlobalConfig(
                environment=environment,
                debug=env_data.get('debug', False),
                consul=ConsulConfig(**env_data.get('consul', {})),
                services=ServiceConfig(**env_data.get('services', {})),
                database=DatabaseConfig(**env_data.get('database', {})),
                deployment=DeploymentConfig(**env_data.get('deployment', {})),
                api=APIConfig(**env_data.get('api', {})),
                serving=ServingConfig(**env_data.get('serving', {})),
                billing=BillingConfig(**env_data.get('billing', {})),
                health=HealthConfig(**env_data.get('health', {})),
                cache=CacheConfig(**env_data.get('cache', {}))
            )
            
            logger.debug(f"Loaded environment config from {env_file}")
            
        except Exception as e:
            logger.error(f"Failed to load environment config: {e}")
            self.global_config = GlobalConfig(environment=environment)
    
    def _load_provider_configs(self):
        """Load provider configurations from YAML files and environment variables"""
        # First load from environment variables (legacy support)
        self._load_provider_configs_from_env()
        
        # Then load from YAML files (enhanced configs)
        self._load_provider_configs_from_yaml()
    
    def _load_provider_configs_from_env(self):
        """Load provider configurations from environment variables (legacy)"""
        # Define provider environment variable patterns from original config.py
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
            Provider.CEREBRAS: {
                "api_key": ["CEREBRAS_API_KEY"],
                "api_base_url": ["CEREBRAS_API_BASE", "CEREBRAS_BASE_URL"],
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
    
    def _load_provider_configs_from_yaml(self):
        """Load provider configurations from YAML files"""
        providers_dir = self.config_dir / "providers"
        
        if not providers_dir.exists():
            logger.warning(f"Providers directory not found: {providers_dir}")
            return
        
        for provider_file in providers_dir.glob("*.yaml"):
            try:
                with open(provider_file, 'r') as f:
                    provider_data = yaml.safe_load(f)
                
                provider_name = provider_data.get('provider')
                if not provider_name:
                    logger.warning(f"No provider name in {provider_file}")
                    continue
                
                # Get existing config (from env) or create new one
                config = self.provider_configs.get(provider_name, ProviderConfig(name=provider_name))
                
                # Load API configuration
                api_config = provider_data.get('api', {})
                api_key_env = api_config.get('api_key_env')
                org_env = api_config.get('organization_env')
                
                # Update config with YAML data (environment takes precedence)
                if not config.api_key and api_key_env:
                    config.api_key = os.getenv(api_key_env)
                if not config.api_base_url:
                    config.api_base_url = api_config.get('base_url')
                if not config.organization and org_env:
                    config.organization = os.getenv(org_env)
                if not config.rate_limit_rpm:
                    config.rate_limit_rpm = api_config.get('rate_limits', {}).get('requests_per_minute')
                if not config.rate_limit_tpm:
                    config.rate_limit_tpm = api_config.get('rate_limits', {}).get('tokens_per_minute')
                
                # Enable if API key is available
                config.enabled = bool(config.api_key)
                config.models = provider_data.get('models', [])
                config.metadata = provider_data
                
                self.provider_configs[provider_name] = config
                logger.debug(f"Loaded provider config for {provider_name}")
                
            except Exception as e:
                logger.error(f"Failed to load provider config from {provider_file}: {e}")
    
    def _load_deployment_configs(self):
        """Load deployment platform configurations"""
        # This can be enhanced later with deployment-specific YAML files
        deployment_env_mapping = {
            DeploymentPlatform.MODAL: {
                "token_id": ["MODAL_TOKEN_ID"],
                "token_secret": ["MODAL_TOKEN_SECRET"],
                "environment": ["MODAL_ENVIRONMENT"],
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
        
        # Store deployment configs if needed
        self.deployment_configs = {}
        for platform, env_vars in deployment_env_mapping.items():
            config = {
                "platform": platform,
                "enabled": False
            }
            
            # Load settings from environment
            for setting, env_var_list in env_vars.items():
                for env_var in env_var_list:
                    if os.getenv(env_var):
                        config[setting] = os.getenv(env_var)
                        config["enabled"] = True
                        break
            
            self.deployment_configs[platform.value] = config
    
    def _load_model_definitions(self):
        """Load model definitions from provider configs"""
        for provider_name, provider_config in self.provider_configs.items():
            for model_data in provider_config.models:
                model_id = model_data.get('model_id')
                if model_id:
                    # Add provider context to model definition
                    model_data['provider'] = provider_name
                    self.model_definitions[model_id] = model_data
        
        logger.info(f"Loaded {len(self.model_definitions)} model definitions")
    
    def _configure_database_for_environment(self):
        """Configure database settings based on environment"""
        if not self.global_config:
            return
            
        env = self.global_config.environment.value
        
        if env in ["development", "testing"]:
            # Local Supabase with schema isolation
            supabase_url = os.getenv("SUPABASE_LOCAL_URL")
            supabase_key = os.getenv("SUPABASE_LOCAL_ANON_KEY") or os.getenv("SUPABASE_LOCAL_SERVICE_ROLE_KEY")
            schema = "dev" if env == "development" else "test"
            
        elif env == "staging":
            # Supabase Cloud staging
            supabase_url = os.getenv("SUPABASE_STAGING_URL") or os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_STAGING_KEY") or os.getenv("SUPABASE_ANON_KEY")
            schema = "staging"
            
        elif env == "production":
            # Supabase Cloud production
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SERVICE_ROLE_KEY")
            schema = "public"  # or "production" if using schema isolation
            
        else:
            logger.warning(f"Unknown environment '{env}', using default configuration")
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            schema = "public"
        
        # Apply configuration
        if supabase_url:
            self.global_config.database.supabase_url = supabase_url
        if supabase_key:
            self.global_config.database.supabase_key = supabase_key
        if schema:
            self.global_config.database.supabase_schema = schema
            
        logger.debug(f"Database configured for {env}: schema={schema}, url={supabase_url}")
    
    def _initialize_consul_discovery(self):
        """Initialize Consul service discovery client"""
        if not self.global_config or not self.global_config.consul.enabled:
            logger.info("Consul discovery disabled")
            return
            
        try:
            from ..discovery.consul_discovery import ConsulServiceDiscovery
            self._consul_discovery = ConsulServiceDiscovery(
                consul_host=self.global_config.consul.host,
                consul_port=self.global_config.consul.port
            )
            
            if self._consul_discovery.is_available():
                logger.info("Consul service discovery initialized successfully")
            else:
                logger.warning("Consul not available, using fallback URLs")
                self._consul_discovery = None
                
        except ImportError as e:
            logger.warning(f"Consul discovery not available: {e}")
            self._consul_discovery = None
        except Exception as e:
            logger.error(f"Failed to initialize Consul discovery: {e}")
            self._consul_discovery = None
    
    def _apply_service_env_overrides(self):
        """Apply service endpoint environment variable overrides"""
        if not self.global_config:
            return
            
        # Consul configuration overrides
        consul_env_mapping = {
            "enabled": ["CONSUL_ENABLED"],
            "host": ["CONSUL_HOST"],
            "port": ["CONSUL_PORT"],
        }
        
        for setting, env_vars in consul_env_mapping.items():
            for env_var in env_vars:
                value = os.getenv(env_var)
                if value:
                    if setting == "enabled":
                        setattr(self.global_config.consul, setting, value.lower() == "true")
                    elif setting == "port":
                        try:
                            setattr(self.global_config.consul, setting, int(value))
                        except ValueError:
                            continue
                    else:
                        setattr(self.global_config.consul, setting, value)
                    break
        
        # Service endpoint overrides
        service_env_mapping = {
            "use_consul_discovery": ["USE_CONSUL_DISCOVERY"],
            "mcp_base_url": ["MCP_BASE_URL", "MCP_URL"],
            "ollama_base_url": ["OLLAMA_BASE_URL", "OLLAMA_URL"],
            "influxdb_url": ["INFLUXDB_URL", "INFLUX_URL"],
            "loki_url": ["LOKI_URL"],
            "minio_endpoint": ["MINIO_ENDPOINT", "MINIO_HOST"],
            "redis_url": ["REDIS_URL"],
            "redis_port": ["REDIS_PORT"],
            "mcp_service_name": ["MCP_SERVICE_NAME"],
            "ollama_service_name": ["OLLAMA_SERVICE_NAME"],
            "influxdb_service_name": ["INFLUXDB_SERVICE_NAME"],
            "loki_service_name": ["LOKI_SERVICE_NAME"],
            "minio_service_name": ["MINIO_SERVICE_NAME"],
            "redis_service_name": ["REDIS_SERVICE_NAME"],
        }
        
        for setting, env_vars in service_env_mapping.items():
            for env_var in env_vars:
                value = os.getenv(env_var)
                if value:
                    if setting == "use_consul_discovery":
                        setattr(self.global_config.services, setting, value.lower() == "true")
                    elif setting in ["redis_port"]:
                        try:
                            setattr(self.global_config.services, setting, int(value))
                        except ValueError:
                            continue
                    else:
                        setattr(self.global_config.services, setting, value)
                    break
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        if not self.global_config:
            return
        
        # Environment-based database configuration
        self._configure_database_for_environment()
        
        # Service configuration overrides
        self._apply_service_env_overrides()
        
        # Serving overrides
        port_env = os.getenv("PORT") or os.getenv("API_PORT")
        if port_env:
            try:
                self.global_config.serving.port = int(port_env)
                self.global_config.services.api_port = int(port_env)
            except ValueError:
                pass
        
        # Debug override
        debug_env = os.getenv("DEBUG")
        if debug_env:
            self.global_config.debug = debug_env.lower() in ('true', '1', 'yes')
    
    # Public API
    def get_global_config(self) -> GlobalConfig:
        """Get global configuration"""
        if not self.global_config:
            raise RuntimeError("Configuration not loaded")
        return self.global_config
    
    def get_service_config(self) -> ServiceConfig:
        """Get service configuration"""
        if not self.global_config:
            raise RuntimeError("Configuration not loaded")
        return self.global_config.services
    
    def get_consul_config(self) -> ConsulConfig:
        """Get Consul configuration"""
        if not self.global_config:
            raise RuntimeError("Configuration not loaded")
        return self.global_config.consul
    
    def discover_service_url(self, service_name: str, fallback_url: Optional[str] = None) -> str:
        """Discover service URL using Consul or return fallback"""
        if not self.global_config or not self.global_config.services.use_consul_discovery:
            return fallback_url or self._get_fallback_service_url(service_name)
            
        if not self._consul_discovery or not self._consul_discovery.is_available():
            logger.debug(f"Consul not available, using fallback for {service_name}")
            return fallback_url or self._get_fallback_service_url(service_name)
            
        try:
            discovered_url = self._consul_discovery.get_service_url(
                service_name, 
                fallback_url or self._get_fallback_service_url(service_name)
            )
            return discovered_url
        except Exception as e:
            logger.warning(f"Failed to discover {service_name}: {e}")
            return fallback_url or self._get_fallback_service_url(service_name)
    
    def _get_fallback_service_url(self, service_name: str) -> str:
        """Get fallback URL for service based on service name"""
        if not self.global_config:
            raise RuntimeError("Configuration not loaded")
            
        service_config = self.global_config.services
        
        # Map service names to fallback URLs
        service_mapping = {
            service_config.mcp_service_name: service_config.mcp_base_url,
            service_config.ollama_service_name: service_config.ollama_base_url,
            service_config.influxdb_service_name: service_config.influxdb_url,
            service_config.loki_service_name: service_config.loki_url,
            service_config.minio_service_name: f"http://{service_config.minio_endpoint}",
            service_config.redis_service_name: service_config.redis_url,
        }
        
        return service_mapping.get(service_name, f"http://localhost:8080")
    
    def get_mcp_url(self) -> str:
        """Get MCP service URL (Consul discovery + fallback)"""
        service_name = self.global_config.services.mcp_service_name
        return self.discover_service_url(service_name, self.global_config.services.mcp_base_url)
    
    def get_ollama_url(self) -> str:
        """Get Ollama service URL (Consul discovery + fallback)"""
        service_name = self.global_config.services.ollama_service_name
        return self.discover_service_url(service_name, self.global_config.services.ollama_base_url)
    
    def get_influxdb_url(self) -> str:
        """Get InfluxDB service URL (Consul discovery + fallback)"""
        service_name = self.global_config.services.influxdb_service_name
        return self.discover_service_url(service_name, self.global_config.services.influxdb_url)
    
    def get_loki_url(self) -> str:
        """Get Loki service URL (Consul discovery + fallback)"""
        service_name = self.global_config.services.loki_service_name
        return self.discover_service_url(service_name, self.global_config.services.loki_url)
    
    def get_minio_url(self) -> str:
        """Get MinIO service URL (Consul discovery + fallback)"""
        service_name = self.global_config.services.minio_service_name
        fallback = f"http://{self.global_config.services.minio_endpoint}"
        return self.discover_service_url(service_name, fallback)
    
    def get_redis_url(self) -> str:
        """Get Redis service URL (Consul discovery + fallback)"""
        service_name = self.global_config.services.redis_service_name
        return self.discover_service_url(service_name, self.global_config.services.redis_url)
    
    def resolve_consul_url(self, url: str) -> str:
        """Resolve consul:// URLs to actual service addresses"""
        if not url or not url.startswith("consul://"):
            return url
            
        if not self._consul_discovery:
            # If Consul not available, try to extract service name and use fallback
            parts = url.replace("consul://", "").split("/", 1)
            service_name = parts[0]
            return self._get_fallback_service_url(service_name)
            
        return self._consul_discovery.resolve_service_url(url)
    
    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        """Get provider configuration"""
        return self.provider_configs.get(provider)
    
    def get_provider_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider"""
        config = self.get_provider_config(provider)
        return config.api_key if config else None
    
    def is_provider_enabled(self, provider: str) -> bool:
        """Check if provider is enabled"""
        config = self.get_provider_config(provider)
        return config is not None and config.enabled and config.api_key is not None
    
    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled providers"""
        return [name for name, config in self.provider_configs.items() if config.enabled]
    
    def get_model_definition(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model definition"""
        return self.model_definitions.get(model_id)
    
    def get_models_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """Get all models for a provider"""
        return [model for model in self.model_definitions.values() 
                if model.get('provider') == provider]
    
    def get_models_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Get models that support a specific capability"""
        return [model for model in self.model_definitions.values()
                if capability in model.get('capabilities', [])]
    
    def reload(self):
        """Reload configuration"""
        self._load_configuration()
        logger.info("Configuration reloaded")
    
    def get_deployment_config(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get deployment platform configuration"""
        return getattr(self, 'deployment_configs', {}).get(platform)
    
    def is_deployment_enabled(self, platform: str) -> bool:
        """Check if deployment platform is enabled"""
        config = self.get_deployment_config(platform)
        return config is not None and config.get("enabled", False)
    
    def save_config(self, config_file: Optional[Path] = None):
        """Save current configuration to YAML file (for compatibility)"""
        if config_file is None:
            config_file = Path.cwd() / "isa_model_config.yaml"
        
        if not self.global_config:
            logger.error("No configuration to save")
            return
        
        config_data = {
            "environment": self.global_config.environment.value,
            "debug": self.global_config.debug,
            "database": {
                "use_supabase": self.global_config.database.use_supabase,
                "fallback_to_sqlite": self.global_config.database.fallback_to_sqlite,
            },
            "providers": {},
        }
        
        # Add provider configs (without API keys for security)
        for provider_name, config in self.provider_configs.items():
            config_data["providers"][provider_name] = {
                "enabled": config.enabled,
                "rate_limit_rpm": config.rate_limit_rpm,
                "rate_limit_tpm": config.rate_limit_tpm,
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
        enabled_providers = self.get_enabled_providers()
        configured_deployments = [p for p in getattr(self, 'deployment_configs', {}).keys()]
        
        return {
            "environment": self.global_config.environment.value if self.global_config else "unknown",
            "debug": self.global_config.debug if self.global_config else False,
            "enabled_providers": enabled_providers,
            "configured_deployments": configured_deployments,
            "total_models": len(self.model_definitions),
            "database_backend": "supabase" if (self.global_config and self.global_config.database.use_supabase) else "sqlite",
            "deployment_platform": self.global_config.deployment.platform if self.global_config else "unknown",
            "cost_tracking": self.global_config.billing.track_costs if self.global_config else False,
            "model_caching": self.global_config.cache.enabled if self.global_config else False,
        }