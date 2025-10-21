"""
Core services for the ISA Model platform

This module contains platform-wide services including:
- IntelligentModelSelector: AI-driven model selection with user feedback
- ServiceRegistry: Managing deployed model services (in separate location)
"""

from .intelligent_model_selector import (
    IntelligentModelSelector,
    get_model_selector
)

__all__ = [
    "IntelligentModelSelector",
    "get_model_selector"
]