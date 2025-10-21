"""
Database Connection Dependencies

Provides database connections and transaction management
with automatic tenant context handling.
"""

import asyncio
import asyncpg
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from ..middleware.tenant_context import get_tenant_context

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool: Optional[asyncpg.Pool] = None

async def initialize_database_pool():
    """Initialize the database connection pool"""
    global _connection_pool
    
    if _connection_pool:
        return _connection_pool
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable not set")
    
    try:
        _connection_pool = await asyncpg.create_pool(
            database_url,
            min_size=5,
            max_size=20,
            command_timeout=60,
            server_settings={
                'search_path': 'dev',
                'timezone': 'UTC'
            }
        )
        
        logger.info("Database connection pool initialized")
        return _connection_pool
        
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise

async def close_database_pool():
    """Close the database connection pool"""
    global _connection_pool
    
    if _connection_pool:
        await _connection_pool.close()
        _connection_pool = None
        logger.info("Database connection pool closed")

@asynccontextmanager
async def get_database_connection():
    """
    Get a database connection from the pool with automatic tenant context.
    
    This context manager automatically:
    1. Gets a connection from the pool
    2. Sets the tenant context if available
    3. Handles transactions
    4. Returns the connection to the pool
    """
    if not _connection_pool:
        await initialize_database_pool()
    
    async with _connection_pool.acquire() as conn:
        try:
            # Set tenant context if available
            tenant_context = get_tenant_context()
            if tenant_context:
                await conn.execute(
                    "SELECT set_config('app.current_organization_id', $1, true)",
                    tenant_context.organization_id
                )
                
            yield conn
            
        except Exception as e:
            logger.error(f"Database operation error: {e}")
            raise
        finally:
            # Clear tenant context
            try:
                await conn.execute(
                    "SELECT set_config('app.current_organization_id', '', true)"
                )
            except:
                pass  # Ignore cleanup errors

@asynccontextmanager 
async def get_database_transaction():
    """
    Get a database connection with an explicit transaction.
    """
    async with get_database_connection() as conn:
        async with conn.transaction():
            yield conn

async def execute_query(query: str, *args, fetch_type: str = "fetch"):
    """
    Execute a query with automatic connection management.
    
    Args:
        query: SQL query
        *args: Query parameters
        fetch_type: 'fetch', 'fetchrow', 'fetchval', or 'execute'
    """
    async with get_database_connection() as conn:
        if fetch_type == "fetch":
            return await conn.fetch(query, *args)
        elif fetch_type == "fetchrow":
            return await conn.fetchrow(query, *args)
        elif fetch_type == "fetchval":
            return await conn.fetchval(query, *args)
        elif fetch_type == "execute":
            return await conn.execute(query, *args)
        else:
            raise ValueError(f"Invalid fetch_type: {fetch_type}")

# FastAPI dependency functions

async def get_db_connection():
    """FastAPI dependency to get database connection"""
    async with get_database_connection() as conn:
        yield conn

async def get_db_transaction():
    """FastAPI dependency to get database transaction"""
    async with get_database_transaction() as conn:
        yield conn