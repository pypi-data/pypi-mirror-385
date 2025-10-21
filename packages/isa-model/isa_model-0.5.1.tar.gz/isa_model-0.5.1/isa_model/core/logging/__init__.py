"""
Logging module for ISA Model

Provides comprehensive logging capabilities including:
- Loki-based centralized application logging (via loki_logger)
- Basic inference logging with request tracking

Architecture:
- Loki: General application logs (INFO, WARNING, ERROR, DEBUG)
- Basic logging: Simple request tracking and basic metrics
"""

# Basic inference logging (no external dependencies)
import uuid
import logging
from .inference_logger import InferenceLogger

def generate_request_id():
    """Generate unique request ID for tracking"""
    return str(uuid.uuid4())

def get_inference_logger():
    """Get enhanced inference logger with compatibility methods"""
    base_logger = logging.getLogger("isa_model.inference")
    return InferenceLogger(base_logger)

# Loki centralized application logging
from .loki_logger import (
    setup_logger,
    app_logger,
    api_logger,
    client_logger,
    inference_logger,
    training_logger,
    eval_logger,
    db_logger,
    deployment_logger,
    model_logger,
)

__all__ = [
    # Basic inference logging
    'get_inference_logger',
    'generate_request_id',

    # Loki application logging
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