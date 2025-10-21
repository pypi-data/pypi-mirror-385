"""
Inference Configuration Models

Configuration models for inference operations, providing structured configuration
management for different providers, models, and inference parameters.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class LoadBalancingStrategy(str, Enum):
    """Load balancing strategy enumeration"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    FASTEST_RESPONSE = "fastest_response"
    RANDOM = "random"
    STICKY_SESSION = "sticky_session"

class RetryStrategy(str, Enum):
    """Retry strategy enumeration"""
    NONE = "none"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_INTERVAL = "fixed_interval"
    IMMEDIATE = "immediate"

class CachingStrategy(str, Enum):
    """Caching strategy enumeration"""
    NONE = "none"
    LRU = "lru"
    TTL = "ttl"
    SEMANTIC = "semantic"
    PROBABILISTIC = "probabilistic"

@dataclass
class ProviderConfig:
    """
    Provider-specific configuration
    
    Contains provider-specific settings, authentication, and limits.
    """
    provider_name: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    organization_id: Optional[str] = None
    project_id: Optional[str] = None
    region: Optional[str] = None
    api_version: Optional[str] = None
    timeout_seconds: int = 300
    max_retries: int = 3
    retry_strategy: str = RetryStrategy.EXPONENTIAL_BACKOFF
    rate_limit_rpm: Optional[int] = None  # requests per minute
    rate_limit_tpm: Optional[int] = None  # tokens per minute
    concurrent_requests: int = 10
    enable_streaming: bool = True
    custom_headers: Optional[Dict[str, str]] = None
    proxy_config: Optional[Dict[str, str]] = None
    ssl_verify: bool = True
    connection_pool_size: int = 100
    keepalive_timeout: int = 30
    user_agent: Optional[str] = None
    
    def __post_init__(self):
        if self.custom_headers is None:
            self.custom_headers = {}
        if self.proxy_config is None:
            self.proxy_config = {}
    
    @property
    def is_configured(self) -> bool:
        """Check if provider is properly configured"""
        return bool(self.provider_name and (self.api_key or self.base_url))
    
    @property
    def has_rate_limits(self) -> bool:
        """Check if rate limits are configured"""
        return self.rate_limit_rpm is not None or self.rate_limit_tpm is not None
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests"""
        headers = {}
        
        if self.api_key:
            if self.provider_name.lower() == "openai":
                headers["Authorization"] = f"Bearer {self.api_key}"
            elif self.provider_name.lower() == "anthropic":
                headers["x-api-key"] = self.api_key
            elif self.provider_name.lower() == "replicate":
                headers["Authorization"] = f"Token {self.api_key}"
            else:
                headers["Authorization"] = f"Bearer {self.api_key}"
        
        if self.organization_id:
            if self.provider_name.lower() == "openai":
                headers["OpenAI-Organization"] = self.organization_id
        
        if self.project_id:
            if self.provider_name.lower() == "openai":
                headers["OpenAI-Project"] = self.project_id
        
        # Add custom headers
        headers.update(self.custom_headers)
        
        return headers
    
    def get_request_timeout(self, model_type: str = "llm") -> int:
        """Get appropriate timeout for model type"""
        # Different model types may need different timeouts
        multipliers = {
            "vision": 2.0,
            "image_gen": 5.0,
            "audio": 3.0,
            "embedding": 0.5,
            "llm": 1.0
        }
        
        multiplier = multipliers.get(model_type, 1.0)
        return int(self.timeout_seconds * multiplier)
    
    def calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay based on strategy"""
        if self.retry_strategy == RetryStrategy.NONE:
            return 0
        elif self.retry_strategy == RetryStrategy.IMMEDIATE:
            return 0
        elif self.retry_strategy == RetryStrategy.FIXED_INTERVAL:
            return 1.0
        elif self.retry_strategy == RetryStrategy.LINEAR_BACKOFF:
            return attempt * 1.0
        elif self.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return min(60, (2 ** attempt) + (attempt * 0.1))
        
        return 1.0

