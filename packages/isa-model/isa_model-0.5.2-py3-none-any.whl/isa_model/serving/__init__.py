"""
ISA Model Serving Module

Core module for model inference services, including:
- API service framework
- Model worker processes
- Caching layer
- Performance optimization

Difference from inference module:
- inference: Client-side inference, calling third-party APIs
- serving: Self-hosted model services, providing API services
"""

__version__ = "0.1.0"

from .api.fastapi_server import create_app

__all__ = ["create_app"]