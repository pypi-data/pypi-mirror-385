"""
Configuration API Routes

Provides comprehensive configuration management capabilities including:
- Provider configuration management
- Environment configuration
- System settings management
- Configuration validation
- Configuration backup and restore
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import logging
from datetime import datetime
import json
import os

try:
    from ..middleware.auth import optional_auth, require_read_access, require_write_access
except ImportError:
    # For development/testing when auth is not required
    def optional_auth():
        return {"user_id": "test_user"}
    
    def require_read_access():
        return {"user_id": "test_user"}
    
    def require_write_access():
        return {"user_id": "test_user"}

# Import configuration modules
from isa_model.core.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response Models
class ProviderConfigRequest(BaseModel):
    """Request model for provider configuration"""
    provider_name: str = Field(..., description="Provider name (e.g., 'openai', 'replicate')")
    config_data: Dict[str, Any] = Field(..., description="Provider configuration data")
    is_active: bool = Field(True, description="Whether the provider is active")

class EnvironmentConfigRequest(BaseModel):
    """Request model for environment configuration"""
    environment: str = Field(..., description="Environment name (e.g., 'development', 'production')")
    config_data: Dict[str, Any] = Field(..., description="Environment configuration data")

class ConfigValidationRequest(BaseModel):
    """Request model for configuration validation"""
    config_type: str = Field(..., description="Type of configuration to validate")
    config_data: Dict[str, Any] = Field(..., description="Configuration data to validate")

class ConfigBackupRequest(BaseModel):
    """Request model for configuration backup"""
    backup_name: str = Field(..., description="Name for the backup")
    include_secrets: bool = Field(False, description="Whether to include sensitive data")
    components: Optional[List[str]] = Field(None, description="Specific components to backup")

class ConfigResponse(BaseModel):
    """Response model for configuration operations"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Global config manager instance
config_manager = ConfigManager()

@router.get("/health")
async def config_health():
    """Health check for configuration service"""
    try:
        health_status = config_manager.get_health_status()
        return {
            "status": "healthy",
            "service": "configuration",
            "components": health_status
        }
    except Exception as e:
        logger.error(f"Config health check failed: {e}")
        return {
            "status": "error",
            "service": "configuration",
            "error": str(e)
        }

@router.get("/providers")
async def get_all_providers(
    include_inactive: bool = Query(False, description="Include inactive providers"),
    user = Depends(require_read_access)
):
    """
    Get all provider configurations
    """
    try:
        providers = config_manager.get_all_providers(include_inactive=include_inactive)
        
        return {
            "success": True,
            "providers": providers,
            "total_count": len(providers)
        }
        
    except Exception as e:
        logger.error(f"Failed to get providers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get providers: {str(e)}")

