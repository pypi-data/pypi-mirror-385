"""
Performance Models

Specialized models for tracking and analyzing inference performance metrics,
latency profiles, and throughput characteristics.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class PerformanceTier(str, Enum):
    """Performance tier enumeration"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"

class LatencyCategory(str, Enum):
    """Latency category enumeration"""
    ULTRA_LOW = "ultra_low"    # < 100ms
    LOW = "low"                # 100-500ms
    MODERATE = "moderate"      # 500ms-2s
    HIGH = "high"              # 2s-10s
    VERY_HIGH = "very_high"    # > 10s

class ThroughputUnit(str, Enum):
    """Throughput measurement unit enumeration"""
    REQUESTS_PER_SECOND = "rps"
    TOKENS_PER_SECOND = "tps"
    TOKENS_PER_MINUTE = "tpm"
    REQUESTS_PER_MINUTE = "rpm"

@dataclass
class PerformanceMetrics:
    """
    Comprehensive performance metrics for inference operations
    
    Tracks detailed performance characteristics including latency, throughput,
    resource utilization, and quality metrics.
    """
    metric_id: str
    model_id: str
    provider: str
    service_type: str
    measurement_period_start: datetime
    measurement_period_end: datetime
    
    # Request volume metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    
    # Latency metrics (in milliseconds)
    min_latency_ms: Optional[float] = None
    max_latency_ms: Optional[float] = None
    mean_latency_ms: Optional[float] = None
    median_latency_ms: Optional[float] = None
    p95_latency_ms: Optional[float] = None
    p99_latency_ms: Optional[float] = None
    p999_latency_ms: Optional[float] = None
    latency_std_dev: Optional[float] = None
    
    # Throughput metrics
    requests_per_second: Optional[float] = None
    tokens_per_second: Optional[float] = None
    tokens_per_minute: Optional[float] = None
    peak_rps: Optional[float] = None
    
    # Token metrics
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    avg_input_tokens: Optional[float] = None
    avg_output_tokens: Optional[float] = None
    max_input_tokens: Optional[int] = None
    max_output_tokens: Optional[int] = None
    
    # Cost metrics
    total_cost_usd: float = 0.0
    cost_per_request: Optional[float] = None
    cost_per_token: Optional[float] = None
    cost_per_second: Optional[float] = None
    
    # Quality metrics
    success_rate: float = 0.0
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    retry_rate: float = 0.0
    cache_hit_rate: float = 0.0
    
    # Resource utilization (if available)
    avg_cpu_usage: Optional[float] = None
    avg_memory_usage: Optional[float] = None
    avg_gpu_usage: Optional[float] = None
    peak_memory_mb: Optional[float] = None
    
    # Queue and concurrency metrics
    avg_queue_time_ms: Optional[float] = None
    max_queue_time_ms: Optional[float] = None
    avg_concurrent_requests: Optional[float] = None
    max_concurrent_requests: Optional[int] = None
    
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        
        # Calculate derived metrics
        self._calculate_derived_metrics()
    
    def _calculate_derived_metrics(self):
        """Calculate derived metrics from base measurements"""
        if self.total_requests > 0:
            self.success_rate = (self.successful_requests / self.total_requests) * 100
            self.error_rate = (self.failed_requests / self.total_requests) * 100
            self.timeout_rate = (self.timeout_requests / self.total_requests) * 100
            
            if self.total_cost_usd > 0:
                self.cost_per_request = self.total_cost_usd / self.total_requests
            
            if self.successful_requests > 0:
                self.avg_input_tokens = self.total_input_tokens / self.successful_requests
                self.avg_output_tokens = self.total_output_tokens / self.successful_requests
        
        # Calculate period-based metrics
        period_seconds = (self.measurement_period_end - self.measurement_period_start).total_seconds()
        if period_seconds > 0:
            self.requests_per_second = self.total_requests / period_seconds
            
            total_tokens = self.total_input_tokens + self.total_output_tokens
            if total_tokens > 0:
                self.tokens_per_second = total_tokens / period_seconds
                self.tokens_per_minute = total_tokens / (period_seconds / 60)
                
                if self.total_cost_usd > 0:
                    self.cost_per_token = self.total_cost_usd / total_tokens
                    self.cost_per_second = self.total_cost_usd / period_seconds
    
    @property
    def measurement_duration_seconds(self) -> float:
        """Get measurement period duration in seconds"""
        return (self.measurement_period_end - self.measurement_period_start).total_seconds()
    
    @property
    def latency_category(self) -> str:
        """Categorize average latency"""
        if self.mean_latency_ms is None:
            return "unknown"
        
        if self.mean_latency_ms < 100:
            return LatencyCategory.ULTRA_LOW
        elif self.mean_latency_ms < 500:
            return LatencyCategory.LOW
        elif self.mean_latency_ms < 2000:
            return LatencyCategory.MODERATE
        elif self.mean_latency_ms < 10000:
            return LatencyCategory.HIGH
        else:
            return LatencyCategory.VERY_HIGH
    
    @property
    def performance_tier(self) -> str:
        """Calculate overall performance tier"""
        score = 100.0
        
        # Latency penalty
        if self.mean_latency_ms:
            if self.mean_latency_ms > 10000:
                score -= 40
            elif self.mean_latency_ms > 5000:
                score -= 25
            elif self.mean_latency_ms > 2000:
                score -= 15
            elif self.mean_latency_ms > 1000:
                score -= 5
        
        # Success rate impact
        score *= (self.success_rate / 100)
        
        # Timeout penalty
        score -= self.timeout_rate * 2
        
        if score >= 85:
            return PerformanceTier.EXCELLENT
        elif score >= 70:
            return PerformanceTier.GOOD
        elif score >= 50:
            return PerformanceTier.AVERAGE
        elif score >= 25:
            return PerformanceTier.POOR
        else:
            return PerformanceTier.CRITICAL
    
    @property
    def efficiency_score(self) -> float:
        """Calculate efficiency score (performance per cost)"""
        if not self.cost_per_request or self.cost_per_request == 0:
            return 0.0
        
        # Higher score for better performance and lower cost
        base_score = self.success_rate
        latency_penalty = (self.mean_latency_ms or 1000) / 1000  # Normalize to seconds
        cost_penalty = self.cost_per_request * 1000  # Scale up cost impact
        
        return max(0, base_score / (latency_penalty * cost_penalty))
    
    @property
    def reliability_score(self) -> float:
        """Calculate reliability score based on error rates"""
        return max(0, 100 - self.error_rate - (self.timeout_rate * 1.5))
    
    def add_request_measurement(self, latency_ms: float, success: bool, tokens_used: int = 0, 
                              cost: float = 0.0, cache_hit: bool = False):
        """Add individual request measurement to aggregate metrics"""
        self.total_requests += 1
        
        if success:
            self.successful_requests += 1
            self.total_input_tokens += tokens_used  # Simplified - would split input/output
            self.total_output_tokens += tokens_used
        else:
            self.failed_requests += 1
        
        if cache_hit:
            # Update cache hit rate calculation
            pass
        
        self.total_cost_usd += cost
        
        # Update latency statistics (simplified - would use proper streaming statistics)
        if self.min_latency_ms is None or latency_ms < self.min_latency_ms:
            self.min_latency_ms = latency_ms
        
        if self.max_latency_ms is None or latency_ms > self.max_latency_ms:
            self.max_latency_ms = latency_ms
        
        # Recalculate derived metrics
        self._calculate_derived_metrics()
    
    def compare_to(self, other: 'PerformanceMetrics') -> Dict[str, Any]:
        """Compare this metrics to another set of metrics"""
        comparison = {
            "baseline_model": other.model_id,
            "comparison_period": {
                "our_period": f"{self.measurement_period_start} to {self.measurement_period_end}",
                "baseline_period": f"{other.measurement_period_start} to {other.measurement_period_end}"
            },
            "improvements": {},
            "regressions": {},
            "summary": {}
        }
        
        # Compare key metrics
        metrics_to_compare = [
            ("mean_latency_ms", "lower_is_better"),
            ("success_rate", "higher_is_better"),
            ("requests_per_second", "higher_is_better"),
            ("tokens_per_second", "higher_is_better"),
            ("cost_per_request", "lower_is_better"),
            ("cost_per_token", "lower_is_better"),
            ("error_rate", "lower_is_better")
        ]
        
        for metric_name, direction in metrics_to_compare:
            our_value = getattr(self, metric_name)
            other_value = getattr(other, metric_name)
            
            if our_value is not None and other_value is not None and other_value != 0:
                change_percent = ((our_value - other_value) / other_value) * 100
                
                is_improvement = (
                    (direction == "higher_is_better" and change_percent > 0) or
                    (direction == "lower_is_better" and change_percent < 0)
                )
                
                change_data = {
                    "our_value": our_value,
                    "baseline_value": other_value,
                    "change_percent": round(change_percent, 2),
                    "absolute_change": our_value - other_value
                }
                
                if abs(change_percent) > 5:  # Significant change threshold
                    if is_improvement:
                        comparison["improvements"][metric_name] = change_data
                    else:
                        comparison["regressions"][metric_name] = change_data
        
        # Overall summary
        comparison["summary"] = {
            "overall_performance_change": self.performance_tier != other.performance_tier,
            "our_tier": self.performance_tier,
            "baseline_tier": other.performance_tier,
            "improvements_count": len(comparison["improvements"]),
            "regressions_count": len(comparison["regressions"])
        }
        
        return comparison

