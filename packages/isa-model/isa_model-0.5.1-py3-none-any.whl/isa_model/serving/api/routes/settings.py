"""
Settings API Routes

Provides API key management and platform configuration endpoints.
This module handles sensitive operations safely without affecting running services.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
import json
import hashlib
from pathlib import Path
from ..middleware.auth import api_key_manager, require_admin_access

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration file path
CONFIG_DIR = Path(os.path.dirname(__file__)).parent.parent.parent / "deployment" / "dev"
ENV_FILE = CONFIG_DIR / ".env"
CONFIG_BACKUP_FILE = CONFIG_DIR / ".env.backup"

class APIKeyEntry(BaseModel):
    provider: str
    key_name: str
    masked_value: str
    is_set: bool
    last_updated: Optional[str] = None

class APIKeyUpdate(BaseModel):
    provider: str
    key_name: str
    key_value: str

class GeneralSettings(BaseModel):
    platform_name: Optional[str] = "ISA Model Platform"
    default_provider: Optional[str] = "auto"
    log_level: Optional[str] = "INFO"
    max_workers: Optional[int] = 1
    request_timeout: Optional[int] = 300

class PlatformAPIKey(BaseModel):
    name: str
    scopes: List[str] = ["read"]

class AuthSettings(BaseModel):
    auth_enabled: bool
    total_keys: int
    active_keys: int

# Known API key mappings
API_KEY_PROVIDERS = {
    "openai": {
        "OPENAI_API_KEY": "OpenAI API Key",
        "OPENAI_API_BASE": "OpenAI API Base URL"
    },
    "replicate": {
        "REPLICATE_API_TOKEN": "Replicate API Token"
    },
    "yyds": {
        "YYDS_API_KEY": "YYDS API Key",
        "YYDS_API_BASE": "YYDS API Base URL"
    },
    "huggingface": {
        "HF_TOKEN": "Hugging Face Token"
    },
    "runpod": {
        "RUNPOD_API_KEY": "RunPod API Key"
    },
    "pypi": {
        "PYPI_API_TOKEN": "PyPI API Token"
    }
}

def mask_api_key(api_key: str) -> str:
    """Mask API key for display, showing only first 4 and last 4 characters"""
    if not api_key or len(api_key) < 8:
        return "••••••••"
    return f"{api_key[:4]}{'•' * (len(api_key) - 8)}{api_key[-4:]}"

def read_env_file() -> Dict[str, str]:
    """Read environment variables from .env file"""
    env_vars = {}
    
    if not ENV_FILE.exists():
        logger.warning(f"Environment file not found: {ENV_FILE}")
        return env_vars
    
    try:
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    env_vars[key] = value
    except Exception as e:
        logger.error(f"Error reading environment file: {e}")
        
    return env_vars

def write_env_file(env_vars: Dict[str, str]) -> bool:
    """Write environment variables to .env file with backup"""
    try:
        # Create backup
        if ENV_FILE.exists():
            import shutil
            shutil.copy2(ENV_FILE, CONFIG_BACKUP_FILE)
            logger.info("Created backup of environment file")
        
        # Write new file
        with open(ENV_FILE, 'w') as f:
            f.write("# ISA Model Local Development Environment\n")
            f.write("# Copy this to .env for local development\n\n")
            
            # Organize by sections
            sections = {
                "Environment": ["ENVIRONMENT", "DEBUG", "LOG_LEVEL", "VERBOSE_LOGGING"],
                "Server Configuration": ["PORT", "MAX_WORKERS", "REQUEST_TIMEOUT", "MAX_REQUEST_SIZE"],
                "API Keys": [k for provider in API_KEY_PROVIDERS.values() for k in provider.keys()],
                "Database Configuration": ["SUPABASE_LOCAL_URL", "SUPABASE_LOCAL_ANON_KEY", "SUPABASE_LOCAL_SERVICE_ROLE_KEY", "SUPABASE_PWD", "DATABASE_URL"],
                "Local Services": ["OLLAMA_BASE_URL"],
                "Model Defaults": [k for k in env_vars.keys() if k.startswith("DEFAULT_")],
                "Development Configuration": ["RATE_LIMIT_REQUESTS_PER_MINUTE", "CORS_ORIGINS", "ENABLE_METRICS", "METRICS_PORT"],
                "Storage Configuration": ["MODEL_STORAGE_PATH"]
            }
            
            for section, keys in sections.items():
                section_vars = {k: v for k, v in env_vars.items() if k in keys}
                if section_vars:
                    f.write(f"\n# ============= {section} =============\n")
                    for key, value in section_vars.items():
                        f.write(f"{key}={value}\n")
            
            # Add any remaining variables
            written_keys = set()
            for keys in sections.values():
                written_keys.update(keys)
            
            remaining = {k: v for k, v in env_vars.items() if k not in written_keys}
            if remaining:
                f.write(f"\n# ============= Other =============\n")
                for key, value in remaining.items():
                    f.write(f"{key}={value}\n")
        
        logger.info("Successfully updated environment file")
        return True
        
    except Exception as e:
        logger.error(f"Error writing environment file: {e}")
        # Restore backup if write failed
        if CONFIG_BACKUP_FILE.exists():
            import shutil
            shutil.copy2(CONFIG_BACKUP_FILE, ENV_FILE)
            logger.info("Restored backup due to write failure")
        return False

@router.get("/api-keys")
async def get_api_keys():
    """Get current API key configuration (masked for security)"""
    try:
        env_vars = read_env_file()
        api_keys = []
        
        for provider, keys in API_KEY_PROVIDERS.items():
            for env_key, display_name in keys.items():
                current_value = env_vars.get(env_key, "")
                api_keys.append(APIKeyEntry(
                    provider=provider,
                    key_name=env_key,
                    masked_value=mask_api_key(current_value) if current_value else "",
                    is_set=bool(current_value)
                ))
        
        return {
            "api_keys": api_keys,
            "total_keys": len(api_keys),
            "configured_keys": sum(1 for key in api_keys if key.is_set)
        }
        
    except Exception as e:
        logger.error(f"Error getting API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve API key configuration")

@router.put("/api-keys")
async def update_api_key(api_key_update: APIKeyUpdate):
    """Update or add an API key"""
    try:
        # Validate provider and key name
        if api_key_update.provider not in API_KEY_PROVIDERS:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        provider_keys = API_KEY_PROVIDERS[api_key_update.provider]
        if api_key_update.key_name not in provider_keys:
            raise HTTPException(status_code=400, detail="Invalid key name for provider")
        
        # Read current environment
        env_vars = read_env_file()
        
        # Update the specific key
        env_vars[api_key_update.key_name] = api_key_update.key_value
        
        # Write back to file
        if not write_env_file(env_vars):
            raise HTTPException(status_code=500, detail="Failed to update configuration file")
        
        return {
            "success": True,
            "message": f"Successfully updated {api_key_update.key_name}",
            "restart_required": True  # Note: Changes require restart to take effect
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to update API key")

@router.delete("/api-keys/{provider}/{key_name}")
async def delete_api_key(provider: str, key_name: str):
    """Remove an API key"""
    try:
        # Validate provider and key name
        if provider not in API_KEY_PROVIDERS:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        provider_keys = API_KEY_PROVIDERS[provider]
        if key_name not in provider_keys:
            raise HTTPException(status_code=400, detail="Invalid key name for provider")
        
        # Read current environment
        env_vars = read_env_file()
        
        # Remove the key
        if key_name in env_vars:
            del env_vars[key_name]
        
        # Write back to file
        if not write_env_file(env_vars):
            raise HTTPException(status_code=500, detail="Failed to update configuration file")
        
        return {
            "success": True,
            "message": f"Successfully removed {key_name}",
            "restart_required": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete API key")

@router.get("/general")
async def get_general_settings():
    """Get general platform settings"""
    try:
        env_vars = read_env_file()
        
        settings = GeneralSettings(
            platform_name=env_vars.get("PLATFORM_NAME", "ISA Model Platform"),
            default_provider=env_vars.get("DEFAULT_LLM_PROVIDER", "auto"),
            log_level=env_vars.get("LOG_LEVEL", "INFO"),
            max_workers=int(env_vars.get("MAX_WORKERS", "1")),
            request_timeout=int(env_vars.get("REQUEST_TIMEOUT", "300"))
        )
        
        return settings
        
    except Exception as e:
        logger.error(f"Error getting general settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve general settings")

@router.put("/general")
async def update_general_settings(settings: GeneralSettings):
    """Update general platform settings"""
    try:
        env_vars = read_env_file()
        
        # Update settings
        if settings.platform_name:
            env_vars["PLATFORM_NAME"] = settings.platform_name
        if settings.default_provider:
            env_vars["DEFAULT_LLM_PROVIDER"] = settings.default_provider
        if settings.log_level:
            env_vars["LOG_LEVEL"] = settings.log_level
        if settings.max_workers:
            env_vars["MAX_WORKERS"] = str(settings.max_workers)
        if settings.request_timeout:
            env_vars["REQUEST_TIMEOUT"] = str(settings.request_timeout)
        
        # Write back to file
        if not write_env_file(env_vars):
            raise HTTPException(status_code=500, detail="Failed to update configuration file")
        
        return {
            "success": True,
            "message": "Successfully updated general settings",
            "restart_required": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating general settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update general settings")

@router.get("/backup")
async def get_config_backup():
    """Get information about configuration backups"""
    try:
        backups = []
        
        if CONFIG_BACKUP_FILE.exists():
            stat = CONFIG_BACKUP_FILE.stat()
            backups.append({
                "filename": CONFIG_BACKUP_FILE.name,
                "size": stat.st_size,
                "created": stat.st_mtime,
                "type": "automatic"
            })
        
        return {
            "backups": backups,
            "backup_location": str(CONFIG_DIR)
        }
        
    except Exception as e:
        logger.error(f"Error getting backup info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve backup information")

@router.post("/backup/restore")
async def restore_config_backup():
    """Restore configuration from backup"""
    try:
        if not CONFIG_BACKUP_FILE.exists():
            raise HTTPException(status_code=404, detail="No backup file found")
        
        import shutil
        shutil.copy2(CONFIG_BACKUP_FILE, ENV_FILE)
        
        return {
            "success": True,
            "message": "Configuration restored from backup",
            "restart_required": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        raise HTTPException(status_code=500, detail="Failed to restore backup")

@router.get("/health")
async def settings_health():
    """Health check for settings service"""
    try:
        env_exists = ENV_FILE.exists()
        backup_exists = CONFIG_BACKUP_FILE.exists()
        
        # Test read access
        env_vars = read_env_file() if env_exists else {}
        
        return {
            "status": "healthy",
            "service": "settings",
            "config_file_exists": env_exists,
            "backup_exists": backup_exists,
            "config_vars_count": len(env_vars),
            "writable": os.access(CONFIG_DIR, os.W_OK) if CONFIG_DIR.exists() else False
        }
        
    except Exception as e:
        logger.error(f"Settings health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "settings",
            "error": str(e)
        }

# =================== PLATFORM API KEY MANAGEMENT ===================

@router.get("/auth/status")
async def get_auth_status():
    """Get current authentication status"""
    try:
        platform_keys = api_key_manager.list_api_keys()
        
        return AuthSettings(
            auth_enabled=api_key_manager.auth_enabled,
            total_keys=len(platform_keys),
            active_keys=sum(1 for key in platform_keys if key.get("active", True))
        )
        
    except Exception as e:
        logger.error(f"Error getting auth status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get authentication status")

@router.post("/auth/bootstrap")
async def bootstrap_authentication():
    """Bootstrap authentication by creating initial admin key (only works when auth is disabled)"""
    try:
        if api_key_manager.auth_enabled:
            raise HTTPException(status_code=400, detail="Authentication is already enabled")
        
        # Enable auth and create default keys
        default_keys = api_key_manager.enable_auth()
        
        return {
            "success": True,
            "message": "Authentication bootstrapped successfully",
            "keys_generated": default_keys,
            "restart_required": False,  # This takes effect immediately
            "warning": "Save the generated API keys securely. They will not be shown again."
        }
        
    except Exception as e:
        logger.error(f"Error bootstrapping authentication: {e}")
        raise HTTPException(status_code=500, detail="Failed to bootstrap authentication")

@router.post("/auth/enable")
async def enable_authentication(current_user: Dict = Depends(require_admin_access)):
    """Enable API key authentication for the platform"""
    try:
        if api_key_manager.auth_enabled:
            return {
                "success": True,
                "message": "Authentication is already enabled",
                "keys_generated": None
            }
        
        # Enable auth and create default keys if needed
        default_keys = api_key_manager.enable_auth()
        
        return {
            "success": True,
            "message": "Authentication enabled successfully",
            "keys_generated": default_keys,
            "restart_required": True,
            "warning": "Save the generated API keys securely. They will not be shown again."
        }
        
    except Exception as e:
        logger.error(f"Error enabling authentication: {e}")
        raise HTTPException(status_code=500, detail="Failed to enable authentication")

@router.post("/auth/disable")
async def disable_authentication(current_user: Dict = Depends(require_admin_access)):
    """Disable API key authentication for the platform"""
    try:
        if not api_key_manager.auth_enabled:
            return {
                "success": True,
                "message": "Authentication is already disabled"
            }
        
        api_key_manager.disable_auth()
        
        return {
            "success": True,
            "message": "Authentication disabled successfully",
            "restart_required": True,
            "warning": "All endpoints are now publicly accessible"
        }
        
    except Exception as e:
        logger.error(f"Error disabling authentication: {e}")
        raise HTTPException(status_code=500, detail="Failed to disable authentication")

@router.get("/auth/platform-keys")
async def get_platform_api_keys(current_user: Dict = Depends(require_admin_access)):
    """Get list of platform API keys"""
    try:
        if not api_key_manager.auth_enabled:
            return {
                "auth_enabled": False,
                "api_keys": [],
                "message": "Authentication is disabled"
            }
        
        keys = api_key_manager.list_api_keys()
        
        return {
            "auth_enabled": True,
            "api_keys": keys,
            "total_keys": len(keys)
        }
        
    except Exception as e:
        logger.error(f"Error getting platform API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to get platform API keys")

@router.post("/auth/platform-keys")
async def create_platform_api_key(
    key_request: PlatformAPIKey,
    current_user: Dict = Depends(require_admin_access)
):
    """Create a new platform API key"""
    try:
        if not api_key_manager.auth_enabled:
            raise HTTPException(status_code=400, detail="Authentication is disabled")
        
        # Validate scopes
        valid_scopes = ["read", "write", "admin"]
        invalid_scopes = [scope for scope in key_request.scopes if scope not in valid_scopes]
        if invalid_scopes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid scopes: {invalid_scopes}. Valid scopes: {valid_scopes}"
            )
        
        # Generate new API key
        new_key = api_key_manager.generate_api_key(key_request.name, key_request.scopes)
        
        return {
            "success": True,
            "message": f"API key '{key_request.name}' created successfully",
            "api_key": new_key,
            "scopes": key_request.scopes,
            "warning": "Save this API key securely. It will not be shown again."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating platform API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to create platform API key")

@router.delete("/auth/platform-keys/{key_hash}")
async def revoke_platform_api_key(
    key_hash: str,
    current_user: Dict = Depends(require_admin_access)
):
    """Revoke a platform API key"""
    try:
        if not api_key_manager.auth_enabled:
            raise HTTPException(status_code=400, detail="Authentication is disabled")
        
        # Find the key by hash prefix
        keys = api_key_manager.list_api_keys()
        target_key = None
        
        for key in keys:
            if key["key_hash"].startswith(key_hash):
                target_key = key
                break
        
        if not target_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Note: We need the actual key to revoke, but we don't store it.
        # In a real implementation, you'd store key hashes and mark them as revoked.
        # For now, we'll mark it as revoked in the key data directly.
        
        # This is a simplified revocation - in production you'd want a proper key management system
        full_hash = None
        for hash_key, data in api_key_manager.api_keys.items():
            if hash_key.startswith(key_hash):
                full_hash = hash_key
                break
        
        if full_hash:
            api_key_manager.api_keys[full_hash]["active"] = False
            api_key_manager.save_api_keys()
            
            return {
                "success": True,
                "message": f"API key '{target_key['name']}' revoked successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="API key not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking platform API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke platform API key")