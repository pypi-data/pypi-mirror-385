"""
Tenant Management API

Handles multi-tenancy operations including:
- Organization/tenant management
- Resource quotas and limits
- Tenant isolation
- Billing and usage tracking per tenant
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
import json

from ..dependencies.auth import get_current_user, get_current_organization, require_admin
from ..dependencies.database import get_database_connection
from ..middleware.tenant_context import get_tenant_context, TenantContext

logger = logging.getLogger(__name__)
router = APIRouter()

# ============= Pydantic Models =============

class TenantCreateRequest(BaseModel):
    """Request model for creating a new tenant/organization"""
    name: str = Field(..., min_length=1, max_length=100, description="Organization name")
    domain: Optional[str] = Field(None, description="Organization domain (optional)")
    plan: str = Field("starter", description="Subscription plan: starter, pro, enterprise")
    billing_email: str = Field(..., description="Billing contact email")
    admin_user_email: str = Field(..., description="Initial admin user email")
    admin_user_name: str = Field(..., description="Initial admin user name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Acme Corporation",
                "domain": "acme.com",
                "plan": "pro",
                "billing_email": "billing@acme.com",
                "admin_user_email": "admin@acme.com",
                "admin_user_name": "John Admin"
            }
        }

class TenantUpdateRequest(BaseModel):
    """Request model for updating tenant settings"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    plan: Optional[str] = Field(None, description="starter, pro, enterprise")
    billing_email: Optional[str] = Field(None)
    status: Optional[str] = Field(None, description="active, suspended, inactive")
    settings: Optional[Dict[str, Any]] = Field(None, description="Tenant-specific settings")
    
class TenantQuotaRequest(BaseModel):
    """Request model for setting tenant resource quotas"""
    api_calls_per_month: Optional[int] = Field(None, ge=0)
    max_concurrent_requests: Optional[int] = Field(None, ge=1)
    max_storage_gb: Optional[float] = Field(None, ge=0)
    max_training_jobs: Optional[int] = Field(None, ge=0)
    max_deployments: Optional[int] = Field(None, ge=0)
    max_users: Optional[int] = Field(None, ge=1)
    
class TenantResponse(BaseModel):
    """Response model for tenant information"""
    organization_id: str
    name: str
    domain: Optional[str]
    plan: str
    status: str
    billing_email: str
    created_at: datetime
    updated_at: datetime
    member_count: int
    current_usage: Dict[str, Any]
    quotas: Dict[str, Any]
    settings: Dict[str, Any]

# ============= Tenant Management =============

@router.post("/", response_model=TenantResponse)
async def create_tenant(
    request: TenantCreateRequest,
    current_user = Depends(require_admin)
):
    """
    Create a new tenant/organization.
    Requires system admin privileges.
    """
    try:
        async with get_database_connection() as conn:
            # Generate unique organization ID
            org_id = f"org_{uuid.uuid4().hex[:12]}"
            
            # Create organization
            org_query = """
                INSERT INTO organizations (
                    organization_id, name, domain, plan, billing_email, 
                    status, settings, credits_pool, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING *
            """
            
            default_settings = {
                "api_rate_limit": 1000,
                "max_file_upload_mb": 100,
                "enable_webhooks": True,
                "data_retention_days": 90
            }
            
            now = datetime.utcnow()
            org_result = await conn.fetchrow(
                org_query, org_id, request.name, request.domain,
                request.plan, request.billing_email, "active",
                json.dumps(default_settings), 1000.0, now, now
            )
            
            # Create default quotas based on plan
            quotas = get_default_quotas(request.plan)
            quota_query = """
                INSERT INTO organization_quotas (
                    organization_id, quotas, created_at, updated_at
                ) VALUES ($1, $2, $3, $4)
            """
            await conn.execute(quota_query, org_id, json.dumps(quotas), now, now)
            
            # Create admin user if doesn't exist
            user_query = """
                INSERT INTO users (user_id, email, name, role, organization_id, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (email) DO UPDATE SET 
                    organization_id = $5, updated_at = $7
                RETURNING user_id
            """
            
            admin_user_id = f"user_{uuid.uuid4().hex[:12]}"
            await conn.execute(
                user_query, admin_user_id, request.admin_user_email,
                request.admin_user_name, "admin", org_id, now, now
            )
            
            # Get full tenant info for response
            tenant_info = await get_tenant_info(org_id, conn)
            
            logger.info(f"Created tenant {org_id} ({request.name}) with admin {request.admin_user_email}")
            return tenant_info
            
    except Exception as e:
        logger.error(f"Error creating tenant: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create tenant: {str(e)}")

