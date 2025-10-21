"""
Inference Record Models

Core data models for inference requests, usage statistics, and model snapshots,
extracted from repository layer to follow the standard ISA Model architecture pattern.
"""

import logging
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class InferenceStatus(str, Enum):
    """Inference status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    QUEUED = "queued"
    RETRYING = "retrying"

class ServiceType(str, Enum):
    """Service type enumeration"""
    LLM = "llm"
    VISION = "vision"
    EMBEDDING = "embedding"
    TTS = "tts"
    STT = "stt"
    IMAGE_GEN = "image_gen"
    AUDIO = "audio"
    RERANK = "rerank"
    OCR = "ocr"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"

class ErrorCategory(str, Enum):
    """Error category enumeration"""
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    MODEL_ERROR = "model_error"
    NETWORK_ERROR = "network_error"
    SERVER_ERROR = "server_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    UNKNOWN = "unknown"

@dataclass
class InferenceRequest:
    """
    Core inference request record
    
    Represents a single inference request with its input, output, performance metrics,
    and tracking information for analytics and billing purposes.
    """
    request_id: str
    service_type: str
    model_id: str
    provider: str
    endpoint: str
    request_data: Dict[str, Any]
    status: str = InferenceStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    client_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_category: Optional[str] = None
    execution_time_ms: Optional[int] = None
    queue_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None
    cache_hit: bool = False
    retry_count: int = 0
    priority: int = 5  # 1-10 scale
    request_hash: Optional[str] = None
    response_hash: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.metadata is None:
            self.metadata = {}
        
        # Generate request hash for deduplication
        if self.request_hash is None and self.request_data:
            self.request_hash = self._generate_content_hash(self.request_data)
    
    def _generate_content_hash(self, content: Any) -> str:
        """Generate consistent hash for content"""
        import json
        try:
            content_str = json.dumps(content, sort_keys=True, ensure_ascii=True)
            return hashlib.sha256(content_str.encode()).hexdigest()[:16]
        except Exception:
            return hashlib.sha256(str(content).encode()).hexdigest()[:16]
    
    @property
    def is_active(self) -> bool:
        """Check if request is in active processing state"""
        return self.status in [InferenceStatus.PENDING, InferenceStatus.PROCESSING, 
                              InferenceStatus.QUEUED, InferenceStatus.RETRYING]
    
    @property
    def is_completed(self) -> bool:
        """Check if request is completed (successfully or not)"""
        return self.status in [InferenceStatus.COMPLETED, InferenceStatus.FAILED, 
                              InferenceStatus.TIMEOUT, InferenceStatus.CANCELLED]
    
    @property
    def was_successful(self) -> bool:
        """Check if request completed successfully"""
        return self.status == InferenceStatus.COMPLETED
    
    @property
    def total_duration_ms(self) -> Optional[int]:
        """Calculate total request duration including queue time"""
        if self.created_at and self.completed_at:
            return int((self.completed_at - self.created_at).total_seconds() * 1000)
        return None
    
    @property
    def total_tokens(self) -> Optional[int]:
        """Get total tokens used (input + output)"""
        if self.input_tokens is not None and self.output_tokens is not None:
            return self.input_tokens + self.output_tokens
        return self.tokens_used
    
    @property
    def cost_per_token(self) -> Optional[float]:
        """Calculate cost per token"""
        total = self.total_tokens
        if self.cost_usd and total and total > 0:
            return self.cost_usd / total
        return None
    
    @property
    def throughput_tokens_per_second(self) -> Optional[float]:
        """Calculate token throughput"""
        total = self.total_tokens
        if total and self.execution_time_ms and self.execution_time_ms > 0:
            return (total * 1000) / self.execution_time_ms
        return None
    
    def update_status(self, new_status: str, error_message: Optional[str] = None, 
                     error_category: Optional[str] = None):
        """Update request status with timestamp tracking"""
        old_status = self.status
        self.status = new_status
        
        now = datetime.now(timezone.utc)
        
        if new_status == InferenceStatus.PROCESSING and old_status in [InferenceStatus.PENDING, InferenceStatus.QUEUED]:
            self.started_at = now
            if self.created_at:
                self.queue_time_ms = int((now - self.created_at).total_seconds() * 1000)
        
        elif new_status in [InferenceStatus.COMPLETED, InferenceStatus.FAILED, 
                           InferenceStatus.TIMEOUT, InferenceStatus.CANCELLED]:
            if not self.completed_at:
                self.completed_at = now
            
            if self.started_at:
                self.execution_time_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        
        if error_message:
            self.error_message = error_message
        if error_category:
            self.error_category = error_category
        
        logger.debug(f"Request {self.request_id} status: {old_status} -> {new_status}")
    
    def complete_request(self, response_data: Dict[str, Any], tokens_used: Optional[int] = None,
                        cost_usd: Optional[float] = None, **kwargs):
        """Mark request as completed with response data"""
        self.response_data = response_data
        self.response_hash = self._generate_content_hash(response_data)
        
        if tokens_used:
            self.tokens_used = tokens_used
        if cost_usd:
            self.cost_usd = cost_usd
        
        # Update any additional metrics
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.update_status(InferenceStatus.COMPLETED)
    
    def fail_request(self, error_message: str, error_category: str = ErrorCategory.UNKNOWN,
                    **kwargs):
        """Mark request as failed with error details"""
        self.error_message = error_message
        self.error_category = error_category
        
        # Update any additional error metrics
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.update_status(InferenceStatus.FAILED, error_message, error_category)
    
    def increment_retry(self):
        """Increment retry count and reset to retrying status"""
        self.retry_count += 1
        self.update_status(InferenceStatus.RETRYING)
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata entry"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata entry"""
        return self.metadata.get(key, default)

