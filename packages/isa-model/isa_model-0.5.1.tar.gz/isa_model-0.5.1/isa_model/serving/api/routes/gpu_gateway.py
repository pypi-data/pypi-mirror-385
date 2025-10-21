"""
GPU Gateway API Routes
云端Rails API与本地GPU网关的集成接口
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta

from ....core.config import get_settings
from ....deployment.local.config import LocalGPUConfig, LocalServiceType, LocalBackend
from ....auth.middleware import get_current_tenant
from ....database.models import Tenant

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gpu-gateway", tags=["GPU Gateway"])


class GPUGatewayClient:
    """GPU网关客户端 - 云端与本地GPU网关通信"""
    
    def __init__(self):
        self.settings = get_settings()
        self.gateways: Dict[str, Dict] = {}  # gateway_id -> {url, status, last_seen}
        self.gateway_pool = []  # 可用网关列表
        
    async def register_gateway(self, gateway_id: str, gateway_url: str, 
                             capabilities: List[str] = None):
        """注册GPU网关"""
        self.gateways[gateway_id] = {
            "url": gateway_url,
            "status": "online",
            "last_seen": datetime.now(),
            "capabilities": capabilities or [],
            "nodes": [],
            "metrics": {}
        }
        
        if gateway_id not in self.gateway_pool:
            self.gateway_pool.append(gateway_id)
        
        logger.info(f"✅ Registered GPU gateway: {gateway_id}")
    
    async def unregister_gateway(self, gateway_id: str):
        """注销GPU网关"""
        if gateway_id in self.gateways:
            del self.gateways[gateway_id]
        
        if gateway_id in self.gateway_pool:
            self.gateway_pool.remove(gateway_id)
        
        logger.info(f"❌ Unregistered GPU gateway: {gateway_id}")
    
    def select_gateway(self, requirements: Dict = None) -> Optional[str]:
        """选择最佳GPU网关"""
        if not self.gateway_pool:
            return None
        
        # 简单轮询选择 (可以改进为基于负载的选择)
        available_gateways = []
        
        for gateway_id in self.gateway_pool:
            gateway = self.gateways.get(gateway_id)
            if gateway and gateway["status"] == "online":
                # 检查是否在5分钟内有心跳
                if datetime.now() - gateway["last_seen"] < timedelta(minutes=5):
                    available_gateways.append(gateway_id)
        
        if available_gateways:
            # 选择负载最低的网关
            best_gateway = None
            min_load = float('inf')
            
            for gateway_id in available_gateways:
                gateway = self.gateways[gateway_id]
                nodes = gateway.get("nodes", [])
                
                if nodes:
                    # 计算平均负载
                    total_load = sum(node.get("current_load", 0) for node in nodes)
                    avg_load = total_load / len(nodes)
                    
                    if avg_load < min_load:
                        min_load = avg_load
                        best_gateway = gateway_id
                else:
                    # 没有节点信息，选择第一个
                    best_gateway = gateway_id
                    break
            
            return best_gateway or available_gateways[0]
        
        return None
    
    async def forward_request(self, gateway_id: str, endpoint: str, 
                            method: str = "POST", data: Dict = None) -> Dict:
        """转发请求到GPU网关"""
        if gateway_id not in self.gateways:
            raise HTTPException(status_code=404, detail="GPU gateway not found")
        
        gateway_url = self.gateways[gateway_id]["url"]
        url = f"{gateway_url}/{endpoint.lstrip('/')}"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                if method.upper() == "GET":
                    async with session.get(url) as response:
                        result = await response.json()
                else:
                    async with session.post(url, json=data) as response:
                        result = await response.json()
                
                return result
                
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Gateway request timeout")
        except Exception as e:
            logger.error(f"❌ Gateway request failed: {e}")
            raise HTTPException(status_code=502, detail=f"Gateway error: {str(e)}")
    
    async def update_gateway_status(self, gateway_id: str, status_data: Dict):
        """更新网关状态"""
        if gateway_id in self.gateways:
            gateway = self.gateways[gateway_id]
            gateway["last_seen"] = datetime.now()
            gateway["status"] = "online"
            gateway["nodes"] = status_data.get("nodes", [])
            gateway["metrics"] = status_data.get("metrics", {})


# 全局GPU网关客户端
gpu_gateway_client = GPUGatewayClient()


@router.post("/register")
async def register_gateway(request: Dict[str, Any]):
    """注册GPU网关"""
    try:
        gateway_id = request.get("gateway_id")
        gateway_url = request.get("gateway_url") 
        capabilities = request.get("capabilities", [])
        
        if not gateway_id or not gateway_url:
            raise HTTPException(status_code=400, detail="Missing gateway_id or gateway_url")
        
        await gpu_gateway_client.register_gateway(
            gateway_id=gateway_id,
            gateway_url=gateway_url,
            capabilities=capabilities
        )
        
        return {"success": True, "message": f"Gateway {gateway_id} registered"}
        
    except Exception as e:
        logger.error(f"❌ Gateway registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unregister")
async def unregister_gateway(request: Dict[str, Any]):
    """注销GPU网关"""
    try:
        gateway_id = request.get("gateway_id")
        
        if not gateway_id:
            raise HTTPException(status_code=400, detail="Missing gateway_id")
        
        await gpu_gateway_client.unregister_gateway(gateway_id)
        
        return {"success": True, "message": f"Gateway {gateway_id} unregistered"}
        
    except Exception as e:
        logger.error(f"❌ Gateway unregistration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/status")
async def receive_gateway_status(request: Dict[str, Any]):
    """接收网关状态报告"""
    try:
        gateway_id = request.get("gateway_id")
        
        if not gateway_id:
            raise HTTPException(status_code=400, detail="Missing gateway_id")
        
        await gpu_gateway_client.update_gateway_status(gateway_id, request)
        
        return {"success": True, "received": True}
        
    except Exception as e:
        logger.error(f"❌ Status update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gateways")
async def list_gateways():
    """列出所有GPU网关"""
    gateways = []
    
    for gateway_id, gateway_info in gpu_gateway_client.gateways.items():
        gateways.append({
            "gateway_id": gateway_id,
            "url": gateway_info["url"],
            "status": gateway_info["status"],
            "last_seen": gateway_info["last_seen"].isoformat(),
            "nodes": len(gateway_info.get("nodes", [])),
            "capabilities": gateway_info.get("capabilities", [])
        })
    
    return {
        "success": True,
        "gateways": gateways,
        "total": len(gateways)
    }


@router.post("/deploy")
async def deploy_model_to_gateway(
    request: Dict[str, Any], 
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """通过网关部署模型"""
    try:
        model_id = request.get("model_id")
        backend = request.get("backend", "transformers")
        preferred_gateway = request.get("preferred_gateway")
        
        if not model_id:
            raise HTTPException(status_code=400, detail="Missing model_id")
        
        # 选择网关
        gateway_id = preferred_gateway or gpu_gateway_client.select_gateway()
        if not gateway_id:
            raise HTTPException(status_code=503, detail="No available GPU gateways")
        
        # 构建部署请求
        deploy_data = {
            "tenant_id": current_tenant.id,
            "model_id": model_id,
            "service_name": f"{current_tenant.id}-{model_id.replace('/', '-')}",
            "service_type": "llm",
            "backend": backend,
            **request  # 包含其他配置参数
        }
        
        # 转发到网关
        result = await gpu_gateway_client.forward_request(
            gateway_id=gateway_id,
            endpoint="/deploy",
            method="POST",
            data=deploy_data
        )
        
        # 记录部署信息到数据库
        # TODO: 保存部署记录
        
        return {
            "success": result.get("success", False),
            "gateway_id": gateway_id,
            "service_name": result.get("service_name"),
            "error": result.get("error"),
            "service_info": result.get("service_info")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Model deployment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inference")
async def inference_through_gateway(
    request: Dict[str, Any],
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """通过网关进行推理"""
    try:
        model_id = request.get("model_id")
        if not model_id:
            raise HTTPException(status_code=400, detail="Missing model_id")
        
        # 选择网关 (可以基于模型ID或其他策略)
        gateway_id = gpu_gateway_client.select_gateway()
        if not gateway_id:
            raise HTTPException(status_code=503, detail="No available GPU gateways")
        
        # 构建推理请求
        inference_data = {
            "tenant_id": current_tenant.id,
            "model_id": model_id,
            "request": {
                key: value for key, value in request.items() 
                if key not in ["model_id"]
            }
        }
        
        # 转发到网关
        result = await gpu_gateway_client.forward_request(
            gateway_id=gateway_id,
            endpoint="/inference", 
            method="POST",
            data=inference_data
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Inference request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_gpu_metrics():
    """获取所有网关的指标"""
    all_metrics = {}
    
    for gateway_id, gateway_info in gpu_gateway_client.gateways.items():
        if gateway_info["status"] == "online":
            try:
                metrics = await gpu_gateway_client.forward_request(
                    gateway_id=gateway_id,
                    endpoint="/metrics",
                    method="GET"
                )
                all_metrics[gateway_id] = metrics
            except Exception as e:
                logger.error(f"❌ Failed to get metrics from {gateway_id}: {e}")
                all_metrics[gateway_id] = {"error": str(e)}
    
    return {
        "success": True,
        "metrics": all_metrics
    }


@router.post("/tenants/register")
async def register_tenant_on_gateways(
    request: Dict[str, Any],
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """在所有网关上注册租户"""
    try:
        tenant_config = {
            "tenant_id": current_tenant.id,
            "gpu_quota": request.get("gpu_quota", 1),
            "memory_quota": request.get("memory_quota", 8192),
            "priority": request.get("priority", 1),
            "allowed_models": request.get("allowed_models", []),
            "rate_limit": request.get("rate_limit", 100)
        }
        
        results = {}
        
        # 在所有在线网关上注册租户
        for gateway_id, gateway_info in gpu_gateway_client.gateways.items():
            if gateway_info["status"] == "online":
                try:
                    result = await gpu_gateway_client.forward_request(
                        gateway_id=gateway_id,
                        endpoint="/tenants",
                        method="POST",
                        data=tenant_config
                    )
                    results[gateway_id] = result
                except Exception as e:
                    logger.error(f"❌ Failed to register tenant on {gateway_id}: {e}")
                    results[gateway_id] = {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "tenant_id": current_tenant.id,
            "gateway_results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Tenant registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 背景任务：监控网关健康状态
async def monitor_gateways():
    """监控网关健康状态"""
    while True:
        try:
            current_time = datetime.now()
            
            for gateway_id in list(gpu_gateway_client.gateways.keys()):
                gateway = gpu_gateway_client.gateways[gateway_id]
                
                # 检查网关是否超时
                if current_time - gateway["last_seen"] > timedelta(minutes=5):
                    logger.warning(f"⚠️ Gateway {gateway_id} is offline")
                    gateway["status"] = "offline"
                    
                    if gateway_id in gpu_gateway_client.gateway_pool:
                        gpu_gateway_client.gateway_pool.remove(gateway_id)
                
                # 尝试ping网关
                try:
                    status = await gpu_gateway_client.forward_request(
                        gateway_id=gateway_id,
                        endpoint="/status",
                        method="GET"
                    )
                    
                    if status:
                        gateway["status"] = "online"
                        gateway["last_seen"] = current_time
                        
                        if gateway_id not in gpu_gateway_client.gateway_pool:
                            gpu_gateway_client.gateway_pool.append(gateway_id)
                
                except Exception as e:
                    logger.debug(f"Gateway {gateway_id} ping failed: {e}")
                    gateway["status"] = "offline"
            
            await asyncio.sleep(30)  # 每30秒检查一次
            
        except Exception as e:
            logger.error(f"❌ Gateway monitoring error: {e}")
            await asyncio.sleep(10)


# 启动监控任务
@router.on_event("startup")
async def startup_event():
    """启动背景监控任务"""
    asyncio.create_task(monitor_gateways())


# 导出客户端供其他模块使用
__all__ = ["router", "gpu_gateway_client", "GPUGatewayClient"]