"""
Inference module for isA_Model

File: isa_model/inference/__init__.py
This module provides the main inference components for the IsA Model system.
"""

from .ai_factory import AIFactory
from .base import ModelType, Capability, RoutingStrategy

# Import legacy model services (migrated from isA_MCP)
try:
    from .legacy_services import (
        ModelTrainingService,
        TrainingConfig,
        TrainingResult,
        ModelEvaluationService,
        EvaluationResult,
        ModelServingService,
        ServingResult,
        ModelService,
        ModelConfig,
        ModelResult
    )
    LEGACY_SERVICES_AVAILABLE = True
except ImportError:
    LEGACY_SERVICES_AVAILABLE = False
    ModelTrainingService = None
    TrainingConfig = None
    TrainingResult = None
    ModelEvaluationService = None
    EvaluationResult = None
    ModelServingService = None
    ServingResult = None
    ModelService = None
    ModelConfig = None
    ModelResult = None

__all__ = [
    "AIFactory", 
    "ModelType", 
    "Capability", 
    "RoutingStrategy",
    
    # Legacy model services (migrated from isA_MCP)
    'ModelTrainingService',
    'TrainingConfig',
    'TrainingResult',
    'ModelEvaluationService',
    'EvaluationResult',
    'ModelServingService',
    'ServingResult',
    'ModelService',
    'ModelConfig',
    'ModelResult',
    'LEGACY_SERVICES_AVAILABLE'
] 