@dataclass
class UsageStatistics:
    """
    Aggregated usage statistics for analytics and billing
    
    Contains summarized metrics for a specific time period, service type,
    model, or user for reporting and analysis purposes.
    """
    stat_id: str
    period_start: datetime
    period_end: datetime
    service_type: str
    model_id: Optional[str] = None
    provider: Optional[str] = None
    user_id: Optional[str] = None
    client_id: Optional[str] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    retry_requests: int = 0
    cache_hits: int = 0
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_response_time_ms: float = 0.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    avg_queue_time_ms: float = 0.0
    requests_per_hour: float = 0.0
    tokens_per_hour: float = 0.0
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    cache_hit_rate: float = 0.0
    avg_tokens_per_request: float = 0.0
    cost_per_token: float = 0.0
    cost_per_request: float = 0.0
    throughput_tokens_per_second: float = 0.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        
        # Calculate derived metrics
        self._calculate_derived_metrics()
    
    def _calculate_derived_metrics(self):
        """Calculate derived metrics from base counts"""
        # Error and success rates
        if self.total_requests > 0:
            self.error_rate = (self.failed_requests / self.total_requests) * 100
            self.timeout_rate = (self.timeout_requests / self.total_requests) * 100
            self.cache_hit_rate = (self.cache_hits / self.total_requests) * 100
            self.cost_per_request = self.total_cost_usd / self.total_requests
        
        # Token metrics
        if self.total_tokens > 0:
            self.cost_per_token = self.total_cost_usd / self.total_tokens
        
        if self.successful_requests > 0:
            self.avg_tokens_per_request = self.total_tokens / self.successful_requests
        
        # Time-based metrics
        period_hours = (self.period_end - self.period_start).total_seconds() / 3600
        if period_hours > 0:
            self.requests_per_hour = self.total_requests / period_hours
            self.tokens_per_hour = self.total_tokens / period_hours
        
        # Throughput
        if self.avg_response_time_ms > 0:
            self.throughput_tokens_per_second = (self.avg_tokens_per_request * 1000) / self.avg_response_time_ms
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        return 100.0 - self.error_rate
    
    @property
    def period_duration_hours(self) -> float:
        """Get period duration in hours"""
        return (self.period_end - self.period_start).total_seconds() / 3600
    
    @property
    def efficiency_score(self) -> float:
        """Calculate efficiency score (0-100) based on performance metrics"""
        score = 100.0
        
        # Penalty for high error rates
        score -= self.error_rate
        
        # Penalty for high timeout rates
        score -= self.timeout_rate * 2  # Timeouts are worse than regular errors
        
        # Bonus for cache hits
        score += self.cache_hit_rate * 0.1
        
        # Penalty for slow responses (relative to service type)
        if self.avg_response_time_ms > 5000:  # 5+ seconds
            score -= 20
        elif self.avg_response_time_ms > 2000:  # 2+ seconds
            score -= 10
        elif self.avg_response_time_ms > 1000:  # 1+ seconds
            score -= 5
        
        return max(0.0, min(100.0, score))
    
    @property
    def performance_tier(self) -> str:
        """Get performance tier classification"""
        efficiency = self.efficiency_score
        
        if efficiency >= 90:
            return "excellent"
        elif efficiency >= 75:
            return "good"
        elif efficiency >= 60:
            return "average"
        elif efficiency >= 40:
            return "poor"
        else:
            return "critical"
    
    def add_request_data(self, request: InferenceRequest):
        """Add data from an individual request to the statistics"""
        self.total_requests += 1
        
        if request.was_successful:
            self.successful_requests += 1
            
            if request.total_tokens:
                self.total_tokens += request.total_tokens
            if request.input_tokens:
                self.input_tokens += request.input_tokens
            if request.output_tokens:
                self.output_tokens += request.output_tokens
            if request.cost_usd:
                self.total_cost_usd += request.cost_usd
        
        elif request.status == InferenceStatus.FAILED:
            self.failed_requests += 1
        elif request.status == InferenceStatus.TIMEOUT:
            self.timeout_requests += 1
        
        if request.retry_count > 0:
            self.retry_requests += 1
        
        if request.cache_hit:
            self.cache_hits += 1
        
        # Recalculate derived metrics
        self._calculate_derived_metrics()
    
    def merge_with(self, other: 'UsageStatistics') -> 'UsageStatistics':
        """Merge this statistics with another to create combined stats"""
        # This would implement proper statistical aggregation
        # For now, just sum the counts and recalculate
        merged = UsageStatistics(
            stat_id=f"merged_{self.stat_id}_{other.stat_id}",
            period_start=min(self.period_start, other.period_start),
            period_end=max(self.period_end, other.period_end),
            service_type="combined" if self.service_type != other.service_type else self.service_type,
            total_requests=self.total_requests + other.total_requests,
            successful_requests=self.successful_requests + other.successful_requests,
            failed_requests=self.failed_requests + other.failed_requests,
            timeout_requests=self.timeout_requests + other.timeout_requests,
            retry_requests=self.retry_requests + other.retry_requests,
            cache_hits=self.cache_hits + other.cache_hits,
            total_tokens=self.total_tokens + other.total_tokens,
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            total_cost_usd=self.total_cost_usd + other.total_cost_usd
        )
        
        # Calculate weighted averages for timing metrics
        if merged.total_requests > 0:
            weight_self = self.total_requests / merged.total_requests
            weight_other = other.total_requests / merged.total_requests
            
            merged.avg_response_time_ms = (self.avg_response_time_ms * weight_self + 
                                         other.avg_response_time_ms * weight_other)
            merged.avg_queue_time_ms = (self.avg_queue_time_ms * weight_self + 
                                      other.avg_queue_time_ms * weight_other)
        
        return merged

