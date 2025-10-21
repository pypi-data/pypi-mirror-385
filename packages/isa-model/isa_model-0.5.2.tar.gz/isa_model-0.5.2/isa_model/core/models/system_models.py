"""
System Models

Data models for system health, resource usage, and service status monitoring,
following the ISA Model architecture pattern.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"

class ServiceType(str, Enum):
    """Service type enumeration"""
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    STORAGE = "storage"
    COMPUTE = "compute"
    MONITORING = "monitoring"
    EXTERNAL = "external"

class AlertSeverity(str, Enum):
    """Alert severity enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SystemHealth:
    """
    System health monitoring record
    
    Tracks overall system health including component status,
    performance metrics, and alert information.
    """
    health_id: str
    system_name: str
    overall_status: str = HealthStatus.HEALTHY
    timestamp: datetime = None
    
    # Component health
    component_status: Dict[str, str] = field(default_factory=dict)
    component_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    failing_components: List[str] = field(default_factory=list)
    degraded_components: List[str] = field(default_factory=list)
    
    # Performance indicators
    response_time_ms: Optional[float] = None
    throughput_rps: Optional[float] = None
    error_rate_percent: Optional[float] = None
    availability_percent: Optional[float] = None
    uptime_seconds: Optional[int] = None
    
    # Resource utilization
    cpu_usage_percent: Optional[float] = None
    memory_usage_percent: Optional[float] = None
    disk_usage_percent: Optional[float] = None
    network_usage_mbps: Optional[float] = None
    
    # Health checks
    last_health_check: Optional[datetime] = None
    health_check_interval_seconds: int = 60
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    
    # Alerts and issues
    active_alerts: List[Dict[str, Any]] = field(default_factory=list)
    resolved_alerts_24h: int = 0
    critical_issues: List[str] = field(default_factory=list)
    
    # Metadata
    version: Optional[str] = None
    environment: str = "production"
    region: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.last_health_check is None:
            self.last_health_check = self.timestamp
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return self.overall_status == HealthStatus.HEALTHY
    
    @property
    def health_score(self) -> float:
        """Calculate overall health score (0-100)"""
        score = 100.0
        
        # Component health impact
        total_components = len(self.component_status)
        if total_components > 0:
            healthy_components = sum(1 for status in self.component_status.values() 
                                   if status == HealthStatus.HEALTHY)
            component_score = (healthy_components / total_components) * 100
            score = min(score, component_score)
        
        # Performance impact
        if self.error_rate_percent is not None:
            score -= min(50, self.error_rate_percent * 5)  # Error rate penalty
        
        if self.availability_percent is not None:
            score = min(score, self.availability_percent)
        
        if self.cpu_usage_percent is not None and self.cpu_usage_percent > 90:
            score -= (self.cpu_usage_percent - 90) * 2
        
        if self.memory_usage_percent is not None and self.memory_usage_percent > 90:
            score -= (self.memory_usage_percent - 90) * 2
        
        # Alert impact
        critical_alert_count = sum(1 for alert in self.active_alerts 
                                 if alert.get('severity') == AlertSeverity.CRITICAL)
        score -= critical_alert_count * 10
        
        return max(0.0, min(100.0, score))
    
    @property
    def needs_attention(self) -> bool:
        """Check if system needs immediate attention"""
        return (self.overall_status in [HealthStatus.CRITICAL, HealthStatus.DEGRADED] or
                len(self.critical_issues) > 0 or
                any(alert.get('severity') == AlertSeverity.CRITICAL for alert in self.active_alerts))
    
    @property
    def time_since_last_check(self) -> int:
        """Get seconds since last health check"""
        if self.last_health_check:
            return int((datetime.now(timezone.utc) - self.last_health_check).total_seconds())
        return 0
    
    def update_component_status(self, component_name: str, status: str, 
                              metrics: Optional[Dict[str, float]] = None):
        """Update status for a specific component"""
        old_status = self.component_status.get(component_name)
        self.component_status[component_name] = status
        
        if metrics:
            self.component_metrics[component_name] = metrics
        
        # Update component lists
        if status == HealthStatus.CRITICAL:
            if component_name not in self.failing_components:
                self.failing_components.append(component_name)
            if component_name in self.degraded_components:
                self.degraded_components.remove(component_name)
        elif status == HealthStatus.DEGRADED:
            if component_name not in self.degraded_components:
                self.degraded_components.append(component_name)
            if component_name in self.failing_components:
                self.failing_components.remove(component_name)
        else:  # Healthy or other
            if component_name in self.failing_components:
                self.failing_components.remove(component_name)
            if component_name in self.degraded_components:
                self.degraded_components.remove(component_name)
        
        # Update overall status
        self._calculate_overall_status()
        
        # Track consecutive failures/successes
        if old_status != status:
            if status in [HealthStatus.CRITICAL, HealthStatus.DEGRADED]:
                self.consecutive_failures += 1
                self.consecutive_successes = 0
            else:
                self.consecutive_successes += 1
                self.consecutive_failures = 0
    
    def _calculate_overall_status(self):
        """Calculate overall system status from component statuses"""
        if not self.component_status:
            self.overall_status = HealthStatus.UNKNOWN
            return
        
        statuses = list(self.component_status.values())
        
        if HealthStatus.CRITICAL in statuses:
            self.overall_status = HealthStatus.CRITICAL
        elif HealthStatus.DEGRADED in statuses:
            self.overall_status = HealthStatus.DEGRADED
        elif HealthStatus.OFFLINE in statuses:
            self.overall_status = HealthStatus.DEGRADED
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            self.overall_status = HealthStatus.HEALTHY
        else:
            self.overall_status = HealthStatus.DEGRADED
    
    def add_alert(self, alert_id: str, severity: str, message: str, 
                 component: Optional[str] = None, **kwargs):
        """Add an active alert"""
        alert = {
            "alert_id": alert_id,
            "severity": severity,
            "message": message,
            "component": component,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs
        }
        
        # Check if alert already exists
        existing_alert = next((a for a in self.active_alerts if a.get("alert_id") == alert_id), None)
        if existing_alert:
            existing_alert.update(alert)
        else:
            self.active_alerts.append(alert)
    
    def resolve_alert(self, alert_id: str):
        """Resolve an active alert"""
        self.active_alerts = [alert for alert in self.active_alerts 
                            if alert.get("alert_id") != alert_id]
        self.resolved_alerts_24h += 1
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        self.last_health_check = datetime.now(timezone.utc)
        
        health_result = {
            "overall_status": self.overall_status,
            "health_score": self.health_score,
            "timestamp": self.last_health_check.isoformat(),
            "component_summary": {
                "total": len(self.component_status),
                "healthy": sum(1 for s in self.component_status.values() if s == HealthStatus.HEALTHY),
                "degraded": len(self.degraded_components),
                "critical": len(self.failing_components)
            },
            "alerts": {
                "active": len(self.active_alerts),
                "critical": sum(1 for a in self.active_alerts if a.get("severity") == AlertSeverity.CRITICAL),
                "resolved_24h": self.resolved_alerts_24h
            },
            "performance": {
                "response_time_ms": self.response_time_ms,
                "error_rate_percent": self.error_rate_percent,
                "availability_percent": self.availability_percent
            },
            "needs_attention": self.needs_attention
        }
        
        return health_result

