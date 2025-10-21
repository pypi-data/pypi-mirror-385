"""
Optional Authentication Middleware

Provides optional API key authentication for the ISA Model Platform.
When authentication is disabled (default), all endpoints remain open.
When enabled, requires API keys for access.
"""

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader, APIKeyQuery
from typing import Optional, Dict, List, Union
import hashlib
import secrets
import time
import logging
import os
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# Configuration
AUTH_ENABLED = os.getenv("REQUIRE_API_KEYS", "false").lower() == "true"
API_KEYS_FILE = Path(os.path.dirname(__file__)).parent.parent.parent / "deployment" / "dev" / ".api_keys.json"

# Security schemes (only used when auth is enabled)
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

class APIKeyManager:
    def __init__(self):
        self.api_keys: Dict[str, Dict] = {}
        
        # Load API keys first to check if auth should be enabled
        self.load_api_keys()
        
        # Determine auth state: check explicit setting first, then auto-detect from keys
        explicit_auth = AUTH_ENABLED
        has_keys = len(self.api_keys) > 0
        
        # If explicitly disabled (REQUIRE_API_KEYS=false), respect that setting
        if os.getenv("REQUIRE_API_KEYS", "").lower() == "false":
            self.auth_enabled = False
        else:
            # Otherwise, enable if explicitly set OR if API keys exist
            self.auth_enabled = explicit_auth or has_keys
        
        if self.auth_enabled:
            logger.info(f"API Key authentication is ENABLED ({'explicit' if explicit_auth else 'auto-detected from keys'})")
        else:
            logger.info("API Key authentication is DISABLED - all endpoints are open")
    
    def load_api_keys(self):
        """Load API keys from file"""
        try:
            if API_KEYS_FILE.exists():
                with open(API_KEYS_FILE, 'r') as f:
                    self.api_keys = json.load(f)
                logger.info(f"Loaded {len(self.api_keys)} API keys")
            else:
                self.api_keys = {}
                logger.info("No API keys file found - authentication will be disabled")
        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
            self.api_keys = {}
    
    def save_api_keys(self):
        """Save API keys to file"""
        try:
            API_KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(API_KEYS_FILE, 'w') as f:
                json.dump(self.api_keys, f, indent=2)
            logger.info("API keys saved successfully")
        except Exception as e:
            logger.error(f"Error saving API keys: {e}")
    
    def create_default_keys(self):
        """Create default API keys for initial setup"""
        admin_key = self.generate_api_key("admin", scopes=["read", "write", "admin"])
        dev_key = self.generate_api_key("development", scopes=["read", "write"])
        
        logger.warning("=== CREATED DEFAULT API KEYS ===")
        logger.warning(f"Admin API Key: {admin_key}")
        logger.warning(f"Development API Key: {dev_key}")
        logger.warning("Please save these keys securely!")
        logger.warning("=====================================")
        
        return {"admin_key": admin_key, "dev_key": dev_key}
    
    def generate_api_key(self, name: str, scopes: List[str] = None) -> str:
        """Generate a new API key"""
        if scopes is None:
            scopes = ["read"]
        
        # Generate secure random key
        key = f"isa_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        # Store key metadata
        self.api_keys[key_hash] = {
            "name": name,
            "scopes": scopes,
            "created_at": time.time(),
            "last_used": None,
            "usage_count": 0,
            "active": True
        }
        
        self.save_api_keys()
        return key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate an API key and return its metadata"""
        if not self.auth_enabled:
            # When auth is disabled, return a default user context
            return {
                "name": "anonymous",
                "scopes": ["read", "write", "admin"],
                "auth_enabled": False
            }
        
        if not api_key:
            return None
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_data = self.api_keys.get(key_hash)
        
        if not key_data or not key_data.get("active", True):
            return None
        
        # Update usage statistics
        key_data["last_used"] = time.time()
        key_data["usage_count"] = key_data.get("usage_count", 0) + 1
        key_data["auth_enabled"] = True
        self.save_api_keys()
        
        return key_data
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key"""
        if not self.auth_enabled:
            return False
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if key_hash in self.api_keys:
            self.api_keys[key_hash]["active"] = False
            self.save_api_keys()
            return True
        return False
    
    def list_api_keys(self) -> List[Dict]:
        """List all API keys (without revealing the actual keys)"""
        if not self.auth_enabled:
            return []
        
        return [
            {
                "key_hash": key_hash[:16] + "...",
                "name": data["name"],
                "scopes": data["scopes"],
                "created_at": data["created_at"],
                "last_used": data.get("last_used"),
                "usage_count": data.get("usage_count", 0),
                "active": data.get("active", True)
            }
            for key_hash, data in self.api_keys.items()
        ]
    
    def enable_auth(self):
        """Enable authentication"""
        self.auth_enabled = True
        if not self.api_keys:
            return self.create_default_keys()
        return None
    
    def disable_auth(self):
        """Disable authentication"""
        self.auth_enabled = False

