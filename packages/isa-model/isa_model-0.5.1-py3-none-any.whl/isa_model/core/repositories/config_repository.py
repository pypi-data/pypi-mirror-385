"""
Configuration Repository - Data persistence layer for configuration management

Provides standardized data access for configuration data, provider settings, and environment configurations
following the ISA Model architecture pattern.
"""

import logging
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

try:
    # Try to import Supabase for centralized data storage
    from ...core.database.supabase_client import get_supabase_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

logger = logging.getLogger(__name__)

class ConfigType(str, Enum):
    """Configuration type enumeration"""
    PROVIDER = "provider"
    ENVIRONMENT = "environment"
    SYSTEM = "system"
    USER = "user"
    API_KEY = "api_key"
    FEATURE_FLAG = "feature_flag"

@dataclass
class ConfigRecord:
    """Configuration record model"""
    config_id: str
    config_type: str
    config_key: str
    config_value: Any
    environment: str = "production"
    is_active: bool = True
    is_encrypted: bool = False
    created_at: datetime = None
    updated_at: datetime = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at

@dataclass
class ProviderConfig:
    """Provider configuration model"""
    provider_name: str
    config_data: Dict[str, Any]
    is_active: bool = True
    environment: str = "production"
    created_at: datetime = None
    updated_at: datetime = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at

@dataclass
class EnvironmentConfig:
    """Environment configuration model"""
    environment: str
    config_data: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at

@dataclass
class ConfigAuditLog:
    """Configuration audit log model"""
    audit_id: str
    config_id: str
    action: str  # create, update, delete, read
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    user_id: Optional[str] = None
    timestamp: datetime = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