@dataclass
class LatencyProfile:
    """
    Detailed latency profile analysis
    
    Provides comprehensive latency analysis including distribution,
    outliers, and temporal patterns.
    """
    profile_id: str
    model_id: str
    provider: str
    measurement_start: datetime
    measurement_end: datetime
    
    # Distribution data
    latency_samples: List[float] = field(default_factory=list)
    sample_count: int = 0
    
    # Statistical measures
    min_latency: float = float('inf')
    max_latency: float = 0.0
    mean_latency: float = 0.0
    median_latency: float = 0.0
    mode_latency: Optional[float] = None
    std_deviation: float = 0.0
    variance: float = 0.0
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    
    # Percentiles
    p10: float = 0.0
    p25: float = 0.0
    p50: float = 0.0
    p75: float = 0.0
    p90: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    p999: float = 0.0
    
    # Outlier analysis
    outlier_threshold_multiplier: float = 3.0
    outlier_count: int = 0
    outlier_rate: float = 0.0
    outliers: List[float] = field(default_factory=list)
    
    # Temporal patterns
    hourly_averages: Dict[int, float] = field(default_factory=dict)
    daily_trends: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.latency_samples:
            self._calculate_statistics()
    
    def _calculate_statistics(self):
        """Calculate comprehensive latency statistics"""
        if not self.latency_samples:
            return
        
        self.sample_count = len(self.latency_samples)
        sorted_samples = sorted(self.latency_samples)
        
        # Basic statistics
        self.min_latency = min(self.latency_samples)
        self.max_latency = max(self.latency_samples)
        self.mean_latency = statistics.mean(self.latency_samples)
        self.median_latency = statistics.median(self.latency_samples)
        
        if self.sample_count > 1:
            self.std_deviation = statistics.stdev(self.latency_samples)
            self.variance = statistics.variance(self.latency_samples)
        
        # Percentiles
        n = len(sorted_samples)
        self.p10 = sorted_samples[int(0.10 * n)]
        self.p25 = sorted_samples[int(0.25 * n)]
        self.p50 = sorted_samples[int(0.50 * n)]
        self.p75 = sorted_samples[int(0.75 * n)]
        self.p90 = sorted_samples[int(0.90 * n)]
        self.p95 = sorted_samples[int(0.95 * n)]
        self.p99 = sorted_samples[int(0.99 * n)] if n > 100 else sorted_samples[-1]
        self.p999 = sorted_samples[int(0.999 * n)] if n > 1000 else sorted_samples[-1]
        
        # Outlier detection using IQR method
        iqr = self.p75 - self.p25
        lower_bound = self.p25 - (self.outlier_threshold_multiplier * iqr)
        upper_bound = self.p75 + (self.outlier_threshold_multiplier * iqr)
        
        self.outliers = [x for x in self.latency_samples if x < lower_bound or x > upper_bound]
        self.outlier_count = len(self.outliers)
        self.outlier_rate = (self.outlier_count / self.sample_count) * 100
    
    @property
    def distribution_type(self) -> str:
        """Classify the latency distribution"""
        if self.sample_count < 10:
            return "insufficient_data"
        
        # Simple heuristics for distribution classification
        if abs(self.mean_latency - self.median_latency) < (0.1 * self.std_deviation):
            return "normal"
        elif self.mean_latency > self.median_latency:
            return "right_skewed"
        else:
            return "left_skewed"
    
    @property
    def stability_score(self) -> float:
        """Calculate latency stability score (0-100)"""
        if self.mean_latency == 0:
            return 100.0
        
        # Lower coefficient of variation = higher stability
        cv = self.std_deviation / self.mean_latency
        base_score = max(0, 100 - (cv * 100))
        
        # Penalty for outliers
        outlier_penalty = min(20, self.outlier_rate)
        
        return max(0, base_score - outlier_penalty)
    
    @property
    def consistency_category(self) -> str:
        """Categorize latency consistency"""
        stability = self.stability_score
        
        if stability >= 90:
            return "very_consistent"
        elif stability >= 75:
            return "consistent"
        elif stability >= 60:
            return "moderately_consistent"
        elif stability >= 40:
            return "inconsistent"
        else:
            return "very_inconsistent"
    
    def add_latency_sample(self, latency_ms: float, timestamp: Optional[datetime] = None):
        """Add a latency sample to the profile"""
        self.latency_samples.append(latency_ms)
        
        if timestamp:
            # Track hourly patterns
            hour = timestamp.hour
            if hour in self.hourly_averages:
                # Update running average
                count = sum(1 for ts in self.hourly_averages if ts == hour)
                self.hourly_averages[hour] = ((self.hourly_averages[hour] * count) + latency_ms) / (count + 1)
            else:
                self.hourly_averages[hour] = latency_ms
        
        # Recalculate if we have enough samples
        if len(self.latency_samples) % 100 == 0:  # Recalculate every 100 samples
            self._calculate_statistics()
    
    def get_latency_bands(self) -> Dict[str, Dict[str, Any]]:
        """Get latency distribution in bands"""
        if not self.latency_samples:
            return {}
        
        bands = {
            "ultra_fast": {"range": "< 100ms", "count": 0, "percentage": 0},
            "fast": {"range": "100-500ms", "count": 0, "percentage": 0},
            "moderate": {"range": "500ms-2s", "count": 0, "percentage": 0},
            "slow": {"range": "2s-10s", "count": 0, "percentage": 0},
            "very_slow": {"range": "> 10s", "count": 0, "percentage": 0}
        }
        
        for latency in self.latency_samples:
            if latency < 100:
                bands["ultra_fast"]["count"] += 1
            elif latency < 500:
                bands["fast"]["count"] += 1
            elif latency < 2000:
                bands["moderate"]["count"] += 1
            elif latency < 10000:
                bands["slow"]["count"] += 1
            else:
                bands["very_slow"]["count"] += 1
        
        # Calculate percentages
        total = len(self.latency_samples)
        for band in bands.values():
            band["percentage"] = (band["count"] / total) * 100
        
        return bands