@dataclass
class ModelConfig:
    """
    Model-specific configuration
    
    Defines model parameters, inference settings, and optimization options.
    """
    model_id: str
    model_name: Optional[str] = None
    model_type: str = "llm"  # llm, vision, audio, embedding, etc.
    provider: Optional[str] = None
    endpoint_path: Optional[str] = None
    
    # Generation parameters
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop_sequences: Optional[List[str]] = None
    
    # Context and formatting
    context_length: Optional[int] = None
    system_message: Optional[str] = None
    prompt_template: Optional[str] = None
    response_format: Optional[str] = None  # "text", "json", "structured"
    
    # Performance settings
    batch_size: int = 1
    streaming: bool = False
    use_cache: bool = True
    cache_ttl_seconds: int = 3600
    
    # Cost and usage controls
    max_cost_per_request: Optional[float] = None
    max_tokens_per_minute: Optional[int] = None
    priority: int = 5  # 1-10 scale
    
    # Advanced settings
    logit_bias: Optional[Dict[str, float]] = None
    seed: Optional[int] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None
    
    def __post_init__(self):
        if self.stop_sequences is None:
            self.stop_sequences = []
        if self.logit_bias is None:
            self.logit_bias = {}
        if self.tools is None:
            self.tools = []
    
    @property
    def supports_streaming(self) -> bool:
        """Check if model supports streaming"""
        return self.streaming and self.model_type in ["llm", "vision"]
    
    @property
    def supports_tools(self) -> bool:
        """Check if model supports function calling"""
        return bool(self.tools) and self.model_type == "llm"
    
    @property
    def estimated_cost_per_1k_tokens(self) -> float:
        """Estimate cost per 1000 tokens (would be provider/model specific)"""
        # This would be loaded from a pricing database in practice
        cost_map = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "claude-3-opus": 0.015,
            "claude-3-sonnet": 0.003,
            "gemini-pro": 0.001
        }
        
        # Simple heuristic based on model name
        for model_prefix, cost in cost_map.items():
            if model_prefix in self.model_id.lower():
                return cost
        
        return 0.01  # Default estimate
    
    def estimate_request_cost(self, input_tokens: int, output_tokens: int = 0) -> float:
        """Estimate cost for a request"""
        total_tokens = input_tokens + output_tokens
        cost_per_1k = self.estimated_cost_per_1k_tokens
        return (total_tokens / 1000) * cost_per_1k
    
    def validate_parameters(self) -> List[str]:
        """Validate model parameters"""
        issues = []
        
        if not self.model_id:
            issues.append("Model ID is required")
        
        if self.temperature is not None and (self.temperature < 0 or self.temperature > 2):
            issues.append("Temperature must be between 0 and 2")
        
        if self.top_p is not None and (self.top_p < 0 or self.top_p > 1):
            issues.append("Top-p must be between 0 and 1")
        
        if self.max_tokens is not None and self.max_tokens < 1:
            issues.append("Max tokens must be positive")
        
        if self.batch_size < 1:
            issues.append("Batch size must be at least 1")
        
        if self.priority < 1 or self.priority > 10:
            issues.append("Priority must be between 1 and 10")
        
        return issues
    
    def get_generation_params(self) -> Dict[str, Any]:
        """Get generation parameters for API calls"""
        params = {}
        
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.top_p is not None:
            params["top_p"] = self.top_p
        if self.top_k is not None:
            params["top_k"] = self.top_k
        if self.frequency_penalty is not None:
            params["frequency_penalty"] = self.frequency_penalty
        if self.presence_penalty is not None:
            params["presence_penalty"] = self.presence_penalty
        if self.stop_sequences:
            params["stop"] = self.stop_sequences
        if self.seed is not None:
            params["seed"] = self.seed
        if self.logit_bias:
            params["logit_bias"] = self.logit_bias
        if self.tools:
            params["tools"] = self.tools
        if self.tool_choice:
            params["tool_choice"] = self.tool_choice
        
        return params
    
    def update_from_request(self, request_params: Dict[str, Any]):
        """Update config from request parameters"""
        for key, value in request_params.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)