@dataclass
class ResourceUsage:
    """
    Resource usage monitoring record
    
    Tracks resource consumption across different dimensions
    including compute, memory, storage, and network resources.
    """
    usage_id: str
    resource_type: str  # cpu, memory, disk, network, gpu
    timestamp: datetime = None
    measurement_period_seconds: int = 60
    
    # Current usage
    current_usage: float = 0.0
    current_usage_percent: Optional[float] = None
    
    # Historical data
    min_usage: float = 0.0
    max_usage: float = 0.0
    avg_usage: float = 0.0
    p95_usage: Optional[float] = None
    p99_usage: Optional[float] = None
    
    # Capacity and limits
    total_capacity: Optional[float] = None
    allocated_capacity: Optional[float] = None
    reserved_capacity: Optional[float] = None
    soft_limit: Optional[float] = None
    hard_limit: Optional[float] = None
    
    # Usage patterns
    usage_samples: List[float] = field(default_factory=list)
    peak_hours: List[int] = field(default_factory=list)
    low_hours: List[int] = field(default_factory=list)
    
    # Trends and predictions
    trend_direction: str = "stable"  # increasing, decreasing, stable, volatile
    predicted_usage_1h: Optional[float] = None
    predicted_usage_24h: Optional[float] = None
    time_to_capacity: Optional[int] = None  # seconds until capacity reached
    
    # Alerts and thresholds
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    threshold_breaches_24h: int = 0
    
    # Metadata
    host: Optional[str] = None
    service: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        
        # Calculate percentage if capacity is known
        if self.total_capacity and self.total_capacity > 0:
            self.current_usage_percent = (self.current_usage / self.total_capacity) * 100
    
    @property
    def is_at_capacity(self) -> bool:
        """Check if resource is at or near capacity"""
        if self.current_usage_percent:
            return self.current_usage_percent >= 95
        return False
    
    @property
    def is_over_soft_limit(self) -> bool:
        """Check if usage exceeds soft limit"""
        if self.soft_limit:
            return self.current_usage > self.soft_limit
        return False
    
    @property
    def is_over_hard_limit(self) -> bool:
        """Check if usage exceeds hard limit"""
        if self.hard_limit:
            return self.current_usage > self.hard_limit
        return False
    
    @property
    def utilization_efficiency(self) -> float:
        """Calculate utilization efficiency (0-100)"""
        if not self.allocated_capacity or self.allocated_capacity == 0:
            return 0.0
        
        return min(100.0, (self.current_usage / self.allocated_capacity) * 100)
    
    @property
    def waste_percentage(self) -> float:
        """Calculate resource waste percentage"""
        if not self.allocated_capacity or self.allocated_capacity == 0:
            return 0.0
        
        unused = max(0, self.allocated_capacity - self.current_usage)
        return (unused / self.allocated_capacity) * 100
    
    def add_usage_sample(self, usage_value: float, timestamp: Optional[datetime] = None):
        """Add a usage measurement sample"""
        self.usage_samples.append(usage_value)
        
        # Update current values
        self.current_usage = usage_value
        if self.total_capacity and self.total_capacity > 0:
            self.current_usage_percent = (usage_value / self.total_capacity) * 100
        
        # Update min/max
        if usage_value < self.min_usage or self.min_usage == 0:
            self.min_usage = usage_value
        if usage_value > self.max_usage:
            self.max_usage = usage_value
        
        # Recalculate statistics if we have enough samples
        if len(self.usage_samples) >= 10:
            self._calculate_statistics()
        
        # Track peak hours
        if timestamp:
            hour = timestamp.hour
            if usage_value > self.avg_usage * 1.5:
                if hour not in self.peak_hours:
                    self.peak_hours.append(hour)
            elif usage_value < self.avg_usage * 0.5:
                if hour not in self.low_hours:
                    self.low_hours.append(hour)
    
    def _calculate_statistics(self):
        """Calculate statistical measures from usage samples"""
        if not self.usage_samples:
            return
        
        self.avg_usage = statistics.mean(self.usage_samples)
        
        if len(self.usage_samples) > 1:
            sorted_samples = sorted(self.usage_samples)
            n = len(sorted_samples)
            
            self.p95_usage = sorted_samples[int(0.95 * n)]
            self.p99_usage = sorted_samples[int(0.99 * n)] if n > 100 else sorted_samples[-1]
        
        # Analyze trend
        if len(self.usage_samples) >= 5:
            recent_avg = statistics.mean(self.usage_samples[-5:])
            older_avg = statistics.mean(self.usage_samples[:-5]) if len(self.usage_samples) > 5 else self.avg_usage
            
            if recent_avg > older_avg * 1.1:
                self.trend_direction = "increasing"
            elif recent_avg < older_avg * 0.9:
                self.trend_direction = "decreasing"
            else:
                # Check for volatility
                std_dev = statistics.stdev(self.usage_samples[-10:]) if len(self.usage_samples) >= 10 else 0
                cv = std_dev / self.avg_usage if self.avg_usage > 0 else 0
                
                if cv > 0.3:  # High coefficient of variation
                    self.trend_direction = "volatile"
                else:
                    self.trend_direction = "stable"
    
    def predict_future_usage(self, hours_ahead: int = 1) -> Optional[float]:
        """Predict future resource usage based on trends"""
        if len(self.usage_samples) < 5:
            return None
        
        # Simple linear trend prediction
        recent_samples = self.usage_samples[-10:]
        x = list(range(len(recent_samples)))
        y = recent_samples
        
        # Calculate linear regression (simplified)
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 - sum_x ** 2 != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            intercept = (sum_y - slope * sum_x) / n
            
            # Predict future value
            future_x = len(recent_samples) + hours_ahead
            predicted = slope * future_x + intercept
            
            return max(0, predicted)
        
        return self.avg_usage
    
    def calculate_time_to_capacity(self) -> Optional[int]:
        """Calculate time until resource reaches capacity"""
        if not self.total_capacity or self.trend_direction != "increasing":
            return None
        
        available_capacity = self.total_capacity - self.current_usage
        if available_capacity <= 0:
            return 0
        
        # Estimate growth rate from recent samples
        if len(self.usage_samples) >= 5:
            recent_growth = self.usage_samples[-1] - self.usage_samples[-5]
            if recent_growth > 0:
                # Estimate hours to capacity based on current growth rate
                growth_per_hour = recent_growth / 5  # Assuming samples are hourly
                hours_to_capacity = available_capacity / growth_per_hour
                return int(hours_to_capacity * 3600)  # Convert to seconds
        
        return None
    
    def check_thresholds(self) -> List[Dict[str, Any]]:
        """Check if usage exceeds configured thresholds"""
        alerts = []
        
        if self.warning_threshold and self.current_usage > self.warning_threshold:
            alerts.append({
                "level": "warning",
                "message": f"{self.resource_type} usage ({self.current_usage}) exceeds warning threshold ({self.warning_threshold})",
                "threshold": self.warning_threshold,
                "current_value": self.current_usage
            })
        
        if self.critical_threshold and self.current_usage > self.critical_threshold:
            alerts.append({
                "level": "critical",
                "message": f"{self.resource_type} usage ({self.current_usage}) exceeds critical threshold ({self.critical_threshold})",
                "threshold": self.critical_threshold,
                "current_value": self.current_usage
            })
        
        return alerts