@dataclass
class ThroughputProfile:
    """
    Throughput analysis and capacity planning
    
    Analyzes request and token throughput patterns for capacity planning
    and performance optimization.
    """
    profile_id: str
    model_id: str
    provider: str
    measurement_start: datetime
    measurement_end: datetime
    
    # Request throughput
    peak_requests_per_second: float = 0.0
    avg_requests_per_second: float = 0.0
    min_requests_per_second: float = 0.0
    
    # Token throughput
    peak_tokens_per_second: float = 0.0
    avg_tokens_per_second: float = 0.0
    min_tokens_per_second: float = 0.0
    
    # Capacity metrics
    max_concurrent_requests: int = 0
    avg_concurrent_requests: float = 0.0
    queue_overflow_events: int = 0
    throttling_events: int = 0
    
    # Temporal patterns
    throughput_samples: List[Tuple[datetime, float, float]] = field(default_factory=list)  # (timestamp, rps, tps)
    peak_hours: List[int] = field(default_factory=list)
    low_hours: List[int] = field(default_factory=list)
    
    # Efficiency metrics
    tokens_per_request_ratio: float = 0.0
    processing_efficiency: float = 0.0  # Actual vs theoretical max throughput
    
    @property
    def measurement_duration_hours(self) -> float:
        """Get measurement duration in hours"""
        return (self.measurement_end - self.measurement_start).total_seconds() / 3600
    
    @property
    def capacity_utilization(self) -> float:
        """Calculate capacity utilization percentage"""
        if self.peak_requests_per_second == 0:
            return 0.0
        return (self.avg_requests_per_second / self.peak_requests_per_second) * 100
    
    @property
    def throughput_consistency(self) -> str:
        """Analyze throughput consistency"""
        if not self.throughput_samples:
            return "unknown"
        
        rps_values = [sample[1] for sample in self.throughput_samples]
        if not rps_values:
            return "unknown"
        
        cv = statistics.stdev(rps_values) / statistics.mean(rps_values) if statistics.mean(rps_values) > 0 else 0
        
        if cv < 0.1:
            return "very_stable"
        elif cv < 0.3:
            return "stable"
        elif cv < 0.5:
            return "variable"
        else:
            return "highly_variable"
    
    @property
    def performance_headroom(self) -> float:
        """Calculate available performance headroom"""
        return max(0, self.peak_requests_per_second - self.avg_requests_per_second)
    
    def add_throughput_sample(self, timestamp: datetime, requests_per_second: float, 
                            tokens_per_second: float, concurrent_requests: int = 0):
        """Add throughput measurement sample"""
        self.throughput_samples.append((timestamp, requests_per_second, tokens_per_second))
        
        # Update peak values
        if requests_per_second > self.peak_requests_per_second:
            self.peak_requests_per_second = requests_per_second
        
        if tokens_per_second > self.peak_tokens_per_second:
            self.peak_tokens_per_second = tokens_per_second
        
        if concurrent_requests > self.max_concurrent_requests:
            self.max_concurrent_requests = concurrent_requests
        
        # Track peak hours
        hour = timestamp.hour
        if requests_per_second > self.avg_requests_per_second * 1.5:
            if hour not in self.peak_hours:
                self.peak_hours.append(hour)
        elif requests_per_second < self.avg_requests_per_second * 0.5:
            if hour not in self.low_hours:
                self.low_hours.append(hour)
    
    def calculate_capacity_recommendations(self) -> Dict[str, Any]:
        """Generate capacity planning recommendations"""
        recommendations = {
            "current_capacity": {
                "peak_rps": self.peak_requests_per_second,
                "avg_rps": self.avg_requests_per_second,
                "utilization": self.capacity_utilization
            },
            "scaling_recommendations": [],
            "optimization_opportunities": []
        }
        
        # Scaling recommendations
        if self.capacity_utilization > 80:
            recommendations["scaling_recommendations"].append({
                "type": "scale_up",
                "urgency": "high",
                "reason": "High capacity utilization detected",
                "suggested_increase": "50%"
            })
        elif self.capacity_utilization < 30:
            recommendations["scaling_recommendations"].append({
                "type": "scale_down",
                "urgency": "low",
                "reason": "Low capacity utilization, cost optimization opportunity",
                "suggested_decrease": "25%"
            })
        
        # Optimization opportunities
        if self.queue_overflow_events > 0:
            recommendations["optimization_opportunities"].append({
                "type": "queue_optimization",
                "description": "Queue overflow events detected",
                "suggestion": "Increase queue size or add load balancing"
            })
        
        if self.throughput_consistency == "highly_variable":
            recommendations["optimization_opportunities"].append({
                "type": "load_smoothing",
                "description": "High throughput variability",
                "suggestion": "Implement request smoothing or auto-scaling"
            })
        
        return recommendations

