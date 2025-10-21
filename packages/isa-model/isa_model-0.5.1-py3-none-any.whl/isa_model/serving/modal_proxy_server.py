#!/usr/bin/env python3
"""
Modal Services Proxy Server (Port 8082)

This server acts as a proxy to Modal services, providing a unified interface
for all Modal-deployed AI services like vision, audio, embedding, etc.
"""

import os
import logging
import uvicorn
import httpx
import asyncio
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="isA Model Modal Proxy",
    description="Proxy server for Modal-deployed AI services",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Configuration
MODAL_SERVICES = {
    "vision": os.getenv("MODAL_VISION_URL", ""),
    "audio": os.getenv("MODAL_AUDIO_URL", ""),
    "embedding": os.getenv("MODAL_EMBED_URL", ""),
    "image_gen": os.getenv("MODAL_IMAGE_GEN_URL", "")
}

API_KEY = os.getenv("API_KEY", "")
REQUEST_TIMEOUT = int(os.getenv("MODAL_TIMEOUT", "120"))


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key if configured"""
    if API_KEY and credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return credentials.credentials


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Test connectivity to Modal services
    service_status = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, service_url in MODAL_SERVICES.items():
            if service_url:
                try:
                    response = await client.get(f"{service_url}/health", timeout=5.0)
                    service_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
                except Exception:
                    service_status[service_name] = "unreachable"
            else:
                service_status[service_name] = "not_configured"
    
    return {
        "status": "healthy",
        "service": "modal-proxy",
        "port": 8082,
        "modal_services": service_status
    }


@app.get("/services")
async def list_services():
    """List available Modal services"""
    return {
        "available_services": list(MODAL_SERVICES.keys()),
        "service_urls": {k: v for k, v in MODAL_SERVICES.items() if v},
        "total_services": len([v for v in MODAL_SERVICES.values() if v])
    }


@app.post("/modal/{service_name}/{endpoint:path}")
async def proxy_modal_service(
    service_name: str,
    endpoint: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """Proxy requests to specific Modal service"""
    
    # Validate service name
    if service_name not in MODAL_SERVICES:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found. Available: {list(MODAL_SERVICES.keys())}"
        )
    
    service_url = MODAL_SERVICES[service_name]
    if not service_url:
        raise HTTPException(
            status_code=503,
            detail=f"Service '{service_name}' not configured"
        )
    
    try:
        # Get request body
        body = await request.body()
        
        # Prepare headers (exclude host and content-length)
        headers = {}
        for key, value in request.headers.items():
            if key.lower() not in ['host', 'content-length']:
                headers[key] = value
        
        # Make request to Modal service
        target_url = f"{service_url}/{endpoint}"
        
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=dict(request.query_params)
            )
            
            # Return response
            return response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            
    except httpx.TimeoutException:
        logger.error(f"Timeout calling Modal service {service_name} at {endpoint}")
        raise HTTPException(
            status_code=504,
            detail=f"Modal service '{service_name}' timeout"
        )
    except httpx.RequestError as e:
        logger.error(f"Request error calling Modal service {service_name}: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Modal service '{service_name}' unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error calling Modal service {service_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@app.get("/modal/{service_name}/{endpoint:path}")
async def proxy_modal_service_get(
    service_name: str,
    endpoint: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """Proxy GET requests to Modal services"""
    return await proxy_modal_service(service_name, endpoint, request, api_key)


# Convenience endpoints for common services
@app.post("/vision/{endpoint:path}")
async def vision_service(
    endpoint: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """Direct access to vision service"""
    return await proxy_modal_service("vision", endpoint, request, api_key)


@app.post("/audio/{endpoint:path}")
async def audio_service(
    endpoint: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """Direct access to audio service"""
    return await proxy_modal_service("audio", endpoint, request, api_key)


@app.post("/embedding/{endpoint:path}")
async def embedding_service(
    endpoint: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """Direct access to embedding service"""
    return await proxy_modal_service("embedding", endpoint, request, api_key)


@app.post("/image-gen/{endpoint:path}")
async def image_gen_service(
    endpoint: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """Direct access to image generation service"""
    return await proxy_modal_service("image_gen", endpoint, request, api_key)


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return {
        "error": "Not Found",
        "detail": "The requested endpoint was not found",
        "available_endpoints": [
            "/health",
            "/services",
            "/modal/{service_name}/{endpoint}",
            "/vision/{endpoint}",
            "/audio/{endpoint}",
            "/embedding/{endpoint}",
            "/image-gen/{endpoint}"
        ]
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8082"))
    workers = int(os.getenv("WORKERS", "1"))
    
    logger.info(f"Starting Modal Proxy Server on port {port}")
    logger.info(f"Configured Modal services: {list(MODAL_SERVICES.keys())}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        workers=workers,
        log_level="info"
    )