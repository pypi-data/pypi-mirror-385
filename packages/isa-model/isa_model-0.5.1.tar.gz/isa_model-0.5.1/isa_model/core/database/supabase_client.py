"""
Centralized Supabase Client for ISA Model Core

Provides a singleton Supabase client instance that:
- Gets configuration from ConfigManager
- Handles environment-based schema selection
- Provides a single point of database access for all services
"""

import logging
import os
from typing import Optional
from urllib.parse import urlparse
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from dotenv import load_dotenv
from functools import wraps
import httpx

from ..config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

def require_client(default_return=None):
    """Decorator to check if client is available before executing method"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self._client is None:
                logger.error(f"Error in {func.__name__}: Supabase client not available")
                return default_return
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

class SupabaseClient:
    """Singleton Supabase client with environment-aware configuration"""
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_client()
            SupabaseClient._initialized = True
    
    def _configure_proxy_bypass(self):
        """Configure proxy bypass for Supabase connections"""
        # Check if URL is localhost or Docker internal
        if self.url:
            parsed_url = urlparse(self.url)
            hostname = parsed_url.hostname or ''
            
            # Check if it's a local connection
            is_local = hostname in ['localhost', '127.0.0.1', '0.0.0.0', 'host.docker.internal']
            is_docker = hostname.startswith('172.') or hostname.startswith('192.168.')
            
            if is_local or is_docker:
                logger.info(f"Detected local Supabase at {hostname}, configuring proxy bypass...")
                
                # Get current proxy settings
                http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
                https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
                
                if http_proxy or https_proxy:
                    # Temporarily disable proxy for this connection
                    no_proxy = os.environ.get('NO_PROXY', '') or os.environ.get('no_proxy', '')
                    
                    # Add local addresses to no_proxy
                    local_addresses = [
                        'localhost', '127.0.0.1', '0.0.0.0',
                        'host.docker.internal', '*.local',
                        '172.*', '192.168.*', '10.*'  # Common Docker/local network ranges
                    ]
                    
                    no_proxy_list = no_proxy.split(',') if no_proxy else []
                    for addr in local_addresses:
                        if addr not in no_proxy_list:
                            no_proxy_list.append(addr)
                    
                    # Also add the specific hostname if it's not already there
                    if hostname and hostname not in no_proxy_list:
                        no_proxy_list.append(hostname)
                    
                    # Update environment variables
                    updated_no_proxy = ','.join(no_proxy_list)
                    os.environ['NO_PROXY'] = updated_no_proxy
                    os.environ['no_proxy'] = updated_no_proxy
                    
                    logger.info(f"Updated NO_PROXY to: {updated_no_proxy}")
                    
                    # For httpx-based connections, we might need to unset proxy for local connections
                    if is_local or is_docker:
                        # Store original values to restore later if needed
                        self._original_http_proxy = os.environ.pop('HTTP_PROXY', None)
                        self._original_https_proxy = os.environ.pop('HTTPS_PROXY', None)
                        os.environ.pop('http_proxy', None)
                        os.environ.pop('https_proxy', None)
                        logger.info("Temporarily disabled HTTP/HTTPS proxy for local Supabase connection")
    
    def _initialize_client(self):
        """Initialize the Supabase client with flexible environment handling"""
        try:
            # Load environment variables with fallback strategy
            load_dotenv()
            
            # Determine environment and load appropriate .env file
            env = os.getenv("ENVIRONMENT", "development")
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
            
            # Load environment-specific .env file
            if env == "development":
                env_file = os.path.join(project_root, "deployment/dev/.env")
            elif env == "staging":
                env_file = os.path.join(project_root, "deployment/staging/env/.env.staging")
            elif env == "production":
                env_file = os.path.join(project_root, "deployment/production/env/.env.production")
            else:
                env_file = os.path.join(project_root, f"deployment/{env}/.env.{env}")
            
            if os.path.exists(env_file):
                load_dotenv(env_file)
                logger.debug(f"Loaded environment from {env_file}")
            
            # Try multiple environment variable names for flexibility
            self.url = (
                os.getenv('SUPABASE_CLOUD_URL') or 
                os.getenv('NEXT_PUBLIC_SUPABASE_URL') or 
                os.getenv('SUPABASE_URL') or
                os.getenv('SUPABASE_LOCAL_URL')
            )
            self.key = (
                os.getenv('SUPABASE_CLOUD_SERVICE_ROLE_KEY') or 
                os.getenv('SUPABASE_SERVICE_ROLE_KEY') or 
                os.getenv('SUPABASE_LOCAL_SERVICE_ROLE_KEY') or
                os.getenv('SUPABASE_ANON_KEY') or
                os.getenv('SUPABASE_LOCAL_ANON_KEY')
            )
            
            # Get schema from environment variable (with dev fallback)
            # Force dev schema for local development
            self.schema = os.getenv('DB_SCHEMA', 'dev')
            self.environment = env
            
            if not self.url or not self.key:
                logger.warning("Missing Supabase credentials. Database operations will not be available.")
                logger.warning(f"URL found: {bool(self.url)}, Key found: {bool(self.key)}")
                self._client = None
                return
            
            # Create the client
            self._client = create_client(self.url, self.key)
            
            logger.info(f"Supabase client initialized for {self.environment} environment (schema: {self.schema})")
            
            # Skip connection test to avoid unnecessary database queries and error logs
            # Database operations will fail gracefully when needed
            logger.debug("Supabase client initialized (connection test skipped)")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            # Don't raise - allow graceful degradation
            self._client = None
    
    def get_client(self) -> Optional[Client]:
        """Get the Supabase client instance"""
        if not self._client:
            logger.warning("Supabase client not available - database operations will be skipped")
            return None
        return self._client
    
    @require_client(default_return=None)
    def table(self, table_name: str):
        """Get a table with the correct schema"""
        # Use the configured schema for the environment
        if self.schema and self.schema != "public":
            return self._client.schema(self.schema).table(table_name)
        else:
            return self._client.table(table_name)
    
    @require_client(default_return=None)
    def rpc(self, function_name: str, params: Optional[dict] = None):
        """Call an RPC function with the correct schema"""
        # RPC functions typically use the public schema
        # But we can extend this if needed for schema-specific functions
        return self._client.rpc(function_name, params)
    
    def get_schema(self) -> str:
        """Get the current schema being used"""
        return self.schema
    
    def get_environment(self) -> str:
        """Get the current environment"""
        return self.environment
    
    def test_connection(self) -> bool:
        """Test the database connection"""
        try:
            # Try a simple query to test connection
            result = self.table('models').select('*').limit(1).execute()
            logger.debug("Database connection test successful")
            return True
        except Exception as e:
            logger.warning(f"Database connection test failed: {e}")
            return False
    
    async def execute_sql(self, sql: str) -> dict:
        """Execute raw SQL command"""
        try:
            result = self._client.rpc('execute_sql', {'sql': sql})
            return {"success": True, "data": result.data}
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_query(self, query: str, params: tuple = None) -> dict:
        """Execute SQL query with parameters"""
        try:
            # For now, use rpc to execute queries
            # In production, you might want to use prepared statements
            if params:
                # Simple parameter substitution (not recommended for production)
                formatted_query = query % params
            else:
                formatted_query = query
            
            result = self._client.rpc('execute_query', {'query': formatted_query})
            return {"success": True, "data": result.data}
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {"success": False, "error": str(e)}

# Global singleton instance
_supabase_client = None

def get_supabase_client() -> SupabaseClient:
    """Get the global Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client

def get_supabase_table(table_name: str):
    """Convenience function to get a table with correct schema"""
    client = get_supabase_client()
    return client.table(table_name)

def get_supabase_rpc(function_name: str, params: Optional[dict] = None):
    """Convenience function to call RPC functions"""
    client = get_supabase_client()
    return client.rpc(function_name, params)