@dataclass
class ModelUsageSnapshot:
    """
    Point-in-time usage snapshot for quick analytics
    
    Provides a snapshot view of model usage at different time granularities
    for real-time monitoring and dashboard displays.
    """
    snapshot_id: str
    model_id: str
    provider: str
    snapshot_time: datetime
    hourly_requests: int = 0
    daily_requests: int = 0
    weekly_requests: int = 0
    monthly_requests: int = 0
    total_tokens_hour: int = 0
    total_tokens_day: int = 0
    total_tokens_week: int = 0
    total_tokens_month: int = 0
    total_cost_hour: float = 0.0
    total_cost_day: float = 0.0
    total_cost_week: float = 0.0
    total_cost_month: float = 0.0
    avg_response_time_hour: float = 0.0
    avg_response_time_day: float = 0.0
    success_rate_hour: float = 100.0
    success_rate_day: float = 100.0
    cache_hit_rate_hour: float = 0.0
    cache_hit_rate_day: float = 0.0
    unique_users_hour: int = 0
    unique_users_day: int = 0
    peak_requests_per_minute: int = 0
    current_queue_size: int = 0
    last_used: Optional[datetime] = None
    health_status: str = "healthy"  # healthy, degraded, critical, offline
    
    def __post_init__(self):
        if self.snapshot_time is None:
            self.snapshot_time = datetime.now(timezone.utc)
    
    @property
    def is_active(self) -> bool:
        """Check if model has been used recently"""
        if not self.last_used:
            return False
        
        time_since_use = datetime.now(timezone.utc) - self.last_used
        return time_since_use.total_seconds() < 3600  # Active if used in last hour
    
    @property
    def utilization_trend(self) -> str:
        """Analyze utilization trend"""
        if self.weekly_requests == 0:
            return "unused"
        
        daily_avg = self.weekly_requests / 7
        hourly_avg = self.daily_requests / 24
        
        if self.hourly_requests > hourly_avg * 2:
            return "surge"
        elif self.hourly_requests > hourly_avg * 1.5:
            return "high"
        elif self.hourly_requests > hourly_avg * 0.8:
            return "normal"
        elif self.hourly_requests > hourly_avg * 0.3:
            return "low"
        else:
            return "minimal"
    
    @property
    def cost_trend(self) -> str:
        """Analyze cost trend"""
        if self.total_cost_week == 0:
            return "no_cost"
        
        daily_avg = self.total_cost_week / 7
        hourly_avg = self.total_cost_day / 24
        
        if self.total_cost_hour > hourly_avg * 3:
            return "expensive_spike"
        elif self.total_cost_hour > hourly_avg * 1.5:
            return "above_average"
        elif self.total_cost_hour > hourly_avg * 0.8:
            return "normal"
        else:
            return "below_average"
    
    @property
    def efficiency_metrics(self) -> Dict[str, float]:
        """Get efficiency metrics"""
        return {
            "requests_per_dollar_hour": self.hourly_requests / max(self.total_cost_hour, 0.01),
            "tokens_per_dollar_hour": self.total_tokens_hour / max(self.total_cost_hour, 0.01),
            "requests_per_dollar_day": self.daily_requests / max(self.total_cost_day, 0.01),
            "tokens_per_dollar_day": self.total_tokens_day / max(self.total_cost_day, 0.01),
            "avg_cost_per_request_hour": self.total_cost_hour / max(self.hourly_requests, 1),
            "avg_cost_per_request_day": self.total_cost_day / max(self.daily_requests, 1)
        }
    
    @property
    def performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        score = 100.0
        
        # Response time penalty
        if self.avg_response_time_day > 5000:
            score -= 30
        elif self.avg_response_time_day > 2000:
            score -= 15
        elif self.avg_response_time_day > 1000:
            score -= 5
        
        # Success rate bonus/penalty
        score = score * (self.success_rate_day / 100)
        
        # Cache hit bonus
        score += self.cache_hit_rate_day * 0.1
        
        # Health status penalty
        if self.health_status == "critical":
            score *= 0.5
        elif self.health_status == "degraded":
            score *= 0.8
        elif self.health_status == "offline":
            score = 0
        
        return max(0.0, min(100.0, score))
    
    def update_health_status(self, new_status: str):
        """Update health status"""
        self.health_status = new_status
        self.snapshot_time = datetime.now(timezone.utc)
    
    def record_usage(self, requests: int = 1, tokens: int = 0, cost: float = 0.0,
                    response_time_ms: float = 0.0, success: bool = True, cache_hit: bool = False):
        """Record usage activity"""
        self.hourly_requests += requests
        self.daily_requests += requests
        self.weekly_requests += requests
        self.monthly_requests += requests
        
        self.total_tokens_hour += tokens
        self.total_tokens_day += tokens
        self.total_tokens_week += tokens
        self.total_tokens_month += tokens
        
        self.total_cost_hour += cost
        self.total_cost_day += cost
        self.total_cost_week += cost
        self.total_cost_month += cost
        
        # Update averages (simplified - would use proper moving averages in production)
        if self.hourly_requests > 0:
            self.avg_response_time_hour = ((self.avg_response_time_hour * (self.hourly_requests - requests)) + 
                                         (response_time_ms * requests)) / self.hourly_requests
        
        if self.daily_requests > 0:
            self.avg_response_time_day = ((self.avg_response_time_day * (self.daily_requests - requests)) + 
                                        (response_time_ms * requests)) / self.daily_requests
        
        self.last_used = datetime.now(timezone.utc)

