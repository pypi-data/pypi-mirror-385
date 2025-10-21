"""
Tenant Context Middleware

Handles tenant isolation by:
1. Extracting tenant info from requests (API keys, JWT tokens, headers)
2. Setting tenant context for all database operations
3. Enforcing resource quotas and access control
4. Logging tenant-specific activities
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional, Dict, Any
import logging
import json
import asyncio
import time

logger = logging.getLogger(__name__)

# Context variables for tenant isolation
_tenant_context: ContextVar[Optional['TenantContext']] = ContextVar('tenant_context', default=None)

class TenantContext:
    """Container for tenant-specific context information"""
    
    def __init__(
        self,
        organization_id: str,
        user_id: Optional[str] = None,
        role: Optional[str] = None,
        plan: str = "starter",
        quotas: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None
    ):
        self.organization_id = organization_id
        self.user_id = user_id
        self.role = role
        self.plan = plan
        self.quotas = quotas or {}
        self.settings = settings or {}
        self.request_start_time = time.time()
        
    def __str__(self):
        return f"TenantContext(org={self.organization_id}, user={self.user_id}, role={self.role})"
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.role in ["admin", "owner"]
    
    def can_access_resource(self, resource_type: str, action: str = "read") -> bool:
        """Check if tenant can access a specific resource type"""
        # TODO: Implement fine-grained permissions
        return True
    
    def check_quota(self, resource: str, current_usage: int = 0) -> bool:
        """Check if tenant is within quota limits"""
        if resource not in self.quotas:
            return True
            
        quota_limit = self.quotas[resource]
        return current_usage < quota_limit
    
    def get_database_filter(self) -> Dict[str, Any]:
        """Get database filter parameters for tenant isolation"""
        return {"organization_id": self.organization_id}

def get_tenant_context() -> Optional[TenantContext]:
    """Get current tenant context"""
    return _tenant_context.get()

def require_tenant_context() -> TenantContext:
    """Get tenant context or raise error if not available"""
    context = get_tenant_context()
    if not context:
        raise HTTPException(
            status_code=401,
            detail="Tenant context required - invalid or missing authentication"
        )
    return context

@contextmanager
def set_tenant_context(context: TenantContext):
    """Context manager to set tenant context"""
    token = _tenant_context.set(context)
    try:
        yield context
    finally:
        _tenant_context.reset(token)

class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and set tenant context for requests"""
    
    def __init__(self, app, database_pool=None):
        super().__init__(app)
        self.database_pool = database_pool
        # Initialize database pool if not provided
        if not self.database_pool:
            try:
                import asyncio
                from ..dependencies.database import initialize_database_pool
                # Will be initialized in first request
                self.database_pool = None
            except ImportError:
                pass
        
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and set tenant context"""
        start_time = time.time()
        
        try:
            # Extract tenant information from request
            tenant_context = await self.extract_tenant_context(request)
            
            # Set context for this request
            if tenant_context:
                token = _tenant_context.set(tenant_context)
                try:
                    # Check quotas before processing request
                    await self.enforce_quotas(tenant_context, request)
                    
                    # Process the request
                    response = await call_next(request)
                    
                    # Log successful request
                    await self.log_tenant_activity(tenant_context, request, response, start_time)
                    
                    return response
                finally:
                    _tenant_context.reset(token)
            else:
                # No tenant context - allow for public endpoints
                return await call_next(request)
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in tenant context middleware: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def extract_tenant_context(self, request: Request) -> Optional[TenantContext]:
        """Extract tenant information from request"""
        try:
            # Skip tenant context for certain paths
            if self.should_skip_tenant_context(request.url.path):
                return None
            
            # Method 1: Extract from Authorization header (API key or JWT)
            auth_header = request.headers.get("Authorization")
            if auth_header:
                tenant_context = await self.extract_from_auth_header(auth_header)
                if tenant_context:
                    return tenant_context
            
            # Method 2: Extract from X-Organization-ID header (for service-to-service calls)
            org_header = request.headers.get("X-Organization-ID")
            if org_header:
                return await self.extract_from_org_header(org_header)
            
            # Method 3: Extract from query parameters (for some public APIs)
            org_param = request.query_params.get("organization_id")
            if org_param:
                return await self.extract_from_org_param(org_param)
                
            return None
            
        except Exception as e:
            logger.error(f"Error extracting tenant context: {e}")
            return None
    
    def should_skip_tenant_context(self, path: str) -> bool:
        """Check if path should skip tenant context extraction"""
        skip_paths = [
            "/health",
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/api/v1/tenants",  # Tenant management endpoints handle their own context
            "/static"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    async def extract_from_auth_header(self, auth_header: str) -> Optional[TenantContext]:
        """Extract tenant context from Authorization header"""
        try:
            if not auth_header.startswith("Bearer "):
                return None
                
            token = auth_header[7:]  # Remove "Bearer "
            
            # If it looks like an API key
            if token.startswith("isa_"):
                return await self.lookup_api_key(token)
            
            # If it looks like a JWT token
            if "." in token:
                return await self.decode_jwt_token(token)
                
            return None
            
        except Exception as e:
            logger.error(f"Error extracting from auth header: {e}")
            return None
    
    async def extract_from_org_header(self, org_id: str) -> Optional[TenantContext]:
        """Extract tenant context from organization header"""
        try:
            # For service-to-service calls, just create basic context
            return await self.lookup_organization(org_id)
            
        except Exception as e:
            logger.error(f"Error extracting from org header: {e}")
            return None
    
    async def extract_from_org_param(self, org_id: str) -> Optional[TenantContext]:
        """Extract tenant context from query parameter"""
        # Similar to org header but maybe more restricted
        return await self.lookup_organization(org_id)
    
    async def lookup_api_key(self, api_key: str) -> Optional[TenantContext]:
        """Look up tenant context from API key"""
        try:
            # For now, create a simple tenant context based on API key
            # In a real implementation, this would lookup the organization
            # associated with the API key from the database
            
            # Create a default organization for testing
            if api_key.startswith("isa_"):
                return TenantContext(
                    organization_id="org_default_test_123",
                    user_id="user_admin",
                    role="admin",
                    plan="pro",
                    quotas={
                        "api_calls_per_month": 100000,
                        "max_training_jobs": 10,
                        "max_deployments": 5
                    },
                    settings={}
                )
                    
            return None
            
        except Exception as e:
            logger.error(f"Error looking up API key: {e}")
            return None
    
    async def decode_jwt_token(self, token: str) -> Optional[TenantContext]:
        """Decode JWT token and extract tenant context"""
        try:
            # TODO: Implement JWT token decoding
            # This would involve verifying the token signature and extracting claims
            logger.info("JWT token decoding not yet implemented")
            return None
            
        except Exception as e:
            logger.error(f"Error decoding JWT token: {e}")
            return None
    
    async def lookup_organization(self, org_id: str) -> Optional[TenantContext]:
        """Look up organization details"""
        try:
            if not self.database_pool:
                return None
                
            async with self.database_pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT o.organization_id, o.plan, o.settings, oq.quotas
                    FROM organizations o
                    LEFT JOIN organization_quotas oq ON o.organization_id = oq.organization_id
                    WHERE o.organization_id = $1 AND o.status = 'active'
                """, org_id)
                
                if result:
                    return TenantContext(
                        organization_id=result['organization_id'],
                        plan=result['plan'],
                        quotas=result['quotas'] or {},
                        settings=result['settings'] or {}
                    )
                    
            return None
            
        except Exception as e:
            logger.error(f"Error looking up organization {org_id}: {e}")
            return None
    
    async def enforce_quotas(self, context: TenantContext, request: Request):
        """Enforce tenant quotas before processing request"""
        try:
            # Check concurrent request quota
            # TODO: Implement concurrent request tracking
            
            # Check API rate limits
            if not context.check_quota("requests_per_minute", 0):  # TODO: Get actual usage
                raise HTTPException(
                    status_code=429,
                    detail="Request rate limit exceeded for your organization"
                )
                
            # Check plan-specific restrictions
            if context.plan == "starter" and request.method in ["POST", "PUT", "DELETE"]:
                # Maybe starter plans have restricted write access to some endpoints
                pass
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error enforcing quotas: {e}")
            # Don't block request on quota enforcement errors
    
    async def log_tenant_activity(
        self, 
        context: TenantContext, 
        request: Request, 
        response: Response, 
        start_time: float
    ):
        """Log tenant-specific activity for billing and monitoring"""
        try:
            duration = time.time() - start_time
            
            activity_log = {
                "timestamp": time.time(),
                "organization_id": context.organization_id,
                "user_id": context.user_id,
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": duration * 1000,
                "plan": context.plan
            }
            
            # Log to structured logger for processing
            logger.info(f"TENANT_ACTIVITY: {json.dumps(activity_log)}")
            
            # TODO: Store in database for billing/analytics
            # await self.store_activity_log(activity_log)
            
        except Exception as e:
            logger.error(f"Error logging tenant activity: {e}")