# Utility functions

def create_performance_metrics(
    model_id: str,
    provider: str,
    service_type: str,
    period_start: datetime,
    period_end: datetime
) -> PerformanceMetrics:
    """Factory function to create performance metrics"""
    import uuid
    
    metric_id = f"perf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    return PerformanceMetrics(
        metric_id=metric_id,
        model_id=model_id,
        provider=provider,
        service_type=service_type,
        measurement_period_start=period_start,
        measurement_period_end=period_end
    )

def analyze_performance_trend(metrics_list: List[PerformanceMetrics]) -> Dict[str, Any]:
    """Analyze performance trends across multiple measurement periods"""
    if not metrics_list:
        return {"status": "no_data"}
    
    # Sort by measurement period
    sorted_metrics = sorted(metrics_list, key=lambda x: x.measurement_period_start)
    
    # Calculate trends
    latencies = [m.mean_latency_ms for m in sorted_metrics if m.mean_latency_ms]
    success_rates = [m.success_rate for m in sorted_metrics]
    throughputs = [m.requests_per_second for m in sorted_metrics if m.requests_per_second]
    
    trends = {
        "period_count": len(sorted_metrics),
        "time_range": {
            "start": sorted_metrics[0].measurement_period_start.isoformat(),
            "end": sorted_metrics[-1].measurement_period_end.isoformat()
        },
        "performance_trend": "stable",
        "key_changes": []
    }
    
    # Analyze latency trend
    if len(latencies) > 1:
        latency_change = ((latencies[-1] - latencies[0]) / latencies[0]) * 100
        if abs(latency_change) > 10:
            trends["key_changes"].append({
                "metric": "latency",
                "change_percent": round(latency_change, 2),
                "direction": "increased" if latency_change > 0 else "decreased"
            })
    
    # Analyze success rate trend
    if len(success_rates) > 1:
        success_change = success_rates[-1] - success_rates[0]
        if abs(success_change) > 5:
            trends["key_changes"].append({
                "metric": "success_rate",
                "change_percent": round(success_change, 2),
                "direction": "improved" if success_change > 0 else "degraded"
            })
    
    # Overall trend assessment
    if len(trends["key_changes"]) > 2:
        trends["performance_trend"] = "volatile"
    elif any(change["metric"] == "latency" and change["direction"] == "increased" for change in trends["key_changes"]):
        trends["performance_trend"] = "degrading"
    elif any(change["metric"] == "success_rate" and change["direction"] == "improved" for change in trends["key_changes"]):
        trends["performance_trend"] = "improving"
    
    return trends