"""
Centralized Logging Configuration with Loki Integration for ISA Model

This module provides centralized application logging with Loki support,
complementing the existing InfluxDB inference logging system.

Architecture:
- Loki: General application logs (INFO, WARNING, ERROR, DEBUG)
- InfluxDB: Inference metrics and performance data (tokens, costs, timing)

Usage:
    from isa_model.core.logging import app_logger, api_logger

    app_logger.info("Service starting...")
    api_logger.error(f"Request failed: {error}", exc_info=True)
"""

import logging
import sys
import os
from typing import Optional


def setup_logger(
    name: str,
    level: Optional[str] = None,
    format_str: Optional[str] = None
) -> logging.Logger:
    """
    Setup logger with centralized Loki integration

    Args:
        name: Logger name (e.g., "ISAModel.API")
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_str: Log format string (optional)

    Returns:
        Configured logger instance

    Example:
        >>> from isa_model.core.logging import setup_logger
        >>> my_logger = setup_logger("ISAModel.MyModule")
        >>> my_logger.info("Processing started")
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Get configuration from environment
    log_level_env = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format_env = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    from ..config.config_manager import ConfigManager
    config_manager = ConfigManager()
    # Use Consul discovery for Loki URL with fallback
    loki_url = os.getenv("LOKI_URL", config_manager.get_loki_url())
    loki_enabled = os.getenv("LOKI_ENABLED", "true").lower() == "true"

    # Set log level
    final_level = (level or log_level_env).upper()
    logger.setLevel(getattr(logging, final_level, logging.INFO))

    # Disable propagation to prevent duplicate logs
    logger.propagate = False

    # Log format
    formatter = logging.Formatter(format_str or log_format_env)

    # 1. Console Handler (for local development and debugging)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Loki Handler (for centralized logging)
    if loki_enabled:
        try:
            from logging_loki import LokiHandler

            # Extract service name and logger component
            # e.g., "ISAModel.API" -> service="isa_model", logger="API"
            service_name = "isa_model"
            logger_component = name.replace("ISAModel.", "").replace("ISAModel", "main")

            # Labels for Loki (used for filtering and searching)
            # Use service_name to match other services (mcp, agent, etc.)
            loki_labels = {
                "service_name": "model",  # Use "model" to match service naming convention
                "logger": logger_component,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "job": "isa_model_service"
            }

            # Create Loki handler
            loki_handler = LokiHandler(
                url=f"{loki_url}/loki/api/v1/push",
                tags=loki_labels,
                version="1",
            )

            # Only send INFO and above to Loki (reduce network traffic)
            loki_handler.setLevel(logging.INFO)

            logger.addHandler(loki_handler)

        except ImportError:
            # Silently fall back to console-only logging during initialization
            pass
        except Exception as e:
            # Loki unavailable - silently fall back to console
            pass

    return logger


# Create application loggers
# Main application logger
app_logger = setup_logger("ISAModel")

# API/Server logger
api_logger = setup_logger("ISAModel.API")

# Client logger
client_logger = setup_logger("ISAModel.Client")

# Inference logger (application-level, not metrics)
inference_logger = setup_logger("ISAModel.Inference")

# Training logger
training_logger = setup_logger("ISAModel.Training")

# Evaluation logger
eval_logger = setup_logger("ISAModel.Evaluation")

# Database logger
db_logger = setup_logger("ISAModel.Database")

# Deployment logger
deployment_logger = setup_logger("ISAModel.Deployment")

# Model manager logger
model_logger = setup_logger("ISAModel.Models")


# Export all loggers
__all__ = [
    'setup_logger',
    'app_logger',
    'api_logger',
    'client_logger',
    'inference_logger',
    'training_logger',
    'eval_logger',
    'db_logger',
    'deployment_logger',
    'model_logger',
]