# Utility functions for working with inference models

def create_inference_request(
    service_type: str,
    model_id: str,
    provider: str,
    endpoint: str,
    request_data: Dict[str, Any],
    user_id: Optional[str] = None,
    **kwargs
) -> InferenceRequest:
    """Factory function to create a new inference request"""
    import uuid
    
    request_id = f"inf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    return InferenceRequest(
        request_id=request_id,
        service_type=service_type,
        model_id=model_id,
        provider=provider,
        endpoint=endpoint,
        request_data=request_data,
        user_id=user_id,
        **kwargs
    )

def create_usage_statistics(
    period_start: datetime,
    period_end: datetime,
    service_type: str,
    model_id: Optional[str] = None,
    provider: Optional[str] = None,
    user_id: Optional[str] = None
) -> UsageStatistics:
    """Factory function to create usage statistics"""
    import uuid
    
    stat_id = f"stat_{period_start.strftime('%Y%m%d_%H')}_{uuid.uuid4().hex[:6]}"
    
    return UsageStatistics(
        stat_id=stat_id,
        period_start=period_start,
        period_end=period_end,
        service_type=service_type,
        model_id=model_id,
        provider=provider,
        user_id=user_id
    )

def create_model_snapshot(
    model_id: str,
    provider: str
) -> ModelUsageSnapshot:
    """Factory function to create model usage snapshot"""
    snapshot_id = f"snap_{model_id}_{provider}_{datetime.now().strftime('%Y%m%d_%H')}"
    
    return ModelUsageSnapshot(
        snapshot_id=snapshot_id,
        model_id=model_id,
        provider=provider
    )