@router.get("/{organization_id}", response_model=TenantResponse)
async def get_tenant(
    organization_id: str,
    current_org = Depends(get_current_organization)
):
    """Get tenant information"""
    try:
        # Ensure user can only access their own tenant (unless system admin)
        if current_org.organization_id != organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        async with get_database_connection() as conn:
            tenant_info = await get_tenant_info(organization_id, conn)
            if not tenant_info:
                raise HTTPException(status_code=404, detail="Tenant not found")
            return tenant_info
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tenant {organization_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tenant information")

@router.put("/{organization_id}", response_model=TenantResponse)
async def update_tenant(
    organization_id: str,
    request: TenantUpdateRequest,
    current_org = Depends(get_current_organization)
):
    """Update tenant settings"""
    try:
        # Check access permissions
        if current_org.organization_id != organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        async with get_database_connection() as conn:
            # Build update query dynamically
            update_fields = []
            values = []
            param_count = 1
            
            for field, value in request.dict(exclude_unset=True).items():
                if field == "settings":
                    update_fields.append(f"settings = ${param_count}")
                    values.append(json.dumps(value))
                else:
                    update_fields.append(f"{field} = ${param_count}")
                    values.append(value)
                param_count += 1
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")
                
            update_fields.append(f"updated_at = ${param_count}")
            values.append(datetime.utcnow())
            values.append(organization_id)  # WHERE clause
            
            query = f"""
                UPDATE organizations 
                SET {', '.join(update_fields)}
                WHERE organization_id = ${param_count + 1}
                RETURNING *
            """
            
            result = await conn.fetchrow(query, *values)
            if not result:
                raise HTTPException(status_code=404, detail="Tenant not found")
                
            # Get updated tenant info
            tenant_info = await get_tenant_info(organization_id, conn)
            
            logger.info(f"Updated tenant {organization_id}")
            return tenant_info
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tenant {organization_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update tenant")

@router.delete("/{organization_id}")
async def delete_tenant(
    organization_id: str,
    current_user = Depends(require_admin)
):
    """
    Delete a tenant and all associated data.
    Requires system admin privileges.
    """
    try:
        async with get_database_connection() as conn:
            # Start transaction
            async with conn.transaction():
                # First, delete all tenant-related data
                tables_to_cleanup = [
                    'training_jobs',
                    'evaluations', 
                    'organization_members',
                    'organization_usage',
                    'organization_credit_transactions',
                    'users'
                ]
                
                for table in tables_to_cleanup:
                    await conn.execute(
                        f"DELETE FROM {table} WHERE organization_id = $1",
                        organization_id
                    )
                
                # Finally delete the organization
                result = await conn.execute(
                    "DELETE FROM organizations WHERE organization_id = $1",
                    organization_id
                )
                
                if result == "DELETE 0":
                    raise HTTPException(status_code=404, detail="Tenant not found")
                    
            logger.info(f"Deleted tenant {organization_id} and all associated data")
            return {"message": "Tenant deleted successfully", "organization_id": organization_id}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tenant {organization_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete tenant")

# ============= Quota Management =============

@router.get("/{organization_id}/quotas")
async def get_tenant_quotas(
    organization_id: str,
    current_org = Depends(get_current_organization)
):
    """Get tenant resource quotas and current usage"""
    try:
        if current_org.organization_id != organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        async with get_database_connection() as conn:
            # Get quotas
            quota_result = await conn.fetchrow(
                "SELECT quotas FROM organization_quotas WHERE organization_id = $1",
                organization_id
            )
            
            if not quota_result:
                raise HTTPException(status_code=404, detail="Quotas not found")
                
            quotas = quota_result['quotas']
            
            # Get current usage
            usage = await get_current_usage(organization_id, conn)
            
            return {
                "organization_id": organization_id,
                "quotas": quotas,
                "current_usage": usage,
                "usage_percentage": calculate_usage_percentage(quotas, usage)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quotas for {organization_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quotas")

@router.put("/{organization_id}/quotas")
async def update_tenant_quotas(
    organization_id: str,
    request: TenantQuotaRequest,
    current_user = Depends(require_admin)
):
    """Update tenant resource quotas (admin only)"""
    try:
        async with get_database_connection() as conn:
            # Get current quotas
            current_result = await conn.fetchrow(
                "SELECT quotas FROM organization_quotas WHERE organization_id = $1",
                organization_id
            )
            
            if not current_result:
                raise HTTPException(status_code=404, detail="Tenant not found")
                
            current_quotas = current_result['quotas']
            
            # Update with new values
            for field, value in request.dict(exclude_unset=True).items():
                if value is not None:
                    current_quotas[field] = value
                    
            # Save updated quotas
            await conn.execute(
                "UPDATE organization_quotas SET quotas = $1, updated_at = $2 WHERE organization_id = $3",
                json.dumps(current_quotas), datetime.utcnow(), organization_id
            )
            
            logger.info(f"Updated quotas for tenant {organization_id}")
            return {
                "organization_id": organization_id,
                "quotas": current_quotas,
                "message": "Quotas updated successfully"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating quotas for {organization_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update quotas")

# ============= Tenant Listing =============

@router.get("/", response_model=List[TenantResponse])
async def list_tenants(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    plan: Optional[str] = None,
    current_user = Depends(require_admin)
):
    """List all tenants (admin only)"""
    try:
        async with get_database_connection() as conn:
            # Build query with filters
            where_conditions = []
            params = []
            param_count = 1
            
            if status:
                where_conditions.append(f"status = ${param_count}")
                params.append(status)
                param_count += 1
                
            if plan:
                where_conditions.append(f"plan = ${param_count}")
                params.append(plan)
                param_count += 1
                
            where_clause = ""
            if where_conditions:
                where_clause = f"WHERE {' AND '.join(where_conditions)}"
                
            # Add limit and offset
            params.extend([limit, offset])
            
            query = f"""
                SELECT organization_id FROM organizations 
                {where_clause}
                ORDER BY created_at DESC 
                LIMIT ${param_count} OFFSET ${param_count + 1}
            """
            
            org_results = await conn.fetch(query, *params)
            
            # Get full info for each tenant
            tenants = []
            for org in org_results:
                tenant_info = await get_tenant_info(org['organization_id'], conn)
                if tenant_info:
                    tenants.append(tenant_info)
                    
            return tenants
            
    except Exception as e:
        logger.error(f"Error listing tenants: {e}")
        raise HTTPException(status_code=500, detail="Failed to list tenants")

# ============= Helper Functions =============

async def get_tenant_info(organization_id: str, conn) -> TenantResponse:
    """Get complete tenant information"""
    try:
        # Get organization data
        org_result = await conn.fetchrow(
            "SELECT * FROM organizations WHERE organization_id = $1",
            organization_id
        )
        
        if not org_result:
            return None
            
        # Get member count
        member_count = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE organization_id = $1",
            organization_id
        )
        
        # Get quotas
        quota_result = await conn.fetchrow(
            "SELECT quotas FROM organization_quotas WHERE organization_id = $1",
            organization_id
        )
        
        quotas = quota_result['quotas'] if quota_result else {}
        
        # Get current usage
        usage = await get_current_usage(organization_id, conn)
        
        return TenantResponse(
            organization_id=org_result['organization_id'],
            name=org_result['name'],
            domain=org_result['domain'],
            plan=org_result['plan'],
            status=org_result['status'],
            billing_email=org_result['billing_email'],
            created_at=org_result['created_at'],
            updated_at=org_result['updated_at'],
            member_count=member_count or 0,
            current_usage=usage,
            quotas=quotas,
            settings=org_result['settings'] or {}
        )
        
    except Exception as e:
        logger.error(f"Error getting tenant info for {organization_id}: {e}")
        return None

async def get_current_usage(organization_id: str, conn) -> Dict[str, Any]:
    """Calculate current resource usage for tenant"""
    try:
        usage = {}
        
        # Training jobs count
        usage['training_jobs'] = await conn.fetchval(
            "SELECT COUNT(*) FROM training_jobs WHERE organization_id = $1",
            organization_id
        ) or 0
        
        # Active deployments count  
        usage['deployments'] = 0  # TODO: Add deployment tracking
        
        # Users count
        usage['users'] = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE organization_id = $1",
            organization_id
        ) or 0
        
        # API calls this month (TODO: implement API call tracking)
        usage['api_calls_this_month'] = 0
        
        # Storage usage (TODO: implement storage tracking)
        usage['storage_gb'] = 0.0
        
        return usage
        
    except Exception as e:
        logger.error(f"Error calculating usage for {organization_id}: {e}")
        return {}

def get_default_quotas(plan: str) -> Dict[str, Any]:
    """Get default quotas based on subscription plan"""
    quotas = {
        "starter": {
            "api_calls_per_month": 10000,
            "max_concurrent_requests": 5,
            "max_storage_gb": 1.0,
            "max_training_jobs": 2,
            "max_deployments": 1,
            "max_users": 3
        },
        "pro": {
            "api_calls_per_month": 100000,
            "max_concurrent_requests": 20,
            "max_storage_gb": 10.0,
            "max_training_jobs": 10,
            "max_deployments": 5,
            "max_users": 10
        },
        "enterprise": {
            "api_calls_per_month": 1000000,
            "max_concurrent_requests": 100,
            "max_storage_gb": 100.0,
            "max_training_jobs": 50,
            "max_deployments": 25,
            "max_users": 100
        }
    }
    
    return quotas.get(plan, quotas["starter"])

def calculate_usage_percentage(quotas: Dict[str, Any], usage: Dict[str, Any]) -> Dict[str, float]:
    """Calculate usage percentages for each quota"""
    percentages = {}
    
    for quota_key, quota_value in quotas.items():
        if quota_key in usage and quota_value > 0:
            usage_value = usage[quota_key]
            percentages[quota_key] = (usage_value / quota_value) * 100
        else:
            percentages[quota_key] = 0.0
            
    return percentages

# ============= Health Check =============

@router.get("/health")
async def tenant_service_health():
    """Health check for tenant management service"""
    try:
        async with get_database_connection() as conn:
            # Test database connectivity
            await conn.fetchval("SELECT 1")
            
            # Count total tenants
            tenant_count = await conn.fetchval("SELECT COUNT(*) FROM organizations")
            
            return {
                "status": "healthy",
                "service": "tenant-management",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "connected",
                "total_tenants": tenant_count
            }
            
    except Exception as e:
        logger.error(f"Tenant service health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Tenant service unhealthy: {str(e)}"
        )