@dataclass
class ServiceStatus:
    """
    Service status monitoring record
    
    Tracks the status and health of individual services
    including availability, performance, and dependencies.
    """
    service_id: str
    service_name: str
    service_type: str
    status: str = HealthStatus.UNKNOWN
    timestamp: datetime = None
    
    # Service details
    version: Optional[str] = None
    endpoint_url: Optional[str] = None
    health_check_url: Optional[str] = None
    last_deployment: Optional[datetime] = None
    
    # Availability metrics
    uptime_seconds: int = 0
    downtime_seconds: int = 0
    availability_percent: float = 100.0
    mttr_seconds: Optional[int] = None  # Mean Time To Repair
    mtbf_seconds: Optional[int] = None  # Mean Time Between Failures
    
    # Performance metrics
    response_time_ms: Optional[float] = None
    throughput_rps: Optional[float] = None
    error_rate_percent: float = 0.0
    success_rate_percent: float = 100.0
    
    # Health check results
    last_health_check: Optional[datetime] = None
    health_check_success: bool = True
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    health_check_interval_seconds: int = 30
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    dependency_statuses: Dict[str, str] = field(default_factory=dict)
    critical_dependencies: List[str] = field(default_factory=list)
    
    # Incidents and alerts
    active_incidents: List[Dict[str, Any]] = field(default_factory=list)
    incidents_24h: int = 0
    last_incident: Optional[datetime] = None
    
    # Configuration
    auto_restart_enabled: bool = False
    restart_count_24h: int = 0
    circuit_breaker_status: str = "closed"  # closed, open, half_open
    
    # Metadata
    environment: str = "production"
    region: Optional[str] = None
    owner_team: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.last_health_check is None:
            self.last_health_check = self.timestamp
    
    @property
    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return self.status == HealthStatus.HEALTHY and self.health_check_success
    
    @property
    def is_available(self) -> bool:
        """Check if service is available (not offline)"""
        return self.status != HealthStatus.OFFLINE
    
    @property
    def needs_attention(self) -> bool:
        """Check if service needs immediate attention"""
        return (self.status in [HealthStatus.CRITICAL, HealthStatus.OFFLINE] or
                self.consecutive_failures >= 3 or
                len(self.active_incidents) > 0)
    
    @property
    def uptime_percent_24h(self) -> float:
        """Calculate uptime percentage for last 24 hours"""
        total_seconds_24h = 24 * 60 * 60
        uptime_24h = min(self.uptime_seconds, total_seconds_24h)
        return (uptime_24h / total_seconds_24h) * 100
    
    @property
    def service_level_indicator(self) -> Dict[str, float]:
        """Calculate Service Level Indicators (SLI)"""
        return {
            "availability": self.availability_percent,
            "success_rate": self.success_rate_percent,
            "response_time_ms": self.response_time_ms or 0,
            "throughput_rps": self.throughput_rps or 0
        }
    
    @property
    def reliability_score(self) -> float:
        """Calculate overall reliability score (0-100)"""
        score = 100.0
        
        # Availability impact
        score *= (self.availability_percent / 100)
        
        # Error rate impact
        score *= (self.success_rate_percent / 100)
        
        # Health check impact
        if self.consecutive_failures > 0:
            score -= min(50, self.consecutive_failures * 10)
        
        # Incident impact
        if self.incidents_24h > 0:
            score -= min(30, self.incidents_24h * 5)
        
        return max(0.0, min(100.0, score))
    
    def update_status(self, new_status: str, reason: Optional[str] = None):
        """Update service status"""
        old_status = self.status
        self.status = new_status
        self.timestamp = datetime.now(timezone.utc)
        
        # Track uptime/downtime
        if old_status != new_status:
            if new_status == HealthStatus.OFFLINE:
                # Service went down
                if reason:
                    self.add_incident(f"Service offline: {reason}", AlertSeverity.CRITICAL)
            elif old_status == HealthStatus.OFFLINE:
                # Service came back up
                self.resolve_incidents("Service restored")
    
    def perform_health_check(self) -> bool:
        """Perform health check and update status"""
        self.last_health_check = datetime.now(timezone.utc)
        
        # This would contain actual health check logic
        # For now, simulate based on current status
        if self.status == HealthStatus.OFFLINE:
            self.health_check_success = False
            self.consecutive_failures += 1
            self.consecutive_successes = 0
        else:
            self.health_check_success = True
            self.consecutive_successes += 1
            self.consecutive_failures = 0
        
        # Update circuit breaker status
        if self.consecutive_failures >= 5:
            self.circuit_breaker_status = "open"
        elif self.consecutive_failures >= 3:
            self.circuit_breaker_status = "half_open"
        else:
            self.circuit_breaker_status = "closed"
        
        return self.health_check_success
    
    def add_incident(self, description: str, severity: str, incident_id: Optional[str] = None):
        """Add an active incident"""
        if not incident_id:
            import uuid
            incident_id = f"inc_{uuid.uuid4().hex[:8]}"
        
        incident = {
            "incident_id": incident_id,
            "description": description,
            "severity": severity,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }
        
        self.active_incidents.append(incident)
        self.incidents_24h += 1
        self.last_incident = datetime.now(timezone.utc)
    
    def resolve_incidents(self, resolution: str):
        """Resolve all active incidents"""
        for incident in self.active_incidents:
            incident["status"] = "resolved"
            incident["end_time"] = datetime.now(timezone.utc).isoformat()
            incident["resolution"] = resolution
        
        self.active_incidents = []
    
    def check_dependencies(self) -> bool:
        """Check status of service dependencies"""
        all_healthy = True
        
        for dependency in self.critical_dependencies:
            status = self.dependency_statuses.get(dependency, HealthStatus.UNKNOWN)
            if status not in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
                all_healthy = False
                
                # Update our status if critical dependency is down
                if self.status == HealthStatus.HEALTHY:
                    self.update_status(HealthStatus.DEGRADED, f"Critical dependency {dependency} is {status}")
        
        return all_healthy
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        return {
            "service_info": {
                "service_id": self.service_id,
                "service_name": self.service_name,
                "service_type": self.service_type,
                "version": self.version,
                "environment": self.environment
            },
            "current_status": {
                "status": self.status,
                "health_check_success": self.health_check_success,
                "is_available": self.is_available,
                "needs_attention": self.needs_attention,
                "timestamp": self.timestamp.isoformat()
            },
            "performance": {
                "response_time_ms": self.response_time_ms,
                "throughput_rps": self.throughput_rps,
                "error_rate_percent": self.error_rate_percent,
                "success_rate_percent": self.success_rate_percent
            },
            "reliability": {
                "availability_percent": self.availability_percent,
                "uptime_percent_24h": self.uptime_percent_24h,
                "reliability_score": self.reliability_score,
                "mttr_seconds": self.mttr_seconds,
                "mtbf_seconds": self.mtbf_seconds
            },
            "incidents": {
                "active_count": len(self.active_incidents),
                "incidents_24h": self.incidents_24h,
                "last_incident": self.last_incident.isoformat() if self.last_incident else None
            },
            "health_checks": {
                "consecutive_failures": self.consecutive_failures,
                "consecutive_successes": self.consecutive_successes,
                "last_check": self.last_health_check.isoformat() if self.last_health_check else None
            },
            "dependencies": {
                "total": len(self.dependencies),
                "critical": len(self.critical_dependencies),
                "statuses": self.dependency_statuses
            }
        }

