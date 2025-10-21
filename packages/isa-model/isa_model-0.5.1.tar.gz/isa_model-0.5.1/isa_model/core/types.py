"""
Unified Type Definitions for ISA Model SDK

This module contains all the common enums and type definitions used across
the entire SDK to ensure consistency and avoid duplication.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

# ===== MODEL TYPES =====

class ModelType(str, Enum):
    """Types of models in the system"""
    LLM = "llm"
    EMBEDDING = "embedding"
    RERANK = "rerank"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    VISION = "vision"
    IMAGE_GEN = "image_gen"  # Added for consistency

class ModelCapability(str, Enum):
    """Model capabilities"""
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    EMBEDDING = "embedding"
    RERANKING = "reranking"
    REASONING = "reasoning"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_REALTIME = "audio_realtime"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    CONVERSATION = "conversation"
    IMAGE_UNDERSTANDING = "image_understanding"
    UI_DETECTION = "ui_detection"
    OCR = "ocr"
    TABLE_DETECTION = "table_detection"
    TABLE_STRUCTURE_RECOGNITION = "table_structure_recognition"

class ModelStage(str, Enum):
    """Model lifecycle stages"""
    REGISTERED = "registered"
    TRAINING = "training"
    EVALUATION = "evaluation"
    DEPLOYMENT = "deployment"
    PRODUCTION = "production"
    RETIRED = "retired"

# ===== SERVICE TYPES =====

class ServiceType(str, Enum):
    """Types of services available in the platform"""
    LLM = "llm"
    EMBEDDING = "embedding"
    VISION = "vision"
    AUDIO = "audio"
    AUDIO_STT = "audio_stt"
    AUDIO_TTS = "audio_tts"
    AUDIO_REALTIME = "audio_realtime"
    IMAGE_GEN = "image_gen"

class ServiceStatus(str, Enum):
    """Service deployment and health status"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STOPPED = "stopped"

class DeploymentPlatform(str, Enum):
    """Supported deployment platforms for self-owned services only"""
    MODAL = "modal"
    KUBERNETES = "kubernetes"
    RUNPOD = "runpod"
    YYDS = "yyds"
    OLLAMA = "ollama"  # Local deployment

# ===== OPERATION TYPES =====

class ModelOperationType(str, Enum):
    """Types of model operations that incur costs"""
    TRAINING = "training"
    EVALUATION = "evaluation"
    DEPLOYMENT = "deployment"
    INFERENCE = "inference"
    STORAGE = "storage"

class InferenceOperationType(str, Enum):
    """Types of inference operations"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE_GENERATION = "image_generation"
    VISION_ANALYSIS = "vision_analysis"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_GENERATION = "audio_generation"

# ===== ROUTING AND LOAD BALANCING =====

class RoutingStrategy(str, Enum):
    """Routing strategies for distributing requests among model replicas"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RESPONSE_TIME = "response_time"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"
    DYNAMIC_LOAD_BALANCING = "dynamic_load_balancing"

# ===== EVALUATION AND TRAINING =====

class MetricType(str, Enum):
    """Types of evaluation metrics"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    BLEU = "bleu"
    ROUGE = "rouge"
    PERPLEXITY = "perplexity"
    BERTSCORE = "bertscore"
    SEMANTIC_SIMILARITY = "semantic_similarity"

class AnnotationType(str, Enum):
    """Types of training data annotations"""
    TEXT_CLASSIFICATION = "text_classification"
    NAMED_ENTITY_RECOGNITION = "named_entity_recognition"
    QUESTION_ANSWERING = "question_answering"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    SEMANTIC_SEGMENTATION = "semantic_segmentation"

class DatasetType(str, Enum):
    """Types of training datasets"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"

class DatasetStatus(str, Enum):
    """Status of training datasets"""
    CREATED = "created"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"

class ExperimentType(str, Enum):
    """Types of ML experiments"""
    TRAINING = "training"
    EVALUATION = "evaluation"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    MODEL_COMPARISON = "model_comparison"

