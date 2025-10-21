"""
Base definitions for the Inference layer.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Any, Union, TypeVar, Generic

T = TypeVar('T')


class ModelType(str, Enum):
    """Types of AI models supported by the framework."""
    LLM = "llm"
    EMBEDDING = "embedding"
    VISION = "vision"
    AUDIO = "audio"
    OCR = "ocr"
    TTS = "tts"
    RERANK = "rerank"
    MULTIMODAL = "multimodal"


class Capability(str, Enum):
    """Capabilities supported by models."""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE_GENERATION = "image_generation"
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    OCR = "ocr"
    RERANKING = "reranking"
    MULTIMODAL_UNDERSTANDING = "multimodal_understanding"


class RoutingStrategy(str, Enum):
    """Routing strategies for distributing requests among model replicas."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RESPONSE_TIME = "response_time"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"
    DYNAMIC_LOAD_BALANCING = "dynamic_load_balancing" 