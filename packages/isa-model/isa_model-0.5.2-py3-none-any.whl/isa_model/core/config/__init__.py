"""
ISA Model Core Configuration Management

Centralized configuration system for:
- Environment settings (dev, prod, etc.)
- Provider API keys and settings
- Database configuration and initialization
- Model definitions and capabilities
- Deployment platform settings
"""

from .config_manager import ConfigManager

__all__ = [
    'ConfigManager'
]