class ConfigRepository:
    """
    Repository for configuration data persistence
    
    Supports multiple backend storage options:
    1. Environment variables (for sensitive data)
    2. File system (for development and local configs)
    3. Supabase (for centralized storage)
    4. In-memory (for testing)
    """
    
    def __init__(self, storage_backend: str = "auto", **kwargs):
        """
        Initialize configuration repository
        
        Args:
            storage_backend: "env", "file", "supabase", "memory", or "auto"
            **kwargs: Backend-specific configuration
        """
        self.storage_backend = self._determine_backend(storage_backend)
        self.config = kwargs
        
        # Initialize storage backend
        if self.storage_backend == "supabase":
            self._init_supabase()
        elif self.storage_backend == "env":
            self._init_env()
        elif self.storage_backend == "memory":
            self._init_memory()
        else:  # file system
            self._init_file_system()
        
        logger.info(f"Configuration repository initialized with {self.storage_backend} backend")
    
    def _determine_backend(self, preference: str) -> str:
        """Determine the best available storage backend"""
        if preference == "supabase" and SUPABASE_AVAILABLE:
            return "supabase"
        elif preference in ["env", "file", "memory", "supabase"]:
            return preference
        
        # Auto-select best available backend
        if SUPABASE_AVAILABLE:
            return "supabase"
        else:
            return "file"
    
    def _init_supabase(self):
        """Initialize Supabase backend"""
        try:
            self.supabase_client = get_supabase_client()
            self._ensure_supabase_tables()
            logger.info("Supabase backend initialized for configurations")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase backend: {e}")
            self.storage_backend = "file"
            self._init_file_system()
    
    def _init_file_system(self):
        """Initialize file system backend"""
        self.config_dir = Path(self.config.get("config_dir", "./config_data"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.config_dir / "providers").mkdir(exist_ok=True)
        (self.config_dir / "environments").mkdir(exist_ok=True)
        (self.config_dir / "system").mkdir(exist_ok=True)
        (self.config_dir / "audit").mkdir(exist_ok=True)
        
        logger.info(f"File system backend initialized: {self.config_dir}")
    
    def _init_env(self):
        """Initialize environment variables backend"""
        self.env_prefix = self.config.get("env_prefix", "ISA_")
        logger.info(f"Environment variables backend initialized with prefix: {self.env_prefix}")
    
    def _init_memory(self):
        """Initialize in-memory backend for testing"""
        self.configs = {}
        self.providers = {}
        self.environments = {}
        self.audit_logs = []
        logger.info("In-memory backend initialized for configurations")
    
    def _ensure_supabase_tables(self):
        """Ensure required Supabase tables exist"""
        try:
            self.supabase_client.table("config_records").select("config_id").limit(1).execute()
            self.supabase_client.table("provider_configs").select("provider_name").limit(1).execute()
            self.supabase_client.table("environment_configs").select("environment").limit(1).execute()
            self.supabase_client.table("config_audit_logs").select("audit_id").limit(1).execute()
        except Exception as e:
            logger.warning(f"Some configuration tables may not exist in Supabase: {e}")
    
    # Provider Configuration Methods
    
    def get_provider_config(
        self,
        provider_name: str,
        environment: str = "production",
        mask_secrets: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Get provider configuration"""
        if self.storage_backend == "supabase":
            return self._get_provider_config_supabase(provider_name, environment, mask_secrets)
        elif self.storage_backend == "env":
            return self._get_provider_config_env(provider_name, environment, mask_secrets)
        elif self.storage_backend == "memory":
            return self._get_provider_config_memory(provider_name, environment, mask_secrets)
        else:
            return self._get_provider_config_file(provider_name, environment, mask_secrets)
    
    def update_provider_config(
        self,
        provider_name: str,
        config_data: Dict[str, Any],
        environment: str = "production",
        is_active: bool = True,
        updated_by: Optional[str] = None
    ) -> bool:
        """Update provider configuration"""
        if self.storage_backend == "supabase":
            return self._update_provider_config_supabase(provider_name, config_data, environment, is_active, updated_by)
        elif self.storage_backend == "env":
            return self._update_provider_config_env(provider_name, config_data, environment, is_active, updated_by)
        elif self.storage_backend == "memory":
            return self._update_provider_config_memory(provider_name, config_data, environment, is_active, updated_by)
        else:
            return self._update_provider_config_file(provider_name, config_data, environment, is_active, updated_by)
    
    def list_provider_configs(
        self,
        environment: str = "production",
        include_inactive: bool = False
    ) -> List[ProviderConfig]:
        """List all provider configurations"""
        if self.storage_backend == "supabase":
            return self._list_provider_configs_supabase(environment, include_inactive)
        elif self.storage_backend == "env":
            return self._list_provider_configs_env(environment, include_inactive)
        elif self.storage_backend == "memory":
            return self._list_provider_configs_memory(environment, include_inactive)
        else:
            return self._list_provider_configs_file(environment, include_inactive)
    
    def delete_provider_config(
        self,
        provider_name: str,
        environment: str = "production",
        deleted_by: Optional[str] = None
    ) -> bool:
        """Delete provider configuration"""
        if self.storage_backend == "supabase":
            return self._delete_provider_config_supabase(provider_name, environment, deleted_by)
        elif self.storage_backend == "env":
            return self._delete_provider_config_env(provider_name, environment, deleted_by)
        elif self.storage_backend == "memory":
            return self._delete_provider_config_memory(provider_name, environment, deleted_by)
        else:
            return self._delete_provider_config_file(provider_name, environment, deleted_by)
    
    # Environment Configuration Methods
    
    def get_environment_config(
        self,
        environment: str,
        mask_secrets: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Get environment configuration"""
        if self.storage_backend == "supabase":
            return self._get_environment_config_supabase(environment, mask_secrets)
        elif self.storage_backend == "env":
            return self._get_environment_config_env(environment, mask_secrets)
        elif self.storage_backend == "memory":
            return self._get_environment_config_memory(environment, mask_secrets)
        else:
            return self._get_environment_config_file(environment, mask_secrets)
    
    def update_environment_config(
        self,
        environment: str,
        config_data: Dict[str, Any],
        updated_by: Optional[str] = None
    ) -> bool:
        """Update environment configuration"""
        if self.storage_backend == "supabase":
            return self._update_environment_config_supabase(environment, config_data, updated_by)
        elif self.storage_backend == "env":
            return self._update_environment_config_env(environment, config_data, updated_by)
        elif self.storage_backend == "memory":
            return self._update_environment_config_memory(environment, config_data, updated_by)
        else:
            return self._update_environment_config_file(environment, config_data, updated_by)
    
    def list_environment_configs(self) -> List[EnvironmentConfig]:
        """List all environment configurations"""
        if self.storage_backend == "supabase":
            return self._list_environment_configs_supabase()
        elif self.storage_backend == "env":
            return self._list_environment_configs_env()
        elif self.storage_backend == "memory":
            return self._list_environment_configs_memory()
        else:
            return self._list_environment_configs_file()
    
    # Generic Configuration Methods
    
    def get_config(
        self,
        config_key: str,
        config_type: str = "system",
        environment: str = "production",
        default_value: Any = None
    ) -> Any:
        """Get generic configuration value"""
        if self.storage_backend == "env":
            return self._get_config_env(config_key, config_type, environment, default_value)
        elif self.storage_backend == "memory":
            return self._get_config_memory(config_key, config_type, environment, default_value)
        elif self.storage_backend == "supabase":
            return self._get_config_supabase(config_key, config_type, environment, default_value)
        else:
            return self._get_config_file(config_key, config_type, environment, default_value)
    
    def set_config(
        self,
        config_key: str,
        config_value: Any,
        config_type: str = "system",
        environment: str = "production",
        updated_by: Optional[str] = None,
        description: Optional[str] = None
    ) -> bool:
        """Set generic configuration value"""
        if self.storage_backend == "env":
            return self._set_config_env(config_key, config_value, config_type, environment, updated_by, description)
        elif self.storage_backend == "memory":
            return self._set_config_memory(config_key, config_value, config_type, environment, updated_by, description)
        elif self.storage_backend == "supabase":
            return self._set_config_supabase(config_key, config_value, config_type, environment, updated_by, description)
        else:
            return self._set_config_file(config_key, config_value, config_type, environment, updated_by, description)
    
    # Validation Methods
    
    def validate_provider_config(
        self,
        provider_name: str,
        config_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate provider configuration"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Basic validation rules
        if not provider_name:
            validation_result["valid"] = False
            validation_result["errors"].append("Provider name is required")
        
        if not config_data:
            validation_result["valid"] = False
            validation_result["errors"].append("Configuration data is required")
        
        # Provider-specific validation
        if provider_name == "openai":
            if "api_key" not in config_data:
                validation_result["valid"] = False
                validation_result["errors"].append("OpenAI API key is required")
        elif provider_name == "anthropic":
            if "api_key" not in config_data:
                validation_result["valid"] = False
                validation_result["errors"].append("Anthropic API key is required")
        elif provider_name == "replicate":
            if "api_token" not in config_data:
                validation_result["valid"] = False
                validation_result["errors"].append("Replicate API token is required")
        
        return validation_result
    
    def validate_environment_config(
        self,
        environment: str,
        config_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate environment configuration"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not environment:
            validation_result["valid"] = False
            validation_result["errors"].append("Environment name is required")
        
        if environment not in ["development", "staging", "production"]:
            validation_result["warnings"].append(f"Unusual environment name: {environment}")
        
        return validation_result
    
    # Audit and Logging Methods
    
    def log_config_change(
        self,
        config_id: str,
        action: str,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """Log configuration change for audit purposes"""
        audit_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(config_id) % 10000}"
        
        audit_log = ConfigAuditLog(
            audit_id=audit_id,
            config_id=config_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            user_id=user_id,
            ip_address=ip_address
        )
        
        if self.storage_backend == "memory":
            self.audit_logs.append(audit_log)
        elif self.storage_backend == "file":
            self._save_audit_log_file(audit_log)
        # Supabase implementation would go here
        
        return audit_id
    
    def get_audit_logs(
        self,
        config_id: Optional[str] = None,
        action: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ConfigAuditLog]:
        """Get configuration audit logs"""
        if self.storage_backend == "memory":
            return self._get_audit_logs_memory(config_id, action, user_id, limit)
        elif self.storage_backend == "file":
            return self._get_audit_logs_file(config_id, action, user_id, limit)
        else:
            return []  # Supabase implementation needed
    
    # Backend-specific implementations (File System)
    
    def _get_provider_config_file(self, provider_name: str, environment: str, mask_secrets: bool) -> Optional[Dict[str, Any]]:
        """Get provider config from file system"""
        try:
            config_file = self.config_dir / "providers" / f"{provider_name}_{environment}.json"
            if not config_file.exists():
                return None
            
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            if mask_secrets:
                config_data = self._mask_sensitive_data(config_data)
            
            return config_data.get("config_data")
        except Exception as e:
            logger.error(f"Failed to get provider config from file: {e}")
            return None
    
    def _update_provider_config_file(
        self, provider_name: str, config_data: Dict[str, Any], 
        environment: str, is_active: bool, updated_by: Optional[str]
    ) -> bool:
        """Update provider config in file system"""
        try:
            config_file = self.config_dir / "providers" / f"{provider_name}_{environment}.json"
            
            provider_config = ProviderConfig(
                provider_name=provider_name,
                config_data=config_data,
                is_active=is_active,
                environment=environment,
                updated_by=updated_by,
                updated_at=datetime.now(timezone.utc)
            )
            
            # Preserve created_at if file exists
            if config_file.exists():
                with open(config_file, 'r') as f:
                    existing_data = json.load(f)
                    if 'created_at' in existing_data:
                        provider_config.created_at = datetime.fromisoformat(existing_data['created_at'])
            
            config_dict = asdict(provider_config)
            # Convert datetime objects to ISO strings
            for key in ['created_at', 'updated_at']:
                if config_dict[key] and isinstance(config_dict[key], datetime):
                    config_dict[key] = config_dict[key].isoformat()
            
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            # Log the change
            self.log_config_change(
                config_id=f"provider_{provider_name}_{environment}",
                action="update",
                new_value=config_data,
                user_id=updated_by
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to update provider config in file: {e}")
            return False
    
    def _list_provider_configs_file(self, environment: str, include_inactive: bool) -> List[ProviderConfig]:
        """List provider configs from file system"""
        try:
            configs = []
            providers_dir = self.config_dir / "providers"
            
            for config_file in providers_dir.glob(f"*_{environment}.json"):
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                if not include_inactive and not config_data.get('is_active', True):
                    continue
                
                # Convert datetime fields
                for key in ['created_at', 'updated_at']:
                    if config_data[key]:
                        config_data[key] = datetime.fromisoformat(config_data[key])
                
                configs.append(ProviderConfig(**config_data))
            
            return configs
        except Exception as e:
            logger.error(f"Failed to list provider configs from file: {e}")
            return []
    
    def _get_environment_config_file(self, environment: str, mask_secrets: bool) -> Optional[Dict[str, Any]]:
        """Get environment config from file system"""
        try:
            config_file = self.config_dir / "environments" / f"{environment}.json"
            if not config_file.exists():
                return None
            
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            if mask_secrets:
                config_data = self._mask_sensitive_data(config_data)
            
            return config_data.get("config_data")
        except Exception as e:
            logger.error(f"Failed to get environment config from file: {e}")
            return None
    
    def _get_config_file(self, config_key: str, config_type: str, environment: str, default_value: Any) -> Any:
        """Get generic config from file system"""
        try:
            config_file = self.config_dir / "system" / f"{config_type}_{environment}.json"
            if not config_file.exists():
                return default_value
            
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            return config_data.get(config_key, default_value)
        except Exception as e:
            logger.error(f"Failed to get config from file: {e}")
            return default_value
    
    def _set_config_file(
        self, config_key: str, config_value: Any, config_type: str, 
        environment: str, updated_by: Optional[str], description: Optional[str]
    ) -> bool:
        """Set generic config in file system"""
        try:
            config_file = self.config_dir / "system" / f"{config_type}_{environment}.json"
            
            # Load existing config or create new
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
            else:
                config_data = {}
            
            config_data[config_key] = config_value
            config_data['_updated_at'] = datetime.now(timezone.utc).isoformat()
            config_data['_updated_by'] = updated_by
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Failed to set config in file: {e}")
            return False
    
    # Backend-specific implementations (Environment Variables)
    
    def _get_provider_config_env(self, provider_name: str, environment: str, mask_secrets: bool) -> Optional[Dict[str, Any]]:
        """Get provider config from environment variables"""
        env_key = f"{self.env_prefix}{provider_name.upper()}_{environment.upper()}_CONFIG"
        config_json = os.getenv(env_key)
        
        if not config_json:
            return None
        
        try:
            config_data = json.loads(config_json)
            if mask_secrets:
                config_data = self._mask_sensitive_data(config_data)
            return config_data
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in environment variable: {env_key}")
            return None
    
    def _get_config_env(self, config_key: str, config_type: str, environment: str, default_value: Any) -> Any:
        """Get config from environment variables"""
        env_key = f"{self.env_prefix}{config_type.upper()}_{environment.upper()}_{config_key.upper()}"
        return os.getenv(env_key, default_value)
    
    # Backend-specific implementations (Memory)
    
    def _get_provider_config_memory(self, provider_name: str, environment: str, mask_secrets: bool) -> Optional[Dict[str, Any]]:
        """Get provider config from memory"""
        key = f"{provider_name}_{environment}"
        config = self.providers.get(key)
        if not config:
            return None
        
        config_data = config.config_data.copy()
        if mask_secrets:
            config_data = self._mask_sensitive_data(config_data)
        return config_data
    
    def _update_provider_config_memory(
        self, provider_name: str, config_data: Dict[str, Any], 
        environment: str, is_active: bool, updated_by: Optional[str]
    ) -> bool:
        """Update provider config in memory"""
        key = f"{provider_name}_{environment}"
        
        provider_config = ProviderConfig(
            provider_name=provider_name,
            config_data=config_data,
            is_active=is_active,
            environment=environment,
            updated_by=updated_by,
            updated_at=datetime.now(timezone.utc)
        )
        
        self.providers[key] = provider_config
        return True
    
    def _get_config_memory(self, config_key: str, config_type: str, environment: str, default_value: Any) -> Any:
        """Get config from memory"""
        key = f"{config_type}_{environment}_{config_key}"
        return self.configs.get(key, default_value)
    
    def _set_config_memory(
        self, config_key: str, config_value: Any, config_type: str, 
        environment: str, updated_by: Optional[str], description: Optional[str]
    ) -> bool:
        """Set config in memory"""
        key = f"{config_type}_{environment}_{config_key}"
        self.configs[key] = config_value
        return True
    
    # Utility Methods
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive configuration data"""
        masked_data = data.copy()
        sensitive_keys = ['api_key', 'api_token', 'secret', 'password', 'private_key']
        
        for key, value in masked_data.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                if isinstance(value, str) and len(value) > 8:
                    masked_data[key] = value[:4] + "***" + value[-4:]
                else:
                    masked_data[key] = "***"
        
        return masked_data
    
    def _save_audit_log_file(self, audit_log: ConfigAuditLog):
        """Save audit log to file system"""
        try:
            audit_file = self.config_dir / "audit" / f"{audit_log.audit_id}.json"
            audit_data = asdict(audit_log)
            
            if audit_data['timestamp'] and isinstance(audit_data['timestamp'], datetime):
                audit_data['timestamp'] = audit_data['timestamp'].isoformat()
            
            with open(audit_file, 'w') as f:
                json.dump(audit_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save audit log to file: {e}")
    
    def _get_audit_logs_file(self, config_id: Optional[str], action: Optional[str], user_id: Optional[str], limit: int) -> List[ConfigAuditLog]:
        """Get audit logs from file system"""
        try:
            logs = []
            audit_dir = self.config_dir / "audit"
            
            for audit_file in audit_dir.glob("*.json"):
                with open(audit_file, 'r') as f:
                    audit_data = json.load(f)
                
                # Apply filters
                if config_id and audit_data.get('config_id') != config_id:
                    continue
                if action and audit_data.get('action') != action:
                    continue
                if user_id and audit_data.get('user_id') != user_id:
                    continue
                
                # Convert timestamp
                if audit_data['timestamp']:
                    audit_data['timestamp'] = datetime.fromisoformat(audit_data['timestamp'])
                
                logs.append(ConfigAuditLog(**audit_data))
                
                if len(logs) >= limit:
                    break
            
            return sorted(logs, key=lambda x: x.timestamp, reverse=True)
        except Exception as e:
            logger.error(f"Failed to get audit logs from file: {e}")
            return []
    
    def _get_audit_logs_memory(self, config_id: Optional[str], action: Optional[str], user_id: Optional[str], limit: int) -> List[ConfigAuditLog]:
        """Get audit logs from memory"""
        filtered_logs = []
        
        for log in self.audit_logs:
            # Apply filters
            if config_id and log.config_id != config_id:
                continue
            if action and log.action != action:
                continue
            if user_id and log.user_id != user_id:
                continue
            
            filtered_logs.append(log)
            
            if len(filtered_logs) >= limit:
                break
        
        return sorted(filtered_logs, key=lambda x: x.timestamp, reverse=True)
    
    # Placeholder implementations for remaining methods
    def _delete_provider_config_file(self, provider_name: str, environment: str, deleted_by: Optional[str]) -> bool:
        try:
            config_file = self.config_dir / "providers" / f"{provider_name}_{environment}.json"
            if config_file.exists():
                config_file.unlink()
                self.log_config_change(
                    config_id=f"provider_{provider_name}_{environment}",
                    action="delete",
                    user_id=deleted_by
                )
            return True
        except Exception as e:
            logger.error(f"Failed to delete provider config from file: {e}")
            return False
    
    def _delete_provider_config_memory(self, provider_name: str, environment: str, deleted_by: Optional[str]) -> bool:
        key = f"{provider_name}_{environment}"
        return self.providers.pop(key, None) is not None
    
    def _delete_provider_config_env(self, provider_name: str, environment: str, deleted_by: Optional[str]) -> bool:
        # Cannot delete environment variables programmatically
        return False
    
    def _update_environment_config_file(self, environment: str, config_data: Dict[str, Any], updated_by: Optional[str]) -> bool:
        try:
            config_file = self.config_dir / "environments" / f"{environment}.json"
            
            env_config = EnvironmentConfig(
                environment=environment,
                config_data=config_data,
                updated_by=updated_by,
                updated_at=datetime.now(timezone.utc)
            )
            
            config_dict = asdict(env_config)
            # Convert datetime objects to ISO strings
            for key in ['created_at', 'updated_at']:
                if config_dict[key] and isinstance(config_dict[key], datetime):
                    config_dict[key] = config_dict[key].isoformat()
            
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update environment config in file: {e}")
            return False
    
    def _list_environment_configs_file(self) -> List[EnvironmentConfig]:
        try:
            configs = []
            environments_dir = self.config_dir / "environments"
            
            for config_file in environments_dir.glob("*.json"):
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Convert datetime fields
                for key in ['created_at', 'updated_at']:
                    if config_data[key]:
                        config_data[key] = datetime.fromisoformat(config_data[key])
                
                configs.append(EnvironmentConfig(**config_data))
            
            return configs
        except Exception as e:
            logger.error(f"Failed to list environment configs from file: {e}")
            return []
    
    # Placeholder implementations for Supabase and other methods
    def _get_provider_config_supabase(self, provider_name: str, environment: str, mask_secrets: bool) -> Optional[Dict[str, Any]]:
        return None  # Implementation needed
    
    def _update_provider_config_supabase(self, provider_name: str, config_data: Dict[str, Any], environment: str, is_active: bool, updated_by: Optional[str]) -> bool:
        return False  # Implementation needed
    
    def _list_provider_configs_supabase(self, environment: str, include_inactive: bool) -> List[ProviderConfig]:
        return []  # Implementation needed
    
    def _update_provider_config_env(self, provider_name: str, config_data: Dict[str, Any], environment: str, is_active: bool, updated_by: Optional[str]) -> bool:
        return False  # Environment variables are read-only
    
    def _list_provider_configs_env(self, environment: str, include_inactive: bool) -> List[ProviderConfig]:
        return []  # Implementation needed
    
    def _list_provider_configs_memory(self, environment: str, include_inactive: bool) -> List[ProviderConfig]:
        configs = []
        for key, config in self.providers.items():
            if environment not in key:
                continue
            if not include_inactive and not config.is_active:
                continue
            configs.append(config)
        return configs
    
    def _get_environment_config_supabase(self, environment: str, mask_secrets: bool) -> Optional[Dict[str, Any]]:
        return None  # Implementation needed
    
    def _get_environment_config_env(self, environment: str, mask_secrets: bool) -> Optional[Dict[str, Any]]:
        return None  # Implementation needed
    
    def _get_environment_config_memory(self, environment: str, mask_secrets: bool) -> Optional[Dict[str, Any]]:
        env_config = self.environments.get(environment)
        if not env_config:
            return None
        
        config_data = env_config.config_data.copy()
        if mask_secrets:
            config_data = self._mask_sensitive_data(config_data)
        return config_data
    
    def _update_environment_config_supabase(self, environment: str, config_data: Dict[str, Any], updated_by: Optional[str]) -> bool:
        return False  # Implementation needed
    
    def _update_environment_config_env(self, environment: str, config_data: Dict[str, Any], updated_by: Optional[str]) -> bool:
        return False  # Environment variables are read-only
    
    def _update_environment_config_memory(self, environment: str, config_data: Dict[str, Any], updated_by: Optional[str]) -> bool:
        env_config = EnvironmentConfig(
            environment=environment,
            config_data=config_data,
            updated_by=updated_by,
            updated_at=datetime.now(timezone.utc)
        )
        self.environments[environment] = env_config
        return True
    
    def _list_environment_configs_supabase(self) -> List[EnvironmentConfig]:
        return []  # Implementation needed
    
    def _list_environment_configs_env(self) -> List[EnvironmentConfig]:
        return []  # Implementation needed
    
    def _list_environment_configs_memory(self) -> List[EnvironmentConfig]:
        return list(self.environments.values())
    
    def _get_config_supabase(self, config_key: str, config_type: str, environment: str, default_value: Any) -> Any:
        return default_value  # Implementation needed
    
    def _set_config_supabase(self, config_key: str, config_value: Any, config_type: str, environment: str, updated_by: Optional[str], description: Optional[str]) -> bool:
        return False  # Implementation needed
    
    def _set_config_env(self, config_key: str, config_value: Any, config_type: str, environment: str, updated_by: Optional[str], description: Optional[str]) -> bool:
        return False  # Environment variables are read-only
    
    def _delete_provider_config_supabase(self, provider_name: str, environment: str, deleted_by: Optional[str]) -> bool:
        return False  # Implementation needed