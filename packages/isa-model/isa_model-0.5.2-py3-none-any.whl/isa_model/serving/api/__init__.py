"""
API Service Module

FastAPI-based API service for model inference
"""

from .fastapi_server import create_app
from .schemas import *

__all__ = ["create_app"]