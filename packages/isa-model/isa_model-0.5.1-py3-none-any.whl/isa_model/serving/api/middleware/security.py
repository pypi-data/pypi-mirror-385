"""
Security middleware for production deployment

Provides comprehensive security features including:
- Rate limiting with Redis backend
- Security headers
- Request size limits
- Input validation and sanitization
- CORS protection
"""

import time
import logging
import os
import redis
from typing import Dict, Any, Optional, Callable
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import html

from ....core.config.config_manager import ConfigManager

# Configure logging
logger = logging.getLogger(__name__)

# Configuration from environment variables
config_manager = ConfigManager()
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE_MB", "50")) * 1024 * 1024  # 50MB default
# Use Consul discovery for Redis URL with fallback
REDIS_URL = os.getenv("REDIS_URL", config_manager.get_redis_url())
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
RATE_LIMIT_PER_MINUTE = os.getenv("RATE_LIMIT_PER_MINUTE", "100")
RATE_LIMIT_PER_HOUR = os.getenv("RATE_LIMIT_PER_HOUR", "1000")

# Security headers configuration
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; font-src 'self' https://fonts.gstatic.com; img-src 'self' https://fastapi.tiangolo.com data:; connect-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}

# Initialize Redis connection for rate limiting
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()  # Test connection
    logger.info("Redis connection established for rate limiting")
except Exception as e:
    logger.warning(f"Redis connection failed, using in-memory rate limiting: {e}")
    redis_client = None

# Initialize rate limiter
def get_remote_address_with_proxy(request: Request):
    """Get client IP considering proxy headers"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return get_remote_address(request)

# Rate limiter with Redis backend if available
if redis_client:
    limiter = Limiter(
        key_func=get_remote_address_with_proxy,
        storage_uri=REDIS_URL,
        strategy="fixed-window"
    )
else:
    limiter = Limiter(
        key_func=get_remote_address_with_proxy,
        strategy="fixed-window"
    )

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            
            # Add security headers
            for header, value in SECURITY_HEADERS.items():
                response.headers[header] = value
            
            # Add processing time header
            if hasattr(request.state, 'start_time'):
                process_time = time.time() - request.state.start_time
                response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in security headers middleware: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"},
                headers=SECURITY_HEADERS
            )

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate request size and sanitize inputs"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Record start time for performance monitoring
        request.state.start_time = time.time()
        
        try:
            # Check request size
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > MAX_REQUEST_SIZE:
                logger.warning(
                    f"Request too large: {content_length} bytes > {MAX_REQUEST_SIZE} bytes "
                    f"from client {get_remote_address_with_proxy(request)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request too large. Maximum size: {MAX_REQUEST_SIZE // (1024*1024)}MB"
                )
            
            # Sanitize query parameters
            if request.url.query:
                sanitized_query = html.escape(request.url.query)
                if sanitized_query != request.url.query:
                    logger.warning(
                        f"Potentially malicious query parameters detected from client {get_remote_address_with_proxy(request)}: "
                        f"'{request.url.query}' -> '{sanitized_query}'"
                    )
            
            # Log request details for monitoring
            logger.info(
                f"Request received: {request.method} {request.url.path} "
                f"from {get_remote_address_with_proxy(request)} "
                f"(UA: {request.headers.get('user-agent', 'unknown')})"
            )
            
            response = await call_next(request)
            
            # Log response details
            process_time = time.time() - request.state.start_time
            logger.info(
                f"Request completed: {request.method} {request.url.path} -> {response.status_code} "
                f"in {process_time:.3f}s from {get_remote_address_with_proxy(request)}"
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error in request validation middleware: {e} "
                f"({request.method} {request.url.path} from {get_remote_address_with_proxy(request)})"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

def setup_security_middleware(app: FastAPI):
    """Setup all security middleware for the FastAPI application"""
    
    # Rate limiting setup
    if ENABLE_RATE_LIMITING:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        logger.info(f"Rate limiting enabled (Redis backend: {redis_client is not None})")
    
    # Trusted hosts (production should specify allowed hosts)
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")
    if allowed_hosts != ["*"]:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
        logger.info(f"Trusted hosts middleware enabled: {allowed_hosts}")
    
    # CORS configuration
    cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"]
    )
    logger.info(f"CORS middleware enabled for origins: {cors_origins}")
    
    # Custom security middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestValidationMiddleware)
    
    logger.info("Security middleware setup completed")

def get_rate_limiter():
    """Get the configured rate limiter"""
    return limiter

# Rate limiting decorators for different use cases
def rate_limit_standard():
    """Standard rate limit for general API usage"""
    return limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")

def rate_limit_heavy():
    """Heavy rate limit for resource-intensive operations"""
    heavy_limit = int(RATE_LIMIT_PER_MINUTE) // 5  # 20% of standard limit
    return limiter.limit(f"{heavy_limit}/minute")

def rate_limit_auth():
    """Strict rate limit for authentication endpoints"""
    return limiter.limit("10/minute")

# Security utilities
def sanitize_input(text: str) -> str:
    """Sanitize text input to prevent XSS attacks"""
    if not isinstance(text, str):
        return text
    return html.escape(text)

def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format"""
    if not isinstance(api_key, str):
        return False
    
    # Check if it starts with expected prefix
    if not api_key.startswith("isa_"):
        return False
    
    # Check minimum length (should be > 20 characters)
    if len(api_key) < 25:
        return False
    
    return True

def get_client_info(request: Request) -> Dict[str, Any]:
    """Extract client information for logging and monitoring"""
    return {
        "ip": get_remote_address_with_proxy(request),
        "user_agent": request.headers.get("user-agent", "unknown"),
        "referer": request.headers.get("referer"),
        "forwarded_for": request.headers.get("x-forwarded-for"),
        "real_ip": request.headers.get("x-real-ip"),
        "method": request.method,
        "path": request.url.path,
        "query": request.url.query
    }

# Health check for Redis connection
async def check_redis_health() -> Dict[str, Any]:
    """Check Redis connection health"""
    if not redis_client:
        return {"redis": "disabled", "status": "ok"}
    
    try:
        redis_client.ping()
        return {"redis": "connected", "status": "ok"}
    except Exception as e:
        return {"redis": "error", "status": "error", "error": str(e)}