@dataclass
class InferenceConfig:
    """
    Complete inference configuration
    
    Combines provider, model, and execution settings for inference operations.
    """
    config_id: Optional[str] = None
    config_name: Optional[str] = None
    provider_config: Optional[ProviderConfig] = None
    model_config: Optional[ModelConfig] = None
    
    # Load balancing and failover
    load_balancing: str = LoadBalancingStrategy.ROUND_ROBIN
    failover_providers: Optional[List[str]] = None
    failover_models: Optional[List[str]] = None
    auto_fallback: bool = True
    
    # Caching configuration
    caching_strategy: str = CachingStrategy.LRU
    cache_size_mb: int = 1024
    cache_ttl_seconds: int = 3600
    semantic_cache_threshold: float = 0.95
    
    # Queue and throttling
    queue_max_size: int = 1000
    queue_timeout_seconds: int = 300
    throttle_requests_per_second: Optional[float] = None
    
    # Monitoring and logging
    enable_metrics: bool = True
    enable_detailed_logging: bool = False
    log_request_data: bool = False
    log_response_data: bool = False
    track_token_usage: bool = True
    
    # Security settings
    input_sanitization: bool = True
    output_filtering: bool = False
    content_moderation: bool = False
    pii_detection: bool = False
    
    # Optimization settings
    batch_processing: bool = False
    connection_pooling: bool = True
    request_compression: bool = True
    response_compression: bool = True
    
    created_at: datetime = None
    updated_at: datetime = None
    created_by: Optional[str] = None
    is_active: bool = True
    tags: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.failover_providers is None:
            self.failover_providers = []
        if self.failover_models is None:
            self.failover_models = []
        if self.tags is None:
            self.tags = {}
    
    @property
    def primary_provider(self) -> Optional[str]:
        """Get primary provider name"""
        return self.provider_config.provider_name if self.provider_config else None
    
    @property
    def primary_model(self) -> Optional[str]:
        """Get primary model ID"""
        return self.model_config.model_id if self.model_config else None
    
    @property
    def has_failover(self) -> bool:
        """Check if failover is configured"""
        return bool(self.failover_providers or self.failover_models)
    
    @property
    def supports_batching(self) -> bool:
        """Check if batching is enabled and supported"""
        return (self.batch_processing and 
                self.model_config and 
                self.model_config.batch_size > 1)
    
    @property
    def cache_enabled(self) -> bool:
        """Check if caching is enabled"""
        return self.caching_strategy != CachingStrategy.NONE
    
    def validate(self) -> List[str]:
        """Validate complete configuration"""
        issues = []
        
        if not self.provider_config:
            issues.append("Provider configuration is required")
        elif not self.provider_config.is_configured:
            issues.append("Provider configuration is incomplete")
        
        if not self.model_config:
            issues.append("Model configuration is required")
        else:
            issues.extend([f"Model: {issue}" for issue in self.model_config.validate_parameters()])
        
        if self.cache_size_mb < 1:
            issues.append("Cache size must be at least 1 MB")
        
        if self.queue_max_size < 1:
            issues.append("Queue max size must be positive")
        
        if self.throttle_requests_per_second is not None and self.throttle_requests_per_second <= 0:
            issues.append("Throttle rate must be positive")
        
        return issues
    
    def get_effective_timeout(self) -> int:
        """Get effective timeout considering provider and model settings"""
        if not self.provider_config or not self.model_config:
            return 300  # Default 5 minutes
        
        return self.provider_config.get_request_timeout(self.model_config.model_type)
    
    def get_cache_key(self, request_data: Dict[str, Any]) -> str:
        """Generate cache key for request"""
        import hashlib
        import json
        
        # Include model and key request parameters in cache key
        cache_data = {
            "model_id": self.primary_model,
            "provider": self.primary_provider,
            "request": request_data
        }
        
        # Add relevant model parameters
        if self.model_config:
            for param in ["temperature", "max_tokens", "top_p", "top_k"]:
                value = getattr(self.model_config, param, None)
                if value is not None:
                    cache_data[param] = value
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()[:32]
    
    def should_use_failover(self, error_type: str, attempt_count: int) -> bool:
        """Determine if failover should be used"""
        if not self.auto_fallback or not self.has_failover:
            return False
        
        # Failover conditions
        failover_errors = ["timeout", "rate_limit", "server_error", "model_error"]
        max_attempts = 3
        
        return (error_type in failover_errors and 
                attempt_count >= max_attempts)
    
    def get_next_failover_option(self, current_provider: str, current_model: str) -> Optional[Dict[str, str]]:
        """Get next failover provider/model combination"""
        # Simple round-robin failover
        if self.failover_providers:
            try:
                current_index = self.failover_providers.index(current_provider)
                next_index = (current_index + 1) % len(self.failover_providers)
                return {"provider": self.failover_providers[next_index], "model": current_model}
            except ValueError:
                if self.failover_providers:
                    return {"provider": self.failover_providers[0], "model": current_model}
        
        if self.failover_models:
            try:
                current_index = self.failover_models.index(current_model)
                next_index = (current_index + 1) % len(self.failover_models)
                return {"provider": current_provider, "model": self.failover_models[next_index]}
            except ValueError:
                if self.failover_models:
                    return {"provider": current_provider, "model": self.failover_models[0]}
        
        return None
    
    def merge_with(self, other: 'InferenceConfig') -> 'InferenceConfig':
        """Merge this configuration with another"""
        merged = InferenceConfig()
        
        # Copy all fields from self
        for field_name in self.__dataclass_fields__:
            setattr(merged, field_name, getattr(self, field_name))
        
        # Override with non-None values from other
        for field_name in other.__dataclass_fields__:
            other_value = getattr(other, field_name)
            if other_value is not None:
                setattr(merged, field_name, other_value)
        
        merged.updated_at = datetime.now(timezone.utc)
        return merged

