"""
UI Analysis API Schemas

Pydantic models for UI analysis endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import time

class UIElement(BaseModel):
    """UI element detection result"""
    id: str = Field(..., description="Unique element identifier")
    type: str = Field(..., description="Element type (textbox, button, etc.)")
    content: str = Field(..., description="Element text content or description")
    center: List[int] = Field(..., description="Center coordinates [x, y]")
    bbox: List[int] = Field(..., description="Bounding box [x1, y1, x2, y2]")
    confidence: float = Field(..., description="Detection confidence score")
    interactable: bool = Field(True, description="Whether element is interactable")

class ActionStep(BaseModel):
    """Single action step in automation plan"""
    step: int = Field(..., description="Step number")
    action: str = Field(..., description="Action type (click, type, scroll)")
    target_coordinates: List[int] = Field(..., description="Target coordinates [x, y]")
    actual_coordinates: List[int] = Field(..., description="Actual coordinates [x, y]")
    description: str = Field(..., description="Human-readable action description")
    confidence: float = Field(0.9, description="Action confidence score")
    text: Optional[str] = Field(None, description="Text to type (for type actions)")

class ActionPlan(BaseModel):
    """Complete action plan for UI automation"""
    steps: List[ActionStep] = Field(..., description="List of action steps")
    success_probability: float = Field(0.9, description="Overall success probability")
    estimated_duration: float = Field(5.0, description="Estimated execution time in seconds")

class AutomationReadiness(BaseModel):
    """Automation readiness assessment"""
    ready: bool = Field(..., description="Whether automation is ready")
    confidence: float = Field(..., description="Automation confidence score")
    page_type: str = Field(..., description="Detected page type")
    steps_count: int = Field(..., description="Number of automation steps")
    estimated_success_rate: float = Field(0.9, description="Estimated success rate")

class UIAnalysisRequest(BaseModel):
    """UI analysis request"""
    image_b64: str = Field(..., description="Base64 encoded image")
    task_type: str = Field("search", description="Analysis task type")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "image_b64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                "task_type": "search"
            }
        }
    }

class UIAnalysisResponse(BaseModel):
    """UI analysis response"""
    success: bool = Field(..., description="Analysis success status")
    service: str = Field("ui_analysis", description="Service identifier")
    total_execution_time: float = Field(..., description="Total processing time in seconds")
    ui_elements: List[UIElement] = Field(..., description="Detected UI elements")
    action_plan: ActionPlan = Field(..., description="Generated action plan")
    automation_ready: AutomationReadiness = Field(..., description="Automation readiness")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: float = Field(default_factory=time.time, description="Response timestamp")

class UIDetectionResponse(BaseModel):
    """UI elements detection only response"""
    success: bool = Field(..., description="Detection success status")
    processing_time: float = Field(..., description="Processing time in seconds")
    ui_elements: List[UIElement] = Field(..., description="Detected UI elements")
    element_count: int = Field(..., description="Number of detected elements")
    task_type: str = Field(..., description="Analysis task type")
    detection_method: str = Field("omniparser", description="Detection method used")
    timestamp: float = Field(default_factory=time.time, description="Response timestamp")