"""
Deployment Billing API Routes

API endpoints for deployment cost estimation, tracking, and billing information.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel

from ..auth import optional_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/deployment", tags=["deployment-billing"])


class CostEstimationRequest(BaseModel):
    """Request model for deployment cost estimation"""
    provider: str
    gpu_type: str
    gpu_count: int = 1
    estimated_hours: float = 1.0
    operation_type: str = "deployment"


class DeploymentBillingQuery(BaseModel):
    """Query parameters for deployment billing"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    provider: Optional[str] = None
    gpu_type: Optional[str] = None
    model_id: Optional[str] = None


@router.post("/estimate-cost")
async def estimate_deployment_cost(
    request: CostEstimationRequest,
    user = Depends(optional_auth)
):
    """
    Estimate deployment costs before starting deployment
    
    Returns cost breakdown for specified provider, GPU type, and duration.
    """
    try:
        from isa_model.core.models.deployment_billing_tracker import get_deployment_billing_tracker
        
        billing_tracker = get_deployment_billing_tracker()
        cost_estimate = billing_tracker.estimate_deployment_cost(
            provider=request.provider,
            gpu_type=request.gpu_type,
            gpu_count=request.gpu_count,
            estimated_hours=request.estimated_hours,
            operation_type=request.operation_type
        )
        
        # Add additional cost breakdown details
        hourly_rate = cost_estimate["compute_cost"] / request.estimated_hours if request.estimated_hours > 0 else 0
        
        return {
            "success": True,
            "estimation": {
                "provider": request.provider,
                "gpu_type": request.gpu_type,
                "gpu_count": request.gpu_count,
                "estimated_hours": request.estimated_hours,
                "cost_breakdown": cost_estimate,
                "hourly_rate": round(hourly_rate, 6),
                "recommendations": _get_cost_recommendations(request.provider, request.gpu_type, cost_estimate)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to estimate deployment cost: {e}")
        raise HTTPException(status_code=500, detail=f"Cost estimation failed: {str(e)}")


@router.get("/billing/summary")
async def get_deployment_billing_summary(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    gpu_type: Optional[str] = Query(None, description="Filter by GPU type"),
    model_id: Optional[str] = Query(None, description="Filter by model ID"),
    user = Depends(optional_auth)
):
    """
    Get deployment billing summary with optional filters
    
    Returns comprehensive billing information for deployments within specified period.
    """
    try:
        from isa_model.core.models.deployment_billing_tracker import get_deployment_billing_tracker
        
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        billing_tracker = get_deployment_billing_tracker()
        
        # Get deployment summary
        deployment_summary = billing_tracker.get_deployment_summary(
            start_date=start_dt,
            end_date=end_dt,
            provider=provider,
            gpu_type=gpu_type
        )
        
        # If model_id filter is specified, get model-specific data
        model_summary = None
        if model_id:
            model_summary = billing_tracker.get_model_usage_summary(model_id)
        
        return {
            "success": True,
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "provider": provider,
                "gpu_type": gpu_type,
                "model_id": model_id
            },
            "deployment_summary": deployment_summary,
            "model_summary": model_summary,
            "recommendations": _get_billing_recommendations(deployment_summary)
        }
        
    except Exception as e:
        logger.error(f"Failed to get deployment billing summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get billing summary: {str(e)}")


@router.get("/pricing")
async def get_deployment_pricing(
    user = Depends(optional_auth)
):
    """
    Get current deployment pricing for all providers and GPU types
    
    Returns up-to-date pricing information for cost planning.
    """
    try:
        from isa_model.core.models.deployment_billing_tracker import get_deployment_billing_tracker
        
        billing_tracker = get_deployment_billing_tracker()
        pricing_data = billing_tracker.pricing_data
        
        # Add provider descriptions and recommendations
        enhanced_pricing = {}
        for provider, pricing in pricing_data.items():
            enhanced_pricing[provider] = {
                "pricing": pricing,
                "description": _get_provider_description(provider),
                "best_for": _get_provider_recommendations(provider),
                "availability": _check_provider_availability(provider)
            }
        
        return {
            "success": True,
            "pricing": enhanced_pricing,
            "currency": "USD",
            "unit": "per hour",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get deployment pricing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pricing: {str(e)}")


@router.get("/providers/compare")
async def compare_providers(
    gpu_type: str = Query(..., description="GPU type to compare"),
    hours: float = Query(1.0, description="Number of hours for comparison"),
    user = Depends(optional_auth)
):
    """
    Compare costs across different providers for the same GPU type
    
    Helps users choose the most cost-effective deployment option.
    """
    try:
        from isa_model.core.models.deployment_billing_tracker import get_deployment_billing_tracker
        
        billing_tracker = get_deployment_billing_tracker()
        comparisons = []
        
        providers = ["modal", "runpod", "lambda_labs", "coreweave"]
        
        for provider in providers:
            try:
                cost_estimate = billing_tracker.estimate_deployment_cost(
                    provider=provider,
                    gpu_type=gpu_type,
                    gpu_count=1,
                    estimated_hours=hours
                )
                
                comparisons.append({
                    "provider": provider,
                    "total_cost": cost_estimate["total_cost"],
                    "hourly_rate": cost_estimate["compute_cost"] / hours if hours > 0 else 0,
                    "breakdown": cost_estimate,
                    "description": _get_provider_description(provider),
                    "availability": _check_provider_availability(provider)
                })
            except Exception as e:
                logger.warning(f"Could not get pricing for {provider}: {e}")
        
        # Sort by total cost
        comparisons.sort(key=lambda x: x["total_cost"])
        
        return {
            "success": True,
            "comparison": {
                "gpu_type": gpu_type,
                "duration_hours": hours,
                "providers": comparisons,
                "cheapest": comparisons[0] if comparisons else None,
                "savings": {
                    "max_savings": comparisons[-1]["total_cost"] - comparisons[0]["total_cost"] if len(comparisons) > 1 else 0,
                    "percentage": ((comparisons[-1]["total_cost"] - comparisons[0]["total_cost"]) / comparisons[-1]["total_cost"] * 100) if len(comparisons) > 1 and comparisons[-1]["total_cost"] > 0 else 0
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to compare providers: {e}")
        raise HTTPException(status_code=500, detail=f"Provider comparison failed: {str(e)}")


def _get_cost_recommendations(provider: str, gpu_type: str, cost_estimate: Dict[str, float]) -> List[str]:
    """Generate cost optimization recommendations"""
    recommendations = []
    
    if cost_estimate["total_cost"] > 10.0:
        recommendations.append("Consider using spot instances if available for significant savings")
    
    if gpu_type in ["h100", "a100_80gb"]:
        recommendations.append("High-end GPU selected - ensure workload requires this performance")
    
    if provider == "modal":
        recommendations.append("Modal offers automatic scaling - costs only incurred during active use")
    
    if provider in ["runpod", "lambda_labs"]:
        recommendations.append("Consider longer-term contracts for better rates on extended deployments")
    
    return recommendations


def _get_billing_recommendations(summary: Dict[str, Any]) -> List[str]:
    """Generate billing optimization recommendations based on usage patterns"""
    recommendations = []
    
    if summary["total_cost"] > 100.0:
        recommendations.append("High usage detected - consider reserved instances for cost savings")
    
    # Analyze provider distribution
    providers = summary.get("by_provider", {})
    if len(providers) > 1:
        costs = [(p, data["cost"]) for p, data in providers.items()]
        costs.sort(key=lambda x: x[1])
        if len(costs) > 1 and costs[-1][1] > costs[0][1] * 2:
            recommendations.append(f"Consider migrating from {costs[-1][0]} to {costs[0][0]} for potential savings")
    
    # Analyze GPU usage
    gpu_types = summary.get("by_gpu_type", {})
    if "h100" in gpu_types and gpu_types["h100"]["gpu_hours"] < 10:
        recommendations.append("Low H100 usage - consider A100 for similar performance at lower cost")
    
    return recommendations


def _get_provider_description(provider: str) -> str:
    """Get description for deployment provider"""
    descriptions = {
        "modal": "Serverless GPU platform with automatic scaling and pay-per-use billing",
        "triton_local": "Local deployment using your own hardware with electricity costs",
        "runpod": "Cloud GPU rental with competitive pricing and flexible instances",
        "lambda_labs": "Professional GPU cloud with reliable infrastructure and support",
        "coreweave": "High-performance GPU infrastructure optimized for AI workloads"
    }
    return descriptions.get(provider, "Unknown provider")


def _get_provider_recommendations(provider: str) -> List[str]:
    """Get recommendations for when to use each provider"""
    recommendations = {
        "modal": ["Development and testing", "Variable workloads", "Automatic scaling needs"],
        "triton_local": ["Long-term deployments", "Data privacy requirements", "Cost optimization"],
        "runpod": ["Budget-conscious deployments", "Flexible scaling", "Spot instance savings"],
        "lambda_labs": ["Production workloads", "Reliable performance", "Enterprise support"],
        "coreweave": ["High-performance requirements", "Large-scale deployments", "Bare metal access"]
    }
    return recommendations.get(provider, [])


def _check_provider_availability(provider: str) -> str:
    """Check if provider is currently available"""
    # This would implement actual availability checking
    # For now, return static status
    availability = {
        "modal": "Available",
        "triton_local": "Available (requires local setup)",
        "runpod": "Available", 
        "lambda_labs": "Available",
        "coreweave": "Available (requires signup)"
    }
    return availability.get(provider, "Unknown")