"""
Direct Database Client for Migrations

Uses direct PostgreSQL connection for database operations like migrations.
This bypasses Supabase API and connects directly to PostgreSQL for admin operations.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
import asyncpg
import os

logger = logging.getLogger(__name__)

class DirectDBClient:
    """
    Direct PostgreSQL client for database administration operations
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize direct database client"""
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            # Fallback to individual components
            host = os.getenv("DB_HOST", "127.0.0.1")
            port = os.getenv("DB_PORT", "54322")
            database = os.getenv("DB_NAME", "postgres")
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASSWORD", "postgres")
            self.database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        self.connection = None
    
    async def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = await asyncpg.connect(self.database_url)
            logger.info("Direct database connection established")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    async def disconnect(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            self.connection = None
    
    async def execute_sql(self, sql: str) -> Dict[str, Any]:
        """Execute raw SQL command"""
        if not self.connection:
            if not await self.connect():
                return {"success": False, "error": "Failed to connect to database"}
        
        try:
            await self.connection.execute(sql)
            return {"success": True}
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_query(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """Execute SQL query with parameters and return results"""
        if not self.connection:
            if not await self.connect():
                return {"success": False, "error": "Failed to connect to database"}
        
        try:
            if params:
                result = await self.connection.fetch(query, *params)
            else:
                result = await self.connection.fetch(query)
            
            # Convert asyncpg records to dicts
            data = [dict(record) for record in result]
            return {"success": True, "data": data}
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_transaction(self, sql_commands: List[str]) -> Dict[str, Any]:
        """Execute multiple SQL commands in a transaction"""
        if not self.connection:
            if not await self.connect():
                return {"success": False, "error": "Failed to connect to database"}
        
        try:
            async with self.connection.transaction():
                for sql in sql_commands:
                    await self.connection.execute(sql)
            return {"success": True}
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if not self.connection:
                if not await self.connect():
                    return False
            
            await self.connection.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

# Factory function
def create_direct_db_client(database_url: Optional[str] = None) -> DirectDBClient:
    """Create a direct database client"""
    return DirectDBClient(database_url)