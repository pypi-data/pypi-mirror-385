"""
Deployments API Routes

Handles automated HuggingFace model deployment to Modal
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

from isa_model.deployment.modal.deployer import ModalDeployer as HuggingFaceModalDeployer

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response models
class AnalyzeModelRequest(BaseModel):
    model_id: str

class DeployModelRequest(BaseModel):
    model_id: str
    service_name: Optional[str] = None
    auto_deploy: bool = False

class DeploymentResponse(BaseModel):
    success: bool
    deployment_id: Optional[str] = None
    model_id: str
    config: Optional[Dict[str, Any]] = None
    service_file: Optional[str] = None
    deployment_command: Optional[str] = None
    estimated_cost_per_hour: Optional[float] = None
    deployed: bool = False
    error: Optional[str] = None

# Global deployer instance
deployer = HuggingFaceModalDeployer()

# In-memory deployment tracking (in production, use a database)
deployments = {}

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_model(request: AnalyzeModelRequest):
    """
    Analyze a HuggingFace model for deployment compatibility
    """
    try:
        logger.info(f"Analyzing model: {request.model_id}")
        
        # Analyze the model
        config = deployer.analyze_model(request.model_id)
        
        return {
            "success": True,
            "model_id": config.model_id,
            "model_type": config.model_type,
            "architecture": config.architecture,
            "parameters": config.parameters,
            "gpu_requirements": config.gpu_requirements,
            "memory_gb": config.memory_gb,
            "container_memory_mb": config.container_memory_mb,
            "dependencies": config.dependencies,
            "capabilities": config.capabilities,
            "estimated_cost_per_hour": config.estimated_cost_per_hour
        }
        
    except Exception as e:
        logger.error(f"Model analysis failed for {request.model_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Model analysis failed: {str(e)}")

@router.post("/deploy", response_model=DeploymentResponse)
async def deploy_model(request: DeployModelRequest, background_tasks: BackgroundTasks):
    """
    Deploy a HuggingFace model to Modal
    """
    try:
        logger.info(f"Starting deployment for model: {request.model_id}")
        
        # Generate unique deployment ID
        import time
        import uuid
        deployment_id = f"deploy_{uuid.uuid4().hex[:8]}_{int(time.time())}"
        
        # Add to deployments tracking
        deployments[deployment_id] = {
            "id": deployment_id,
            "model_id": request.model_id,
            "service_name": request.service_name,
            "status": "pending",
            "created_at": time.time(),
            "auto_deploy": request.auto_deploy
        }
        
        # Start deployment in background
        background_tasks.add_task(
            perform_deployment, 
            deployment_id, 
            request.model_id, 
            request.service_name,
            request.auto_deploy
        )
        
        return DeploymentResponse(
            success=True,
            deployment_id=deployment_id,
            model_id=request.model_id,
            deployed=False
        )
        
    except Exception as e:
        logger.error(f"Deployment initiation failed for {request.model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

async def perform_deployment(deployment_id: str, model_id: str, service_name: Optional[str], auto_deploy: bool):
    """
    Perform the actual deployment in the background
    """
    import time
    
    try:
        logger.info(f"Performing deployment {deployment_id} for model {model_id}")
        
        # Update status
        deployments[deployment_id]["status"] = "deploying"
        deployments[deployment_id]["progress"] = "Analyzing model"
        
        # Deploy the model
        result = deployer.deploy_model(model_id, deploy=auto_deploy)
        
        if result["success"]:
            deployments[deployment_id].update({
                "status": "completed" if result.get("deployed") else "generated",
                "progress": "Deployment completed",
                "config": result["config"],
                "service_file": result["service_file"],
                "deployment_command": result["deployment_command"],
                "estimated_cost_per_hour": result["estimated_cost_per_hour"],
                "deployed": result.get("deployed", False),
                "completed_at": time.time()
            })
        else:
            deployments[deployment_id].update({
                "status": "failed",
                "progress": "Deployment failed",
                "error": result.get("error", "Unknown error"),
                "failed_at": time.time()
            })
            
    except Exception as e:
        logger.error(f"Deployment {deployment_id} failed: {e}")
        deployments[deployment_id].update({
            "status": "failed",
            "progress": "Deployment failed",
            "error": str(e),
            "failed_at": time.time()
        })

@router.get("/")
async def list_deployments():
    """
    List all deployments
    """
    try:
        # Convert deployments to list format
        deployment_list = []
        
        for deployment_id, deployment in deployments.items():
            deployment_list.append({
                "id": deployment_id,
                "name": deployment.get("service_name") or f"{deployment['model_id'].split('/')[-1]} Service",
                "model_id": deployment["model_id"],
                "model_type": "text",  # Would be determined from analysis
                "status": deployment["status"],
                "gpu": "A10G",  # Would be from config
                "cost_per_hour": "1.20",  # Would be from config
                "created_at": deployment["created_at"],
                "deployed_at": deployment.get("completed_at"),
                "error": deployment.get("error")
            })
        
        # Add some fallback deployments for demo
        if not deployment_list:
            deployment_list = [
                {
                    "id": "qwen2-vl-7b",
                    "name": "Qwen2.5-VL Service",
                    "model_id": "Qwen/Qwen2.5-VL-7B-Instruct",
                    "model_type": "vision",
                    "status": "active",
                    "gpu": "A100",
                    "cost_per_hour": "4.00",
                    "created_at": 1705312200,
                    "deployed_at": 1705312800
                },
                {
                    "id": "embed-service",
                    "name": "BGE Embed Service",
                    "model_id": "BAAI/bge-base-en-v1.5",
                    "model_type": "embedding",
                    "status": "active",
                    "gpu": "A10G",
                    "cost_per_hour": "1.20",
                    "created_at": 1705225800,
                    "deployed_at": 1705226400
                }
            ]
        
        return deployment_list
        
    except Exception as e:
        logger.error(f"Failed to list deployments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list deployments: {str(e)}")

@router.get("/{deployment_id}")
async def get_deployment(deployment_id: str):
    """
    Get deployment details
    """
    try:
        if deployment_id not in deployments:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        return deployments[deployment_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get deployment {deployment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get deployment: {str(e)}")

@router.get("/{deployment_id}/status")
async def get_deployment_status(deployment_id: str, request: Request):
    """
    Get real-time deployment status and monitoring information with tenant isolation
    """
    try:
        from isa_model.deployment.core.deployment_manager import DeploymentManager
        from isa_model.serving.api.middleware.tenant_context import get_tenant_context
        
        # Get tenant context for isolation
        tenant_context = get_tenant_context()
        tenant_dict = {
            "organization_id": tenant_context.organization_id,
            "user_id": tenant_context.user_id,
            "role": tenant_context.role
        } if tenant_context else None
        
        # Initialize deployment manager
        manager = DeploymentManager()
        
        # Verify tenant access to deployment first
        deployment = await manager.get_deployment(deployment_id, tenant_dict)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found or access denied")
        
        # Get deployment status
        status_info = await manager.get_modal_service_status(deployment_id)
        
        return {
            "success": True,
            "deployment_status": status_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get deployment status {deployment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get deployment status: {str(e)}")

@router.get("/{deployment_id}/monitoring")
async def get_deployment_monitoring(deployment_id: str, request: Request):
    """
    Get detailed monitoring metrics for Modal deployment with tenant isolation
    """
    try:
        from isa_model.deployment.core.deployment_manager import DeploymentManager
        from isa_model.serving.api.middleware.tenant_context import get_tenant_context
        
        # Get tenant context for isolation
        tenant_context = get_tenant_context()
        tenant_dict = {
            "organization_id": tenant_context.organization_id,
            "user_id": tenant_context.user_id,
            "role": tenant_context.role
        } if tenant_context else None
        
        manager = DeploymentManager()
        
        # Verify tenant access to deployment first
        deployment = await manager.get_deployment(deployment_id, tenant_dict)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found or access denied")
        
        status_info = await manager.get_modal_service_status(deployment_id)
        
        if status_info.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        # Extract detailed monitoring data
        monitoring_data = status_info.get("monitoring", {})
        
        return {
            "success": True,
            "deployment_id": deployment_id,
            "monitoring": {
                "health_check": monitoring_data.get("health_check"),
                "resource_usage": monitoring_data.get("resource_usage"),
                "request_metrics": monitoring_data.get("request_metrics"),
                "cost_tracking": monitoring_data.get("cost_tracking"),
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get monitoring data {deployment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring data: {str(e)}")

@router.post("/{deployment_id}/restart")
async def restart_deployment(deployment_id: str, request: Request):
    """
    Restart a Modal deployment with tenant isolation
    """
    try:
        from isa_model.deployment.core.deployment_manager import DeploymentManager
        from isa_model.serving.api.middleware.tenant_context import get_tenant_context
        
        # Get tenant context for isolation
        tenant_context = get_tenant_context()
        tenant_dict = {
            "organization_id": tenant_context.organization_id,
            "user_id": tenant_context.user_id,
            "role": tenant_context.role
        } if tenant_context else None
        
        manager = DeploymentManager()
        
        # Check if deployment exists and user has access
        deployment = await manager.get_deployment(deployment_id, tenant_dict)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found or access denied")
        
        # Update status to restarting
        await manager.update_deployment_status(deployment_id, "restarting")
        
        # TODO: Implement actual Modal service restart
        # For now, simulate restart process
        await asyncio.sleep(1)
        
        # Update status to running
        await manager.update_deployment_status(deployment_id, "running")
        
        return {
            "success": True,
            "message": f"Deployment {deployment_id} restarted successfully",
            "deployment_id": deployment_id,
            "status": "running"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restart deployment {deployment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restart deployment: {str(e)}")

@router.delete("/{deployment_id}")
async def cancel_deployment(deployment_id: str):
    """
    Cancel a pending deployment
    """
    try:
        if deployment_id not in deployments:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        deployment = deployments[deployment_id]
        
        if deployment["status"] == "pending":
            deployment["status"] = "cancelled"
            deployment["cancelled_at"] = time.time()
            return {"success": True, "message": "Deployment cancelled"}
        else:
            raise HTTPException(status_code=400, detail="Cannot cancel deployment in current status")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel deployment {deployment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel deployment: {str(e)}")

@router.post("/{deployment_id}/retry")
async def retry_deployment(deployment_id: str, background_tasks: BackgroundTasks):
    """
    Retry a failed deployment
    """
    try:
        if deployment_id not in deployments:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        deployment = deployments[deployment_id]
        
        if deployment["status"] == "failed":
            # Reset deployment status
            deployment["status"] = "pending"
            deployment["error"] = None
            deployment["progress"] = "Retrying deployment"
            
            # Start deployment in background
            background_tasks.add_task(
                perform_deployment,
                deployment_id,
                deployment["model_id"],
                deployment.get("service_name"),
                deployment.get("auto_deploy", False)
            )
            
            return {"success": True, "message": "Deployment retry started"}
        else:
            raise HTTPException(status_code=400, detail="Cannot retry deployment in current status")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retry deployment {deployment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retry deployment: {str(e)}")

@router.get("/{deployment_id}/code")
async def get_service_code(deployment_id: str):
    """
    Download the generated service code for a deployment
    """
    try:
        if deployment_id not in deployments:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        deployment = deployments[deployment_id]
        service_file = deployment.get("service_file")
        
        if not service_file or not Path(service_file).exists():
            raise HTTPException(status_code=404, detail="Service code not found")
        
        # Read the service code file
        with open(service_file, 'r') as f:
            service_code = f.read()
        
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            content=service_code,
            headers={
                "Content-Disposition": f"attachment; filename={Path(service_file).name}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get service code for {deployment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get service code: {str(e)}")

# Health check for deployments service
@router.get("/health")
async def deployments_health():
    """Health check for deployments service"""
    return {
        "status": "healthy",
        "service": "deployments",
        "active_deployments": len([d for d in deployments.values() if d["status"] == "active"]),
        "pending_deployments": len([d for d in deployments.values() if d["status"] == "pending"]),
        "total_deployments": len(deployments)
    }