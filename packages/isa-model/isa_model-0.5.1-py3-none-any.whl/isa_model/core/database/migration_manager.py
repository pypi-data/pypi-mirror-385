"""
Database Migration Manager

Manages database schema migrations for the ISA Model SDK.
Handles creation, validation, and rollback of database schemas across all modules.
"""

import logging
import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import hashlib
import json

from .direct_db_client import DirectDBClient

logger = logging.getLogger(__name__)

class MigrationManager:
    """
    Database migration manager for ISA Model SDK
    
    Handles schema creation, migration tracking, and rollback operations
    across all modules (training, deployment, evaluation, inference, config).
    """
    
    def __init__(self, db_client: Optional[DirectDBClient] = None):
        """Initialize migration manager"""
        self.db_client = db_client or DirectDBClient()
        self.base_path = Path(__file__).parent.parent.parent
        self.migration_table = "schema_migrations"
        
        # Schema file locations
        self.schema_files = {
            "training": self.base_path / "training" / "storage" / "database_schema.sql",
            "deployment": self.base_path / "deployment" / "storage" / "deployment_schema.sql", 
            "evaluation": self.base_path / "eval" / "storage" / "evaluation_schema.sql",
            "inference": self.base_path / "inference" / "storage" / "inference_schema.sql",
            "configuration": self.base_path / "core" / "storage" / "config_schema.sql"
        }
        
        # Module dependencies (order matters for creation/deletion)
        self.migration_order = [
            "configuration",  # Config first (other modules may depend on it)
            "training",       # Training (independent)
            "deployment",     # Deployment (may reference models from training)
            "evaluation",     # Evaluation (may reference models and deployments)
            "inference"       # Inference (may reference all above)
        ]
    
    async def initialize_migration_tracking(self) -> bool:
        """
        Initialize migration tracking table
        
        Returns:
            bool: True if successful
        """
        try:
            create_migration_table_sql = """
            -- Create migration tracking table
            CREATE TABLE IF NOT EXISTS public.schema_migrations (
                id BIGSERIAL PRIMARY KEY,
                migration_id VARCHAR(255) UNIQUE NOT NULL,
                module_name VARCHAR(100) NOT NULL,
                schema_name VARCHAR(100) NOT NULL,
                version VARCHAR(50) NOT NULL,
                checksum VARCHAR(64) NOT NULL,
                migration_type VARCHAR(20) NOT NULL DEFAULT 'create', -- create, update, rollback
                status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, running, completed, failed
                
                -- Migration content
                sql_content TEXT NOT NULL,
                
                -- Execution details
                started_at TIMESTAMPTZ,
                completed_at TIMESTAMPTZ,
                execution_time_ms DECIMAL(10, 3),
                
                -- Error tracking
                error_message TEXT,
                error_details JSONB,
                
                -- Rollback information
                rollback_sql TEXT,
                can_rollback BOOLEAN DEFAULT true,
                
                -- Metadata
                applied_by VARCHAR(255),
                applied_from VARCHAR(255), -- hostname/container
                git_commit VARCHAR(40),
                
                -- Timestamps
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                
                -- Constraints
                CONSTRAINT valid_migration_type CHECK (migration_type IN ('create', 'update', 'rollback', 'validate')),
                CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped'))
            );
            
            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_schema_migrations_module_name ON public.schema_migrations(module_name);
            CREATE INDEX IF NOT EXISTS idx_schema_migrations_status ON public.schema_migrations(status);
            CREATE INDEX IF NOT EXISTS idx_schema_migrations_created_at ON public.schema_migrations(created_at);
            
            -- Create view for migration status
            CREATE OR REPLACE VIEW public.migration_status AS
            SELECT 
                module_name,
                schema_name,
                version,
                status,
                migration_type,
                completed_at,
                execution_time_ms,
                error_message,
                can_rollback
            FROM public.schema_migrations
            WHERE id IN (
                SELECT MAX(id) 
                FROM public.schema_migrations 
                GROUP BY module_name
            )
            ORDER BY module_name;
            """
            
            result = await self.db_client.execute_sql(create_migration_table_sql)
            if result["success"]:
                logger.info("Migration tracking table initialized successfully")
                return True
            else:
                logger.error(f"Failed to initialize migration tracking: {result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing migration tracking: {e}")
            return False
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate checksum of SQL file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum for {file_path}: {e}")
            return ""
    
    async def check_migration_status(self, module_name: str) -> Dict[str, Any]:
        """
        Check current migration status for a module
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            Dict with migration status information
        """
        try:
            query = """
            SELECT 
                migration_id,
                schema_name,
                version,
                checksum,
                status,
                completed_at,
                error_message,
                can_rollback
            FROM public.schema_migrations 
            WHERE module_name = %s 
            ORDER BY created_at DESC 
            LIMIT 1
            """
            
            result = await self.db_client.execute_query(query, (module_name,))
            
            if result["success"] and result["data"]:
                return {
                    "exists": True,
                    "migration": result["data"][0]
                }
            else:
                return {
                    "exists": False,
                    "migration": None
                }
                
        except Exception as e:
            logger.error(f"Error checking migration status for {module_name}: {e}")
            return {"exists": False, "error": str(e)}
    
    async def needs_migration(self, module_name: str) -> Tuple[bool, str]:
        """
        Check if module needs migration (new or updated schema)
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            Tuple of (needs_migration, reason)
        """
        try:
            schema_file = self.schema_files.get(module_name)
            if not schema_file or not schema_file.exists():
                return False, f"Schema file not found for {module_name}"
            
            current_checksum = self.calculate_file_checksum(schema_file)
            if not current_checksum:
                return False, "Could not calculate file checksum"
            
            status = await self.check_migration_status(module_name)
            
            if not status["exists"]:
                return True, "Module not yet migrated"
            
            last_migration = status["migration"]
            if last_migration["status"] != "completed":
                return True, f"Last migration failed: {last_migration.get('error_message', 'Unknown error')}"
            
            if last_migration["checksum"] != current_checksum:
                return True, "Schema file has been updated"
            
            return False, "Schema is up to date"
            
        except Exception as e:
            logger.error(f"Error checking if {module_name} needs migration: {e}")
            return True, f"Error checking migration status: {e}"
    
    async def apply_migration(self, module_name: str, migration_type: str = "create") -> Dict[str, Any]:
        """
        Apply migration for a specific module
        
        Args:
            module_name: Name of the module to migrate
            migration_type: Type of migration (create, update)
            
        Returns:
            Dict with migration result
        """
        start_time = datetime.now(timezone.utc)
        migration_id = f"{module_name}_{migration_type}_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Get schema file
            schema_file = self.schema_files.get(module_name)
            if not schema_file or not schema_file.exists():
                return {
                    "success": False,
                    "error": f"Schema file not found for {module_name}"
                }
            
            # Read SQL content
            with open(schema_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            checksum = self.calculate_file_checksum(schema_file)
            
            # Record migration start
            insert_migration_sql = """
            INSERT INTO public.schema_migrations 
            (migration_id, module_name, schema_name, version, checksum, migration_type, status, sql_content, started_at, applied_by)
            VALUES (%s, %s, %s, %s, %s, %s, 'running', %s, %s, 'migration_manager')
            """
            
            schema_name = module_name
            version = "1.0.0"  # Could be extracted from schema file or config
            
            await self.db_client.execute_query(insert_migration_sql, (
                migration_id, module_name, schema_name, version, checksum, 
                migration_type, sql_content, start_time
            ))
            
            # Execute the migration
            logger.info(f"Applying {migration_type} migration for {module_name}...")
            migration_result = await self.db_client.execute_sql(sql_content)
            
            end_time = datetime.now(timezone.utc)
            execution_time = (end_time - start_time).total_seconds() * 1000
            
            if migration_result["success"]:
                # Update migration record as completed
                update_sql = """
                UPDATE public.schema_migrations 
                SET status = 'completed', completed_at = %s, execution_time_ms = %s
                WHERE migration_id = %s
                """
                await self.db_client.execute_query(update_sql, (end_time, execution_time, migration_id))
                
                logger.info(f"Migration {migration_id} completed successfully in {execution_time:.2f}ms")
                return {
                    "success": True,
                    "migration_id": migration_id,
                    "execution_time_ms": execution_time
                }
            else:
                # Update migration record as failed
                error_message = migration_result.get("error", "Unknown error")
                update_sql = """
                UPDATE public.schema_migrations 
                SET status = 'failed', completed_at = %s, execution_time_ms = %s, error_message = %s
                WHERE migration_id = %s
                """
                await self.db_client.execute_query(update_sql, (end_time, execution_time, error_message, migration_id))
                
                logger.error(f"Migration {migration_id} failed: {error_message}")
                return {
                    "success": False,
                    "error": error_message,
                    "migration_id": migration_id
                }
                
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error applying migration for {module_name}: {e}")
            
            # Update migration record as failed
            try:
                end_time = datetime.now(timezone.utc)
                execution_time = (end_time - start_time).total_seconds() * 1000
                update_sql = """
                UPDATE public.schema_migrations 
                SET status = 'failed', completed_at = %s, execution_time_ms = %s, error_message = %s
                WHERE migration_id = %s
                """
                await self.db_client.execute_query(update_sql, (end_time, execution_time, error_message, migration_id))
            except:
                pass  # Don't fail on logging failure
            
            return {
                "success": False,
                "error": error_message,
                "migration_id": migration_id
            }
    
    async def migrate_all_modules(self, force: bool = False) -> Dict[str, Any]:
        """
        Migrate all modules in the correct order
        
        Args:
            force: Force migration even if schema appears up to date
            
        Returns:
            Dict with overall migration results
        """
        logger.info("Starting migration of all modules...")
        
        # Initialize migration tracking first
        if not await self.initialize_migration_tracking():
            return {
                "success": False,
                "error": "Failed to initialize migration tracking"
            }
        
        results = {}
        overall_success = True
        
        for module_name in self.migration_order:
            try:
                logger.info(f"Processing module: {module_name}")
                
                # Check if migration is needed
                needs_migration, reason = await self.needs_migration(module_name)
                
                if not needs_migration and not force:
                    logger.info(f"Skipping {module_name}: {reason}")
                    results[module_name] = {
                        "success": True,
                        "skipped": True,
                        "reason": reason
                    }
                    continue
                
                # Apply migration
                migration_result = await self.apply_migration(module_name)
                results[module_name] = migration_result
                
                if not migration_result["success"]:
                    overall_success = False
                    logger.error(f"Migration failed for {module_name}: {migration_result.get('error')}")
                    
                    # Optionally stop on first failure
                    if not force:
                        logger.error("Stopping migration due to failure. Use force=True to continue on errors.")
                        break
                        
            except Exception as e:
                logger.error(f"Unexpected error migrating {module_name}: {e}")
                results[module_name] = {
                    "success": False,
                    "error": str(e)
                }
                overall_success = False
                
                if not force:
                    break
        
        return {
            "success": overall_success,
            "results": results,
            "migrated_modules": [m for m, r in results.items() if r.get("success") and not r.get("skipped")]
        }
    
    async def get_migration_summary(self) -> Dict[str, Any]:
        """Get summary of all migrations"""
        try:
            query = """
            SELECT 
                module_name,
                schema_name,
                version,
                status,
                migration_type,
                completed_at,
                execution_time_ms,
                error_message
            FROM public.migration_status
            ORDER BY module_name
            """
            
            result = await self.db_client.execute_query(query)
            
            if result["success"]:
                return {
                    "success": True,
                    "migrations": result["data"]
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Error getting migration summary: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_all_schemas(self) -> Dict[str, Any]:
        """
        Validate that all schemas are properly created and accessible
        
        Returns:
            Dict with validation results
        """
        logger.info("Validating all database schemas...")
        
        validation_results = {}
        
        # Schema validation queries
        schema_checks = {
            "training": [
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'training'",
                "SELECT COUNT(*) FROM training.training_jobs LIMIT 0"  # Test table access
            ],
            "deployment": [
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'deployment'", 
                "SELECT COUNT(*) FROM deployment.deployment_records LIMIT 0"
            ],
            "evaluation": [
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'evaluation'",
                "SELECT COUNT(*) FROM evaluation.evaluation_tasks LIMIT 0"
            ],
            "inference": [
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'inference'",
                "SELECT COUNT(*) FROM inference.inference_requests LIMIT 0"
            ],
            "configuration": [
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'configuration'",
                "SELECT COUNT(*) FROM configuration.config_records LIMIT 0"
            ]
        }
        
        for module_name, queries in schema_checks.items():
            try:
                module_valid = True
                errors = []
                
                for query in queries:
                    result = await self.db_client.execute_query(query)
                    if not result["success"]:
                        module_valid = False
                        errors.append(f"Query failed: {query} - {result.get('error')}")
                
                validation_results[module_name] = {
                    "valid": module_valid,
                    "errors": errors
                }
                
                if module_valid:
                    logger.info(f"✓ {module_name} schema validation passed")
                else:
                    logger.error(f"✗ {module_name} schema validation failed: {errors}")
                    
            except Exception as e:
                logger.error(f"Error validating {module_name} schema: {e}")
                validation_results[module_name] = {
                    "valid": False,
                    "errors": [str(e)]
                }
        
        overall_valid = all(result["valid"] for result in validation_results.values())
        
        return {
            "success": overall_valid,
            "validation_results": validation_results,
            "all_schemas_valid": overall_valid
        }

# Utility functions

async def run_migrations(force: bool = False) -> Dict[str, Any]:
    """
    Run database migrations for all modules
    
    Args:
        force: Force migration even if schemas appear up to date
        
    Returns:
        Dict with migration results
    """
    migration_manager = MigrationManager()
    return await migration_manager.migrate_all_modules(force=force)

async def validate_database() -> Dict[str, Any]:
    """
    Validate all database schemas
    
    Returns:
        Dict with validation results
    """
    migration_manager = MigrationManager()
    return await migration_manager.validate_all_schemas()

async def get_migration_status() -> Dict[str, Any]:
    """
    Get current migration status for all modules
    
    Returns:
        Dict with migration status
    """
    migration_manager = MigrationManager()
    return await migration_manager.get_migration_summary()

if __name__ == "__main__":
    import sys
    
    async def main():
        if len(sys.argv) > 1 and sys.argv[1] == "validate":
            result = await validate_database()
            print(json.dumps(result, indent=2, default=str))
        elif len(sys.argv) > 1 and sys.argv[1] == "status":
            result = await get_migration_status()
            print(json.dumps(result, indent=2, default=str))
        else:
            force = len(sys.argv) > 1 and sys.argv[1] == "force"
            result = await run_migrations(force=force)
            print(json.dumps(result, indent=2, default=str))
    
    asyncio.run(main())