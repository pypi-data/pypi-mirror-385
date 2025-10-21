#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Vision服务包
包含所有视觉相关服务模块，包括stacked services
"""

# Vision understanding services
from .base_vision_service import BaseVisionService  
from .openai_vision_service import OpenAIVisionService
from .replicate_vision_service import ReplicateVisionService

# Stacked Vision Services (disabled - files don't exist)
# from .doc_analysis_service import DocAnalysisStackedService
# from .ui_analysis_service import UIAnalysisService

# ISA Vision service
try:
    from .isA_vision_service import ISAVisionService
    ISA_VISION_AVAILABLE = True
except ImportError:
    ISAVisionService = None
    ISA_VISION_AVAILABLE = False

# Optional services - import only if available
try:
    from .ollama_vision_service import OllamaVisionService
    OLLAMA_VISION_AVAILABLE = True
except ImportError:
    OllamaVisionService = None
    OLLAMA_VISION_AVAILABLE = False

# Computer Vision specialized services
try:
    from .vgg16_vision_service import VGG16VisionService
    VGG16_VISION_AVAILABLE = True
except ImportError:
    VGG16VisionService = None
    VGG16_VISION_AVAILABLE = False

try:
    from .blip_vision_service import BLIPVisionService
    BLIP_VISION_AVAILABLE = True
except ImportError:
    BLIPVisionService = None
    BLIP_VISION_AVAILABLE = False

__all__ = [
    "BaseVisionService",
    "OpenAIVisionService", 
    "ReplicateVisionService",
    # "DocAnalysisStackedService",  # Disabled - file doesn't exist
    # "UIAnalysisService"           # Disabled - file doesn't exist
]

if ISA_VISION_AVAILABLE:
    __all__.append("ISAVisionService")

if OLLAMA_VISION_AVAILABLE:
    __all__.append("OllamaVisionService")

if VGG16_VISION_AVAILABLE:
    __all__.append("VGG16VisionService")

if BLIP_VISION_AVAILABLE:
    __all__.append("BLIPVisionService") 