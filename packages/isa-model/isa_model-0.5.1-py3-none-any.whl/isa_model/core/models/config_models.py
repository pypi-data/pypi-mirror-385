"""
Configuration Models

Core data models for configuration management, extracted from repository layer
to follow the standard ISA Model architecture pattern.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class ConfigType(str, Enum):
    """Configuration type enumeration"""
    PROVIDER = "provider"
    ENVIRONMENT = "environment"
    SYSTEM = "system"
    USER = "user"
    API_KEY = "api_key"
    FEATURE_FLAG = "feature_flag"
    DEPLOYMENT = "deployment"
    SECURITY = "security"

class ConfigStatus(str, Enum):
    """Configuration status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    PENDING = "pending"
    ARCHIVED = "archived"

class SecurityLevel(str, Enum):
    """Security level enumeration"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

@dataclass
class ConfigRecord:
    """
    Core configuration record model
    
    Represents a single configuration entry with metadata, versioning,
    and audit information for comprehensive configuration management.
    """
    config_id: str
    config_type: str
    config_key: str
    config_value: Any
    environment: str = "production"
    is_active: bool = True
    is_encrypted: bool = False
    security_level: str = SecurityLevel.INTERNAL
    version: int = 1
    previous_version_id: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    effective_from: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    change_reason: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.effective_from is None:
            self.effective_from = self.created_at
        if self.tags is None:
            self.tags = {}
        if self.metadata is None:
            self.metadata = {}
        if self.validation_rules is None:
            self.validation_rules = {}
    
    @property
    def is_effective(self) -> bool:
        """Check if configuration is currently effective"""
        now = datetime.now(timezone.utc)
        
        if not self.is_active:
            return False
        
        if self.effective_from and now < self.effective_from:
            return False
        
        if self.expires_at and now > self.expires_at:
            return False
        
        return True
    
    @property
    def is_expired(self) -> bool:
        """Check if configuration has expired"""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_sensitive(self) -> bool:
        """Check if configuration contains sensitive data"""
        return (self.is_encrypted or 
                self.security_level in [SecurityLevel.CONFIDENTIAL, SecurityLevel.SECRET, SecurityLevel.TOP_SECRET] or
                any(keyword in self.config_key.lower() for keyword in ['password', 'key', 'secret', 'token']))
    
    @property
    def age_days(self) -> int:
        """Get configuration age in days"""
        return (datetime.now(timezone.utc) - self.created_at).days
    
    def update_value(self, new_value: Any, updated_by: Optional[str] = None, 
                    change_reason: Optional[str] = None, increment_version: bool = True):
        """Update configuration value with versioning"""
        if increment_version:
            self.previous_version_id = f"{self.config_id}_v{self.version}"
            self.version += 1
        
        self.config_value = new_value
        self.updated_at = datetime.now(timezone.utc)
        
        if updated_by:
            self.updated_by = updated_by
        if change_reason:
            self.change_reason = change_reason
    
    def add_tag(self, key: str, value: str):
        """Add or update a configuration tag"""
        self.tags[key] = value
        self.updated_at = datetime.now(timezone.utc)
    
    def validate(self) -> List[str]:
        """Validate configuration according to rules"""
        issues = []
        
        if not self.config_key:
            issues.append("Configuration key is required")
        
        if self.config_value is None:
            issues.append("Configuration value cannot be None")
        
        if self.version < 1:
            issues.append("Version must be positive")
        
        # Apply validation rules
        for rule_name, rule_config in self.validation_rules.items():
            rule_type = rule_config.get("type")
            
            if rule_type == "required" and not self.config_value:
                issues.append(f"Value is required by rule '{rule_name}'")
            
            elif rule_type == "type_check":
                expected_type = rule_config.get("expected_type")
                if expected_type and not isinstance(self.config_value, eval(expected_type)):
                    issues.append(f"Value type mismatch for rule '{rule_name}': expected {expected_type}")
            
            elif rule_type == "range" and isinstance(self.config_value, (int, float)):
                min_val = rule_config.get("min")
                max_val = rule_config.get("max")
                if min_val is not None and self.config_value < min_val:
                    issues.append(f"Value below minimum for rule '{rule_name}': {min_val}")
                if max_val is not None and self.config_value > max_val:
                    issues.append(f"Value above maximum for rule '{rule_name}': {max_val}")
            
            elif rule_type == "enum" and isinstance(self.config_value, str):
                allowed_values = rule_config.get("allowed_values", [])
                if allowed_values and self.config_value not in allowed_values:
                    issues.append(f"Value not in allowed list for rule '{rule_name}': {allowed_values}")
        
        return issues
    
    def get_masked_value(self) -> Any:
        """Get masked version of sensitive configuration values"""
        if not self.is_sensitive:
            return self.config_value
        
        if isinstance(self.config_value, str):
            if len(self.config_value) > 8:
                return self.config_value[:4] + "***" + self.config_value[-4:]
            else:
                return "***"
        elif isinstance(self.config_value, dict):
            masked = {}
            for key, value in self.config_value.items():
                if any(keyword in key.lower() for keyword in ['password', 'key', 'secret', 'token']):
                    masked[key] = "***"
                else:
                    masked[key] = value
            return masked
        else:
            return "***"

@dataclass
class ProviderConfig:
    """
    Provider configuration model
    
    Contains provider-specific settings, credentials, and operational parameters
    for external service integrations.
    """
    provider_name: str
    config_data: Dict[str, Any]
    is_active: bool = True
    environment: str = "production"
    priority: int = 5  # 1-10 scale
    health_check_enabled: bool = True
    health_check_interval_seconds: int = 300
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"  # healthy, unhealthy, unknown, maintenance
    rate_limit_config: Optional[Dict[str, Any]] = None
    retry_config: Optional[Dict[str, Any]] = None
    timeout_config: Optional[Dict[str, Any]] = None
    cost_tracking_enabled: bool = True
    usage_limits: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.rate_limit_config is None:
            self.rate_limit_config = {}
        if self.retry_config is None:
            self.retry_config = {"max_retries": 3, "backoff_factor": 2}
        if self.timeout_config is None:
            self.timeout_config = {"default_timeout": 300}
        if self.usage_limits is None:
            self.usage_limits = {}
    
    @property
    def is_healthy(self) -> bool:
        """Check if provider is currently healthy"""
        return self.health_status == "healthy" and self.is_active
    
    @property
    def time_since_last_check(self) -> Optional[int]:
        """Get seconds since last health check"""
        if self.last_health_check:
            return int((datetime.now(timezone.utc) - self.last_health_check).total_seconds())
        return None
    
    @property
    def needs_health_check(self) -> bool:
        """Check if health check is due"""
        if not self.health_check_enabled:
            return False
        
        if not self.last_health_check:
            return True
        
        time_since = self.time_since_last_check
        return time_since is None or time_since >= self.health_check_interval_seconds
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value with default fallback"""
        return self.config_data.get(key, default)
    
    def update_config_value(self, key: str, value: Any, updated_by: Optional[str] = None):
        """Update specific configuration value"""
        self.config_data[key] = value
        self.updated_at = datetime.now(timezone.utc)
        if updated_by:
            self.updated_by = updated_by
    
    def update_health_status(self, status: str, check_time: Optional[datetime] = None):
        """Update health status with timestamp"""
        self.health_status = status
        self.last_health_check = check_time or datetime.now(timezone.utc)
        self.updated_at = self.last_health_check
    
    def validate_config(self) -> List[str]:
        """Validate provider configuration"""
        issues = []
        
        if not self.provider_name:
            issues.append("Provider name is required")
        
        if not self.config_data:
            issues.append("Configuration data is required")
        
        # Provider-specific validation
        if self.provider_name.lower() == "openai":
            if "api_key" not in self.config_data:
                issues.append("OpenAI API key is required")
            if "base_url" not in self.config_data:
                self.config_data["base_url"] = "https://api.openai.com/v1"
        
        elif self.provider_name.lower() == "anthropic":
            if "api_key" not in self.config_data:
                issues.append("Anthropic API key is required")
            if "base_url" not in self.config_data:
                self.config_data["base_url"] = "https://api.anthropic.com"
        
        elif self.provider_name.lower() == "replicate":
            if "api_token" not in self.config_data:
                issues.append("Replicate API token is required")
        
        # Validate numeric configurations
        if self.priority < 1 or self.priority > 10:
            issues.append("Priority must be between 1 and 10")
        
        if self.health_check_interval_seconds < 60:
            issues.append("Health check interval must be at least 60 seconds")
        
        return issues
    
    def get_masked_config(self) -> Dict[str, Any]:
        """Get configuration with sensitive values masked"""
        masked_config = {}
        sensitive_keys = ['api_key', 'api_token', 'secret', 'password', 'private_key']
        
        for key, value in self.config_data.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                if isinstance(value, str) and len(value) > 8:
                    masked_config[key] = value[:4] + "***" + value[-4:]
                else:
                    masked_config[key] = "***"
            else:
                masked_config[key] = value
        
        return masked_config

