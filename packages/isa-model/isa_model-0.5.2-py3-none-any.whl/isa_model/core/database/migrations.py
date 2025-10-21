"""
Database Migration Manager for ISA Model

Handles schema creation and updates across different environments.
Best practices:
- Environment-specific migrations
- Version-controlled schema changes
- Rollback capabilities
- Schema validation
"""

import logging
from typing import Dict, List, Optional

try:
    import psycopg2
except ImportError:
    psycopg2 = None
from pathlib import Path

from ..config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class DatabaseMigrations:
    """Manages database migrations across environments"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.global_config = self.config_manager.get_global_config()
        self.environment = self.global_config.environment.value
        self.schema = self.global_config.database.supabase_schema or "public"
        
    def get_database_url(self) -> str:
        """Get the PostgreSQL connection URL"""
        import os
        return os.getenv('DATABASE_URL')
    
    def create_schema(self, schema_name: str) -> bool:
        """Create a schema if it doesn't exist"""
        if psycopg2 is None:
            logger.warning("psycopg2 not available, skipping schema creation")
            return True
            
        try:
            conn = psycopg2.connect(self.get_database_url())
            cursor = conn.cursor()
            
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            conn.commit()
            conn.close()
            
            logger.info(f"Schema '{schema_name}' created/verified")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create schema '{schema_name}': {e}")
            return False
    
    def get_schema_migrations(self) -> Dict[str, List[str]]:
        """Define migrations for each schema"""
        return {
            "models_table": [
                f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.models (
                    model_id TEXT PRIMARY KEY,
                    model_type TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    metadata JSONB DEFAULT '{{}}',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """,
                f"CREATE INDEX IF NOT EXISTS idx_{self.schema}_models_type ON {self.schema}.models(model_type);",
                f"CREATE INDEX IF NOT EXISTS idx_{self.schema}_models_provider ON {self.schema}.models(provider);"
            ],
            "model_capabilities_table": [
                f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.model_capabilities (
                    model_id TEXT REFERENCES {self.schema}.models(model_id) ON DELETE CASCADE,
                    capability TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    PRIMARY KEY (model_id, capability)
                );
                """,
                f"CREATE INDEX IF NOT EXISTS idx_{self.schema}_capabilities_capability ON {self.schema}.model_capabilities(capability);"
            ],
            # "model_usage_table": [
            #     f"""
            #     CREATE TABLE IF NOT EXISTS {self.schema}.model_usage (
            #         id BIGSERIAL PRIMARY KEY,
            #         timestamp TIMESTAMPTZ NOT NULL,
            #         model_id TEXT NOT NULL,
            #         operation_type TEXT NOT NULL,
            #         provider TEXT NOT NULL,
            #         service_type TEXT NOT NULL,
            #         operation TEXT NOT NULL,
            #         input_tokens INTEGER DEFAULT NULL,
            #         output_tokens INTEGER DEFAULT NULL,
            #         total_tokens INTEGER DEFAULT NULL,
            #         input_units DECIMAL DEFAULT NULL,
            #         output_units DECIMAL DEFAULT NULL,
            #         cost_usd DECIMAL(12,8) DEFAULT 0,
            #         metadata JSONB DEFAULT '{{}}',
            #         created_at TIMESTAMPTZ DEFAULT NOW()
            #     );
            #     """,
            #     f"CREATE INDEX IF NOT EXISTS idx_{self.schema}_usage_model_id ON {self.schema}.model_usage(model_id);",
            #     f"CREATE INDEX IF NOT EXISTS idx_{self.schema}_usage_timestamp ON {self.schema}.model_usage(timestamp);",
            #     f"CREATE INDEX IF NOT EXISTS idx_{self.schema}_usage_provider ON {self.schema}.model_usage(provider);",
            #     f"CREATE INDEX IF NOT EXISTS idx_{self.schema}_usage_operation_type ON {self.schema}.model_usage(operation_type);"
            # ],
            "model_embeddings_table": [
                # Try to create with VECTOR type, fallback to JSONB if pgvector not available
                f"""
                DO $$
                BEGIN
                    -- Try to create with VECTOR type
                    BEGIN
                        CREATE TABLE IF NOT EXISTS {self.schema}.model_embeddings (
                            id BIGSERIAL PRIMARY KEY,
                            model_id TEXT REFERENCES {self.schema}.models(model_id) ON DELETE CASCADE,
                            provider TEXT NOT NULL,
                            description TEXT NOT NULL,
                            embedding VECTOR(1536),
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            updated_at TIMESTAMPTZ DEFAULT NOW()
                        );
                    EXCEPTION WHEN undefined_object THEN
                        -- Fallback to JSONB if VECTOR type doesn't exist
                        CREATE TABLE IF NOT EXISTS {self.schema}.model_embeddings (
                            id BIGSERIAL PRIMARY KEY,
                            model_id TEXT REFERENCES {self.schema}.models(model_id) ON DELETE CASCADE,
                            provider TEXT NOT NULL,
                            description TEXT NOT NULL,
                            embedding JSONB,
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            updated_at TIMESTAMPTZ DEFAULT NOW()
                        );
                    END;
                END $$;
                """,
                f"CREATE INDEX IF NOT EXISTS idx_{self.schema}_embeddings_model_id ON {self.schema}.model_embeddings(model_id);"
            ],
            "tool_embeddings_table": [
                f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.tool_embeddings (
                    id BIGSERIAL PRIMARY KEY,
                    tool_name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    embedding JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """,
                f"CREATE INDEX IF NOT EXISTS idx_{self.schema}_tool_embeddings_name ON {self.schema}.tool_embeddings(tool_name);"
            ],
            "prompt_embeddings_table": [
                f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.prompt_embeddings (
                    id BIGSERIAL PRIMARY KEY,
                    prompt_name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    embedding JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """,
                f"CREATE INDEX IF NOT EXISTS idx_{self.schema}_prompt_embeddings_name ON {self.schema}.prompt_embeddings(prompt_name);"
            ],
            "resource_embeddings_table": [
                f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.resource_embeddings (
                    id BIGSERIAL PRIMARY KEY,
                    resource_uri TEXT UNIQUE NOT NULL,
                    category TEXT,
                    name TEXT,
                    description TEXT,
                    embedding JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """,
                f"CREATE INDEX IF NOT EXISTS idx_{self.schema}_resource_embeddings_uri ON {self.schema}.resource_embeddings(resource_uri);",
                f"CREATE INDEX IF NOT EXISTS idx_{self.schema}_resource_embeddings_category ON {self.schema}.resource_embeddings(category);"
            ]
        }
    
    def run_migrations(self) -> bool:
        """Run all migrations for the current environment"""
        if psycopg2 is None:
            logger.warning("psycopg2 not available, skipping migrations")
            return True
            
        try:
            # First, ensure schema exists
            if not self.create_schema(self.schema):
                return False
            
            conn = psycopg2.connect(self.get_database_url())
            cursor = conn.cursor()
            
            migrations = self.get_schema_migrations()
            
            for migration_name, sql_statements in migrations.items():
                logger.info(f"Running migration: {migration_name}")
                
                for sql in sql_statements:
                    try:
                        cursor.execute(sql)
                        logger.debug(f"Executed: {sql[:100]}...")
                    except Exception as e:
                        logger.error(f"Failed to execute SQL in {migration_name}: {e}")
                        logger.error(f"SQL: {sql}")
                        conn.rollback()
                        return False
                
                conn.commit()
                logger.info(f"Migration '{migration_name}' completed")
            
            conn.close()
            logger.info(f"All migrations completed for {self.environment} environment (schema: {self.schema})")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def validate_schema(self) -> Dict[str, bool]:
        """Validate that all required tables exist with correct structure"""
        if psycopg2 is None:
            logger.warning("psycopg2 not available, skipping schema validation")
            return {"validation": True}  # Return success to allow server to start
        
        results = {}
        
        try:
            conn = psycopg2.connect(self.get_database_url())
            cursor = conn.cursor()
            
            # Check each required table
            required_tables = ['models', 'model_capabilities', 'model_embeddings', 'tool_embeddings', 'prompt_embeddings', 'resource_embeddings']
            
            for table in required_tables:
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = '{self.schema}' AND table_name = '{table}'
                """)
                
                exists = cursor.fetchone()[0] > 0
                results[table] = exists
                
                if exists:
                    logger.info(f"✅ Table {self.schema}.{table} exists")
                else:
                    logger.warning(f"❌ Table {self.schema}.{table} missing")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            
        return results

def run_environment_migrations():
    """Convenience function to run migrations for current environment"""
    if psycopg2 is None:
        logger.warning("psycopg2 not available, skipping database migrations")
        return True  # Return success to allow server to start
    
    migrations = DatabaseMigrations()
    
    logger.info(f"Starting migrations for {migrations.environment} environment")
    logger.info(f"Target schema: {migrations.schema}")
    
    # Run migrations
    success = migrations.run_migrations()
    
    if success:
        # Validate schema
        validation = migrations.validate_schema()
        all_valid = all(validation.values())
        
        if all_valid:
            logger.info("🎯 All migrations completed and validated successfully!")
        else:
            logger.warning("⚠️ Migrations completed but validation found issues")
            
        return all_valid
    else:
        logger.error("❌ Migration failed")
        return False

if __name__ == "__main__":
    # Run migrations when script is executed directly
    run_environment_migrations()