# Utility functions for working with system models

def create_system_health(
    system_name: str,
    environment: str = "production"
) -> SystemHealth:
    """Factory function to create system health record"""
    import uuid
    
    health_id = f"health_{system_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    return SystemHealth(
        health_id=health_id,
        system_name=system_name,
        environment=environment
    )

def create_resource_usage(
    resource_type: str,
    current_usage: float,
    total_capacity: Optional[float] = None,
    host: Optional[str] = None,
    service: Optional[str] = None
) -> ResourceUsage:
    """Factory function to create resource usage record"""
    import uuid
    
    usage_id = f"usage_{resource_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    return ResourceUsage(
        usage_id=usage_id,
        resource_type=resource_type,
        current_usage=current_usage,
        total_capacity=total_capacity,
        host=host,
        service=service
    )

def create_service_status(
    service_name: str,
    service_type: str,
    endpoint_url: Optional[str] = None,
    environment: str = "production"
) -> ServiceStatus:
    """Factory function to create service status record"""
    import uuid
    
    service_id = f"svc_{service_name}_{uuid.uuid4().hex[:8]}"
    
    return ServiceStatus(
        service_id=service_id,
        service_name=service_name,
        service_type=service_type,
        endpoint_url=endpoint_url,
        environment=environment
    )

def calculate_system_overview(
    health_records: List[SystemHealth],
    resource_records: List[ResourceUsage],
    service_records: List[ServiceStatus]
) -> Dict[str, Any]:
    """Calculate comprehensive system overview"""
    overview = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_health": {},
        "resource_utilization": {},
        "service_availability": {},
        "overall_status": HealthStatus.HEALTHY,
        "alerts": []
    }
    
    # System health summary
    if health_records:
        healthy_systems = sum(1 for h in health_records if h.is_healthy)
        overview["system_health"] = {
            "total_systems": len(health_records),
            "healthy_systems": healthy_systems,
            "health_percentage": (healthy_systems / len(health_records)) * 100,
            "avg_health_score": sum(h.health_score for h in health_records) / len(health_records)
        }
    
    # Resource utilization summary
    if resource_records:
        cpu_records = [r for r in resource_records if r.resource_type == "cpu"]
        memory_records = [r for r in resource_records if r.resource_type == "memory"]
        
        overview["resource_utilization"] = {
            "avg_cpu_usage": sum(r.current_usage_percent or 0 for r in cpu_records) / len(cpu_records) if cpu_records else 0,
            "avg_memory_usage": sum(r.current_usage_percent or 0 for r in memory_records) / len(memory_records) if memory_records else 0,
            "resources_at_capacity": sum(1 for r in resource_records if r.is_at_capacity),
            "resources_over_threshold": sum(1 for r in resource_records if r.is_over_soft_limit)
        }
    
    # Service availability summary
    if service_records:
        available_services = sum(1 for s in service_records if s.is_available)
        overview["service_availability"] = {
            "total_services": len(service_records),
            "available_services": available_services,
            "availability_percentage": (available_services / len(service_records)) * 100,
            "avg_reliability_score": sum(s.reliability_score for s in service_records) / len(service_records)
        }
    
    # Overall status determination
    if overview["system_health"].get("health_percentage", 100) < 80:
        overview["overall_status"] = HealthStatus.CRITICAL
    elif overview["service_availability"].get("availability_percentage", 100) < 90:
        overview["overall_status"] = HealthStatus.DEGRADED
    elif overview["resource_utilization"].get("resources_at_capacity", 0) > 0:
        overview["overall_status"] = HealthStatus.DEGRADED
    
    return overview