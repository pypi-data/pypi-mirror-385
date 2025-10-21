"""
Model Metadata Models

Data models for model metadata, versioning, and billing information,
following the ISA Model architecture pattern.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class ModelStatus(str, Enum):
    """Model status enumeration"""
    DRAFT = "draft"
    TRAINING = "training"
    VALIDATING = "validating"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    FAILED = "failed"

class ModelType(str, Enum):
    """Model type enumeration"""
    LLM = "llm"
    VISION = "vision"
    AUDIO = "audio"
    EMBEDDING = "embedding"
    MULTIMODAL = "multimodal"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    GENERATIVE = "generative"
    CUSTOM = "custom"

class BillingModel(str, Enum):
    """Billing model enumeration"""
    PAY_PER_USE = "pay_per_use"
    SUBSCRIPTION = "subscription"
    TIER_BASED = "tier_based"
    FREE = "free"
    CUSTOM = "custom"

class LicenseType(str, Enum):
    """License type enumeration"""
    OPEN_SOURCE = "open_source"
    COMMERCIAL = "commercial"
    ACADEMIC = "academic"
    PROPRIETARY = "proprietary"
    CUSTOM = "custom"

@dataclass
class ModelMetadata:
    """
    Comprehensive model metadata
    
    Contains all metadata about a model including its capabilities,
    performance characteristics, usage information, and billing details.
    """
    model_id: str
    model_name: str
    model_type: str
    provider: str
    status: str = ModelStatus.DRAFT
    version: str = "1.0.0"
    description: Optional[str] = None
    
    # Model characteristics
    capabilities: Optional[List[str]] = None
    supported_languages: Optional[List[str]] = None
    context_length: Optional[int] = None
    parameter_count: Optional[int] = None
    training_data_size: Optional[str] = None
    training_completion_date: Optional[datetime] = None
    
    # Performance metrics
    benchmark_scores: Optional[Dict[str, float]] = None
    latency_ms: Optional[float] = None
    throughput_tokens_per_second: Optional[float] = None
    accuracy_metrics: Optional[Dict[str, float]] = None
    
    # Usage and availability
    is_public: bool = False
    requires_approval: bool = False
    max_concurrent_requests: Optional[int] = None
    rate_limits: Optional[Dict[str, Any]] = None
    geographic_restrictions: Optional[List[str]] = None
    
    # Billing and cost
    billing_model: str = BillingModel.PAY_PER_USE
    cost_per_1k_input_tokens: Optional[float] = None
    cost_per_1k_output_tokens: Optional[float] = None
    cost_per_request: Optional[float] = None
    monthly_subscription_cost: Optional[float] = None
    free_tier_limits: Optional[Dict[str, Any]] = None
    
    # Legal and compliance
    license_type: str = LicenseType.PROPRIETARY
    license_url: Optional[str] = None
    terms_of_service_url: Optional[str] = None
    privacy_policy_url: Optional[str] = None
    compliance_certifications: Optional[List[str]] = None
    data_residency_requirements: Optional[List[str]] = None
    
    # Technical details
    supported_formats: Optional[List[str]] = None
    input_modalities: Optional[List[str]] = None
    output_modalities: Optional[List[str]] = None
    api_endpoints: Optional[Dict[str, str]] = None
    sdk_availability: Optional[Dict[str, str]] = None
    documentation_url: Optional[str] = None
    
    # Metadata
    created_at: datetime = None
    updated_at: datetime = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    custom_metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.capabilities is None:
            self.capabilities = []
        if self.supported_languages is None:
            self.supported_languages = []
        if self.benchmark_scores is None:
            self.benchmark_scores = {}
        if self.accuracy_metrics is None:
            self.accuracy_metrics = {}
        if self.rate_limits is None:
            self.rate_limits = {}
        if self.geographic_restrictions is None:
            self.geographic_restrictions = []
        if self.free_tier_limits is None:
            self.free_tier_limits = {}
        if self.compliance_certifications is None:
            self.compliance_certifications = []
        if self.data_residency_requirements is None:
            self.data_residency_requirements = []
        if self.supported_formats is None:
            self.supported_formats = []
        if self.input_modalities is None:
            self.input_modalities = []
        if self.output_modalities is None:
            self.output_modalities = []
        if self.api_endpoints is None:
            self.api_endpoints = {}
        if self.sdk_availability is None:
            self.sdk_availability = {}
        if self.tags is None:
            self.tags = {}
        if self.custom_metadata is None:
            self.custom_metadata = {}
    
    @property
    def is_active(self) -> bool:
        """Check if model is active and available"""
        return self.status == ModelStatus.ACTIVE
    
    @property
    def is_multimodal(self) -> bool:
        """Check if model supports multiple modalities"""
        return len(self.input_modalities) > 1 or len(self.output_modalities) > 1
    
    @property
    def supports_streaming(self) -> bool:
        """Check if model supports streaming responses"""
        return "streaming" in self.capabilities
    
    @property
    def supports_function_calling(self) -> bool:
        """Check if model supports function calling"""
        return "function_calling" in self.capabilities or "tools" in self.capabilities
    
    @property
    def model_size_category(self) -> str:
        """Categorize model size based on parameter count"""
        if not self.parameter_count:
            return "unknown"
        
        if self.parameter_count < 1_000_000:  # < 1M
            return "small"
        elif self.parameter_count < 10_000_000:  # < 10M
            return "medium"
        elif self.parameter_count < 100_000_000:  # < 100M
            return "large"
        elif self.parameter_count < 1_000_000_000:  # < 1B
            return "very_large"
        else:  # >= 1B
            return "massive"
    
    @property
    def estimated_cost_per_request(self) -> float:
        """Estimate cost per request based on billing model"""
        if self.billing_model == BillingModel.FREE:
            return 0.0
        
        if self.cost_per_request:
            return self.cost_per_request
        
        # Estimate based on token costs (assume average 1000 tokens per request)
        if self.cost_per_1k_input_tokens and self.cost_per_1k_output_tokens:
            return (self.cost_per_1k_input_tokens + self.cost_per_1k_output_tokens) / 2
        elif self.cost_per_1k_input_tokens:
            return self.cost_per_1k_input_tokens
        
        return 0.01  # Default estimate
    
    @property
    def performance_tier(self) -> str:
        """Classify model performance tier"""
        if not self.benchmark_scores:
            return "unknown"
        
        # Calculate average benchmark score
        scores = [score for score in self.benchmark_scores.values() if isinstance(score, (int, float))]
        if not scores:
            return "unknown"
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 90:
            return "excellent"
        elif avg_score >= 80:
            return "good"
        elif avg_score >= 70:
            return "average"
        elif avg_score >= 60:
            return "below_average"
        else:
            return "poor"
    
    def add_capability(self, capability: str):
        """Add a model capability"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.updated_at = datetime.now(timezone.utc)
    
    def add_benchmark_score(self, benchmark_name: str, score: float):
        """Add or update a benchmark score"""
        self.benchmark_scores[benchmark_name] = score
        self.updated_at = datetime.now(timezone.utc)
    
    def update_status(self, new_status: str, updated_by: Optional[str] = None):
        """Update model status"""
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)
        if updated_by:
            self.updated_by = updated_by
    
    def calculate_usage_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for specific token usage"""
        total_cost = 0.0
        
        if self.cost_per_1k_input_tokens:
            total_cost += (input_tokens / 1000) * self.cost_per_1k_input_tokens
        
        if self.cost_per_1k_output_tokens:
            total_cost += (output_tokens / 1000) * self.cost_per_1k_output_tokens
        
        return total_cost
    
    def check_rate_limit_compliance(self, requests_per_minute: int, tokens_per_minute: int) -> bool:
        """Check if usage complies with rate limits"""
        if "requests_per_minute" in self.rate_limits:
            if requests_per_minute > self.rate_limits["requests_per_minute"]:
                return False
        
        if "tokens_per_minute" in self.rate_limits:
            if tokens_per_minute > self.rate_limits["tokens_per_minute"]:
                return False
        
        return True
    
    def validate_metadata(self) -> List[str]:
        """Validate model metadata completeness and consistency"""
        issues = []
        
        if not self.model_id:
            issues.append("Model ID is required")
        
        if not self.model_name:
            issues.append("Model name is required")
        
        if not self.provider:
            issues.append("Provider is required")
        
        # Billing validation
        if self.billing_model == BillingModel.PAY_PER_USE:
            if not (self.cost_per_1k_input_tokens or self.cost_per_1k_output_tokens or self.cost_per_request):
                issues.append("Pay-per-use billing requires cost information")
        
        if self.billing_model == BillingModel.SUBSCRIPTION:
            if not self.monthly_subscription_cost:
                issues.append("Subscription billing requires monthly cost")
        
        # Performance validation
        if self.latency_ms and self.latency_ms < 0:
            issues.append("Latency cannot be negative")
        
        if self.parameter_count and self.parameter_count < 0:
            issues.append("Parameter count cannot be negative")
        
        # Context length validation
        if self.context_length and self.context_length < 1:
            issues.append("Context length must be positive")
        
        return issues

@dataclass
class ModelVersion:
    """
    Model version information
    
    Tracks different versions of a model with their specific characteristics
    and deployment information.
    """
    version_id: str
    model_id: str
    version_number: str
    is_current: bool = False
    is_deprecated: bool = False
    release_date: Optional[datetime] = None
    deprecation_date: Optional[datetime] = None
    end_of_life_date: Optional[datetime] = None
    
    # Version-specific details
    changes_from_previous: Optional[List[str]] = None
    performance_improvements: Optional[Dict[str, float]] = None
    bug_fixes: Optional[List[str]] = None
    new_features: Optional[List[str]] = None
    breaking_changes: Optional[List[str]] = None
    
    # Technical specifications for this version
    model_file_url: Optional[str] = None
    model_file_size_gb: Optional[float] = None
    model_file_checksum: Optional[str] = None
    docker_image: Optional[str] = None
    deployment_config: Optional[Dict[str, Any]] = None
    
    # Compatibility and requirements
    minimum_hardware_requirements: Optional[Dict[str, Any]] = None
    supported_frameworks: Optional[List[str]] = None
    python_version_requirements: Optional[str] = None
    dependencies: Optional[List[str]] = None
    
    created_at: datetime = None
    created_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.changes_from_previous is None:
            self.changes_from_previous = []
        if self.performance_improvements is None:
            self.performance_improvements = {}
        if self.bug_fixes is None:
            self.bug_fixes = []
        if self.new_features is None:
            self.new_features = []
        if self.breaking_changes is None:
            self.breaking_changes = []
        if self.supported_frameworks is None:
            self.supported_frameworks = []
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_active(self) -> bool:
        """Check if version is active (not deprecated and within lifecycle)"""
        now = datetime.now(timezone.utc)
        
        if self.is_deprecated:
            return False
        
        if self.end_of_life_date and now > self.end_of_life_date:
            return False
        
        return True
    
    @property
    def lifecycle_stage(self) -> str:
        """Get current lifecycle stage"""
        now = datetime.now(timezone.utc)
        
        if self.end_of_life_date and now > self.end_of_life_date:
            return "end_of_life"
        elif self.deprecation_date and now > self.deprecation_date:
            return "deprecated"
        elif self.is_current:
            return "current"
        else:
            return "legacy"
    
    @property
    def has_breaking_changes(self) -> bool:
        """Check if version introduces breaking changes"""
        return len(self.breaking_changes) > 0
    
    def add_change(self, change_type: str, description: str):
        """Add a change description"""
        if change_type == "improvement":
            self.changes_from_previous.append(f"Improvement: {description}")
        elif change_type == "bug_fix":
            self.bug_fixes.append(description)
        elif change_type == "new_feature":
            self.new_features.append(description)
        elif change_type == "breaking_change":
            self.breaking_changes.append(description)
    
    def deprecate(self, deprecation_date: Optional[datetime] = None, 
                 end_of_life_date: Optional[datetime] = None):
        """Mark version as deprecated"""
        self.is_deprecated = True
        self.deprecation_date = deprecation_date or datetime.now(timezone.utc)
        
        if end_of_life_date:
            self.end_of_life_date = end_of_life_date

@dataclass
class ModelBilling:
    """
    Model billing and usage tracking
    
    Tracks billing information, usage patterns, and cost analytics
    for model usage across different time periods and users.
    """
    billing_id: str
    model_id: str
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    billing_period_start: datetime = None
    billing_period_end: datetime = None
    
    # Usage metrics
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_processing_time_ms: int = 0
    unique_users: int = 0
    
    # Cost breakdown
    input_token_cost: float = 0.0
    output_token_cost: float = 0.0
    request_cost: float = 0.0
    subscription_cost: float = 0.0
    overage_charges: float = 0.0
    discounts_applied: float = 0.0
    taxes: float = 0.0
    total_cost: float = 0.0
    
    # Billing status
    billing_status: str = "active"  # active, suspended, overdue, paid
    last_payment_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    
    # Cost analytics
    cost_per_request: float = 0.0
    cost_per_token: float = 0.0
    cost_per_minute: float = 0.0
    daily_average_cost: float = 0.0
    projected_monthly_cost: float = 0.0
    
    # Usage analytics
    avg_requests_per_day: float = 0.0
    avg_tokens_per_request: float = 0.0
    peak_usage_hour: Optional[int] = None
    usage_trend: str = "stable"  # growing, stable, declining
    
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at
        
        # Calculate derived metrics
        self._calculate_derived_metrics()
    
    def _calculate_derived_metrics(self):
        """Calculate derived billing and usage metrics"""
        # Cost analytics
        if self.total_requests > 0:
            self.cost_per_request = self.total_cost / self.total_requests
        
        total_tokens = self.total_input_tokens + self.total_output_tokens
        if total_tokens > 0:
            self.cost_per_token = self.total_cost / total_tokens
            self.avg_tokens_per_request = total_tokens / self.total_requests if self.total_requests > 0 else 0
        
        if self.total_processing_time_ms > 0:
            processing_minutes = self.total_processing_time_ms / (1000 * 60)
            self.cost_per_minute = self.total_cost / processing_minutes
        
        # Period-based analytics
        if self.billing_period_start and self.billing_period_end:
            period_days = (self.billing_period_end - self.billing_period_start).days
            if period_days > 0:
                self.daily_average_cost = self.total_cost / period_days
                self.avg_requests_per_day = self.total_requests / period_days
                
                # Project monthly cost based on current usage
                self.projected_monthly_cost = self.daily_average_cost * 30
    
    @property
    def billing_period_days(self) -> int:
        """Get billing period duration in days"""
        if self.billing_period_start and self.billing_period_end:
            return (self.billing_period_end - self.billing_period_start).days
        return 0
    
    @property
    def is_over_budget(self) -> bool:
        """Check if costs exceed typical thresholds (would be configurable)"""
        # This would be based on user-defined budgets
        return self.projected_monthly_cost > 1000  # Example threshold
    
    @property
    def efficiency_score(self) -> float:
        """Calculate cost efficiency score (0-100)"""
        if self.cost_per_token == 0:
            return 100.0
        
        # Compare to industry benchmarks (simplified)
        benchmark_cost_per_token = 0.002  # Example benchmark
        efficiency = min(100, (benchmark_cost_per_token / self.cost_per_token) * 100)
        return max(0, efficiency)
    
    @property
    def usage_intensity(self) -> str:
        """Classify usage intensity"""
        if self.avg_requests_per_day < 10:
            return "light"
        elif self.avg_requests_per_day < 100:
            return "moderate"
        elif self.avg_requests_per_day < 1000:
            return "heavy"
        else:
            return "intensive"
    
    def add_usage(self, requests: int = 0, input_tokens: int = 0, output_tokens: int = 0,
                 processing_time_ms: int = 0, cost: float = 0.0):
        """Add usage data to billing record"""
        self.total_requests += requests
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_processing_time_ms += processing_time_ms
        self.total_cost += cost
        
        # Recalculate derived metrics
        self._calculate_derived_metrics()
        self.updated_at = datetime.now(timezone.utc)
    
    def apply_discount(self, discount_amount: float, reason: str = ""):
        """Apply discount to billing"""
        self.discounts_applied += discount_amount
        self.total_cost = max(0, self.total_cost - discount_amount)
        self.updated_at = datetime.now(timezone.utc)
    
    def process_payment(self, payment_amount: float, payment_method: str):
        """Record payment processing"""
        self.last_payment_date = datetime.now(timezone.utc)
        self.payment_method = payment_method
        
        if payment_amount >= self.total_cost:
            self.billing_status = "paid"
        
        self.updated_at = datetime.now(timezone.utc)
    
    def generate_billing_summary(self) -> Dict[str, Any]:
        """Generate comprehensive billing summary"""
        return {
            "billing_period": {
                "start": self.billing_period_start.isoformat() if self.billing_period_start else None,
                "end": self.billing_period_end.isoformat() if self.billing_period_end else None,
                "days": self.billing_period_days
            },
            "usage_summary": {
                "total_requests": self.total_requests,
                "total_tokens": self.total_input_tokens + self.total_output_tokens,
                "avg_requests_per_day": round(self.avg_requests_per_day, 2),
                "avg_tokens_per_request": round(self.avg_tokens_per_request, 2),
                "usage_intensity": self.usage_intensity
            },
            "cost_breakdown": {
                "input_token_cost": round(self.input_token_cost, 4),
                "output_token_cost": round(self.output_token_cost, 4),
                "request_cost": round(self.request_cost, 4),
                "subscription_cost": round(self.subscription_cost, 4),
                "overage_charges": round(self.overage_charges, 4),
                "discounts_applied": round(self.discounts_applied, 4),
                "taxes": round(self.taxes, 4),
                "total_cost": round(self.total_cost, 4)
            },
            "analytics": {
                "cost_per_request": round(self.cost_per_request, 6),
                "cost_per_token": round(self.cost_per_token, 8),
                "efficiency_score": round(self.efficiency_score, 2),
                "projected_monthly_cost": round(self.projected_monthly_cost, 2),
                "usage_trend": self.usage_trend
            },
            "billing_status": {
                "status": self.billing_status,
                "last_payment_date": self.last_payment_date.isoformat() if self.last_payment_date else None,
                "next_billing_date": self.next_billing_date.isoformat() if self.next_billing_date else None,
                "is_over_budget": self.is_over_budget
            }
        }

# Utility functions for working with model models

def create_model_metadata(
    model_id: str,
    model_name: str,
    model_type: str,
    provider: str,
    created_by: Optional[str] = None
) -> ModelMetadata:
    """Factory function to create model metadata"""
    return ModelMetadata(
        model_id=model_id,
        model_name=model_name,
        model_type=model_type,
        provider=provider,
        created_by=created_by
    )

def create_model_version(
    model_id: str,
    version_number: str,
    is_current: bool = False,
    created_by: Optional[str] = None
) -> ModelVersion:
    """Factory function to create model version"""
    import uuid
    
    version_id = f"version_{model_id}_{version_number}_{uuid.uuid4().hex[:8]}"
    
    return ModelVersion(
        version_id=version_id,
        model_id=model_id,
        version_number=version_number,
        is_current=is_current,
        created_by=created_by
    )

def create_model_billing(
    model_id: str,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    billing_period_start: Optional[datetime] = None,
    billing_period_end: Optional[datetime] = None
) -> ModelBilling:
    """Factory function to create model billing record"""
    import uuid
    
    billing_id = f"bill_{model_id}_{datetime.now().strftime('%Y%m')}_{uuid.uuid4().hex[:8]}"
    
    # Default to current month if no period specified
    if not billing_period_start:
        now = datetime.now(timezone.utc)
        billing_period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    if not billing_period_end:
        # End of current month
        import calendar
        now = datetime.now(timezone.utc)
        last_day = calendar.monthrange(now.year, now.month)[1]
        billing_period_end = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    
    return ModelBilling(
        billing_id=billing_id,
        model_id=model_id,
        user_id=user_id,
        organization_id=organization_id,
        billing_period_start=billing_period_start,
        billing_period_end=billing_period_end
    )