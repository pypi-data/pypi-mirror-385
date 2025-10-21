"""
Triton deployment provider

Handles deployment of models to Triton Inference Server with TensorRT-LLM optimization.
"""

import os
import json
import logging
import subprocess
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import asyncio
import docker

from .config import TritonConfig, TritonServiceType, TritonBackend

logger = logging.getLogger(__name__)


class TritonProvider:
    """
    Provider for deploying models to Triton Inference Server with TensorRT-LLM.
    
    This provider handles:
    - Model conversion to TensorRT engines
    - Triton model configuration generation
    - Docker container deployment
    - Health monitoring and scaling
    """
    
    def __init__(self, workspace_dir: str = "./triton_deployments"):
        """
        Initialize Triton provider.
        
        Args:
            workspace_dir: Directory for deployment artifacts
        """
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {e}")
            self.docker_client = None
        
        # Deployment tracking
        self.deployments: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Triton provider initialized")
        logger.info(f"Workspace directory: {self.workspace_dir}")
    
    async def deploy(self, config: TritonConfig) -> Dict[str, Any]:
        """
        Deploy a model to Triton Inference Server.
        
        Args:
            config: Triton deployment configuration
            
        Returns:
            Deployment result with endpoint information
        """
        deployment_id = f"{config.service_name}-triton-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        logger.info("=" * 60)
        logger.info(f"STARTING TRITON DEPLOYMENT: {deployment_id}")
        logger.info("=" * 60)
        
        try:
            # Step 1: Prepare workspace
            logger.info("Step 1/6: Preparing deployment workspace...")
            workspace = await self._prepare_workspace(deployment_id, config)
            
            # Step 2: Download HF model
            logger.info("Step 2/6: Downloading HuggingFace model...")
            hf_model_path = await self._download_hf_model(config, workspace)
            
            # Step 3: Convert to TensorRT engine (if needed)
            if config.use_tensorrt and config.service_type == TritonServiceType.LLM:
                logger.info("Step 3/6: Converting model to TensorRT engine...")
                engine_path = await self._build_tensorrt_engine(config, workspace, hf_model_path)
            else:
                logger.info("Step 3/6: Skipping TensorRT conversion...")
                engine_path = hf_model_path
            
            # Step 4: Generate Triton model configuration
            logger.info("Step 4/6: Generating Triton model configuration...")
            await self._generate_triton_config(config, workspace, engine_path)
            
            # Step 5: Deploy container
            logger.info("Step 5/6: Deploying Triton container...")
            container_info = await self._deploy_container(config, workspace)
            
            # Step 6: Verify deployment
            logger.info("Step 6/6: Verifying deployment...")
            endpoint_url = await self._verify_deployment(config, container_info)
            
            result = {
                "provider": "triton",
                "deployment_id": deployment_id,
                "service_name": config.service_name,
                "service_type": config.service_type.value,
                "endpoint_url": endpoint_url,
                "container_id": container_info.get("container_id"),
                "status": "deployed",
                "deployed_at": datetime.now().isoformat()
            }
            
            # Register deployment
            self.deployments[deployment_id] = {
                "config": config.to_dict(),
                "result": result,
                "workspace": str(workspace)
            }
            
            logger.info("=" * 60)
            logger.info("TRITON DEPLOYMENT COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"Deployment ID: {deployment_id}")
            logger.info(f"Endpoint URL: {endpoint_url}")
            
            return result
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error("TRITON DEPLOYMENT FAILED!")
            logger.error("=" * 60)
            logger.error(f"Error: {e}")
            raise
    
    async def _prepare_workspace(self, deployment_id: str, config: TritonConfig) -> Path:
        """Prepare deployment workspace"""
        workspace = self.workspace_dir / deployment_id
        workspace.mkdir(exist_ok=True)
        
        # Create required directories
        (workspace / "hf_model").mkdir(exist_ok=True)
        (workspace / "engines").mkdir(exist_ok=True)
        (workspace / "model_repository" / config.model_name / config.model_version).mkdir(parents=True, exist_ok=True)
        
        # Save deployment config
        with open(workspace / "deployment_config.json", 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
        
        logger.info(f"Workspace prepared at: {workspace}")
        return workspace
    
    async def _download_hf_model(self, config: TritonConfig, workspace: Path) -> Path:
        """Download HuggingFace model"""
        hf_model_path = workspace / "hf_model"
        
        # Use git clone or huggingface_hub to download
        try:
            from huggingface_hub import snapshot_download
            
            logger.info(f"Downloading model: {config.model_id}")
            snapshot_download(
                repo_id=config.model_id,
                local_dir=str(hf_model_path),
                local_dir_use_symlinks=False
            )
            
            logger.info(f"Model downloaded to: {hf_model_path}")
            return hf_model_path
            
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise
    
    async def _build_tensorrt_engine(self, config: TritonConfig, workspace: Path, hf_model_path: Path) -> Path:
        """Build TensorRT engine using Docker"""
        engine_output_path = workspace / "engines"
        
        logger.info("Building TensorRT engine using Docker...")
        
        # Prepare build command
        build_options = config.build_options
        build_cmd_parts = [
            "trtllm-build",
            f"--checkpoint_dir /workspace/hf_model",
            f"--output_dir /workspace/engines",
        ]
        
        # Add build options
        for key, value in build_options.items():
            if isinstance(value, bool):
                if value:
                    build_cmd_parts.append(f"--{key}")
            else:
                build_cmd_parts.append(f"--{key} {value}")
        
        build_cmd = " && ".join([
            "set -e",
            "echo '>>> Building TensorRT engine...'",
            " ".join(build_cmd_parts),
            "echo '>>> TensorRT engine build completed!'"
        ])
        
        # Run Docker container for building
        if self.docker_client:
            try:
                logger.info("Starting TensorRT build container...")
                
                container = self.docker_client.containers.run(
                    config.build_container_image,
                    command=f"bash -c \"{build_cmd}\"",
                    volumes={
                        str(hf_model_path): {"bind": "/workspace/hf_model", "mode": "ro"},
                        str(engine_output_path): {"bind": "/workspace/engines", "mode": "rw"}
                    },
                    device_requests=[
                        docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
                    ],
                    remove=True,
                    detach=False
                )
                
                logger.info("TensorRT engine build completed")
                
            except Exception as e:
                logger.error(f"TensorRT build failed: {e}")
                raise
        else:
            # Fallback to subprocess if Docker client unavailable
            logger.warning("Docker client unavailable, using subprocess...")
            # Implementation would depend on having docker command available
            raise RuntimeError("Docker client required for TensorRT build")
        
        return engine_output_path
    
    async def _generate_triton_config(self, config: TritonConfig, workspace: Path, model_path: Path):
        """Generate Triton model configuration"""
        model_repo_path = workspace / "model_repository" / config.model_name
        
        # Generate config.pbtxt
        if config.backend == TritonBackend.TENSORRT_LLM:
            config_content = self._generate_tensorrt_llm_config(config)
        elif config.backend == TritonBackend.PYTHON:
            config_content = self._generate_python_backend_config(config)
        else:
            raise ValueError(f"Unsupported backend: {config.backend}")
        
        # Write config file
        with open(model_repo_path / "config.pbtxt", 'w') as f:
            f.write(config_content)
        
        # Copy model files to model repository
        model_version_path = model_repo_path / config.model_version
        if config.use_tensorrt:
            # Copy engine files
            import shutil
            if (model_path / "model.engine").exists():
                shutil.copy2(model_path / "model.engine", model_version_path)
            else:
                # Copy all engine files
                for engine_file in model_path.glob("*.engine"):
                    shutil.copy2(engine_file, model_version_path)
        else:
            # Copy HF model files
            import shutil
            shutil.copytree(model_path, model_version_path / "model", dirs_exist_ok=True)
        
        logger.info(f"Triton configuration generated at: {model_repo_path}")
    
    def _generate_tensorrt_llm_config(self, config: TritonConfig) -> str:
        """Generate TensorRT-LLM backend configuration"""
        return f'''name: "{config.model_name}"
backend: "tensorrtllm"
max_batch_size: {config.max_batch_size}

{"decoupled: true" if config.enable_streaming else ""}

input [
  {{
    name: "text_input"
    data_type: TYPE_STRING
    dims: [ -1 ]
  }},
  {{
    name: "max_new_tokens"
    data_type: TYPE_UINT32
    dims: [ 1 ]
    optional: true
  }},
  {{
    name: "stream"
    data_type: TYPE_BOOL
    dims: [ 1 ]
    optional: true
  }},
  {{
    name: "temperature"
    data_type: TYPE_FP32
    dims: [ 1 ]
    optional: true
  }},
  {{
    name: "top_p"
    data_type: TYPE_FP32
    dims: [ 1 ]
    optional: true
  }}
]

output [
  {{
    name: "text_output"
    data_type: TYPE_STRING
    dims: [ -1 ]
  }}
]

instance_group [
  {{
    count: {config.instance_group_count}
    kind: {config.instance_group_kind}
  }}
]

parameters {{
  key: "model_type"
  value: {{ string_value: "{"inflight_batching_llm" if config.use_inflight_batching else "llm"}" }}
}}

parameters {{
  key: "max_tokens_in_paged_kv_cache"
  value: {{ string_value: "{config.max_sequence_length * config.max_batch_size}" }}
}}'''
    
    def _generate_python_backend_config(self, config: TritonConfig) -> str:
        """Generate Python backend configuration"""
        return f'''name: "{config.model_name}"
backend: "python"
max_batch_size: {config.max_batch_size}

input [
  {{
    name: "input"
    data_type: TYPE_STRING
    dims: [ -1 ]
  }}
]

output [
  {{
    name: "output"
    data_type: TYPE_STRING
    dims: [ -1 ]
  }}
]

instance_group [
  {{
    count: {config.instance_group_count}
    kind: {config.instance_group_kind}
  }}
]'''
    
    async def _deploy_container(self, config: TritonConfig, workspace: Path) -> Dict[str, Any]:
        """Deploy Triton container"""
        if not self.docker_client:
            raise RuntimeError("Docker client required for container deployment")
        
        # Generate docker-compose.yml
        await self._generate_docker_compose(config, workspace)
        
        # Deploy using docker-compose
        compose_file = workspace / "docker-compose.yml"
        
        try:
            # Run docker-compose up
            cmd = f"cd {workspace} && docker-compose up -d"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Docker compose failed: {result.stderr}")
            
            logger.info("Triton container deployed successfully")
            
            return {
                "container_id": f"triton-{config.service_name}",
                "compose_file": str(compose_file)
            }
            
        except Exception as e:
            logger.error(f"Container deployment failed: {e}")
            raise
    
    async def _generate_docker_compose(self, config: TritonConfig, workspace: Path):
        """Generate docker-compose.yml for Triton deployment"""
        compose_content = f'''version: '3.8'

services:
  triton-{config.service_name}:
    image: {config.container_image}
    ports:
      - "{config.http_port}:{config.http_port}"
      - "{config.grpc_port}:{config.grpc_port}"
      - "{config.metrics_port}:{config.metrics_port}"
    volumes:
      - ./model_repository:/models
    environment:
      - CUDA_VISIBLE_DEVICES=0
{self._format_env_vars(config.environment)}
    command: >
      tritonserver
      --model-repository=/models
      --allow-http=true
      --allow-grpc=true
      --allow-metrics=true
      --http-port={config.http_port}
      --grpc-port={config.grpc_port}
      --metrics-port={config.metrics_port}
      --log-verbose=1
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: {config.gpu_count}
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{config.http_port}/v2/health/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
'''
        
        with open(workspace / "docker-compose.yml", 'w') as f:
            f.write(compose_content)
        
        logger.info("Docker compose configuration generated")
    
    def _format_env_vars(self, env_vars: Dict[str, str]) -> str:
        """Format environment variables for docker-compose"""
        if not env_vars:
            return ""
        
        formatted = []
        for key, value in env_vars.items():
            formatted.append(f"      - {key}={value}")
        
        return "\n" + "\n".join(formatted)
    
    async def _verify_deployment(self, config: TritonConfig, container_info: Dict[str, Any]) -> str:
        """Verify deployment is healthy"""
        import time
        import requests
        
        endpoint_url = f"http://localhost:{config.http_port}"
        health_url = f"{endpoint_url}/v2/health/ready"
        
        # Wait for service to be ready
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    logger.info("Triton service is healthy and ready")
                    return endpoint_url
            except Exception:
                pass
            
            if i < max_retries - 1:
                logger.info(f"Waiting for Triton service... ({i+1}/{max_retries})")
                time.sleep(10)
        
        raise RuntimeError("Triton service failed to become ready")
    
    async def list_deployments(self) -> List[Dict[str, Any]]:
        """List all Triton deployments"""
        return [
            {
                "deployment_id": deployment_id,
                **info
            }
            for deployment_id, info in self.deployments.items()
        ]
    
    async def delete_deployment(self, deployment_id: str) -> bool:
        """Delete a Triton deployment"""
        if deployment_id not in self.deployments:
            return False
        
        try:
            deployment_info = self.deployments[deployment_id]
            workspace = Path(deployment_info["workspace"])
            
            # Stop docker-compose services
            if (workspace / "docker-compose.yml").exists():
                cmd = f"cd {workspace} && docker-compose down"
                subprocess.run(cmd, shell=True, capture_output=True)
            
            # Clean up workspace
            import shutil
            if workspace.exists():
                shutil.rmtree(workspace)
            
            # Remove from tracking
            del self.deployments[deployment_id]
            
            logger.info(f"Triton deployment deleted: {deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Triton deployment {deployment_id}: {e}")
            return False