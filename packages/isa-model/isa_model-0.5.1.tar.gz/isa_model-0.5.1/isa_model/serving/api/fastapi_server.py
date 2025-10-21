"""
FastAPI Server for ISA Model Serving

Main FastAPI application that serves model inference endpoints
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
import time
import logging
import os
from typing import Dict, Any, Optional

from .routes import health, inference, deployments, logs, analytics, settings, inference_monitoring, webhooks, tenants  # Using inference.py (direct AIFactory access)
from .middleware.request_logger import RequestLoggerMiddleware
from .middleware.security import setup_security_middleware, check_redis_health
from .middleware.tenant_context import TenantContextMiddleware
from .startup import run_startup_initialization
from ...core.logging import api_logger, setup_logger

logger = api_logger  # Use Loki-configured logger instead of standard logging

def configure_logging():
    """Configure logging based on environment variables

    Note: Loki integration is handled automatically by isa_model.core.logging.setup_logger
    This function only sets log levels for existing loggers.
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    verbose_logging = os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true'

    # Set log level
    level = getattr(logging, log_level, logging.INFO)

    # Note: Don't call logging.basicConfig() here as it conflicts with Loki handlers
    # The Loki logger (api_logger) is already configured with proper handlers
    
    # Set uvicorn logger level to match
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(level)
    
    # Set app logger level
    app_logger = logging.getLogger("isa_model")
    app_logger.setLevel(level)
    
    # Suppress verbose third-party library logs
    # HTTP libraries - only show WARNING and above
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
    logging.getLogger("httpcore.connection").setLevel(logging.WARNING)
    
    # Database and ORM libraries
    logging.getLogger("supabase").setLevel(logging.WARNING)
    logging.getLogger("postgrest").setLevel(logging.WARNING)
    
    # AI/ML libraries
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("google.cloud").setLevel(logging.WARNING)
    logging.getLogger("google.generativeai").setLevel(logging.WARNING)
    
    # Other verbose libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    
    # Reduce startup debug logs
    if not verbose_logging:
        # Reduce startup initialization debug logs
        startup_logger = logging.getLogger("isa_model.serving.api.startup")
        startup_logger.setLevel(logging.WARNING)
        
        # Reduce model registry debug logs
        model_logger = logging.getLogger("isa_model.core.models.model_repo")
        model_logger.setLevel(logging.WARNING)
        
        # Reduce intelligent selector debug logs
        selector_logger = logging.getLogger("isa_model.core.services.intelligent_model_selector")
        selector_logger.setLevel(logging.WARNING)
        
        # Training module removed - logger configuration no longer needed
        
        # Reduce knowledge base logs
        kb_logger = logging.getLogger("isa_model.core.knowledge_base")
        kb_logger.setLevel(logging.WARNING)
        
        # Reduce database migration logs
        migration_logger = logging.getLogger("isa_model.core.database.migrations")
        migration_logger.setLevel(logging.WARNING)
        
        # Reduce AI factory logs
        ai_factory_logger = logging.getLogger("isa_model.inference.ai_factory")
        ai_factory_logger.setLevel(logging.WARNING)
        
        # Reduce embedding service logs
        embed_logger = logging.getLogger("isa_model.inference.services.embedding")
        embed_logger.setLevel(logging.WARNING)
        
        # Reduce config manager logs
        config_logger = logging.getLogger("isa_model.core.config")
        config_logger.setLevel(logging.WARNING)
        
        # Reduce core integration logs
        core_logger = logging.getLogger("isa_model.core")
        core_logger.setLevel(logging.WARNING)
    
    logger.info(f"Logging configured - Level: {log_level}, Verbose: {verbose_logging}")

