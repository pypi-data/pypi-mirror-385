"""
Unified Deployment Manager

Orchestrates deployment of AI models to multiple platforms (Modal, Triton, Local GPU).
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import asyncio

from ...core.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class DeploymentManager:
    """
    Unified deployment manager for multiple platforms.
    
    This manager coordinates:
    - Local GPU deployment with vLLM, TensorRT-LLM, Transformers
    - Cloud deployment to Modal platform
    - Container deployment with Triton Inference Server
    - Deployment tracking and monitoring
    
    Example:
        ```python
        from isa_model.deployment import DeploymentManager
        from isa_model.deployment.local import create_vllm_config
        
        # Initialize deployment manager
        manager = DeploymentManager()
        
        # Deploy to local GPU
        local_config = create_vllm_config("llama2-7b", "meta-llama/Llama-2-7b-chat-hf")
        local_deployment = await manager.deploy_to_local(local_config)
        
        # Deploy to Modal
        modal_deployment = await manager.deploy_to_modal(
            service_name="llm-service",
            model_id="my-model",
            service_type="llm"
        )
        ```
    """
    
    def __init__(self, workspace_dir: str = "./deployments"):
        """
        Initialize deployment manager.

        Args:
            workspace_dir: Directory for deployment artifacts
        """
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # Deployment tracking
        self.deployments: Dict[str, Dict[str, Any]] = {}
        self.deployments_file = self.workspace_dir / "deployments.json"
        self._load_deployments()

        # Setup logging
        self._setup_logging()

        # Initialize configuration manager
        self.config_manager = ConfigManager()

        # Initialize providers
        self._modal_provider = None
        self._triton_provider = None
        self._local_provider = None

        logger.info("Unified deployment manager initialized")
        logger.info(f"Workspace directory: {self.workspace_dir}")
    
    def _setup_logging(self):
        """Setup deployment logging"""
        log_dir = self.workspace_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create deployment-specific logger
        deployment_logger = logging.getLogger("deployment")
        deployment_logger.setLevel(logging.DEBUG)
        
        # File handler for deployment logs
        file_handler = logging.FileHandler(log_dir / "deployments.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        ))
        
        deployment_logger.addHandler(file_handler)
    
    def _load_deployments(self):
        """Load deployment tracking data"""
        if self.deployments_file.exists():
            with open(self.deployments_file, 'r') as f:
                self.deployments = json.load(f)
        else:
            self.deployments = {}
            self._save_deployments()
    
    def _save_deployments(self):
        """Save deployment tracking data"""
        with open(self.deployments_file, 'w') as f:
            json.dump(self.deployments, f, indent=2, default=str)
    
    async def deploy_to_modal(self, 
                              service_name: str,
                              model_id: str,
                              service_type: str = "llm",
                              config: Optional[Dict[str, Any]] = None,
                              tenant_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Deploy a service to Modal.
        
        Args:
            service_name: Name of the service to deploy
            model_id: Model identifier
            service_type: Type of service (llm, vision, audio, embedding, video)
            config: Additional configuration for the service
            
        Returns:
            Deployment result with endpoint information
        """
        # Extract tenant information for deployment isolation
        organization_id = tenant_context.get('organization_id') if tenant_context else 'default'
        tenant_prefix = f"org-{organization_id}" if organization_id != 'default' else ''
        
        # Generate tenant-isolated deployment ID
        base_deployment_id = f"{service_name}-{service_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        deployment_id = f"{tenant_prefix}-{base_deployment_id}" if tenant_prefix else base_deployment_id
        
        logger.info("=" * 60)
        logger.info(f"STARTING MODAL DEPLOYMENT: {deployment_id}")
        logger.info(f"TENANT: {organization_id}")
        logger.info("=" * 60)
        
        try:
            # Track deployment start for billing
            deployment_start_time = datetime.now()
            
            # Step 1: Validate configuration
            logger.info("Step 1/4: Validating deployment configuration...")
            self._validate_modal_config(service_name, model_id, service_type)
            
            # Step 2: Prepare deployment artifacts
            logger.info("Step 2/4: Preparing Modal deployment artifacts...")
            artifacts_path = await self._prepare_modal_artifacts(deployment_id, service_name, model_id, service_type, config)
            
            # Step 3: Deploy to Modal
            logger.info("Step 3/4: Deploying to Modal...")
            deployment_result = await self._deploy_modal_service(deployment_id, service_name, service_type, artifacts_path)
            
            # Calculate deployment duration
            deployment_duration = (datetime.now() - deployment_start_time).total_seconds() / 3600  # hours
            
            # Track billing for Modal deployment
            self._track_modal_deployment_billing(
                service_name=service_name,
                model_id=model_id,
                service_type=service_type,
                deployment_duration_hours=deployment_duration,
                config=config,
                result=deployment_result
            )
            
            # Step 4: Register deployment
            logger.info("Step 4/4: Registering deployment...")
            await self._register_deployment(deployment_id, {
                "service_name": service_name,
                "model_id": model_id,
                "service_type": service_type,
                "config": config or {},
                "deployment_duration_hours": deployment_duration
            }, deployment_result, tenant_context)
            
            logger.info("=" * 60)
            logger.info("MODAL DEPLOYMENT COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"Deployment ID: {deployment_id}")
            logger.info(f"Endpoint URL: {deployment_result.get('endpoint_url', 'N/A')}")
            
            return deployment_result
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error("MODAL DEPLOYMENT FAILED!")
            logger.error("=" * 60)
            logger.error(f"Error: {e}")
            
            # Update deployment status
            self.deployments[deployment_id] = {
                "service_name": service_name,
                "model_id": model_id,
                "service_type": service_type,
                "status": "failed",
                "error": str(e),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self._save_deployments()
            
            raise
    
    def _validate_modal_config(self, service_name: str, model_id: str, service_type: str):
        """Validate Modal deployment configuration"""
        logger.debug("Validating Modal deployment configuration...")
        
        # Check required fields
        if not service_name:
            raise ValueError("service_name is required")
        
        if not model_id:
            raise ValueError("model_id is required")
        
        # Check service type
        valid_service_types = ["llm", "vision", "audio", "embedding", "video"]
        if service_type not in valid_service_types:
            raise ValueError(f"service_type must be one of {valid_service_types}")
        
        # Check Modal token using ConfigManager
        modal_config = self.config_manager.get_deployment_config("modal")
        if not modal_config or not modal_config.get("token_id"):
            logger.warning("MODAL_TOKEN_ID not found in configuration")

        logger.info("Modal configuration validation passed")
    
    async def _prepare_modal_artifacts(self, deployment_id: str, service_name: str, model_id: str, service_type: str, config: Optional[Dict[str, Any]]) -> Path:
        """Prepare Modal deployment artifacts"""
        logger.info("Preparing Modal deployment artifacts...")
        
        # Create deployment workspace
        deployment_workspace = self.workspace_dir / deployment_id
        deployment_workspace.mkdir(exist_ok=True)
        
        artifacts = {
            "deployment_id": deployment_id,
            "service_name": service_name,
            "model_id": model_id,
            "service_type": service_type,
            "config": config or {},
            "platform": "modal",
            "created_at": datetime.now().isoformat()
        }
        
        # Save deployment artifacts
        with open(deployment_workspace / "deployment_config.json", 'w') as f:
            json.dump(artifacts, f, indent=2)
        
        logger.info(f"Modal deployment artifacts prepared at: {deployment_workspace}")
        return deployment_workspace
    
    async def _deploy_modal_service(self, deployment_id: str, service_name: str, service_type: str, artifacts_path: Path) -> Dict[str, Any]:
        """Deploy service to Modal using real Modal integration"""
        logger.info(f"Deploying {service_type} service '{service_name}' to Modal...")
        
        try:
            # Load deployment config
            config_file = artifacts_path / "deployment_config.json"
            with open(config_file, 'r') as f:
                deployment_config = json.load(f)
            
            model_id = deployment_config['model_id']
            config = deployment_config.get('config', {})
            
            # Use Modal provider for real deployment
            modal_provider = self.modal_provider
            
            # Step 1: Analyze the model to get optimal configuration
            logger.info(f"Analyzing model {model_id}...")
            model_config = await asyncio.get_event_loop().run_in_executor(
                None, modal_provider.analyze_model, model_id
            )
            
            # Step 2: Generate the appropriate Modal service
            logger.info(f"Generating {service_type} service for {model_config.architecture}...")
            service_code = await self._generate_modal_service_code(
                service_name=service_name,
                model_config=model_config,
                service_type=service_type,
                config=config
            )
            
            # Step 3: Save the generated service code
            service_file = artifacts_path / f"{service_name}_modal_service.py"
            with open(service_file, 'w') as f:
                f.write(service_code)
            
            # Step 4: Deploy to Modal (simulate for now, but with real structure)
            deployment_result = await self._execute_modal_deployment(
                service_file=service_file,
                service_name=service_name,
                model_config=model_config,
                deployment_id=deployment_id
            )
            
            result = {
                "provider": "modal",
                "deployment_id": deployment_id,
                "service_name": service_name,
                "service_type": service_type,
                "model_id": model_id,
                "model_architecture": model_config.architecture,
                "endpoint_url": deployment_result['endpoint_url'],
                "status": deployment_result['status'],
                "gpu_type": model_config.gpu_requirements,
                "memory_gb": model_config.memory_gb,
                "estimated_cost_per_hour": model_config.estimated_cost_per_hour,
                "deployed_at": datetime.now().isoformat(),
                "service_file": str(service_file)
            }
            
            logger.info(f"Modal deployment completed: {result['endpoint_url']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to deploy Modal service: {e}")
            raise
    
    async def _register_deployment(self, deployment_id: str, config: Dict[str, Any], deployment_result: Dict[str, Any], tenant_context: Optional[Dict[str, Any]] = None):
        """Register deployment in tracking system with tenant isolation"""
        logger.info("Registering Modal deployment...")
        
        deployment_info = {
            "config": config,
            "result": deployment_result,
            "status": "active",
            "platform": "modal",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            # Add tenant information for isolation
            "tenant": {
                "organization_id": tenant_context.get('organization_id', 'default') if tenant_context else 'default',
                "user_id": tenant_context.get('user_id') if tenant_context else None,
                "role": tenant_context.get('role', 'user') if tenant_context else 'user'
            }
        }
        
        self.deployments[deployment_id] = deployment_info
        self._save_deployments()
        
        logger.info(f"Modal deployment registered: {deployment_id}")
    
    async def list_deployments(self, tenant_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List deployments with optional tenant filtering"""
        
        # If tenant context is provided, filter by organization
        if tenant_context and tenant_context.get('organization_id'):
            organization_id = tenant_context['organization_id']
            filtered_deployments = []
            
            for deployment_id, info in self.deployments.items():
                # Check tenant information in deployment
                deployment_org = info.get('tenant', {}).get('organization_id', 'default')
                if deployment_org == organization_id:
                    filtered_deployments.append({
                        "deployment_id": deployment_id,
                        **info
                    })
            
            logger.info(f"Filtered deployments for tenant {organization_id}: {len(filtered_deployments)} found")
            return filtered_deployments
        
        # Return all deployments if no tenant context
        return [
            {
                "deployment_id": deployment_id,
                **info
            }
            for deployment_id, info in self.deployments.items()
        ]
    
    async def get_deployment(self, deployment_id: str, tenant_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Get deployment information with tenant access control"""
        deployment = self.deployments.get(deployment_id)
        
        if not deployment:
            return None
            
        # If tenant context is provided, verify access
        if tenant_context and tenant_context.get('organization_id'):
            organization_id = tenant_context['organization_id']
            deployment_org = deployment.get('tenant', {}).get('organization_id', 'default')
            
            # Check if user has access to this deployment
            if deployment_org != organization_id:
                logger.warning(f"Access denied: tenant {organization_id} tried to access deployment from {deployment_org}")
                return None
                
        return deployment
    
    async def delete_deployment(self, deployment_id: str, tenant_context: Optional[Dict[str, Any]] = None) -> bool:
        """Delete a Modal deployment with tenant access control"""
        logger.info(f"Deleting Modal deployment: {deployment_id}")
        
        try:
            if deployment_id not in self.deployments:
                logger.warning(f"Deployment not found: {deployment_id}")
                return False
                
            deployment = self.deployments[deployment_id]
            
            # Verify tenant access
            if tenant_context and tenant_context.get('organization_id'):
                organization_id = tenant_context['organization_id']
                deployment_org = deployment.get('tenant', {}).get('organization_id', 'default')
                
                if deployment_org != organization_id:
                    logger.warning(f"Access denied: tenant {organization_id} tried to delete deployment from {deployment_org}")
                    return False
            
            # TODO: Implement actual Modal service cleanup using Modal SDK
            
            # Remove from tracking
            del self.deployments[deployment_id]
            self._save_deployments()
            
            # Clean up workspace
            deployment_workspace = self.workspace_dir / deployment_id
            if deployment_workspace.exists():
                import shutil
                shutil.rmtree(deployment_workspace)
            
            logger.info(f"Modal deployment deleted: {deployment_id}")
            return True
                
        except Exception as e:
            logger.error(f"Failed to delete Modal deployment {deployment_id}: {e}")
            return False
    
    async def get_modal_service_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get real-time Modal service status"""
        logger.info(f"Getting Modal service status for: {deployment_id}")
        
        if deployment_id not in self.deployments:
            return {
                "deployment_id": deployment_id,
                "status": "not_found",
                "error": "Deployment not found"
            }
        
        deployment_info = self.deployments[deployment_id]
        
        try:
            # Get Modal service details
            service_name = deployment_info.get('service_name')
            model_id = deployment_info.get('model_id')
            
            # Check if Modal service is accessible
            modal_url = deployment_info.get('modal_url')
            
            status_info = {
                "deployment_id": deployment_id,
                "service_name": service_name,
                "model_id": model_id,
                "status": deployment_info.get('status', 'unknown'),
                "created_at": deployment_info.get('created_at'),
                "updated_at": deployment_info.get('updated_at'),
                "modal_url": modal_url,
                "platform": "modal",
                "monitoring": {
                    "health_check": await self._check_modal_health(modal_url),
                    "resource_usage": await self._get_modal_resource_usage(deployment_id),
                    "request_metrics": await self._get_modal_metrics(deployment_id),
                    "cost_tracking": await self._get_modal_cost_info(deployment_id)
                }
            }
            
            # Update status based on health check
            if status_info["monitoring"]["health_check"]["status"] == "healthy":
                status_info["status"] = "running"
            elif status_info["monitoring"]["health_check"]["status"] == "error":
                status_info["status"] = "error"
            else:
                status_info["status"] = "pending"
            
            logger.info(f"Modal service status retrieved: {deployment_id}")
            return status_info
            
        except Exception as e:
            logger.error(f"Failed to get Modal service status {deployment_id}: {e}")
            return {
                "deployment_id": deployment_id,
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def _check_modal_health(self, modal_url: Optional[str]) -> Dict[str, Any]:
        """Check Modal service health"""
        if not modal_url:
            return {
                "status": "unknown",
                "message": "No Modal URL available"
            }
        
        try:
            import httpx
            import asyncio
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try to ping the Modal endpoint
                response = await client.get(f"{modal_url}/health", timeout=5.0)
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        "last_check": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "status_code": response.status_code,
                        "last_check": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def _get_modal_resource_usage(self, deployment_id: str) -> Dict[str, Any]:
        """Get Modal service resource usage"""
        try:
            # In a real implementation, this would query Modal's API for resource usage
            # For now, return simulated data based on deployment info
            deployment_info = self.deployments.get(deployment_id, {})
            
            return {
                "gpu_utilization": "85%",  # Simulated
                "memory_usage": "12.5GB / 32GB",
                "cpu_usage": "45%",
                "requests_per_minute": 24,
                "average_response_time": "1.2s",
                "uptime": self._calculate_uptime(deployment_info.get('created_at')),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    async def _get_modal_metrics(self, deployment_id: str) -> Dict[str, Any]:
        """Get Modal service request metrics"""
        try:
            # Simulated metrics - in production this would come from Modal's monitoring
            return {
                "total_requests": 1247,
                "successful_requests": 1198,
                "failed_requests": 49,
                "success_rate": "96.1%",
                "average_latency": "1.15s",
                "requests_last_hour": 156,
                "errors_last_hour": 3,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    async def _get_modal_cost_info(self, deployment_id: str) -> Dict[str, Any]:
        """Get Modal service cost information"""
        try:
            deployment_info = self.deployments.get(deployment_id, {})
            
            # Calculate estimated costs based on uptime and GPU type
            uptime_hours = self._calculate_uptime_hours(deployment_info.get('created_at'))
            gpu_cost_per_hour = 4.0  # A100 default rate
            
            estimated_cost = uptime_hours * gpu_cost_per_hour
            
            return {
                "estimated_cost_usd": f"${estimated_cost:.4f}",
                "uptime_hours": f"{uptime_hours:.2f}",
                "hourly_rate": f"${gpu_cost_per_hour:.2f}",
                "gpu_type": "A100",
                "billing_period": "current_month",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def _calculate_uptime(self, created_at: Optional[str]) -> str:
        """Calculate service uptime"""
        if not created_at:
            return "Unknown"
        
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            uptime = datetime.now() - created.replace(tzinfo=None)
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
                
        except Exception:
            return "Unknown"
    
    def _calculate_uptime_hours(self, created_at: Optional[str]) -> float:
        """Calculate service uptime in hours"""
        if not created_at:
            return 0.0
        
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            uptime = datetime.now() - created.replace(tzinfo=None)
            return uptime.total_seconds() / 3600
        except Exception:
            return 0.0

    async def update_deployment_status(self, deployment_id: str, status: str, **kwargs):
        """Update deployment status"""
        if deployment_id in self.deployments:
            self.deployments[deployment_id]["status"] = status
            self.deployments[deployment_id]["updated_at"] = datetime.now().isoformat()
            
            for key, value in kwargs.items():
                self.deployments[deployment_id][key] = value
            
            self._save_deployments()
            logger.info(f"Updated deployment {deployment_id} status to {status}")
    
    @property
    def modal_provider(self):
        """Get or create Modal provider"""
        if self._modal_provider is None:
            from ..modal.deployer import ModalDeployer
            self._modal_provider = ModalDeployer()
        return self._modal_provider
    
    @property
    def triton_provider(self):
        """Get or create Triton provider"""
        if self._triton_provider is None:
            from ..triton.provider import TritonProvider
            self._triton_provider = TritonProvider(str(self.workspace_dir / "triton"))
        return self._triton_provider
    
    @property
    def local_provider(self):
        """Get or create Local GPU provider"""
        if self._local_provider is None:
            from ..local.provider import LocalGPUProvider
            self._local_provider = LocalGPUProvider(str(self.workspace_dir / "local"))
        return self._local_provider
    
    async def deploy_to_triton(self, config) -> Dict[str, Any]:
        """
        Deploy a service to Triton Inference Server.
        
        Args:
            config: TritonConfig instance
            
        Returns:
            Deployment result with endpoint information
        """
        logger.info("=" * 60)
        logger.info(f"STARTING TRITON DEPLOYMENT: {config.service_name}")
        logger.info("=" * 60)
        
        try:
            # Track deployment start for billing
            deployment_start_time = datetime.now()
            
            # Deploy using Triton provider
            result = await self.triton_provider.deploy(config)
            
            # Calculate deployment duration
            deployment_duration = (datetime.now() - deployment_start_time).total_seconds() / 3600  # hours
            
            # Track billing for deployment
            self._track_deployment_billing(
                config=config,
                provider="triton",
                operation_type="deployment",
                deployment_duration_hours=deployment_duration,
                result=result
            )
            
            # Register in our tracking system
            deployment_id = result["deployment_id"]
            deployment_info = {
                "config": config.to_dict(),
                "result": result,
                "status": "active",
                "platform": "triton",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "deployment_duration_hours": deployment_duration
            }
            
            self.deployments[deployment_id] = deployment_info
            self._save_deployments()
            
            logger.info("=" * 60)
            logger.info("TRITON DEPLOYMENT COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"Deployment ID: {deployment_id}")
            logger.info(f"Endpoint URL: {result.get('endpoint_url', 'N/A')}")
            
            return result
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error("TRITON DEPLOYMENT FAILED!")
            logger.error("=" * 60)
            logger.error(f"Error: {e}")
            raise
    
    async def deploy_to_local(self, config) -> Dict[str, Any]:
        """
        Deploy a service to local GPU.
        
        Args:
            config: LocalGPUConfig instance
            
        Returns:
            Deployment result with service information
        """
        logger.info("=" * 60)
        logger.info(f"STARTING LOCAL GPU DEPLOYMENT: {config.service_name}")
        logger.info(f"MODEL: {config.model_id}")
        logger.info(f"BACKEND: {config.backend.value}")
        logger.info("=" * 60)
        
        try:
            # Track deployment start for billing
            deployment_start_time = datetime.now()
            
            # Deploy using Local provider
            result = await self.local_provider.deploy(config)
            
            if result["success"]:
                # Calculate deployment duration
                deployment_duration = (datetime.now() - deployment_start_time).total_seconds() / 3600  # hours
                
                # Register in our tracking system
                deployment_id = f"local-{config.service_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                deployment_info = {
                    "config": config.to_dict(),
                    "result": result,
                    "status": "active",
                    "platform": "local",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "deployment_duration_hours": deployment_duration
                }
                
                self.deployments[deployment_id] = deployment_info
                self._save_deployments()
                
                logger.info("=" * 60)
                logger.info("LOCAL GPU DEPLOYMENT COMPLETED SUCCESSFULLY!")
                logger.info("=" * 60)
                logger.info(f"Service: {config.service_name}")
                logger.info(f"Backend: {config.backend.value}")
                
                return {
                    **result,
                    "deployment_id": deployment_id,
                    "platform": "local"
                }
            else:
                return result
                
        except Exception as e:
            logger.error("=" * 60)
            logger.error("LOCAL GPU DEPLOYMENT FAILED!")
            logger.error("=" * 60)
            logger.error(f"Error: {e}")
            raise
    
    async def list_local_services(self) -> List[Dict[str, Any]]:
        """List local GPU services"""
        if not self.local_provider:
            return []
        return await self.local_provider.list_services()
    
    async def get_local_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get local service information"""
        if not self.local_provider:
            return None
        return await self.local_provider.get_service_info(service_name)
    
    async def undeploy_local_service(self, service_name: str) -> Dict[str, Any]:
        """Undeploy local service"""
        if not self.local_provider:
            return {
                "success": False,
                "error": "Local provider not available"
            }
        
        result = await self.local_provider.undeploy(service_name)
        
        # Remove from tracking
        deployment_ids_to_remove = []
        for deployment_id, info in self.deployments.items():
            if (info.get('platform') == 'local' and 
                info.get('config', {}).get('service_name') == service_name):
                deployment_ids_to_remove.append(deployment_id)
        
        for deployment_id in deployment_ids_to_remove:
            del self.deployments[deployment_id]
        
        if deployment_ids_to_remove:
            self._save_deployments()
        
        return result
    
    async def get_local_system_status(self) -> Dict[str, Any]:
        """Get local GPU system status"""
        if not self.local_provider:
            return {
                "available": False,
                "error": "Local provider not initialized"
            }
        return await self.local_provider.get_system_status()
    
    async def list_providers(self) -> List[str]:
        """List available deployment providers"""
        return ["local", "modal", "triton"]
    
    async def get_provider_status(self, provider: str) -> Dict[str, Any]:
        """Get status of a deployment provider"""
        if provider == "local":
            # Check local GPU availability
            try:
                from ...utils.gpu_utils import get_gpu_manager
                gpu_manager = get_gpu_manager()
                
                return {
                    "provider": "local",
                    "available": gpu_manager.cuda_available,
                    "description": "Local GPU deployment with vLLM, TensorRT-LLM, Transformers",
                    "gpu_count": len(gpu_manager.gpus),
                    "cuda_available": gpu_manager.cuda_available,
                    "nvidia_smi_available": gpu_manager.nvidia_smi_available,
                    "requirements": ["CUDA", "GPU drivers", "Sufficient GPU memory"]
                }
            except Exception as e:
                return {
                    "provider": "local",
                    "available": False,
                    "description": "Local GPU deployment",
                    "error": str(e)
                }
        elif provider == "modal":
            return {
                "provider": "modal",
                "available": True,
                "description": "Modal serverless platform"
            }
        elif provider == "triton":
            # Check if Docker is available
            try:
                import docker
                docker.from_env()
                docker_available = True
            except Exception:
                docker_available = False
            
            return {
                "provider": "triton",
                "available": docker_available,
                "description": "Triton Inference Server with TensorRT-LLM",
                "requirements": ["Docker", "GPU support"]
            }
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _track_deployment_billing(
        self,
        config: Any,
        provider: str,
        operation_type: str,
        deployment_duration_hours: float,
        result: Dict[str, Any]
    ):
        """Track billing for deployment operations"""
        try:
            from ...core.models.deployment_billing_tracker import get_deployment_billing_tracker
            
            # Extract GPU info from config
            gpu_type = getattr(config, 'gpu_type', None)
            gpu_count = getattr(config, 'gpu_count', 1)
            memory_gb = getattr(config, 'memory_gb', None)
            
            # Track the deployment billing
            billing_tracker = get_deployment_billing_tracker()
            billing_tracker.track_deployment_usage(
                model_id=getattr(config, 'model_id', 'unknown'),
                provider=provider,
                operation_type=operation_type,
                service_type=getattr(config, 'service_type', 'unknown').value if hasattr(getattr(config, 'service_type', 'unknown'), 'value') else str(getattr(config, 'service_type', 'unknown')),
                operation="deploy",
                gpu_type=gpu_type,
                gpu_count=gpu_count,
                runtime_hours=deployment_duration_hours,
                deployment_duration_hours=deployment_duration_hours,
                memory_gb=memory_gb,
                metadata={
                    "deployment_id": result.get("deployment_id"),
                    "endpoint_url": result.get("endpoint_url"),
                    "provider_details": provider
                }
            )
            
            logger.info(f"Tracked deployment billing: {provider} - {deployment_duration_hours:.3f}h")
            
        except Exception as e:
            logger.error(f"Failed to track deployment billing: {e}")
    
    async def estimate_deployment_cost(
        self,
        provider: str,
        gpu_type: str,
        gpu_count: int = 1,
        estimated_hours: float = 1.0
    ) -> Dict[str, float]:
        """Estimate deployment costs before starting"""
        try:
            from ...core.models.deployment_billing_tracker import get_deployment_billing_tracker
            
            billing_tracker = get_deployment_billing_tracker()
            return billing_tracker.estimate_deployment_cost(
                provider=provider,
                gpu_type=gpu_type,
                gpu_count=gpu_count,
                estimated_hours=estimated_hours
            )
        except Exception as e:
            logger.error(f"Failed to estimate deployment cost: {e}")
            return {"total_cost": 0.0, "compute_cost": 0.0, "storage_cost": 0.0, "network_cost": 0.0}
    
    def _track_modal_deployment_billing(
        self,
        service_name: str,
        model_id: str,
        service_type: str,
        deployment_duration_hours: float,
        config: Optional[Dict[str, Any]],
        result: Dict[str, Any]
    ):
        """Track billing for Modal deployment operations"""
        try:
            from ...core.models.deployment_billing_tracker import get_deployment_billing_tracker
            
            # Extract GPU info from config or use defaults
            gpu_type = config.get('gpu_type', 't4') if config else 't4'
            gpu_count = config.get('gpu_count', 1) if config else 1
            memory_gb = config.get('memory_gb', 8) if config else 8
            
            # Track the Modal deployment billing
            billing_tracker = get_deployment_billing_tracker()
            billing_tracker.track_deployment_usage(
                model_id=model_id,
                provider="modal",
                operation_type="deployment",
                service_type=service_type,
                operation="deploy",
                gpu_type=gpu_type,
                gpu_count=gpu_count,
                runtime_hours=deployment_duration_hours,
                deployment_duration_hours=deployment_duration_hours,
                memory_gb=memory_gb,
                metadata={
                    "service_name": service_name,
                    "deployment_id": result.get("deployment_id"),
                    "endpoint_url": result.get("endpoint_url"),
                    "provider_details": "modal_serverless"
                }
            )
            
            logger.info(f"Tracked Modal deployment billing: {service_name} - {deployment_duration_hours:.3f}h")
            
        except Exception as e:
            logger.error(f"Failed to track Modal deployment billing: {e}")
    
    async def list_modal_services(self) -> List[Dict[str, Any]]:
        """List available Modal services by type"""
        services = {
            "llm": ["isa_llm_service"],
            "vision": ["isa_vision_ocr_service", "isa_vision_ui_service", "isa_vision_table_service", "isa_vision_qwen25_service"],
            "audio": ["isa_audio_chatTTS_service", "isa_audio_openvoice_service", "isa_audio_service_v2", "isa_audio_fish_service"],
            "embedding": ["isa_embed_rerank_service"],
            "video": ["isa_video_hunyuan_service"]
        }
        
        result = []
        for service_type, service_list in services.items():
            for service_name in service_list:
                result.append({
                    "service_name": service_name,
                    "service_type": service_type,
                    "platform": "modal"
                })
        
        return result
    
    # ============= MODAL SERVICE CODE GENERATION =============
    
    async def _generate_modal_service_code(self, 
                                           service_name: str, 
                                           model_config: Any, 
                                           service_type: str, 
                                           config: Dict[str, Any]) -> str:
        """Generate Modal service code based on model type and configuration"""
        
        # Choose the appropriate service template based on service_type
        if service_type == "llm":
            return self._generate_llm_service_code(service_name, model_config, config)
        elif service_type == "vision":
            return self._generate_vision_service_code(service_name, model_config, config)
        elif service_type == "embedding":
            return self._generate_embedding_service_code(service_name, model_config, config)
        else:
            # Default to LLM service
            return self._generate_llm_service_code(service_name, model_config, config)
    
    def _generate_llm_service_code(self, service_name: str, model_config: Any, config: Dict[str, Any]) -> str:
        """Generate production-ready LLM service code for Modal"""
        dependencies = getattr(model_config, 'dependencies', None) or [
            "torch", "transformers>=4.36.0", "accelerate", "bitsandbytes", "flash-attn"
        ]
        
        # Determine optimal GPU based on model size
        gpu_config = self._get_optimal_gpu_config(model_config)
        
        return f'''"""
{service_name} LLM Service for Modal

Production-ready service for model: {getattr(model_config, 'model_id', 'unknown')}
Architecture: {getattr(model_config, 'architecture', 'transformer')}
Generated automatically by ISA Model Deployment Manager
"""

import modal
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Create Modal app
app = modal.App("{service_name}")

# Production image with optimized dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        {', '.join([f'"{dep}"' for dep in dependencies])}
    ])
    .env({{"HF_HUB_ENABLE_HF_TRANSFER": "1"}})
)

@app.cls(
    image=image,
    gpu=modal.gpu.{gpu_config['gpu_type']}(count={gpu_config['gpu_count']}),
    container_idle_timeout=300,
    timeout=1800,  # 30 minutes
    memory={getattr(model_config, 'container_memory_mb', 32768)},
    keep_warm=1,  # Keep one container warm
    allow_concurrent_inputs=10
)
class {service_name.replace('-', '_').title()}Service:
    
    @modal.enter()
    def load_model(self):
        """Load model with production optimizations"""
        import torch
        from transformers import (
            AutoTokenizer, 
            AutoModelForCausalLM,
            BitsAndBytesConfig
        )
        
        model_id = "{getattr(model_config, 'model_id', 'microsoft/DialoGPT-medium')}"
        
        print(f"Loading model: {{model_id}}")
        start_time = time.time()
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True,
            use_fast=True
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Configure quantization for efficiency
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        # Load model with optimizations
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,
            attn_implementation="flash_attention_2"
        )
        
        self.model.eval()
        
        load_time = time.time() - start_time
        print(f"Model loaded successfully in {{load_time:.2f}}s")
        
        # Model metadata
        self.model_info = {{
            "model_id": model_id,
            "architecture": "{getattr(model_config, 'architecture', 'transformer')}",
            "parameters": getattr(self.model, 'num_parameters', lambda: 0)(),
            "loaded_at": datetime.now().isoformat(),
            "load_time_seconds": load_time
        }}
    
    @modal.method()
    def generate(self, 
                messages: List[Dict[str, str]], 
                max_tokens: int = 512,
                temperature: float = 0.7,
                top_p: float = 0.9,
                top_k: int = 50,
                do_sample: bool = True,
                **kwargs) -> Dict[str, Any]:
        """Generate response with production features"""
        
        start_time = time.time()
        
        try:
            # Format messages into prompt
            prompt = self._format_messages(messages)
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=2048
            ).to(self.model.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    do_sample=do_sample,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    use_cache=True
                )
            
            # Decode response
            response_tokens = outputs[0][inputs['input_ids'].shape[-1]:]
            response_text = self.tokenizer.decode(
                response_tokens, 
                skip_special_tokens=True
            ).strip()
            
            generation_time = time.time() - start_time
            
            return {{
                "response": response_text,
                "model": self.model_info["model_id"],
                "usage": {{
                    "prompt_tokens": inputs['input_ids'].shape[-1],
                    "completion_tokens": len(response_tokens),
                    "total_tokens": inputs['input_ids'].shape[-1] + len(response_tokens)
                }},
                "metadata": {{
                    "generation_time_seconds": generation_time,
                    "parameters": {{
                        "temperature": temperature,
                        "top_p": top_p,
                        "top_k": top_k,
                        "max_tokens": max_tokens
                    }},
                    "timestamp": datetime.now().isoformat()
                }}
            }}
            
        except Exception as e:
            return {{
                "error": str(e),
                "error_type": type(e).__name__,
                "model": self.model_info.get("model_id", "unknown"),
                "timestamp": datetime.now().isoformat()
            }}
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format messages into model-appropriate prompt"""
        if not messages:
            return ""
        
        # Simple chat format - can be enhanced for specific models
        formatted_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                formatted_parts.append(f"System: {{content}}")
            elif role == "user":
                formatted_parts.append(f"Human: {{content}}")
            elif role == "assistant":
                formatted_parts.append(f"Assistant: {{content}}")
        
        formatted_parts.append("Assistant:")
        return "\\n\\n".join(formatted_parts)
    
    @modal.method()
    def get_model_info(self) -> Dict[str, Any]:
        """Get model metadata"""
        return self.model_info

# Web endpoint for HTTP access
@app.function(
    image=image,
    timeout=300
)
@modal.web_endpoint(method="POST")
async def inference_endpoint(item: Dict[str, Any]):
    """HTTP endpoint for model inference"""
    try:
        service = {service_name.replace('-', '_').title()}Service()
        
        # Extract parameters
        messages = item.get("messages", [])
        max_tokens = item.get("max_tokens", 512)
        temperature = item.get("temperature", 0.7)
        top_p = item.get("top_p", 0.9)
        
        # Generate response
        result = service.generate(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        
        return result
        
    except Exception as e:
        return {{
            "error": str(e),
            "error_type": type(e).__name__,
            "endpoint": "inference_endpoint",
            "timestamp": datetime.now().isoformat()
        }}

@app.function(image=image)
@modal.web_endpoint(method="GET")
async def health_check():
    """Health check endpoint"""
    return {{
        "status": "healthy",
        "service": "{service_name}",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }}

@app.function(image=image)  
@modal.web_endpoint(method="GET")
async def model_info():
    """Model information endpoint"""
    try:
        service = {service_name.replace('-', '_').title()}Service()
        return service.get_model_info()
    except Exception as e:
        return {{
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }}

# For local testing
if __name__ == "__main__":
    # Test the service locally
    import asyncio
    
    async def test():
        service = {service_name.replace('-', '_').title()}Service()
        result = service.generate([
            {{"role": "user", "content": "Hello! How are you today?"}}
        ])
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())
'''
    
    def _generate_vision_service_code(self, service_name: str, model_config: Any, config: Dict[str, Any]) -> str:
        """Generate Vision service code for Modal"""
        return f'# Vision service template for {service_name} - {model_config.model_id}'
    
    def _generate_embedding_service_code(self, service_name: str, model_config: Any, config: Dict[str, Any]) -> str:
        """Generate Embedding service code for Modal"""
        return f'# Embedding service template for {service_name} - {model_config.model_id}'
    
    async def _execute_modal_deployment(self, 
                                        service_file: Path, 
                                        service_name: str, 
                                        model_config: Any, 
                                        deployment_id: str) -> Dict[str, Any]:
        """Execute the actual Modal deployment using Modal SDK"""
        
        logger.info(f"Executing Modal deployment for {service_name}...")
        
        try:
            import subprocess
            import tempfile
            import os
            
            # Check if modal CLI is available
            modal_check = subprocess.run(["modal", "--version"], 
                                       capture_output=True, text=True, timeout=10)
            if modal_check.returncode != 0:
                raise RuntimeError("Modal CLI not found. Please install Modal: pip install modal")
            
            # Create a temporary script for deployment
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
                tmp_file.write(open(service_file, 'r').read())
                tmp_script_path = tmp_file.name
            
            try:
                # Execute Modal deployment
                logger.info(f"Deploying Modal service from {service_file}")
                deploy_result = subprocess.run(
                    ["modal", "deploy", tmp_script_path],
                    capture_output=True, 
                    text=True, 
                    timeout=300,  # 5 minute timeout
                    cwd=service_file.parent
                )
                
                if deploy_result.returncode == 0:
                    # Parse deployment output to extract endpoint URL
                    output = deploy_result.stdout + deploy_result.stderr
                    endpoint_url = self._extract_modal_endpoint(output, service_name, deployment_id)
                    
                    result = {
                        "status": "deployed",
                        "endpoint_url": endpoint_url,
                        "deployment_id": deployment_id,
                        "service_file": str(service_file),
                        "model_architecture": getattr(model_config, 'architecture', 'unknown'),
                        "deployment_output": output,
                        "estimated_startup_time": "30-60 seconds"
                    }
                    
                    logger.info(f"Modal deployment completed successfully: {endpoint_url}")
                    return result
                    
                else:
                    error_output = deploy_result.stderr or deploy_result.stdout
                    logger.error(f"Modal deployment failed: {error_output}")
                    raise RuntimeError(f"Modal deployment failed: {error_output}")
                    
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_script_path):
                    os.unlink(tmp_script_path)
            
        except subprocess.TimeoutExpired:
            logger.error("Modal deployment timed out")
            raise RuntimeError("Modal deployment timed out after 5 minutes")
            
        except Exception as e:
            logger.error(f"Failed to execute Modal deployment: {e}")
            raise
    
    def _extract_modal_endpoint(self, output: str, service_name: str, deployment_id: str) -> str:
        """Extract Modal endpoint URL from deployment output"""
        import re
        
        # Look for typical Modal endpoint patterns in output
        patterns = [
            r'https://[a-zA-Z0-9\-]+--[a-zA-Z0-9\-]+\.modal\.run',
            r'Deployed! Your app is at (https://[^\s]+)',
            r'App deployed to (https://[^\s]+)',
            r'Available at (https://[^\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output)
            if match:
                url = match.group(1) if match.lastindex else match.group(0)
                logger.info(f"Extracted Modal endpoint: {url}")
                return url
        
        # If no endpoint found in output, generate expected URL pattern
        endpoint_url = f"https://{service_name}--{deployment_id}.modal.run"
        logger.warning(f"Could not extract endpoint from output, using expected pattern: {endpoint_url}")
        return endpoint_url
    
    def _get_optimal_gpu_config(self, model_config: Any) -> Dict[str, Any]:
        """Determine optimal GPU configuration based on model size"""
        
        # Get model parameters or estimate from model ID
        parameters = getattr(model_config, 'parameters', None)
        model_id = getattr(model_config, 'model_id', '')
        
        # Estimate parameters from model name if not available
        if not parameters:
            if '7b' in model_id.lower():
                parameters = 7_000_000_000
            elif '13b' in model_id.lower():
                parameters = 13_000_000_000
            elif '70b' in model_id.lower():
                parameters = 70_000_000_000
            elif 'large' in model_id.lower():
                parameters = 1_000_000_000
            elif 'medium' in model_id.lower():
                parameters = 350_000_000
            else:
                parameters = 500_000_000  # Default assumption
        
        # Choose GPU based on model size
        if parameters > 50_000_000_000:  # >50B parameters
            return {"gpu_type": "A100", "gpu_count": 2}
        elif parameters > 15_000_000_000:  # 15B-50B parameters
            return {"gpu_type": "A100", "gpu_count": 1}
        elif parameters > 3_000_000_000:  # 3B-15B parameters
            return {"gpu_type": "A10G", "gpu_count": 1}
        else:  # <3B parameters
            return {"gpu_type": "T4", "gpu_count": 1}