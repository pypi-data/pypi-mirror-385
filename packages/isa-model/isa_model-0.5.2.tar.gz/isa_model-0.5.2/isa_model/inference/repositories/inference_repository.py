"""
Inference Repository - Data persistence layer for inference operations

Provides standardized data access for inference requests, usage statistics, and history
following the ISA Model architecture pattern.
"""

import logging
import json
import uuid
from datetime import datetime, timezone, timedelta
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

class InferenceStatus(str, Enum):
    """Inference status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

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

@dataclass
class InferenceRequest:
    """Inference request record"""
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
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

@dataclass
class UsageStatistics:
    """Usage statistics record"""
    stat_id: str
    period_start: datetime
    period_end: datetime
    service_type: str
    model_id: Optional[str] = None
    provider: Optional[str] = None
    user_id: Optional[str] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    requests_per_hour: float = 0.0
    error_rate: float = 0.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

@dataclass
class ModelUsageSnapshot:
    """Model usage snapshot for quick analytics"""
    snapshot_id: str
    model_id: str
    provider: str
    snapshot_time: datetime
    hourly_requests: int = 0
    daily_requests: int = 0
    weekly_requests: int = 0
    monthly_requests: int = 0
    total_tokens_today: int = 0
    total_cost_today: float = 0.0
    avg_response_time_today: float = 0.0
    success_rate_today: float = 100.0
    last_used: Optional[datetime] = None
    
    def __post_init__(self):
        if self.snapshot_time is None:
            self.snapshot_time = datetime.now(timezone.utc)

class InferenceRepository:
    """
    Repository for inference data persistence
    
    Supports multiple backend storage options:
    1. Supabase (preferred for centralized storage)
    2. Local file system (fallback for development)
    3. In-memory storage (for testing)
    """
    
    def __init__(self, storage_backend: str = "auto", **kwargs):
        """
        Initialize inference repository
        
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
        
        logger.info(f"Inference repository initialized with {self.storage_backend} backend")
    
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
            logger.info("Supabase backend initialized for inference")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase backend: {e}")
            self.storage_backend = "file"
            self._init_file_system()
    
    def _init_file_system(self):
        """Initialize file system backend"""
        self.data_dir = Path(self.config.get("data_dir", "./inference_data"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.data_dir / "requests").mkdir(exist_ok=True)
        (self.data_dir / "statistics").mkdir(exist_ok=True)
        (self.data_dir / "snapshots").mkdir(exist_ok=True)
        
        logger.info(f"File system backend initialized: {self.data_dir}")
    
    def _init_memory(self):
        """Initialize in-memory backend for testing"""
        self.requests = {}
        self.statistics = {}
        self.snapshots = {}
        logger.info("In-memory backend initialized for inference")
    
    def _ensure_supabase_tables(self):
        """Ensure required Supabase tables exist"""
        try:
            self.supabase_client.table("inference_requests").select("request_id").limit(1).execute()
            self.supabase_client.table("usage_statistics").select("stat_id").limit(1).execute()
            self.supabase_client.table("model_usage_snapshots").select("snapshot_id").limit(1).execute()
        except Exception as e:
            logger.warning(f"Some inference tables may not exist in Supabase: {e}")
    
    # Request Management Methods
    
    def create_inference_request(
        self,
        service_type: str,
        model_id: str,
        provider: str,
        endpoint: str,
        request_data: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new inference request record"""
        request_id = f"inf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        request = InferenceRequest(
            request_id=request_id,
            service_type=service_type,
            model_id=model_id,
            provider=provider,
            endpoint=endpoint,
            request_data=request_data,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata
        )
        
        if self.storage_backend == "supabase":
            return self._create_request_supabase(request)
        elif self.storage_backend == "memory":
            return self._create_request_memory(request)
        else:
            return self._create_request_file(request)
    
    def update_inference_status(
        self,
        request_id: str,
        status: str,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
        cost_usd: Optional[float] = None,
        additional_updates: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update inference request status and results"""
        updates = {"status": status}
        
        if status == InferenceStatus.PROCESSING:
            updates["started_at"] = datetime.now(timezone.utc).isoformat()
        elif status in [InferenceStatus.COMPLETED, InferenceStatus.FAILED, InferenceStatus.TIMEOUT]:
            updates["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        if response_data:
            updates["response_data"] = response_data
        if error_message:
            updates["error_message"] = error_message
        if execution_time_ms:
            updates["execution_time_ms"] = execution_time_ms
        if tokens_used:
            updates["tokens_used"] = tokens_used
        if cost_usd:
            updates["cost_usd"] = cost_usd
        
        if additional_updates:
            updates.update(additional_updates)
        
        if self.storage_backend == "supabase":
            return self._update_request_supabase(request_id, updates)
        elif self.storage_backend == "memory":
            return self._update_request_memory(request_id, updates)
        else:
            return self._update_request_file(request_id, updates)
    
    def get_inference_request(self, request_id: str) -> Optional[InferenceRequest]:
        """Get inference request by ID"""
        if self.storage_backend == "supabase":
            return self._get_request_supabase(request_id)
        elif self.storage_backend == "memory":
            return self._get_request_memory(request_id)
        else:
            return self._get_request_file(request_id)
    
    def list_recent_requests(
        self,
        service_type: Optional[str] = None,
        model_id: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[InferenceRequest]:
        """List recent inference requests with optional filtering"""
        if self.storage_backend == "supabase":
            return self._list_requests_supabase(service_type, model_id, user_id, status, hours, limit)
        elif self.storage_backend == "memory":
            return self._list_requests_memory(service_type, model_id, user_id, status, hours, limit)
        else:
            return self._list_requests_file(service_type, model_id, user_id, status, hours, limit)
    
    # Usage Statistics Methods
    
    def record_usage_statistics(
        self,
        period_start: datetime,
        period_end: datetime,
        service_type: str,
        model_id: Optional[str] = None,
        provider: Optional[str] = None,
        user_id: Optional[str] = None,
        total_requests: int = 0,
        successful_requests: int = 0,
        failed_requests: int = 0,
        total_tokens: int = 0,
        total_cost_usd: float = 0.0,
        avg_response_time_ms: float = 0.0,
        p95_response_time_ms: float = 0.0,
        requests_per_hour: float = 0.0,
        error_rate: float = 0.0
    ) -> str:
        """Record usage statistics for a time period"""
        stat_id = f"stat_{period_start.strftime('%Y%m%d_%H')}_{uuid.uuid4().hex[:6]}"
        
        stats = UsageStatistics(
            stat_id=stat_id,
            period_start=period_start,
            period_end=period_end,
            service_type=service_type,
            model_id=model_id,
            provider=provider,
            user_id=user_id,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_tokens=total_tokens,
            total_cost_usd=total_cost_usd,
            avg_response_time_ms=avg_response_time_ms,
            p95_response_time_ms=p95_response_time_ms,
            requests_per_hour=requests_per_hour,
            error_rate=error_rate
        )
        
        if self.storage_backend == "supabase":
            return self._record_stats_supabase(stats)
        elif self.storage_backend == "memory":
            return self._record_stats_memory(stats)
        else:
            return self._record_stats_file(stats)
    
    def get_usage_statistics(
        self,
        service_type: Optional[str] = None,
        model_id: Optional[str] = None,
        user_id: Optional[str] = None,
        days: int = 7,
        limit: int = 100
    ) -> List[UsageStatistics]:
        """Get usage statistics for specified period"""
        if self.storage_backend == "supabase":
            return self._get_stats_supabase(service_type, model_id, user_id, days, limit)
        elif self.storage_backend == "memory":
            return self._get_stats_memory(service_type, model_id, user_id, days, limit)
        else:
            return self._get_stats_file(service_type, model_id, user_id, days, limit)
    
    def get_aggregated_usage(
        self,
        service_type: Optional[str] = None,
        model_id: Optional[str] = None,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get aggregated usage statistics"""
        stats = self.get_usage_statistics(service_type, model_id, user_id, days, 1000)
        
        if not stats:
            return {
                "total_requests": 0,
                "total_cost_usd": 0.0,
                "total_tokens": 0,
                "avg_response_time_ms": 0.0,
                "success_rate": 100.0,
                "period_days": days
            }
        
        total_requests = sum(s.total_requests for s in stats)
        total_successful = sum(s.successful_requests for s in stats)
        total_cost = sum(s.total_cost_usd for s in stats)
        total_tokens = sum(s.total_tokens for s in stats)
        
        # Weighted average for response time
        weighted_response_times = [s.avg_response_time_ms * s.total_requests for s in stats if s.total_requests > 0]
        avg_response_time = sum(weighted_response_times) / total_requests if total_requests > 0 else 0.0
        
        success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 100.0
        
        return {
            "total_requests": total_requests,
            "successful_requests": total_successful,
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "avg_response_time_ms": round(avg_response_time, 2),
            "success_rate": round(success_rate, 2),
            "period_days": days,
            "stats_count": len(stats)
        }
    
    # Model Usage Snapshots Methods
    
    def update_model_snapshot(
        self,
        model_id: str,
        provider: str,
        hourly_requests: int = 0,
        daily_requests: int = 0,
        weekly_requests: int = 0,
        monthly_requests: int = 0,
        total_tokens_today: int = 0,
        total_cost_today: float = 0.0,
        avg_response_time_today: float = 0.0,
        success_rate_today: float = 100.0
    ) -> str:
        """Update or create model usage snapshot"""
        snapshot_id = f"snap_{model_id}_{provider}_{datetime.now().strftime('%Y%m%d')}"
        
        snapshot = ModelUsageSnapshot(
            snapshot_id=snapshot_id,
            model_id=model_id,
            provider=provider,
            snapshot_time=datetime.now(timezone.utc),
            hourly_requests=hourly_requests,
            daily_requests=daily_requests,
            weekly_requests=weekly_requests,
            monthly_requests=monthly_requests,
            total_tokens_today=total_tokens_today,
            total_cost_today=total_cost_today,
            avg_response_time_today=avg_response_time_today,
            success_rate_today=success_rate_today,
            last_used=datetime.now(timezone.utc)
        )
        
        if self.storage_backend == "supabase":
            return self._update_snapshot_supabase(snapshot)
        elif self.storage_backend == "memory":
            return self._update_snapshot_memory(snapshot)
        else:
            return self._update_snapshot_file(snapshot)
    
    def get_model_snapshots(
        self,
        model_id: Optional[str] = None,
        provider: Optional[str] = None,
        days: int = 7
    ) -> List[ModelUsageSnapshot]:
        """Get model usage snapshots"""
        if self.storage_backend == "supabase":
            return self._get_snapshots_supabase(model_id, provider, days)
        elif self.storage_backend == "memory":
            return self._get_snapshots_memory(model_id, provider, days)
        else:
            return self._get_snapshots_file(model_id, provider, days)
    
    def get_top_models(self, metric: str = "daily_requests", limit: int = 10) -> List[Dict[str, Any]]:
        """Get top models by specified metric"""
        snapshots = self.get_model_snapshots(days=1)  # Get latest snapshots
        
        if not snapshots:
            return []
        
        # Sort by the specified metric
        valid_metrics = ["hourly_requests", "daily_requests", "weekly_requests", "monthly_requests", 
                        "total_tokens_today", "total_cost_today"]
        
        if metric not in valid_metrics:
            metric = "daily_requests"
        
        sorted_snapshots = sorted(
            snapshots, 
            key=lambda x: getattr(x, metric, 0), 
            reverse=True
        )[:limit]
        
        return [
            {
                "model_id": s.model_id,
                "provider": s.provider,
                "metric_value": getattr(s, metric, 0),
                "daily_requests": s.daily_requests,
                "total_cost_today": s.total_cost_today,
                "success_rate_today": s.success_rate_today,
                "last_used": s.last_used.isoformat() if s.last_used else None
            }
            for s in sorted_snapshots
        ]
    
    # Cleanup and Maintenance Methods
    
    def cleanup_old_requests(self, days: int = 30) -> int:
        """Clean up old inference requests"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        if self.storage_backend == "supabase":
            return self._cleanup_requests_supabase(cutoff_date)
        elif self.storage_backend == "memory":
            return self._cleanup_requests_memory(cutoff_date)
        else:
            return self._cleanup_requests_file(cutoff_date)
    
    def cleanup_old_statistics(self, days: int = 90) -> int:
        """Clean up old usage statistics"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        if self.storage_backend == "supabase":
            return self._cleanup_stats_supabase(cutoff_date)
        elif self.storage_backend == "memory":
            return self._cleanup_stats_memory(cutoff_date)
        else:
            return self._cleanup_stats_file(cutoff_date)
    
    # Backend-specific implementations
    
    def _create_request_file(self, request: InferenceRequest) -> str:
        """Create request in file system"""
        try:
            request_file = self.data_dir / "requests" / f"{request.request_id}.json"
            request_data = asdict(request)
            
            # Convert datetime objects to ISO strings
            for key in ['created_at', 'started_at', 'completed_at']:
                if request_data[key] and isinstance(request_data[key], datetime):
                    request_data[key] = request_data[key].isoformat()
            
            with open(request_file, 'w') as f:
                json.dump(request_data, f, indent=2, ensure_ascii=False)
            
            return request.request_id
        except Exception as e:
            logger.error(f"Failed to create request in file system: {e}")
            raise
    
    def _create_request_memory(self, request: InferenceRequest) -> str:
        """Create request in memory"""
        self.requests[request.request_id] = request
        return request.request_id
    
    def _update_request_file(self, request_id: str, updates: Dict[str, Any]) -> bool:
        """Update request in file system"""
        try:
            request_file = self.data_dir / "requests" / f"{request_id}.json"
            if not request_file.exists():
                return False
            
            with open(request_file, 'r') as f:
                request_data = json.load(f)
            
            request_data.update(updates)
            
            with open(request_file, 'w') as f:
                json.dump(request_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update request in file system: {e}")
            return False
    
    def _update_request_memory(self, request_id: str, updates: Dict[str, Any]) -> bool:
        """Update request in memory"""
        if request_id not in self.requests:
            return False
        
        request_dict = asdict(self.requests[request_id])
        request_dict.update(updates)
        
        # Convert datetime strings back to datetime objects if needed
        for key in ['created_at', 'started_at', 'completed_at']:
            if key in request_dict and isinstance(request_dict[key], str):
                request_dict[key] = datetime.fromisoformat(request_dict[key])
        
        self.requests[request_id] = InferenceRequest(**request_dict)
        return True
    
    def _get_request_file(self, request_id: str) -> Optional[InferenceRequest]:
        """Get request from file system"""
        try:
            request_file = self.data_dir / "requests" / f"{request_id}.json"
            if not request_file.exists():
                return None
            
            with open(request_file, 'r') as f:
                request_data = json.load(f)
            
            # Convert ISO strings back to datetime objects
            for key in ['created_at', 'started_at', 'completed_at']:
                if request_data[key]:
                    request_data[key] = datetime.fromisoformat(request_data[key])
            
            return InferenceRequest(**request_data)
        except Exception as e:
            logger.error(f"Failed to get request from file system: {e}")
            return None
    
    def _get_request_memory(self, request_id: str) -> Optional[InferenceRequest]:
        """Get request from memory"""
        return self.requests.get(request_id)
    
    def _list_requests_file(
        self, service_type: Optional[str], model_id: Optional[str], 
        user_id: Optional[str], status: Optional[str], hours: int, limit: int
    ) -> List[InferenceRequest]:
        """List requests from file system"""
        try:
            requests = []
            requests_dir = self.data_dir / "requests"
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            for request_file in requests_dir.glob("*.json"):
                with open(request_file, 'r') as f:
                    request_data = json.load(f)
                
                # Convert datetime fields
                for key in ['created_at', 'started_at', 'completed_at']:
                    if request_data[key]:
                        request_data[key] = datetime.fromisoformat(request_data[key])
                
                request = InferenceRequest(**request_data)
                
                # Apply filters
                if request.created_at < cutoff_time:
                    continue
                if service_type and request.service_type != service_type:
                    continue
                if model_id and request.model_id != model_id:
                    continue
                if user_id and request.user_id != user_id:
                    continue
                if status and request.status != status:
                    continue
                
                requests.append(request)
                
                if len(requests) >= limit:
                    break
            
            return sorted(requests, key=lambda x: x.created_at, reverse=True)
        except Exception as e:
            logger.error(f"Failed to list requests from file system: {e}")
            return []
    
    def _list_requests_memory(
        self, service_type: Optional[str], model_id: Optional[str], 
        user_id: Optional[str], status: Optional[str], hours: int, limit: int
    ) -> List[InferenceRequest]:
        """List requests from memory"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        requests = []
        
        for request in self.requests.values():
            # Apply filters
            if request.created_at < cutoff_time:
                continue
            if service_type and request.service_type != service_type:
                continue
            if model_id and request.model_id != model_id:
                continue
            if user_id and request.user_id != user_id:
                continue
            if status and request.status != status:
                continue
            
            requests.append(request)
            
            if len(requests) >= limit:
                break
        
        return sorted(requests, key=lambda x: x.created_at, reverse=True)
    
    # Simplified placeholder implementations for statistics and snapshots
    def _record_stats_file(self, stats: UsageStatistics) -> str:
        """Record statistics in file system"""
        try:
            stats_file = self.data_dir / "statistics" / f"{stats.stat_id}.json"
            stats_data = asdict(stats)
            
            # Convert datetime objects to ISO strings
            for key in ['period_start', 'period_end', 'created_at']:
                if stats_data[key] and isinstance(stats_data[key], datetime):
                    stats_data[key] = stats_data[key].isoformat()
            
            with open(stats_file, 'w') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False)
            
            return stats.stat_id
        except Exception as e:
            logger.error(f"Failed to record statistics in file system: {e}")
            raise
    
    def _record_stats_memory(self, stats: UsageStatistics) -> str:
        """Record statistics in memory"""
        self.statistics[stats.stat_id] = stats
        return stats.stat_id
    
    def _update_snapshot_file(self, snapshot: ModelUsageSnapshot) -> str:
        """Update snapshot in file system"""
        try:
            snapshot_file = self.data_dir / "snapshots" / f"{snapshot.snapshot_id}.json"
            snapshot_data = asdict(snapshot)
            
            # Convert datetime objects to ISO strings
            for key in ['snapshot_time', 'last_used']:
                if snapshot_data[key] and isinstance(snapshot_data[key], datetime):
                    snapshot_data[key] = snapshot_data[key].isoformat()
            
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
            
            return snapshot.snapshot_id
        except Exception as e:
            logger.error(f"Failed to update snapshot in file system: {e}")
            raise
    
    def _update_snapshot_memory(self, snapshot: ModelUsageSnapshot) -> str:
        """Update snapshot in memory"""
        self.snapshots[snapshot.snapshot_id] = snapshot
        return snapshot.snapshot_id
    
    # Cleanup implementations
    def _cleanup_requests_file(self, cutoff_date: datetime) -> int:
        """Cleanup old requests from file system"""
        count = 0
        try:
            requests_dir = self.data_dir / "requests"
            for request_file in requests_dir.glob("*.json"):
                if request_file.stat().st_mtime < cutoff_date.timestamp():
                    request_file.unlink()
                    count += 1
        except Exception as e:
            logger.error(f"Failed to cleanup requests from file system: {e}")
        return count
    
    def _cleanup_requests_memory(self, cutoff_date: datetime) -> int:
        """Cleanup old requests from memory"""
        count = 0
        to_remove = []
        for request_id, request in self.requests.items():
            if request.created_at < cutoff_date:
                to_remove.append(request_id)
        
        for request_id in to_remove:
            del self.requests[request_id]
            count += 1
        
        return count
    
    # Placeholder implementations for Supabase backend
    def _create_request_supabase(self, request: InferenceRequest) -> str:
        return request.request_id  # Implementation needed
    
    def _update_request_supabase(self, request_id: str, updates: Dict[str, Any]) -> bool:
        return False  # Implementation needed
    
    def _get_request_supabase(self, request_id: str) -> Optional[InferenceRequest]:
        return None  # Implementation needed
    
    def _list_requests_supabase(self, service_type, model_id, user_id, status, hours, limit) -> List[InferenceRequest]:
        return []  # Implementation needed
    
    def _record_stats_supabase(self, stats: UsageStatistics) -> str:
        return stats.stat_id  # Implementation needed
    
    def _get_stats_supabase(self, service_type, model_id, user_id, days, limit) -> List[UsageStatistics]:
        return []  # Implementation needed
    
    def _get_stats_memory(self, service_type, model_id, user_id, days, limit) -> List[UsageStatistics]:
        return list(self.statistics.values())[:limit]
    
    def _get_stats_file(self, service_type, model_id, user_id, days, limit) -> List[UsageStatistics]:
        return []  # Implementation needed
    
    def _update_snapshot_supabase(self, snapshot: ModelUsageSnapshot) -> str:
        return snapshot.snapshot_id  # Implementation needed
    
    def _get_snapshots_supabase(self, model_id, provider, days) -> List[ModelUsageSnapshot]:
        return []  # Implementation needed
    
    def _get_snapshots_memory(self, model_id, provider, days) -> List[ModelUsageSnapshot]:
        return list(self.snapshots.values())
    
    def _get_snapshots_file(self, model_id, provider, days) -> List[ModelUsageSnapshot]:
        return []  # Implementation needed
    
    def _cleanup_requests_supabase(self, cutoff_date: datetime) -> int:
        return 0  # Implementation needed
    
    def _cleanup_stats_supabase(self, cutoff_date: datetime) -> int:
        return 0  # Implementation needed
    
    def _cleanup_stats_memory(self, cutoff_date: datetime) -> int:
        count = 0
        to_remove = []
        for stat_id, stat in self.statistics.items():
            if stat.created_at < cutoff_date:
                to_remove.append(stat_id)
        
        for stat_id in to_remove:
            del self.statistics[stat_id]
            count += 1
        
        return count
    
    def _cleanup_stats_file(self, cutoff_date: datetime) -> int:
        count = 0
        try:
            stats_dir = self.data_dir / "statistics"
            for stats_file in stats_dir.glob("*.json"):
                if stats_file.stat().st_mtime < cutoff_date.timestamp():
                    stats_file.unlink()
                    count += 1
        except Exception as e:
            logger.error(f"Failed to cleanup statistics from file system: {e}")
        return count