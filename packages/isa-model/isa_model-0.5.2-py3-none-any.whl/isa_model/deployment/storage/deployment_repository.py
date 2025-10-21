"""
Deployment Repository - Data persistence layer for deployment operations

Provides standardized data access for deployment records, configurations, and metrics
following the ISA Model architecture pattern.
"""

import logging
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

try:
    # Try to import Supabase for centralized data storage
    from ...core.database.supabase_client import get_supabase_client, SupabaseClient
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    SupabaseClient = None

logger = logging.getLogger(__name__)

class DeploymentStatus(str, Enum):
    """Deployment status enumeration"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"
    UPDATING = "updating"
    SCALING = "scaling"

class DeploymentPlatform(str, Enum):
    """Deployment platform enumeration"""
    HUGGINGFACE = "huggingface"
    MODAL = "modal"
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"

@dataclass
class DeploymentRecord:
    """Deployment record model"""
    deployment_id: str
    model_id: str
    deployment_name: str
    platform: str
    status: str = DeploymentStatus.PENDING
    endpoint_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    environment: str = "production"
    created_at: datetime = None
    updated_at: datetime = None
    deployed_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    user_id: Optional[str] = None
    project_name: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at

@dataclass
class DeploymentMetrics:
    """Deployment metrics record"""
    metric_id: str
    deployment_id: str
    timestamp: datetime
    requests_per_minute: Optional[int] = None
    avg_response_time_ms: Optional[float] = None
    error_rate: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    cost_per_hour: Optional[float] = None
    uptime_percentage: Optional[float] = None
    custom_metrics: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

@dataclass
class ServiceRegistryEntry:
    """Service registry entry for tracking deployed services"""
    service_id: str
    deployment_id: str
    service_name: str
    service_type: str
    endpoint_url: str
    health_check_url: Optional[str] = None
    is_active: bool = True
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"  # healthy, unhealthy, unknown
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

class DeploymentRepository:
    """
    Repository for deployment data persistence
    
    Supports multiple backend storage options:
    1. Supabase (preferred for centralized storage)
    2. Local file system (fallback for development)
    3. In-memory storage (for testing)
    """
    
    def __init__(self, storage_backend: str = "auto", **kwargs):
        """
        Initialize deployment repository
        
        Args:
            storage_backend: "supabase", "file", "memory", or "auto"
            **kwargs: Backend-specific configuration
        """
        self.storage_backend = self._determine_backend(storage_backend)
        self.config = kwargs
        
        # Initialize storage backend
        if self.storage_backend == "supabase":
            self._init_supabase()
        elif self.storage_backend == "memory":
            self._init_memory()
        else:  # file system fallback
            self._init_file_system()
        
        logger.info(f"Deployment repository initialized with {self.storage_backend} backend")
    
    def _determine_backend(self, preference: str) -> str:
        """Determine the best available storage backend"""
        if preference == "supabase" and SUPABASE_AVAILABLE:
            return "supabase"
        elif preference in ["supabase", "file", "memory"]:
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
            logger.info("Supabase backend initialized for deployments")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase backend: {e}")
            self.storage_backend = "file"
            self._init_file_system()
    
    def _init_file_system(self):
        """Initialize file system backend"""
        self.data_dir = Path(self.config.get("data_dir", "./deployment_data"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.data_dir / "deployments").mkdir(exist_ok=True)
        (self.data_dir / "metrics").mkdir(exist_ok=True)
        (self.data_dir / "services").mkdir(exist_ok=True)
        
        logger.info(f"File system backend initialized: {self.data_dir}")
    
    def _init_memory(self):
        """Initialize in-memory backend for testing"""
        self.deployments = {}
        self.metrics = {}
        self.services = {}
        logger.info("In-memory backend initialized for deployments")
    
    def _ensure_supabase_tables(self):
        """Ensure required Supabase tables exist"""
        try:
            self.supabase_client.table("deployment_records").select("deployment_id").limit(1).execute()
            self.supabase_client.table("deployment_metrics").select("metric_id").limit(1).execute()
            self.supabase_client.table("service_registry").select("service_id").limit(1).execute()
        except Exception as e:
            logger.warning(f"Some deployment tables may not exist in Supabase: {e}")
    
    # Deployment Management Methods
    
    def create_deployment_record(
        self,
        model_id: str,
        deployment_name: str,
        platform: str,
        config: Optional[Dict[str, Any]] = None,
        environment: str = "production",
        user_id: Optional[str] = None,
        project_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """Create a new deployment record"""
        deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        deployment = DeploymentRecord(
            deployment_id=deployment_id,
            model_id=model_id,
            deployment_name=deployment_name,
            platform=platform,
            config=config or {},
            environment=environment,
            user_id=user_id,
            project_name=project_name,
            tags=tags
        )
        
        if self.storage_backend == "supabase":
            return self._create_deployment_supabase(deployment)
        elif self.storage_backend == "memory":
            return self._create_deployment_memory(deployment)
        else:
            return self._create_deployment_file(deployment)
    
    def update_deployment_status(
        self,
        deployment_id: str,
        status: str,
        endpoint_url: Optional[str] = None,
        error_message: Optional[str] = None,
        additional_updates: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update deployment status and information"""
        updates = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if status == DeploymentStatus.RUNNING and endpoint_url:
            updates["endpoint_url"] = endpoint_url
            updates["deployed_at"] = datetime.now(timezone.utc).isoformat()
        elif status == DeploymentStatus.STOPPED:
            updates["stopped_at"] = datetime.now(timezone.utc).isoformat()
        
        if error_message:
            updates["error_message"] = error_message
        
        if additional_updates:
            updates.update(additional_updates)
        
        if self.storage_backend == "supabase":
            return self._update_deployment_supabase(deployment_id, updates)
        elif self.storage_backend == "memory":
            return self._update_deployment_memory(deployment_id, updates)
        else:
            return self._update_deployment_file(deployment_id, updates)
    
    def get_deployment_info(self, deployment_id: str) -> Optional[DeploymentRecord]:
        """Get deployment information by ID"""
        if self.storage_backend == "supabase":
            return self._get_deployment_supabase(deployment_id)
        elif self.storage_backend == "memory":
            return self._get_deployment_memory(deployment_id)
        else:
            return self._get_deployment_file(deployment_id)
    
    def list_active_deployments(
        self,
        platform: Optional[str] = None,
        environment: Optional[str] = None,
        user_id: Optional[str] = None,
        project_name: Optional[str] = None,
        limit: int = 100
    ) -> List[DeploymentRecord]:
        """List active deployments with optional filtering"""
        if self.storage_backend == "supabase":
            return self._list_deployments_supabase(platform, environment, user_id, project_name, limit)
        elif self.storage_backend == "memory":
            return self._list_deployments_memory(platform, environment, user_id, project_name, limit)
        else:
            return self._list_deployments_file(platform, environment, user_id, project_name, limit)
    
    def delete_deployment_record(self, deployment_id: str) -> bool:
        """Delete deployment record and associated data"""
        if self.storage_backend == "supabase":
            return self._delete_deployment_supabase(deployment_id)
        elif self.storage_backend == "memory":
            return self._delete_deployment_memory(deployment_id)
        else:
            return self._delete_deployment_file(deployment_id)
    
    # Metrics Management Methods
    
    def record_deployment_metrics(
        self,
        deployment_id: str,
        requests_per_minute: Optional[int] = None,
        avg_response_time_ms: Optional[float] = None,
        error_rate: Optional[float] = None,
        cpu_usage: Optional[float] = None,
        memory_usage: Optional[float] = None,
        disk_usage: Optional[float] = None,
        cost_per_hour: Optional[float] = None,
        uptime_percentage: Optional[float] = None,
        custom_metrics: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record deployment metrics"""
        metric_id = f"metric_{deployment_id}_{uuid.uuid4().hex[:8]}"
        
        metrics = DeploymentMetrics(
            metric_id=metric_id,
            deployment_id=deployment_id,
            timestamp=datetime.now(timezone.utc),
            requests_per_minute=requests_per_minute,
            avg_response_time_ms=avg_response_time_ms,
            error_rate=error_rate,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            cost_per_hour=cost_per_hour,
            uptime_percentage=uptime_percentage,
            custom_metrics=custom_metrics
        )
        
        if self.storage_backend == "supabase":
            return self._record_metrics_supabase(metrics)
        elif self.storage_backend == "memory":
            return self._record_metrics_memory(metrics)
        else:
            return self._record_metrics_file(metrics)
    
    def get_deployment_metrics(
        self,
        deployment_id: str,
        hours: int = 24,
        limit: int = 1000
    ) -> List[DeploymentMetrics]:
        """Get deployment metrics for specified time period"""
        if self.storage_backend == "supabase":
            return self._get_metrics_supabase(deployment_id, hours, limit)
        elif self.storage_backend == "memory":
            return self._get_metrics_memory(deployment_id, hours, limit)
        else:
            return self._get_metrics_file(deployment_id, hours, limit)
    
    def get_deployment_statistics(self, deployment_id: str) -> Dict[str, Any]:
        """Get aggregated deployment statistics"""
        metrics = self.get_deployment_metrics(deployment_id, hours=24)
        
        if not metrics:
            return {"total_metrics": 0, "period_hours": 24}
        
        # Calculate basic statistics
        response_times = [m.avg_response_time_ms for m in metrics if m.avg_response_time_ms is not None]
        error_rates = [m.error_rate for m in metrics if m.error_rate is not None]
        cpu_usage = [m.cpu_usage for m in metrics if m.cpu_usage is not None]
        
        stats = {
            "total_metrics": len(metrics),
            "period_hours": 24,
            "latest_timestamp": max(m.timestamp for m in metrics).isoformat(),
            "avg_response_time_ms": sum(response_times) / len(response_times) if response_times else None,
            "avg_error_rate": sum(error_rates) / len(error_rates) if error_rates else None,
            "avg_cpu_usage": sum(cpu_usage) / len(cpu_usage) if cpu_usage else None,
            "total_requests": sum(m.requests_per_minute or 0 for m in metrics),
            "uptime_percentage": metrics[-1].uptime_percentage if metrics and metrics[-1].uptime_percentage else None
        }
        
        return stats
    
    # Service Registry Methods
    
    def register_service(
        self,
        deployment_id: str,
        service_name: str,
        service_type: str,
        endpoint_url: str,
        health_check_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a service in the service registry"""
        service_id = f"service_{deployment_id}_{uuid.uuid4().hex[:6]}"
        
        service = ServiceRegistryEntry(
            service_id=service_id,
            deployment_id=deployment_id,
            service_name=service_name,
            service_type=service_type,
            endpoint_url=endpoint_url,
            health_check_url=health_check_url,
            metadata=metadata
        )
        
        if self.storage_backend == "supabase":
            return self._register_service_supabase(service)
        elif self.storage_backend == "memory":
            return self._register_service_memory(service)
        else:
            return self._register_service_file(service)
    
    def update_service_health(
        self,
        service_id: str,
        health_status: str,
        last_check_time: Optional[datetime] = None
    ) -> bool:
        """Update service health status"""
        updates = {
            "health_status": health_status,
            "last_health_check": (last_check_time or datetime.now(timezone.utc)).isoformat()
        }
        
        if self.storage_backend == "supabase":
            return self._update_service_supabase(service_id, updates)
        elif self.storage_backend == "memory":
            return self._update_service_memory(service_id, updates)
        else:
            return self._update_service_file(service_id, updates)
    
    def list_services(
        self,
        deployment_id: Optional[str] = None,
        service_type: Optional[str] = None,
        is_active: bool = True
    ) -> List[ServiceRegistryEntry]:
        """List registered services"""
        if self.storage_backend == "supabase":
            return self._list_services_supabase(deployment_id, service_type, is_active)
        elif self.storage_backend == "memory":
            return self._list_services_memory(deployment_id, service_type, is_active)
        else:
            return self._list_services_file(deployment_id, service_type, is_active)
    
    def deregister_service(self, service_id: str) -> bool:
        """Deregister a service"""
        if self.storage_backend == "supabase":
            return self._deregister_service_supabase(service_id)
        elif self.storage_backend == "memory":
            return self._deregister_service_memory(service_id)
        else:
            return self._deregister_service_file(service_id)
    
    # Backend-specific implementations
    
    def _create_deployment_file(self, deployment: DeploymentRecord) -> str:
        """Create deployment in file system"""
        try:
            deployment_file = self.data_dir / "deployments" / f"{deployment.deployment_id}.json"
            deployment_data = asdict(deployment)
            
            # Convert datetime objects to ISO strings
            for key in ['created_at', 'updated_at', 'deployed_at', 'stopped_at']:
                if deployment_data[key] and isinstance(deployment_data[key], datetime):
                    deployment_data[key] = deployment_data[key].isoformat()
            
            with open(deployment_file, 'w') as f:
                json.dump(deployment_data, f, indent=2, ensure_ascii=False)
            
            return deployment.deployment_id
        except Exception as e:
            logger.error(f"Failed to create deployment in file system: {e}")
            raise
    
    def _create_deployment_memory(self, deployment: DeploymentRecord) -> str:
        """Create deployment in memory"""
        self.deployments[deployment.deployment_id] = deployment
        return deployment.deployment_id
    
    def _update_deployment_file(self, deployment_id: str, updates: Dict[str, Any]) -> bool:
        """Update deployment in file system"""
        try:
            deployment_file = self.data_dir / "deployments" / f"{deployment_id}.json"
            if not deployment_file.exists():
                return False
            
            with open(deployment_file, 'r') as f:
                deployment_data = json.load(f)
            
            deployment_data.update(updates)
            
            with open(deployment_file, 'w') as f:
                json.dump(deployment_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update deployment in file system: {e}")
            return False
    
    def _update_deployment_memory(self, deployment_id: str, updates: Dict[str, Any]) -> bool:
        """Update deployment in memory"""
        if deployment_id not in self.deployments:
            return False
        
        deployment_dict = asdict(self.deployments[deployment_id])
        deployment_dict.update(updates)
        
        # Convert datetime strings back to datetime objects if needed
        for key in ['created_at', 'updated_at', 'deployed_at', 'stopped_at']:
            if key in deployment_dict and isinstance(deployment_dict[key], str):
                deployment_dict[key] = datetime.fromisoformat(deployment_dict[key])
        
        self.deployments[deployment_id] = DeploymentRecord(**deployment_dict)
        return True
    
    def _get_deployment_file(self, deployment_id: str) -> Optional[DeploymentRecord]:
        """Get deployment from file system"""
        try:
            deployment_file = self.data_dir / "deployments" / f"{deployment_id}.json"
            if not deployment_file.exists():
                return None
            
            with open(deployment_file, 'r') as f:
                deployment_data = json.load(f)
            
            # Convert ISO strings back to datetime objects
            for key in ['created_at', 'updated_at', 'deployed_at', 'stopped_at']:
                if deployment_data[key]:
                    deployment_data[key] = datetime.fromisoformat(deployment_data[key])
            
            return DeploymentRecord(**deployment_data)
        except Exception as e:
            logger.error(f"Failed to get deployment from file system: {e}")
            return None
    
    def _get_deployment_memory(self, deployment_id: str) -> Optional[DeploymentRecord]:
        """Get deployment from memory"""
        return self.deployments.get(deployment_id)
    
    def _list_deployments_file(
        self, platform: Optional[str], environment: Optional[str], 
        user_id: Optional[str], project_name: Optional[str], limit: int
    ) -> List[DeploymentRecord]:
        """List deployments from file system"""
        try:
            deployments = []
            deployments_dir = self.data_dir / "deployments"
            
            for deployment_file in deployments_dir.glob("*.json"):
                with open(deployment_file, 'r') as f:
                    deployment_data = json.load(f)
                
                # Apply filters
                if platform and deployment_data.get('platform') != platform:
                    continue
                if environment and deployment_data.get('environment') != environment:
                    continue
                if user_id and deployment_data.get('user_id') != user_id:
                    continue
                if project_name and deployment_data.get('project_name') != project_name:
                    continue
                
                # Convert datetime fields
                for key in ['created_at', 'updated_at', 'deployed_at', 'stopped_at']:
                    if deployment_data[key]:
                        deployment_data[key] = datetime.fromisoformat(deployment_data[key])
                
                deployments.append(DeploymentRecord(**deployment_data))
                
                if len(deployments) >= limit:
                    break
            
            return sorted(deployments, key=lambda x: x.created_at, reverse=True)
        except Exception as e:
            logger.error(f"Failed to list deployments from file system: {e}")
            return []
    
    def _list_deployments_memory(
        self, platform: Optional[str], environment: Optional[str], 
        user_id: Optional[str], project_name: Optional[str], limit: int
    ) -> List[DeploymentRecord]:
        """List deployments from memory"""
        deployments = []
        
        for deployment in self.deployments.values():
            # Apply filters
            if platform and deployment.platform != platform:
                continue
            if environment and deployment.environment != environment:
                continue
            if user_id and deployment.user_id != user_id:
                continue
            if project_name and deployment.project_name != project_name:
                continue
            
            deployments.append(deployment)
            
            if len(deployments) >= limit:
                break
        
        return sorted(deployments, key=lambda x: x.created_at, reverse=True)
    
    def _record_metrics_file(self, metrics: DeploymentMetrics) -> str:
        """Record metrics in file system"""
        try:
            metrics_file = self.data_dir / "metrics" / f"{metrics.metric_id}.json"
            metrics_data = asdict(metrics)
            
            if metrics_data['timestamp'] and isinstance(metrics_data['timestamp'], datetime):
                metrics_data['timestamp'] = metrics_data['timestamp'].isoformat()
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
            
            return metrics.metric_id
        except Exception as e:
            logger.error(f"Failed to record metrics in file system: {e}")
            raise
    
    def _record_metrics_memory(self, metrics: DeploymentMetrics) -> str:
        """Record metrics in memory"""
        if metrics.deployment_id not in self.metrics:
            self.metrics[metrics.deployment_id] = []
        self.metrics[metrics.deployment_id].append(metrics)
        return metrics.metric_id
    
    def _get_metrics_file(self, deployment_id: str, hours: int, limit: int) -> List[DeploymentMetrics]:
        """Get metrics from file system"""
        try:
            metrics = []
            metrics_dir = self.data_dir / "metrics"
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            for metrics_file in metrics_dir.glob("*.json"):
                with open(metrics_file, 'r') as f:
                    metrics_data = json.load(f)
                
                if metrics_data.get('deployment_id') != deployment_id:
                    continue
                
                if metrics_data['timestamp']:
                    timestamp = datetime.fromisoformat(metrics_data['timestamp'])
                    if timestamp < cutoff_time:
                        continue
                    metrics_data['timestamp'] = timestamp
                
                metrics.append(DeploymentMetrics(**metrics_data))
                
                if len(metrics) >= limit:
                    break
            
            return sorted(metrics, key=lambda x: x.timestamp, reverse=True)
        except Exception as e:
            logger.error(f"Failed to get metrics from file system: {e}")
            return []
    
    def _get_metrics_memory(self, deployment_id: str, hours: int, limit: int) -> List[DeploymentMetrics]:
        """Get metrics from memory"""
        from datetime import timedelta
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        deployment_metrics = self.metrics.get(deployment_id, [])
        filtered_metrics = [
            m for m in deployment_metrics 
            if m.timestamp >= cutoff_time
        ]
        
        return sorted(filtered_metrics[:limit], key=lambda x: x.timestamp, reverse=True)
    
    # Service registry implementations (simplified)
    def _register_service_file(self, service: ServiceRegistryEntry) -> str:
        """Register service in file system"""
        try:
            service_file = self.data_dir / "services" / f"{service.service_id}.json"
            service_data = asdict(service)
            
            if service_data['created_at'] and isinstance(service_data['created_at'], datetime):
                service_data['created_at'] = service_data['created_at'].isoformat()
            if service_data['last_health_check'] and isinstance(service_data['last_health_check'], datetime):
                service_data['last_health_check'] = service_data['last_health_check'].isoformat()
            
            with open(service_file, 'w') as f:
                json.dump(service_data, f, indent=2, ensure_ascii=False)
            
            return service.service_id
        except Exception as e:
            logger.error(f"Failed to register service in file system: {e}")
            raise
    
    def _register_service_memory(self, service: ServiceRegistryEntry) -> str:
        """Register service in memory"""
        self.services[service.service_id] = service
        return service.service_id
    
    # Placeholder implementations for Supabase backend
    def _create_deployment_supabase(self, deployment: DeploymentRecord) -> str:
        return deployment.deployment_id  # Implementation needed
    
    def _update_deployment_supabase(self, deployment_id: str, updates: Dict[str, Any]) -> bool:
        return False  # Implementation needed
    
    def _get_deployment_supabase(self, deployment_id: str) -> Optional[DeploymentRecord]:
        return None  # Implementation needed
    
    def _list_deployments_supabase(self, platform, environment, user_id, project_name, limit) -> List[DeploymentRecord]:
        return []  # Implementation needed
    
    def _delete_deployment_supabase(self, deployment_id: str) -> bool:
        return False  # Implementation needed
    
    def _delete_deployment_file(self, deployment_id: str) -> bool:
        try:
            deployment_file = self.data_dir / "deployments" / f"{deployment_id}.json"
            if deployment_file.exists():
                deployment_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to delete deployment from file system: {e}")
            return False
    
    def _delete_deployment_memory(self, deployment_id: str) -> bool:
        return self.deployments.pop(deployment_id, None) is not None
    
    # Additional placeholder implementations
    def _record_metrics_supabase(self, metrics: DeploymentMetrics) -> str:
        return metrics.metric_id
    
    def _get_metrics_supabase(self, deployment_id: str, hours: int, limit: int) -> List[DeploymentMetrics]:
        return []
    
    def _register_service_supabase(self, service: ServiceRegistryEntry) -> str:
        return service.service_id
    
    def _update_service_supabase(self, service_id: str, updates: Dict[str, Any]) -> bool:
        return False
    
    def _update_service_memory(self, service_id: str, updates: Dict[str, Any]) -> bool:
        if service_id not in self.services:
            return False
        
        service_dict = asdict(self.services[service_id])
        service_dict.update(updates)
        
        # Convert datetime strings back if needed
        for key in ['created_at', 'last_health_check']:
            if key in service_dict and isinstance(service_dict[key], str):
                service_dict[key] = datetime.fromisoformat(service_dict[key])
        
        self.services[service_id] = ServiceRegistryEntry(**service_dict)
        return True
    
    def _update_service_file(self, service_id: str, updates: Dict[str, Any]) -> bool:
        try:
            service_file = self.data_dir / "services" / f"{service_id}.json"
            if not service_file.exists():
                return False
            
            with open(service_file, 'r') as f:
                service_data = json.load(f)
            
            service_data.update(updates)
            
            with open(service_file, 'w') as f:
                json.dump(service_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update service in file system: {e}")
            return False
    
    def _list_services_supabase(self, deployment_id, service_type, is_active) -> List[ServiceRegistryEntry]:
        return []
    
    def _list_services_memory(self, deployment_id, service_type, is_active) -> List[ServiceRegistryEntry]:
        services = []
        for service in self.services.values():
            if deployment_id and service.deployment_id != deployment_id:
                continue
            if service_type and service.service_type != service_type:
                continue
            if service.is_active != is_active:
                continue
            services.append(service)
        return services
    
    def _list_services_file(self, deployment_id, service_type, is_active) -> List[ServiceRegistryEntry]:
        try:
            services = []
            services_dir = self.data_dir / "services"
            
            for service_file in services_dir.glob("*.json"):
                with open(service_file, 'r') as f:
                    service_data = json.load(f)
                
                if deployment_id and service_data.get('deployment_id') != deployment_id:
                    continue
                if service_type and service_data.get('service_type') != service_type:
                    continue
                if service_data.get('is_active') != is_active:
                    continue
                
                # Convert datetime fields
                for key in ['created_at', 'last_health_check']:
                    if service_data[key]:
                        service_data[key] = datetime.fromisoformat(service_data[key])
                
                services.append(ServiceRegistryEntry(**service_data))
            
            return services
        except Exception as e:
            logger.error(f"Failed to list services from file system: {e}")
            return []
    
    def _deregister_service_supabase(self, service_id: str) -> bool:
        return False
    
    def _deregister_service_memory(self, service_id: str) -> bool:
        return self.services.pop(service_id, None) is not None
    
    def _deregister_service_file(self, service_id: str) -> bool:
        try:
            service_file = self.data_dir / "services" / f"{service_id}.json"
            if service_file.exists():
                service_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to deregister service from file system: {e}")
            return False