def create_app(config: Dict[str, Any] = None) -> FastAPI:
    """
    Create and configure FastAPI application
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured FastAPI application
    """
    # Configure logging first
    configure_logging()
    
    app = FastAPI(
        title="ISA Model Serving API",
        description="High-performance model inference API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Setup comprehensive security middleware
    # This includes CORS, rate limiting, security headers, request validation
    setup_security_middleware(app)
    
    # Add tenant context middleware (before request logger)
    app.add_middleware(TenantContextMiddleware)
    
    # Add custom middleware
    app.add_middleware(RequestLoggerMiddleware)
    
    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if config and config.get("debug") else "An error occurred"
            }
        )
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    
    # MAIN INFERENCE API - Direct AIFactory access (no ISAModelClient middleman)
    app.include_router(inference.router, prefix="/api/v1", tags=["inference-api"])
    
    # DEPLOYMENTS API - Model deployment management
    app.include_router(deployments.router, prefix="/api/v1/deployments", tags=["deployments"])
    
    # LOGS API - Log management and streaming
    app.include_router(logs.router, prefix="/api/v1/logs", tags=["logs"])
    
    # ANALYTICS API - Usage analytics and reporting
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
    
    # SETTINGS API - Configuration and API key management
    app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])
    
    # EVALUATIONS API - Temporarily disabled for staging optimization
    # app.include_router(evaluations.router, prefix="/api/v1/evaluations", tags=["evaluations"])
    
    # INFERENCE MONITORING API - InfluxDB-based inference monitoring and analytics
    app.include_router(inference_monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
    
    # TRAINING API - Disabled for staging optimization
    # app.include_router(training.router, prefix="/api/v1/training", tags=["training"])
    
    # WEBHOOKS API - Webhook management and notifications
    app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
    
    # TENANTS API - Multi-tenancy and organization management
    app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["tenants"])
    
    # ANNOTATION API - Temporarily disabled for staging optimization
    # app.include_router(annotation.router, prefix="/api/v1/annotations", tags=["annotations"])
    
    # CONFIG API - Configuration management
    # app.include_router(config.router, prefix="/api/v1/config", tags=["config"])  # Temporarily disabled
    
    # Mount static files
    static_path = os.path.join(os.path.dirname(__file__), "../static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
        
        # Serve management dashboard at /admin
        @app.get("/admin")
        async def admin_dashboard():
            from fastapi.responses import FileResponse
            index_path = os.path.join(static_path, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
            return {"error": "Management dashboard not found"}
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": "isa-model-serving",
            "version": "1.0.0",
            "status": "running",
            "timestamp": time.time(),
            "admin_url": "/admin"
        }
    
    # Add startup event handler
    @app.on_event("startup")
    async def startup_event():
        logger.info("🚀 Starting application startup initialization...")
        try:
            await run_startup_initialization()
            logger.info("✅ Application startup completed successfully")
        except Exception as e:
            logger.error(f"❌ Application startup failed: {e}")
            logger.error("⚠️ Server will continue but may have reduced functionality")
            # Store startup failure state for health checks
            app.state.startup_failed = True
            app.state.startup_error = str(e)
            # Continue running to allow debugging and partial functionality
    
    # Add shutdown event handler
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("🧹 Starting application shutdown cleanup...")
        try:
            # Close database connections
            try:
                from .dependencies.database import close_database_pool
                await close_database_pool()
                logger.info("✅ Database connections closed")
            except Exception as e:
                logger.error(f"❌ Error closing database connections: {e}")
            
            # Clean up AI factory and services
            try:
                from ...inference.ai_factory import AIFactory
                factory = AIFactory.get_instance()
                await factory.cleanup()
                logger.info("✅ AI Factory cleaned up")
            except Exception as e:
                logger.error(f"❌ Error cleaning up AI Factory: {e}")
            
            # Clean up startup initializer resources
            try:
                from .startup import startup_initializer
                await startup_initializer.cleanup()
                logger.info("✅ Startup resources cleaned up")
            except Exception as e:
                logger.error(f"❌ Error cleaning up startup resources: {e}")
            
            logger.info("✅ Application shutdown completed successfully")
        except Exception as e:
            logger.error(f"❌ Error during application shutdown: {e}")
    
    return app

# Create default app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    import os
    import signal
    
    port = int(os.getenv("PORT", 8082))
    
    # Configure uvicorn for graceful shutdown
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        access_log=True,
        loop="asyncio",
        # Graceful shutdown configuration
        timeout_keep_alive=30,  # Keep connections alive for 30 seconds
        timeout_graceful_shutdown=30,  # 30 second graceful shutdown timeout
    )
    
    server = uvicorn.Server(config)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        server.should_exit = True
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    finally:
        logger.info("Server shutdown complete")