def calculate_usage_summary(requests: List[InferenceRequest]) -> Dict[str, Any]:
    """Calculate usage summary from list of requests"""
    if not requests:
        return {"total_requests": 0}
    
    total_requests = len(requests)
    successful = sum(1 for r in requests if r.was_successful)
    failed = sum(1 for r in requests if r.status == InferenceStatus.FAILED)
    timeouts = sum(1 for r in requests if r.status == InferenceStatus.TIMEOUT)
    
    total_cost = sum(r.cost_usd or 0 for r in requests)
    total_tokens = sum(r.total_tokens or 0 for r in requests)
    
    execution_times = [r.execution_time_ms for r in requests if r.execution_time_ms]
    avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
    
    return {
        "total_requests": total_requests,
        "successful_requests": successful,
        "failed_requests": failed,
        "timeout_requests": timeouts,
        "success_rate": (successful / total_requests) * 100 if total_requests > 0 else 0,
        "total_cost_usd": round(total_cost, 4),
        "total_tokens": total_tokens,
        "avg_execution_time_ms": round(avg_execution_time, 2),
        "cost_per_request": round(total_cost / total_requests, 6) if total_requests > 0 else 0,
        "cost_per_token": round(total_cost / total_tokens, 8) if total_tokens > 0 else 0
    }