# Dependency functions for FastAPI

def get_current_tenant() -> TenantContext:
    """FastAPI dependency to get current tenant context"""
    return require_tenant_context()

def get_current_organization_id() -> str:
    """FastAPI dependency to get current organization ID"""
    context = require_tenant_context()
    return context.organization_id

def require_admin_role() -> TenantContext:
    """FastAPI dependency to require admin role"""
    context = require_tenant_context()
    if not context.is_admin():
        raise HTTPException(
            status_code=403,
            detail="Admin role required for this operation"
        )
    return context

def check_resource_quota(resource_type: str):
    """FastAPI dependency factory to check specific resource quotas"""
    def _check_quota():
        context = require_tenant_context()
        # TODO: Get current usage and check against quota
        if not context.check_quota(resource_type):
            raise HTTPException(
                status_code=429,
                detail=f"Quota exceeded for {resource_type}"
            )
        return context
    return _check_quota

# Database query helpers that respect tenant context

def add_tenant_filter(base_query: str, params: list, table_alias: str = "") -> tuple[str, list]:
    """Add tenant filter to database queries"""
    context = get_tenant_context()
    if not context:
        return base_query, params
    
    # Add organization_id filter
    table_prefix = f"{table_alias}." if table_alias else ""
    
    if "WHERE" in base_query.upper():
        filtered_query = f"{base_query} AND {table_prefix}organization_id = ${len(params) + 1}"
    else:
        filtered_query = f"{base_query} WHERE {table_prefix}organization_id = ${len(params) + 1}"
    
    params.append(context.organization_id)
    
    return filtered_query, params

async def tenant_safe_query(conn, query: str, *params, table_alias: str = ""):
    """Execute query with automatic tenant filtering"""
    filtered_query, filtered_params = add_tenant_filter(query, list(params), table_alias)
    return await conn.fetch(filtered_query, *filtered_params)

async def tenant_safe_fetchrow(conn, query: str, *params, table_alias: str = ""):
    """Execute fetchrow with automatic tenant filtering"""
    filtered_query, filtered_params = add_tenant_filter(query, list(params), table_alias)
    return await conn.fetchrow(filtered_query, *filtered_params)

async def tenant_safe_execute(conn, query: str, *params, table_alias: str = ""):
    """Execute query with automatic tenant filtering"""
    filtered_query, filtered_params = add_tenant_filter(query, list(params), table_alias)
    return await conn.execute(filtered_query, *filtered_params)