@dataclass
class EnvironmentConfig:
    """
    Environment configuration model
    
    Manages environment-specific settings and configurations for different
    deployment environments (development, staging, production, etc.).
    """
    environment: str
    config_data: Dict[str, Any]
    is_active: bool = True
    is_default: bool = False
    deployment_settings: Optional[Dict[str, Any]] = None
    resource_limits: Optional[Dict[str, Any]] = None
    feature_flags: Optional[Dict[str, bool]] = None
    monitoring_config: Optional[Dict[str, Any]] = None
    security_settings: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.deployment_settings is None:
            self.deployment_settings = {}
        if self.resource_limits is None:
            self.resource_limits = {}
        if self.feature_flags is None:
            self.feature_flags = {}
        if self.monitoring_config is None:
            self.monitoring_config = {}
        if self.security_settings is None:
            self.security_settings = {}
    
    @property
    def environment_type(self) -> str:
        """Classify environment type"""
        env_lower = self.environment.lower()
        
        if any(keyword in env_lower for keyword in ['prod', 'production']):
            return "production"
        elif any(keyword in env_lower for keyword in ['stag', 'staging']):
            return "staging"
        elif any(keyword in env_lower for keyword in ['dev', 'development']):
            return "development"
        elif any(keyword in env_lower for keyword in ['test', 'testing']):
            return "testing"
        else:
            return "custom"
    
    @property
    def is_production(self) -> bool:
        """Check if this is a production environment"""
        return self.environment_type == "production"
    
    @property
    def security_level(self) -> str:
        """Get security level based on environment type"""
        if self.is_production:
            return "high"
        elif self.environment_type == "staging":
            return "medium"
        else:
            return "low"
    
    def get_feature_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get feature flag value"""
        return self.feature_flags.get(flag_name, default)
    
    def set_feature_flag(self, flag_name: str, enabled: bool, updated_by: Optional[str] = None):
        """Set feature flag value"""
        self.feature_flags[flag_name] = enabled
        self.updated_at = datetime.now(timezone.utc)
        if updated_by:
            self.updated_by = updated_by
    
    def get_resource_limit(self, resource_type: str, default: Any = None) -> Any:
        """Get resource limit value"""
        return self.resource_limits.get(resource_type, default)
    
    def set_resource_limit(self, resource_type: str, limit: Any, updated_by: Optional[str] = None):
        """Set resource limit"""
        self.resource_limits[resource_type] = limit
        self.updated_at = datetime.now(timezone.utc)
        if updated_by:
            self.updated_by = updated_by
    
    def validate_environment(self) -> List[str]:
        """Validate environment configuration"""
        issues = []
        
        if not self.environment:
            issues.append("Environment name is required")
        
        # Environment name validation
        if self.environment not in ["development", "staging", "production", "testing"]:
            if not self.environment.replace("_", "").replace("-", "").isalnum():
                issues.append("Environment name should contain only alphanumeric characters, hyphens, and underscores")
        
        # Production environment specific validations
        if self.is_production:
            required_security_settings = ["authentication_required", "encryption_enabled", "audit_logging"]
            for setting in required_security_settings:
                if setting not in self.security_settings:
                    issues.append(f"Production environment missing required security setting: {setting}")
        
        return issues

@dataclass
class ConfigAuditLog:
    """
    Configuration audit log model
    
    Tracks all configuration changes for compliance, debugging,
    and security auditing purposes.
    """
    audit_id: str
    config_id: str
    config_key: str
    action: str  # create, update, delete, read, activate, deactivate
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    change_reason: Optional[str] = None
    approval_status: Optional[str] = None  # pending, approved, rejected
    approved_by: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    risk_level: str = "low"  # low, medium, high, critical
    compliance_flags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.compliance_flags is None:
            self.compliance_flags = []
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_sensitive_change(self) -> bool:
        """Check if this represents a sensitive configuration change"""
        sensitive_keys = ['api_key', 'password', 'secret', 'token', 'private_key']
        sensitive_actions = ['create', 'update', 'delete']
        
        return (self.action in sensitive_actions and
                any(keyword in self.config_key.lower() for keyword in sensitive_keys))
    
    @property
    def requires_approval(self) -> bool:
        """Check if change requires approval"""
        return (self.risk_level in ["high", "critical"] or
                self.is_sensitive_change or
                self.action == "delete")
    
    @property
    def is_approved(self) -> bool:
        """Check if change is approved"""
        return self.approval_status == "approved"
    
    @property
    def change_summary(self) -> str:
        """Generate human-readable change summary"""
        action_descriptions = {
            "create": "created",
            "update": "updated", 
            "delete": "deleted",
            "read": "accessed",
            "activate": "activated",
            "deactivate": "deactivated"
        }
        
        action_desc = action_descriptions.get(self.action, self.action)
        return f"Configuration '{self.config_key}' was {action_desc}"
    
    def add_compliance_flag(self, flag: str):
        """Add compliance flag"""
        if flag not in self.compliance_flags:
            self.compliance_flags.append(flag)
    
    def approve_change(self, approved_by: str, approval_reason: Optional[str] = None):
        """Approve the configuration change"""
        self.approval_status = "approved"
        self.approved_by = approved_by
        self.approval_timestamp = datetime.now(timezone.utc)
        
        if approval_reason:
            self.metadata["approval_reason"] = approval_reason
    
    def reject_change(self, rejected_by: str, rejection_reason: Optional[str] = None):
        """Reject the configuration change"""
        self.approval_status = "rejected"
        self.approved_by = rejected_by
        self.approval_timestamp = datetime.now(timezone.utc)
        
        if rejection_reason:
            self.metadata["rejection_reason"] = rejection_reason

# Utility functions for working with configuration models

def create_config_record(
    config_key: str,
    config_value: Any,
    config_type: str = ConfigType.SYSTEM,
    environment: str = "production",
    created_by: Optional[str] = None,
    description: Optional[str] = None
) -> ConfigRecord:
    """Factory function to create a new configuration record"""
    import uuid
    
    config_id = f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    return ConfigRecord(
        config_id=config_id,
        config_type=config_type,
        config_key=config_key,
        config_value=config_value,
        environment=environment,
        created_by=created_by,
        description=description
    )

def create_provider_config(
    provider_name: str,
    config_data: Dict[str, Any],
    environment: str = "production",
    created_by: Optional[str] = None
) -> ProviderConfig:
    """Factory function to create a new provider configuration"""
    return ProviderConfig(
        provider_name=provider_name,
        config_data=config_data,
        environment=environment,
        created_by=created_by
    )

def create_environment_config(
    environment: str,
    config_data: Dict[str, Any],
    created_by: Optional[str] = None
) -> EnvironmentConfig:
    """Factory function to create a new environment configuration"""
    return EnvironmentConfig(
        environment=environment,
        config_data=config_data,
        created_by=created_by
    )

def create_audit_log(
    config_id: str,
    config_key: str,
    action: str,
    user_id: Optional[str] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
    change_reason: Optional[str] = None
) -> ConfigAuditLog:
    """Factory function to create a new audit log entry"""
    import uuid
    
    audit_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Determine risk level based on action and values
    risk_level = "low"
    if action in ["delete", "deactivate"]:
        risk_level = "high"
    elif action == "update" and old_value != new_value:
        risk_level = "medium"
    
    return ConfigAuditLog(
        audit_id=audit_id,
        config_id=config_id,
        config_key=config_key,
        action=action,
        old_value=old_value,
        new_value=new_value,
        user_id=user_id,
        change_reason=change_reason,
        risk_level=risk_level
    )