"""
Logs API Routes

Handles log retrieval, filtering, and streaming for the ISA Model Platform
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
import logging
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory log storage (in production, use a proper logging system like ELK, Grafana Loki, etc.)
logs_storage = []
max_logs = 10000  # Limit logs in memory

class LogEntry(BaseModel):
    timestamp: float
    level: str
    service: str
    component: Optional[str] = None
    message: str
    request_id: Optional[str] = None
    duration: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None

class LogFilter(BaseModel):
    level: Optional[str] = None
    service: Optional[str] = None
    component: Optional[str] = None
    time_range: Optional[str] = "24h"
    since: Optional[float] = None
    limit: Optional[int] = 1000
    search: Optional[str] = None

def add_log_entry(
    level: str,
    service: str,
    message: str,
    component: Optional[str] = None,
    request_id: Optional[str] = None,
    duration: Optional[float] = None,
    details: Optional[Dict[str, Any]] = None,
    stack_trace: Optional[str] = None
):
    """Add a log entry to the storage"""
    global logs_storage
    
    log_entry = {
        "timestamp": time.time() * 1000,  # Convert to milliseconds
        "level": level,
        "service": service,
        "component": component,
        "message": message,
        "request_id": request_id,
        "duration": duration,
        "details": details,
        "stack_trace": stack_trace
    }
    
    # Add to beginning of list (newest first)
    logs_storage.insert(0, log_entry)
    
    # Limit storage size
    if len(logs_storage) > max_logs:
        logs_storage = logs_storage[:max_logs]

def get_time_range_timestamp(time_range: str) -> float:
    """Convert time range string to timestamp"""
    now = time.time() * 1000
    
    time_ranges = {
        "1h": now - (1 * 60 * 60 * 1000),
        "6h": now - (6 * 60 * 60 * 1000),
        "24h": now - (24 * 60 * 60 * 1000),
        "7d": now - (7 * 24 * 60 * 60 * 1000),
        "30d": now - (30 * 24 * 60 * 60 * 1000)
    }
    
    return time_ranges.get(time_range, now - (24 * 60 * 60 * 1000))

def filter_logs(logs: List[Dict], filters: LogFilter) -> List[Dict]:
    """Apply filters to log list"""
    filtered_logs = logs
    
    # Time range filter
    if filters.time_range:
        since_timestamp = get_time_range_timestamp(filters.time_range)
        filtered_logs = [log for log in filtered_logs if log["timestamp"] >= since_timestamp]
    
    # Since timestamp filter (for streaming)
    if filters.since:
        filtered_logs = [log for log in filtered_logs if log["timestamp"] > filters.since]
    
    # Level filter
    if filters.level:
        filtered_logs = [log for log in filtered_logs if log["level"] == filters.level]
    
    # Service filter
    if filters.service:
        filtered_logs = [log for log in filtered_logs if log["service"] == filters.service]
    
    # Component filter
    if filters.component:
        filtered_logs = [log for log in filtered_logs if log.get("component") == filters.component]
    
    # Search filter
    if filters.search:
        search_term = filters.search.lower()
        filtered_logs = [
            log for log in filtered_logs
            if search_term in log["message"].lower() or
               search_term in log["service"].lower() or
               (log.get("component") and search_term in log["component"].lower())
        ]
    
    # Limit results
    if filters.limit:
        filtered_logs = filtered_logs[:filters.limit]
    
    return filtered_logs

@router.get("/")
async def get_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    service: Optional[str] = Query(None, description="Filter by service"),
    component: Optional[str] = Query(None, description="Filter by component"),
    time_range: Optional[str] = Query("24h", description="Time range (1h, 6h, 24h, 7d, 30d)"),
    limit: Optional[int] = Query(1000, description="Maximum number of logs"),
    search: Optional[str] = Query(None, description="Search term")
):
    """
    Get filtered logs
    """
    try:
        filters = LogFilter(
            level=level,
            service=service,
            component=component,
            time_range=time_range,
            limit=limit,
            search=search
        )
        
        # If no logs in storage, generate some sample logs
        if not logs_storage:
            populate_sample_logs()
        
        filtered_logs = filter_logs(logs_storage, filters)
        
        return {
            "logs": filtered_logs,
            "total": len(logs_storage),
            "filtered": len(filtered_logs),
            "filters": filters.dict()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")

@router.get("/stream")
async def get_logs_stream(
    since: Optional[float] = Query(None, description="Get logs since timestamp"),
    level: Optional[str] = Query(None, description="Filter by log level"),
    service: Optional[str] = Query(None, description="Filter by service"),
    limit: Optional[int] = Query(50, description="Maximum number of logs")
):
    """
    Get new logs for streaming (since a specific timestamp)
    """
    try:
        filters = LogFilter(
            level=level,
            service=service,
            since=since,
            limit=limit
        )
        
        # Generate some new sample logs periodically
        if len(logs_storage) < 20:
            add_sample_log()
        
        filtered_logs = filter_logs(logs_storage, filters)
        
        return filtered_logs
        
    except Exception as e:
        logger.error(f"Error streaming logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stream logs: {str(e)}")

@router.post("/")
async def add_log(log_entry: LogEntry):
    """
    Add a new log entry
    """
    try:
        add_log_entry(
            level=log_entry.level,
            service=log_entry.service,
            message=log_entry.message,
            component=log_entry.component,
            request_id=log_entry.request_id,
            duration=log_entry.duration,
            details=log_entry.details,
            stack_trace=log_entry.stack_trace
        )
        
        return {"success": True, "message": "Log entry added"}
        
    except Exception as e:
        logger.error(f"Error adding log entry: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add log entry: {str(e)}")

@router.get("/stats")
async def get_log_stats():
    """
    Get log statistics
    """
    try:
        if not logs_storage:
            populate_sample_logs()
        
        # Calculate statistics
        one_hour_ago = time.time() * 1000 - (60 * 60 * 1000)
        
        stats = {
            "total_logs": len(logs_storage),
            "logs_last_hour": len([log for log in logs_storage if log["timestamp"] > one_hour_ago]),
            "by_level": defaultdict(int),
            "by_service": defaultdict(int),
            "errors_last_hour": 0,
            "warnings_last_hour": 0
        }
        
        for log in logs_storage:
            stats["by_level"][log["level"]] += 1
            stats["by_service"][log["service"]] += 1
            
            if log["timestamp"] > one_hour_ago:
                if log["level"] == "ERROR":
                    stats["errors_last_hour"] += 1
                elif log["level"] == "WARNING":
                    stats["warnings_last_hour"] += 1
        
        # Convert defaultdict to regular dict for JSON serialization
        stats["by_level"] = dict(stats["by_level"])
        stats["by_service"] = dict(stats["by_service"])
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting log stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get log stats: {str(e)}")

@router.delete("/")
async def clear_logs():
    """
    Clear all logs
    """
    try:
        global logs_storage
        logs_storage = []
        
        return {"success": True, "message": "All logs cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear logs: {str(e)}")

def populate_sample_logs():
    """Populate storage with sample logs for demonstration"""
    sample_logs = [
        {
            "level": "INFO",
            "service": "api",
            "component": "fastapi",
            "message": "FastAPI server started successfully",
            "request_id": "req_001",
            "duration": 125
        },
        {
            "level": "INFO",
            "service": "deployments",
            "component": "deployer",
            "message": "HuggingFace model analysis completed for microsoft/DialoGPT-medium",
            "request_id": "dep_001",
            "details": {
                "model_id": "microsoft/DialoGPT-medium",
                "model_type": "text",
                "gpu_requirements": "A10G",
                "estimated_cost": 1.20
            }
        },
        {
            "level": "WARNING",
            "service": "api",
            "component": "middleware",
            "message": "High request rate detected from client 192.168.1.100",
            "request_id": "req_002",
            "details": {
                "client_ip": "192.168.1.100",
                "requests_per_minute": 120,
                "threshold": 100
            }
        },
        {
            "level": "ERROR",
            "service": "deployments",
            "component": "modal",
            "message": "Failed to deploy model: insufficient GPU resources",
            "request_id": "dep_002",
            "details": {
                "model_id": "meta-llama/Llama-2-70b-chat-hf",
                "required_gpu": "A100-80GB",
                "available_gpu": "A10G-24GB"
            },
            "stack_trace": "Traceback (most recent call last):\n  File \"modal_deployer.py\", line 45, in deploy\n    raise InsufficientResourcesError(\"GPU resources unavailable\")\nInsufficientResourcesError: GPU resources unavailable"
        },
        {
            "level": "INFO",
            "service": "models",
            "component": "registry",
            "message": "Model registry updated with 3 new models",
            "request_id": "mod_001",
            "details": {
                "new_models": ["Qwen/Qwen2-VL-7B-Instruct", "BAAI/bge-base-en-v1.5", "openai/whisper-large-v3"],
                "total_models": 156
            }
        },
        {
            "level": "DEBUG",
            "service": "api",
            "component": "auth",
            "message": "User authentication successful",
            "request_id": "auth_001",
            "details": {
                "user_id": "user_123",
                "method": "api_key",
                "permissions": ["read", "deploy"]
            }
        },
        {
            "level": "INFO",
            "service": "api",
            "component": "models",
            "message": "Model inference request completed",
            "request_id": "inf_001",
            "duration": 245,
            "details": {
                "model": "gpt-4-turbo",
                "tokens": 150,
                "cost": 0.003
            }
        },
        {
            "level": "WARNING",
            "service": "system",
            "component": "monitoring",
            "message": "High memory usage detected",
            "details": {
                "memory_usage": "85%",
                "threshold": "80%",
                "service": "deployments"
            }
        }
    ]
    
    current_time = time.time() * 1000
    
    for i, log in enumerate(sample_logs):
        add_log_entry(
            level=log["level"],
            service=log["service"],
            message=log["message"],
            component=log.get("component"),
            request_id=log.get("request_id"),
            duration=log.get("duration"),
            details=log.get("details"),
            stack_trace=log.get("stack_trace")
        )
        
        # Adjust timestamps to be recent
        logs_storage[i]["timestamp"] = current_time - (i * 5000)  # 5 seconds apart

def add_sample_log():
    """Add a new sample log entry for live streaming demo"""
    import random
    
    sample_messages = [
        ("INFO", "api", "HTTP request processed", "fastapi", {"status": 200, "path": "/api/v1/models"}),
        ("INFO", "deployments", "Model deployment started", "deployer", {"model": "BAAI/bge-base-en-v1.5"}),
        ("WARNING", "api", "Rate limiting applied", "middleware", {"client": "192.168.1.50", "rate": 105}),
        ("DEBUG", "models", "Model cache hit", "registry", {"model": "gpt-4-turbo", "cache_size": "2.1GB"}),
        ("INFO", "system", "Health check completed", "monitor", {"status": "healthy", "services": 5}),
        ("ERROR", "deployments", "Model loading failed", "loader", {"model": "invalid/model-id", "error": "not found"}),
    ]
    
    level, service, message, component, details = random.choice(sample_messages)
    request_id = f"req_{random.randint(1000, 9999)}"
    duration = random.randint(50, 500) if level == "INFO" else None
    
    add_log_entry(
        level=level,
        service=service,
        message=message,
        component=component,
        request_id=request_id,
        duration=duration,
        details=details
    )

# Health check for logs service
@router.get("/health")
async def logs_health():
    """Health check for logs service"""
    return {
        "status": "healthy",
        "service": "logs",
        "total_logs": len(logs_storage),
        "memory_usage": f"{len(logs_storage)}/{max_logs} logs"
    }