# Factory functions for common configurations

def create_openai_config(
    api_key: str,
    model_id: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> InferenceConfig:
    """Create OpenAI inference configuration"""
    return InferenceConfig(
        provider_config=ProviderConfig(
            provider_name="openai",
            base_url="https://api.openai.com/v1",
            api_key=api_key,
            timeout_seconds=120,
            max_retries=3
        ),
        model_config=ModelConfig(
            model_id=model_id,
            model_type="llm",
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True
        )
    )

def create_anthropic_config(
    api_key: str,
    model_id: str = "claude-3-sonnet-20240229",
    max_tokens: int = 1000
) -> InferenceConfig:
    """Create Anthropic inference configuration"""
    return InferenceConfig(
        provider_config=ProviderConfig(
            provider_name="anthropic",
            base_url="https://api.anthropic.com",
            api_key=api_key,
            api_version="2023-06-01",
            timeout_seconds=180
        ),
        model_config=ModelConfig(
            model_id=model_id,
            model_type="llm",
            max_tokens=max_tokens
        )
    )

def create_multi_provider_config(
    configs: List[InferenceConfig],
    load_balancing: str = LoadBalancingStrategy.ROUND_ROBIN
) -> InferenceConfig:
    """Create multi-provider configuration with failover"""
    if not configs:
        raise ValueError("At least one configuration is required")
    
    primary = configs[0]
    failover_providers = [config.primary_provider for config in configs[1:] if config.primary_provider]
    
    return InferenceConfig(
        provider_config=primary.provider_config,
        model_config=primary.model_config,
        load_balancing=load_balancing,
        failover_providers=failover_providers,
        auto_fallback=True
    )