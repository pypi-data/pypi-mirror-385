"""
Vision API Routes

Endpoints for general vision tasks (placeholder)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

@router.get("/")
async def vision_info():
    """Vision service information"""
    return {
        "service": "vision",
        "status": "placeholder",
        "description": "General vision processing endpoints"
    }