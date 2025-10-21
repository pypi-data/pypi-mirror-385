"""
Inference Monitoring API Routes

Provides comprehensive monitoring and analytics for model inference activities.
Uses InfluxDB as the backend for time-series data analysis.

Features:
- Real-time inference metrics
- Cost analysis and tracking
- Performance monitoring
- Usage statistics by provider/model
- Error tracking and alerting
- Token usage analytics
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import logging
from datetime import datetime, timedelta
import json

from isa_model.core.logging import get_inference_logger
from ..middleware.auth import optional_auth, require_read_access

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response Models
class InferenceMetricsResponse(BaseModel):
    """Response model for inference metrics"""
    success: bool
    data: Any  # More flexible data field
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class UsageStatsRequest(BaseModel):
    """Request model for usage statistics"""
    hours: int = Field(24, ge=1, le=168, description="Time range in hours (1-168)")
    group_by: str = Field("provider", description="Group by: provider, model_name, service_type")
    include_costs: bool = Field(True, description="Include cost analysis")

class ErrorAnalysisRequest(BaseModel):
    """Request model for error analysis"""
    hours: int = Field(24, ge=1, le=168, description="Time range in hours")
    error_types: Optional[List[str]] = Field(None, description="Filter by error types")
    providers: Optional[List[str]] = Field(None, description="Filter by providers")

@router.get("/health")
async def monitoring_health():
    """Health check for inference monitoring service"""
    inference_logger = get_inference_logger()
    
    return {
        "status": "healthy" if inference_logger.enabled else "disabled",
        "service": "inference_monitoring",
        "influxdb_enabled": inference_logger.enabled,
        "influxdb_url": inference_logger.url if inference_logger.enabled else None,
        "bucket": inference_logger.bucket if inference_logger.enabled else None
    }

@router.get("/recent-requests", response_model=InferenceMetricsResponse)
async def get_recent_requests(
    limit: int = Query(50, ge=1, le=500, description="Number of recent requests to fetch"),
    hours: int = Query(24, ge=1, le=168, description="Time range in hours"),
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    status: Optional[str] = Query(None, description="Filter by status (completed, failed)"),
    user = Depends(optional_auth)
):
    """
    Get recent inference requests with optional filtering
    """
    try:
        inference_logger = get_inference_logger()
        
        if not inference_logger.enabled:
            raise HTTPException(
                status_code=503,
                detail="Inference logging is disabled. Enable ENABLE_INFERENCE_LOGGING."
            )
        
        # Fetch recent requests
        requests = inference_logger.get_recent_requests(
            limit=limit,
            hours=hours,
            service_type=service_type,
            provider=provider,
            status=status
        )
        
        return InferenceMetricsResponse(
            success=True,
            data=requests,
            metadata={
                "total_requests": len(requests),
                "time_range_hours": hours,
                "filters": {
                    "service_type": service_type,
                    "provider": provider,
                    "status": status
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching recent requests: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent requests: {str(e)}")

@router.post("/usage-stats", response_model=InferenceMetricsResponse)
async def get_usage_statistics(
    request: UsageStatsRequest,
    user = Depends(optional_auth)
):
    """
    Get usage statistics and analytics
    """
    try:
        inference_logger = get_inference_logger()
        
        if not inference_logger.enabled:
            raise HTTPException(
                status_code=503,
                detail="Inference logging is disabled"
            )
        
        # Get usage statistics
        stats = inference_logger.get_usage_statistics(
            hours=request.hours,
            group_by=request.group_by
        )
        
        # Calculate totals and summaries
        total_requests = sum(data.get('total_requests', 0) for data in stats.values())
        
        metadata = {
            "time_range_hours": request.hours,
            "group_by": request.group_by,
            "total_requests": total_requests,
            "unique_groups": len(stats),
            "include_costs": request.include_costs
        }
        
        return InferenceMetricsResponse(
            success=True,
            data=stats,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Error fetching usage statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch usage statistics: {str(e)}")

@router.get("/cost-analysis", response_model=InferenceMetricsResponse)
async def get_cost_analysis(
    hours: int = Query(24, ge=1, le=168, description="Time range in hours"),
    group_by: str = Query("provider", description="Group by: provider, model_name, service_type"),
    user = Depends(optional_auth)
):
    """
    Get cost analysis and spending breakdown
    """
    try:
        inference_logger = get_inference_logger()
        
        if not inference_logger.enabled:
            raise HTTPException(status_code=503, detail="Inference logging is disabled")
        
        # This would typically involve more complex InfluxDB queries
        # For now, we'll use the existing usage statistics method
        stats = inference_logger.get_usage_statistics(hours=hours, group_by=group_by)
        
        # Calculate cost summaries (this would be enhanced with actual cost queries)
        cost_analysis = {}
        total_cost = 0.0
        total_requests = 0
        
        for group, data in stats.items():
            requests = data.get('total_requests', 0)
            # Estimate costs (in a real implementation, this would come from the database)
            estimated_cost = requests * 0.002  # Rough estimate
            
            cost_analysis[group] = {
                "requests": requests,
                "estimated_cost_usd": estimated_cost,
                "cost_per_request": estimated_cost / requests if requests > 0 else 0,
                "hourly_data": data.get('hourly_data', [])
            }
            
            total_cost += estimated_cost
            total_requests += requests
        
        return InferenceMetricsResponse(
            success=True,
            data=cost_analysis,
            metadata={
                "time_range_hours": hours,
                "group_by": group_by,
                "total_cost_usd": total_cost,
                "total_requests": total_requests,
                "average_cost_per_request": total_cost / total_requests if total_requests > 0 else 0
            }
        )
        
    except Exception as e:
        logger.error(f"Error performing cost analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform cost analysis: {str(e)}")

@router.get("/performance-metrics", response_model=InferenceMetricsResponse)
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=168, description="Time range in hours"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    model_name: Optional[str] = Query(None, description="Filter by model"),
    user = Depends(optional_auth)
):
    """
    Get performance metrics including response times, success rates, etc.
    """
    try:
        inference_logger = get_inference_logger()
        
        if not inference_logger.enabled:
            raise HTTPException(status_code=503, detail="Inference logging is disabled")
        
        # Get recent requests for performance analysis
        requests = inference_logger.get_recent_requests(
            limit=1000,  # Large sample for accurate metrics
            hours=hours,
            provider=provider
        )
        
        if not requests:
            return InferenceMetricsResponse(
                success=True,
                data={},
                metadata={"message": "No data found for the specified criteria"}
            )
        
        # Calculate performance metrics
        total_requests = len(requests)
        successful_requests = len([r for r in requests if r.get('status') == 'completed'])
        failed_requests = total_requests - successful_requests
        
        execution_times = [r.get('execution_time_ms', 0) for r in requests if r.get('execution_time_ms')]
        
        performance_data = {
            "request_counts": {
                "total": total_requests,
                "successful": successful_requests,
                "failed": failed_requests,
                "success_rate": (successful_requests / total_requests) * 100 if total_requests > 0 else 0
            },
            "response_times": {
                "count": len(execution_times),
                "average_ms": sum(execution_times) / len(execution_times) if execution_times else 0,
                "min_ms": min(execution_times) if execution_times else 0,
                "max_ms": max(execution_times) if execution_times else 0,
            } if execution_times else {}
        }
        
        # Group by provider if not filtered
        if not provider:
            provider_stats = {}
            for req in requests:
                prov = req.get('provider', 'unknown')
                if prov not in provider_stats:
                    provider_stats[prov] = {"requests": 0, "successful": 0, "total_time": 0}
                
                provider_stats[prov]["requests"] += 1
                if req.get('status') == 'completed':
                    provider_stats[prov]["successful"] += 1
                if req.get('execution_time_ms'):
                    provider_stats[prov]["total_time"] += req.get('execution_time_ms', 0)
            
            performance_data["by_provider"] = {
                prov: {
                    "requests": stats["requests"],
                    "success_rate": (stats["successful"] / stats["requests"]) * 100,
                    "avg_response_time_ms": stats["total_time"] / stats["requests"] if stats["requests"] > 0 else 0
                }
                for prov, stats in provider_stats.items()
            }
        
        return InferenceMetricsResponse(
            success=True,
            data=performance_data,
            metadata={
                "time_range_hours": hours,
                "provider": provider,
                "model_name": model_name,
                "sample_size": total_requests
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch performance metrics: {str(e)}")

@router.post("/error-analysis", response_model=InferenceMetricsResponse)
async def get_error_analysis(
    request: ErrorAnalysisRequest,
    user = Depends(optional_auth)
):
    """
    Analyze errors and failure patterns
    """
    try:
        inference_logger = get_inference_logger()
        
        if not inference_logger.enabled:
            raise HTTPException(status_code=503, detail="Inference logging is disabled")
        
        # Get recent failed requests
        failed_requests = inference_logger.get_recent_requests(
            limit=500,
            hours=request.hours,
            status="failed"
        )
        
        if not failed_requests:
            return InferenceMetricsResponse(
                success=True,
                data={"message": "No errors found in the specified time range"},
                metadata={"error_count": 0}
            )
        
        # Analyze error patterns
        error_analysis = {
            "total_errors": len(failed_requests),
            "error_rate": 0,  # Would calculate from total requests
            "by_provider": {},
            "by_model": {},
            "by_service_type": {},
            "recent_errors": failed_requests[:10]  # Most recent 10 errors
        }
        
        # Group errors by different dimensions
        for req in failed_requests:
            provider = req.get('provider', 'unknown')
            model = req.get('model_name', 'unknown')
            service_type = req.get('service_type', 'unknown')
            
            # Count by provider
            if provider not in error_analysis["by_provider"]:
                error_analysis["by_provider"][provider] = 0
            error_analysis["by_provider"][provider] += 1
            
            # Count by model
            if model not in error_analysis["by_model"]:
                error_analysis["by_model"][model] = 0
            error_analysis["by_model"][model] += 1
            
            # Count by service type
            if service_type not in error_analysis["by_service_type"]:
                error_analysis["by_service_type"][service_type] = 0
            error_analysis["by_service_type"][service_type] += 1
        
        return InferenceMetricsResponse(
            success=True,
            data=error_analysis,
            metadata={
                "time_range_hours": request.hours,
                "filters": {
                    "error_types": request.error_types,
                    "providers": request.providers
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error performing error analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform error analysis: {str(e)}")

@router.get("/dashboard-summary", response_model=InferenceMetricsResponse)
async def get_dashboard_summary(
    hours: int = Query(24, ge=1, le=168, description="Time range in hours"),
    user = Depends(optional_auth)
):
    """
    Get summary metrics for the monitoring dashboard
    """
    try:
        inference_logger = get_inference_logger()
        
        if not inference_logger.enabled:
            raise HTTPException(status_code=503, detail="Inference logging is disabled")
        
        # Get recent requests for summary
        recent_requests = inference_logger.get_recent_requests(limit=1000, hours=hours)
        
        if not recent_requests:
            return InferenceMetricsResponse(
                success=True,
                data={"message": "No data available"},
                metadata={"hours": hours}
            )
        
        # Calculate summary metrics
        total_requests = len(recent_requests)
        successful_requests = len([r for r in recent_requests if r.get('status') == 'completed'])
        failed_requests = total_requests - successful_requests
        
        # Cost summary
        total_cost = sum(r.get('cost_usd', 0) or 0 for r in recent_requests)
        avg_cost = total_cost / total_requests if total_requests > 0 else 0
        
        # Token summary  
        total_tokens = sum(r.get('tokens', 0) or 0 for r in recent_requests)
        avg_tokens = total_tokens / total_requests if total_requests > 0 else 0
        
        # Top providers
        provider_counts = {}
        for req in recent_requests:
            provider = req.get('provider', 'unknown')
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        # Top models
        model_counts = {}
        for req in recent_requests:
            model = req.get('model_name', 'unknown')
            model_counts[model] = model_counts.get(model, 0) + 1
        
        summary = {
            "overview": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": (successful_requests / total_requests) * 100 if total_requests > 0 else 0,
                "total_cost_usd": total_cost,
                "average_cost_per_request": avg_cost,
                "total_tokens": total_tokens,
                "average_tokens_per_request": avg_tokens
            },
            "top_providers": dict(sorted(provider_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            "top_models": dict(sorted(model_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            "time_range": {
                "hours": hours,
                "start_time": (datetime.now() - timedelta(hours=hours)).isoformat(),
                "end_time": datetime.now().isoformat()
            }
        }
        
        return InferenceMetricsResponse(
            success=True,
            data=summary,
            metadata={"generated_at": datetime.now()}
        )
        
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard summary: {str(e)}")

@router.delete("/clear-logs")
async def clear_inference_logs(
    confirm: bool = Query(False, description="Confirmation required to clear logs"),
    user = Depends(require_read_access)  # Require authentication for destructive operations
):
    """
    Clear all inference logs (DANGEROUS - requires confirmation)
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required. Set confirm=true to clear all logs."
        )
    
    try:
        inference_logger = get_inference_logger()
        
        if not inference_logger.enabled:
            raise HTTPException(status_code=503, detail="Inference logging is disabled")
        
        # This would implement log clearing in InfluxDB
        # For safety, we'll just return a warning for now
        
        logger.warning("Log clearing requested but not implemented for safety")
        
        return {
            "success": False,
            "message": "Log clearing not implemented for safety. Contact administrator.",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear logs: {str(e)}")