@router.get("/providers/{provider_name}")
async def get_provider_config(
    provider_name: str,
    mask_secrets: bool = Query(True, description="Whether to mask sensitive data"),
    user = Depends(require_read_access)
):
    """
    Get configuration for a specific provider
    """
    try:
        config = config_manager.get_provider_config(
            provider_name=provider_name,
            mask_secrets=mask_secrets
        )
        
        if not config:
            raise HTTPException(status_code=404, detail=f"Provider not found: {provider_name}")
        
        return {
            "success": True,
            "provider_name": provider_name,
            "config": config,
            "masked_secrets": mask_secrets
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get provider config for {provider_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get provider config: {str(e)}")

@router.put("/providers/{provider_name}")
async def update_provider_config(
    provider_name: str,
    request: ProviderConfigRequest,
    user = Depends(require_write_access)
):
    """
    Update configuration for a specific provider
    """
    try:
        # Validate configuration first
        validation_result = config_manager.validate_provider_config(
            provider_name=provider_name,
            config_data=request.config_data
        )
        
        if not validation_result["valid"]:
            return ConfigResponse(
                success=False,
                message="Configuration validation failed",
                error=validation_result.get("error"),
                data={"validation_errors": validation_result.get("errors", [])}
            )
        
        # Update configuration
        success = config_manager.update_provider_config(
            provider_name=provider_name,
            config_data=request.config_data,
            is_active=request.is_active,
            updated_by=user.get("user_id") if user else None
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update provider configuration")
        
        return ConfigResponse(
            success=True,
            message=f"Provider {provider_name} configuration updated successfully",
            data={
                "provider_name": provider_name,
                "is_active": request.is_active,
                "config_keys": list(request.config_data.keys())
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update provider config for {provider_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update provider config: {str(e)}")

@router.post("/providers/{provider_name}/test")
async def test_provider_config(
    provider_name: str,
    config_data: Optional[Dict[str, Any]] = None,
    user = Depends(require_read_access)
):
    """
    Test provider configuration connectivity
    """
    try:
        # Use provided config or get existing config
        test_config = config_data
        if not test_config:
            test_config = config_manager.get_provider_config(provider_name, mask_secrets=False)
            if not test_config:
                raise HTTPException(status_code=404, detail=f"Provider not found: {provider_name}")
        
        # Test the configuration
        test_result = config_manager.test_provider_connection(
            provider_name=provider_name,
            config_data=test_config
        )
        
        return {
            "success": test_result["success"],
            "provider_name": provider_name,
            "test_result": test_result,
            "message": test_result.get("message", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test provider config for {provider_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test provider config: {str(e)}")

@router.delete("/providers/{provider_name}")
async def delete_provider_config(
    provider_name: str,
    user = Depends(require_write_access)
):
    """
    Delete provider configuration
    """
    try:
        success = config_manager.delete_provider_config(
            provider_name=provider_name,
            deleted_by=user.get("user_id") if user else None
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Provider not found: {provider_name}")
        
        return {
            "success": True,
            "message": f"Provider {provider_name} configuration deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete provider config for {provider_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete provider config: {str(e)}")

@router.get("/environments")
async def get_all_environments(user = Depends(require_read_access)):
    """
    Get all environment configurations
    """
    try:
        environments = config_manager.get_all_environments()
        
        return {
            "success": True,
            "environments": environments,
            "total_count": len(environments)
        }
        
    except Exception as e:
        logger.error(f"Failed to get environments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get environments: {str(e)}")

@router.get("/environments/{environment}")
async def get_environment_config(
    environment: str,
    mask_secrets: bool = Query(True, description="Whether to mask sensitive data"),
    user = Depends(require_read_access)
):
    """
    Get configuration for a specific environment
    """
    try:
        config = config_manager.get_environment_config(
            environment=environment,
            mask_secrets=mask_secrets
        )
        
        if not config:
            raise HTTPException(status_code=404, detail=f"Environment not found: {environment}")
        
        return {
            "success": True,
            "environment": environment,
            "config": config,
            "masked_secrets": mask_secrets
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get environment config for {environment}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get environment config: {str(e)}")

@router.put("/environments/{environment}")
async def update_environment_config(
    environment: str,
    request: EnvironmentConfigRequest,
    user = Depends(require_write_access)
):
    """
    Update configuration for a specific environment
    """
    try:
        # Validate environment configuration
        validation_result = config_manager.validate_environment_config(
            environment=environment,
            config_data=request.config_data
        )
        
        if not validation_result["valid"]:
            return ConfigResponse(
                success=False,
                message="Environment configuration validation failed",
                error=validation_result.get("error"),
                data={"validation_errors": validation_result.get("errors", [])}
            )
        
        # Update configuration
        success = config_manager.update_environment_config(
            environment=environment,
            config_data=request.config_data,
            updated_by=user.get("user_id") if user else None
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update environment configuration")
        
        return ConfigResponse(
            success=True,
            message=f"Environment {environment} configuration updated successfully",
            data={
                "environment": environment,
                "config_keys": list(request.config_data.keys())
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update environment config for {environment}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update environment config: {str(e)}")

@router.post("/validate")
async def validate_configuration(
    request: ConfigValidationRequest,
    user = Depends(require_read_access)
):
    """
    Validate configuration data
    """
    try:
        if request.config_type == "provider":
            # Extract provider name from config data or use a default validation
            provider_name = request.config_data.get("provider_name", "generic")
            validation_result = config_manager.validate_provider_config(
                provider_name=provider_name,
                config_data=request.config_data
            )
        elif request.config_type == "environment":
            environment = request.config_data.get("environment", "generic")
            validation_result = config_manager.validate_environment_config(
                environment=environment,
                config_data=request.config_data
            )
        else:
            # Generic validation
            validation_result = config_manager.validate_generic_config(
                config_type=request.config_type,
                config_data=request.config_data
            )
        
        return {
            "success": True,
            "config_type": request.config_type,
            "validation_result": validation_result
        }
        
    except Exception as e:
        logger.error(f"Failed to validate configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate configuration: {str(e)}")

@router.get("/settings")
async def get_system_settings(
    category: Optional[str] = Query(None, description="Filter by settings category"),
    user = Depends(require_read_access)
):
    """
    Get system settings
    """
    try:
        settings = config_manager.get_system_settings(category=category)
        
        return {
            "success": True,
            "settings": settings,
            "category": category
        }
        
    except Exception as e:
        logger.error(f"Failed to get system settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system settings: {str(e)}")

@router.put("/settings/{setting_key}")
async def update_system_setting(
    setting_key: str,
    setting_value: Any,
    user = Depends(require_write_access)
):
    """
    Update a specific system setting
    """
    try:
        success = config_manager.update_system_setting(
            setting_key=setting_key,
            setting_value=setting_value,
            updated_by=user.get("user_id") if user else None
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update system setting")
        
        return {
            "success": True,
            "message": f"System setting {setting_key} updated successfully",
            "setting_key": setting_key,
            "setting_value": setting_value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update system setting {setting_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update system setting: {str(e)}")

@router.post("/backup")
async def create_configuration_backup(
    request: ConfigBackupRequest,
    user = Depends(require_write_access)
):
    """
    Create a backup of configuration data
    """
    try:
        backup_result = config_manager.create_backup(
            backup_name=request.backup_name,
            include_secrets=request.include_secrets,
            components=request.components,
            created_by=user.get("user_id") if user else None
        )
        
        return {
            "success": backup_result["success"],
            "message": backup_result.get("message", "Backup created successfully"),
            "backup_info": {
                "backup_name": request.backup_name,
                "backup_id": backup_result.get("backup_id"),
                "created_at": backup_result.get("created_at"),
                "include_secrets": request.include_secrets,
                "components": request.components or "all"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create configuration backup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@router.get("/backups")
async def list_configuration_backups(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of backups to return"),
    user = Depends(require_read_access)
):
    """
    List available configuration backups
    """
    try:
        backups = config_manager.list_backups(limit=limit)
        
        return {
            "success": True,
            "backups": backups,
            "total_count": len(backups)
        }
        
    except Exception as e:
        logger.error(f"Failed to list configuration backups: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")

@router.post("/restore/{backup_id}")
async def restore_configuration_backup(
    backup_id: str,
    components: Optional[List[str]] = None,
    dry_run: bool = Query(False, description="Perform a dry run without making changes"),
    user = Depends(require_write_access)
):
    """
    Restore configuration from a backup
    """
    try:
        restore_result = config_manager.restore_backup(
            backup_id=backup_id,
            components=components,
            dry_run=dry_run,
            restored_by=user.get("user_id") if user else None
        )
        
        return {
            "success": restore_result["success"],
            "message": restore_result.get("message", "Configuration restored successfully"),
            "restore_info": {
                "backup_id": backup_id,
                "components": components or "all",
                "dry_run": dry_run,
                "changes_applied": restore_result.get("changes_applied", [])
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to restore configuration backup {backup_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restore backup: {str(e)}")

@router.get("/export")
async def export_configuration(
    format_type: str = Query("json", description="Export format (json, yaml)"),
    components: Optional[List[str]] = Query(None, description="Specific components to export"),
    mask_secrets: bool = Query(True, description="Whether to mask sensitive data"),
    user = Depends(require_read_access)
):
    """
    Export configuration data
    """
    try:
        export_result = config_manager.export_configuration(
            format_type=format_type,
            components=components,
            mask_secrets=mask_secrets
        )
        
        return {
            "success": True,
            "export_format": format_type,
            "components": components or "all",
            "masked_secrets": mask_secrets,
            "data": export_result["data"],
            "metadata": export_result.get("metadata", {})
        }
        
    except Exception as e:
        logger.error(f"Failed to export configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export configuration: {str(e)}")

@router.post("/import")
async def import_configuration(
    import_data: Dict[str, Any],
    merge_strategy: str = Query("merge", description="Import strategy (merge, replace)"),
    validate_only: bool = Query(False, description="Only validate without importing"),
    user = Depends(require_write_access)
):
    """
    Import configuration data
    """
    try:
        import_result = config_manager.import_configuration(
            import_data=import_data,
            merge_strategy=merge_strategy,
            validate_only=validate_only,
            imported_by=user.get("user_id") if user else None
        )
        
        return {
            "success": import_result["success"],
            "message": import_result.get("message", "Configuration imported successfully"),
            "import_info": {
                "merge_strategy": merge_strategy,
                "validate_only": validate_only,
                "changes_applied": import_result.get("changes_applied", []),
                "validation_errors": import_result.get("validation_errors", [])
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to import configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import configuration: {str(e)}")

@router.get("/audit")
async def get_configuration_audit_log(
    component: Optional[str] = Query(None, description="Filter by component"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    user = Depends(require_read_access)
):
    """
    Get configuration audit log
    """
    try:
        # Parse dates if provided
        from datetime import datetime
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        audit_log = config_manager.get_audit_log(
            component=component,
            action=action,
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit
        )
        
        return {
            "success": True,
            "audit_log": audit_log,
            "filters": {
                "component": component,
                "action": action,
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit
            },
            "total_records": len(audit_log)
        }
        
    except Exception as e:
        logger.error(f"Failed to get configuration audit log: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit log: {str(e)}")