# Global API key manager instance
api_key_manager = APIKeyManager()

async def get_api_key_from_request(
    request: Request,
    bearer_token: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    header_key: Optional[str] = Depends(api_key_header),
    query_key: Optional[str] = Depends(api_key_query)
) -> Optional[str]:
    """Extract API key from various sources"""
    
    # If auth is disabled, return None (will be handled as anonymous)
    if not api_key_manager.auth_enabled:
        return None
    
    # Try Bearer token first
    if bearer_token:
        return bearer_token.credentials
    
    # Try X-API-Key header
    if header_key:
        return header_key
    
    # Try query parameter
    if query_key:
        return query_key
    
    return None

async def authenticate_api_key(api_key: str = Depends(get_api_key_from_request)) -> Dict:
    """Authenticate API key and return user info (optional when auth disabled)"""
    
    # When auth is disabled, always succeed with anonymous user
    if not api_key_manager.auth_enabled:
        return {
            "name": "anonymous",
            "scopes": ["read", "write", "admin"],
            "auth_enabled": False,
            "authenticated": False
        }
    
    # When auth is enabled, require valid API key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide via Authorization header, X-API-Key header, or api_key query parameter",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    key_data = api_key_manager.validate_api_key(api_key)
    
    if not key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    key_data["authenticated"] = True
    return key_data

async def require_scope(required_scope: str):
    """Create a dependency that requires a specific scope"""
    async def check_scope(current_user: Dict = Depends(authenticate_api_key)) -> Dict:
        # When auth is disabled, always allow
        if not current_user.get("auth_enabled", True):
            return current_user
        
        user_scopes = current_user.get("scopes", [])
        
        if required_scope not in user_scopes and "admin" not in user_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scope: {required_scope}"
            )
        
        return current_user
    
    return check_scope

# Convenience dependencies for common scopes
async def require_read_access(current_user: Dict = Depends(authenticate_api_key)) -> Dict:
    """Require read access (or auth disabled)"""
    if not current_user.get("auth_enabled", True):
        return current_user
    
    user_scopes = current_user.get("scopes", [])
    if not any(scope in user_scopes for scope in ["read", "write", "admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Read access required"
        )
    return current_user

async def require_write_access(current_user: Dict = Depends(authenticate_api_key)) -> Dict:
    """Require write access (or auth disabled)"""
    if not current_user.get("auth_enabled", True):
        return current_user
    
    user_scopes = current_user.get("scopes", [])
    if not any(scope in user_scopes for scope in ["write", "admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Write access required"
        )
    return current_user

async def require_admin_access(current_user: Dict = Depends(authenticate_api_key)) -> Dict:
    """Require admin access (or auth disabled)"""
    if not current_user.get("auth_enabled", True):
        return current_user
    
    user_scopes = current_user.get("scopes", [])
    if "admin" not in user_scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Optional authentication (always returns user info, never fails)
async def optional_auth(api_key: str = Depends(get_api_key_from_request)) -> Dict:
    """Optional authentication - returns user info if available, anonymous if not"""
    try:
        return api_key_manager.validate_api_key(api_key) or {
            "name": "anonymous",
            "scopes": [],
            "auth_enabled": api_key_manager.auth_enabled,
            "authenticated": False
        }
    except Exception:
        return {
            "name": "anonymous", 
            "scopes": [],
            "auth_enabled": api_key_manager.auth_enabled,
            "authenticated": False
        }