# ===== STACKED SERVICES =====

class LayerType(Enum):
    """Types of layers in stacked services"""
    INPUT_PROCESSING = "input_processing"
    MODEL_INFERENCE = "model_inference"
    OUTPUT_PROCESSING = "output_processing"
    VALIDATION = "validation"
    CACHING = "caching"

class WorkflowType(Enum):
    """Types of workflows"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"

# ===== PROVIDER TYPES =====

class Provider(str, Enum):
    """AI service providers"""
    OPENAI = "openai"
    REPLICATE = "replicate"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    YYDS = "yyds"
    CEREBRAS = "cerebras"
    MODAL = "modal"

# ===== DATA CLASSES =====

@dataclass
class HealthMetrics:
    """Service health metrics"""
    is_healthy: bool
    response_time_ms: Optional[int] = None
    status_code: Optional[int] = None
    cpu_usage_percent: Optional[float] = None
    memory_usage_mb: Optional[int] = None
    gpu_usage_percent: Optional[float] = None
    error_message: Optional[str] = None
    checked_at: Optional[datetime] = None

@dataclass
class ServiceMetrics:
    """Service runtime metrics"""
    request_count: int = 0
    total_processing_time_ms: int = 0
    error_count: int = 0
    total_cost_usd: float = 0.0
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None

@dataclass
class ResourceRequirements:
    """Service resource requirements"""
    gpu_type: Optional[str] = None
    memory_mb: Optional[int] = None
    cpu_cores: Optional[int] = None
    storage_gb: Optional[int] = None
    min_replicas: int = 0
    max_replicas: int = 1

@dataclass
class ModelInfo:
    """Model information structure"""
    model_id: str
    model_type: ModelType
    capabilities: List[ModelCapability]
    stage: ModelStage
    provider: str
    provider_model_name: str
    metadata: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class UsageData:
    """Usage data for billing tracking"""
    operation_type: ModelOperationType
    inference_operation: Optional[InferenceOperationType] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    input_units: Optional[float] = None
    output_units: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

# ===== TYPE ALIASES =====

# Common type aliases for better readability
ModelID = str
ServiceID = str
DeploymentID = str
ProviderName = str
ModelName = str
EndpointURL = str
ConfigDict = Dict[str, Any]
MetadataDict = Dict[str, Any]

# ===== BACKWARD COMPATIBILITY =====

# Legacy aliases for backward compatibility during migration
# These should be removed once all modules are updated

# From inference/billing_tracker.py
class LegacyServiceType(Enum):
    """Legacy service type - use ServiceType instead"""
    LLM = "llm"
    EMBEDDING = "embedding"
    VISION = "vision"
    IMAGE_GENERATION = "image_generation"
    AUDIO_STT = "audio_stt"
    AUDIO_TTS = "audio_tts"

# Migration mapping
LEGACY_SERVICE_TYPE_MAPPING = {
    LegacyServiceType.LLM: ServiceType.LLM,
    LegacyServiceType.EMBEDDING: ServiceType.EMBEDDING,
    LegacyServiceType.VISION: ServiceType.VISION,
    LegacyServiceType.IMAGE_GENERATION: ServiceType.IMAGE_GEN,
    LegacyServiceType.AUDIO_STT: ServiceType.AUDIO,
    LegacyServiceType.AUDIO_TTS: ServiceType.AUDIO,
}

def migrate_legacy_service_type(legacy_type: Union[LegacyServiceType, str]) -> ServiceType:
    """Migrate legacy service type to new unified type"""
    if isinstance(legacy_type, str):
        # Try to find matching legacy enum
        for legacy_enum in LegacyServiceType:
            if legacy_enum.value == legacy_type:
                return LEGACY_SERVICE_TYPE_MAPPING[legacy_enum]
        # Fallback to direct mapping
        return ServiceType(legacy_type)
    else:
        return LEGACY_SERVICE_TYPE_MAPPING.get(legacy_type, ServiceType.LLM)