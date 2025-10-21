"""
Authentication and Authorization Dependencies

FastAPI dependencies for handling authentication, authorization,
and tenant access control. Integrates with existing auth middleware.
"""

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging

from ..middleware.tenant_context import get_tenant_context, require_tenant_context, TenantContext
from ..middleware.auth import authenticate_api_key, require_admin_access as require_api_admin

logger = logging.getLogger(__name__)

class User:
    """User model for authentication"""
    def __init__(self, user_id: str, email: str, role: str = "member", organization_id: str = None):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.organization_id = organization_id
    
    def is_admin(self) -> bool:
        return self.role in ["admin", "owner"]
    
    def is_system_admin(self) -> bool:
        return self.role == "system_admin"

class Organization:
    """Organization model"""
    def __init__(self, organization_id: str, name: str, plan: str = "starter", status: str = "active"):
        self.organization_id = organization_id
        self.name = name
        self.plan = plan
        self.status = status

async def get_current_user(
    auth_data: Dict = Depends(authenticate_api_key)
) -> Optional[User]:
    """
    Get current authenticated user from existing auth system.
    Integrates with the existing API key authentication.
    """
    try:
        if not auth_data.get("authenticated", True):  # Anonymous when auth disabled
            return None
            
        # Get tenant context which should contain user info
        tenant_context = get_tenant_context()
        
        # Create user from auth data and tenant context
        user_id = tenant_context.user_id if tenant_context else auth_data.get("name", "anonymous")
        organization_id = tenant_context.organization_id if tenant_context else None
        
        # Map API key scopes to user roles
        scopes = auth_data.get("scopes", [])
        if "admin" in scopes:
            role = "admin"
        elif "write" in scopes:
            role = "member"
        else:
            role = "viewer"
            
        return User(
            user_id=user_id,
            email=f"{user_id}@example.com",  # TODO: Get from database
            role=role,
            organization_id=organization_id
        )
        
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return None

async def require_authenticated_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Require authenticated user or raise 401 error.
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    return current_user

async def get_current_organization() -> Optional[Organization]:
    """
    Get current organization from tenant context.
    """
    try:
        tenant_context = get_tenant_context()
        if tenant_context:
            return Organization(
                organization_id=tenant_context.organization_id,
                name="Organization",  # TODO: Get from database
                plan=tenant_context.plan,
                status="active"
            )
        return None
        
    except Exception as e:
        logger.error(f"Error getting current organization: {e}")
        return None

async def require_organization_access() -> Organization:
    """
    Require organization context or raise 401 error.
    """
    org = await get_current_organization()
    if not org:
        raise HTTPException(
            status_code=401,
            detail="Organization access required"
        )
    return org

async def require_admin(
    auth_data: Dict = Depends(require_api_admin),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin role within organization.
    Uses existing API key admin check plus tenant context.
    """
    if not current_user or not current_user.is_admin():
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    return current_user

async def require_system_admin(
    auth_data: Dict = Depends(require_api_admin)
) -> Dict:
    """
    Require system admin role (for tenant management).
    For now, maps to API key admin access.
    """
    # For system admin, require API key admin access
    return auth_data

def require_plan(min_plan: str):
    """
    Factory function to create dependency that requires specific plan level.
    Usage: Depends(require_plan("pro"))
    """
    async def _check_plan():
        tenant_context = get_tenant_context()
        if not tenant_context:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
        
        plan_hierarchy = {
            "starter": 1,
            "pro": 2,
            "enterprise": 3
        }
        
        current_plan_level = plan_hierarchy.get(tenant_context.plan, 0)
        required_plan_level = plan_hierarchy.get(min_plan, 99)
        
        if current_plan_level < required_plan_level:
            raise HTTPException(
                status_code=403,
                detail=f"Plan upgrade required. Current: {tenant_context.plan}, Required: {min_plan}"
            )
        
        return tenant_context
    
    return _check_plan

def check_resource_access(resource_type: str, action: str = "read"):
    """
    Factory function to create dependency that checks resource access permissions.
    """
    async def _check_access():
        tenant_context = require_tenant_context()
        
        if not tenant_context.can_access_resource(resource_type, action):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied to {resource_type}"
            )
        
        return tenant_context
    
    return _check_access