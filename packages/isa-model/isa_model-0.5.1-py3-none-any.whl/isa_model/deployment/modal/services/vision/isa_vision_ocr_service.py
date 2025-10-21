"""
ISA Vision OCR Service

Specialized service for multilingual OCR using SuryaOCR
Supports 90+ languages with high accuracy text detection and recognition
"""

import modal
import torch
import base64
import io
import numpy as np
from PIL import Image
from typing import Dict, List, Optional, Any
import time
import json
import os
import logging

# Define Modal application
app = modal.App("isa-vision-ocr")

# Download SuryaOCR models
def download_surya_models():
    """Download SuryaOCR models and dependencies"""
    print("= Downloading SuryaOCR models...")
    os.makedirs("/models", exist_ok=True)
    
    try:
        # SuryaOCR will auto-download models on first use
        # Just verify the installation works
        print(" SuryaOCR models will be downloaded on first use")
        
    except Exception as e:
        print(f" SuryaOCR setup warning: {e}")
    
    print(" SuryaOCR setup completed")

# Define Modal container image
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install([
        # Graphics libraries for image processing
        "libgl1-mesa-glx",
        "libglib2.0-0", 
        "libsm6",
        "libxext6",
        "libxrender-dev",
        "libgomp1",
        # Font support for multilingual text
        "fontconfig",
        "fonts-dejavu-core",
        "fonts-liberation",
    ])
    .pip_install([
        # Core AI libraries
        "torch>=2.0.0",
        "torchvision", 
        "transformers>=4.35.0",
        "huggingface_hub",
        "accelerate",
        
        # SuryaOCR specific dependencies
        "surya-ocr>=0.5.0",  # Latest stable version
        
        # Image processing
        "pillow>=10.0.1",
        "opencv-python-headless",
        "numpy>=1.24.3",
        
        # HTTP libraries
        "httpx>=0.26.0",
        "requests",
        
        # Utilities
        "pydantic>=2.0.0",
        "python-dotenv",
    ])
    .run_function(download_surya_models)
    .env({
        "TRANSFORMERS_CACHE": "/models",
        "TORCH_HOME": "/models/torch",
        "SURYA_CACHE": "/models/surya",
        "HF_HOME": "/models",
    })
)

# SuryaOCR Service - Optimized for T4 GPU
@app.cls(
    gpu="T4",          # T4 4GB GPU - cost effective for OCR
    image=image,
    memory=8192,       # 8GB RAM
    timeout=1800,      # 30 minutes
    scaledown_window=60,   # 1 minute idle timeout
    min_containers=0,  # Scale to zero to save costs
    max_containers=20, # Support up to 20 concurrent containers
)
class SuryaOCRService:
    """
    SuryaOCR Multilingual Text Detection and Recognition Service
    
    Provides high-accuracy OCR for 90+ languages
    Optimized for document processing with cost-effective deployment
    """
        
    @modal.enter()
    def load_models(self):
        """Load SuryaOCR models on container startup"""
        print("= Loading SuryaOCR models...")
        start_time = time.time()
        
        # Initialize instance variables
        self.models_loaded = False
        self.logger = logging.getLogger(__name__)
        self.request_count = 0
        self.total_processing_time = 0.0
        
        try:
            # Import SuryaOCR components - correct API
            from surya.recognition import RecognitionPredictor
            from surya.detection import DetectionPredictor
            
            print("= Loading SuryaOCR predictors...")
            self.recognition_predictor = RecognitionPredictor()
            self.detection_predictor = DetectionPredictor()
            
            print("= SuryaOCR predictors loaded successfully")
            self.models_loaded = True
            
            load_time = time.time() - start_time
            print(f" SuryaOCR models loaded successfully in {load_time:.2f}s")
            
        except Exception as e:
            print(f"L SuryaOCR model loading failed: {e}")
            import traceback
            traceback.print_exc()
            # Don't raise - allow service to start with degraded functionality
            print(" Service will run with reduced functionality")
    
    @modal.method()
    def extract_text(
        self, 
        image_b64: str, 
        languages: List[str] = ["en"], 
        detection_threshold: float = 0.6
    ) -> Dict[str, Any]:
        """
        Extract text from image using SuryaOCR
        
        Args:
            image_b64: Base64 encoded image
            languages: List of languages to detect (e.g., ["en", "zh", "ja"])
            detection_threshold: Text detection confidence threshold
            
        Returns:
            OCR results with text, bounding boxes, and metadata
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Validate models are loaded
            if not hasattr(self, 'models_loaded') or not self.models_loaded:
                raise RuntimeError("SuryaOCR models not loaded")
            
            # Decode and process image
            image = self._decode_image(image_b64)
            
            # Run SuryaOCR detection and recognition
            text_results = self._run_surya_ocr(image, languages, detection_threshold)
            
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            # Calculate cost (T4 GPU: ~$0.40/hour)
            gpu_cost = (processing_time / 3600) * 0.40
            
            result = {
                'success': True,
                'service': 'isa-vision-ocr',
                'provider': 'ISA',
                'text_results': text_results,
                'text_count': len(text_results),
                'languages': languages,
                'processing_time': processing_time,
                'ocr_method': 'surya-ocr',
                'billing': {
                    'request_id': f"req_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round(gpu_cost, 6),
                    'gpu_type': 'T4'
                },
                'model_info': {
                    'model': 'SuryaOCR Detection + Recognition',
                    'provider': 'ISA',
                    'gpu': 'T4',
                    'languages_supported': 90,
                    'container_id': os.environ.get('MODAL_TASK_ID', 'unknown')
                }
            }
            
            # Output JSON for client parsing
            print("=== JSON_RESULT_START ===")
            print(json.dumps(result, default=str))
            print("=== JSON_RESULT_END ===")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"SuryaOCR extraction failed: {e}")
            error_result = {
                'success': False,
                'service': 'isa-vision-ocr',
                'provider': 'ISA',
                'error': str(e),
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"req_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round((processing_time / 3600) * 0.40, 6),
                    'gpu_type': 'T4'
                }
            }
            
            print("=== JSON_RESULT_START ===")
            print(json.dumps(error_result, default=str))
            print("=== JSON_RESULT_END ===")
            
            return error_result
    
    def _run_surya_ocr(self, image: Image.Image, languages: List[str], threshold: float) -> List[Dict[str, Any]]:
        """Run SuryaOCR detection and recognition"""
        print(f" Running SuryaOCR for languages: {languages}")
        
        try:
            # Run OCR with SuryaOCR using correct API
            predictions = self.recognition_predictor(
                [image], 
                det_predictor=self.detection_predictor
            )
            
            text_results = []
            
            # Process OCR results
            if predictions and len(predictions) > 0:
                prediction = predictions[0]  # First (and only) image
                
                for idx, text_line in enumerate(prediction.text_lines):
                    # Extract bounding box coordinates
                    bbox = text_line.bbox
                    x1, y1, x2, y2 = bbox
                    
                    # Extract text and confidence
                    text_content = text_line.text
                    confidence = text_line.confidence if hasattr(text_line, 'confidence') else 0.9
                    
                    # Skip low-confidence detections
                    if confidence < threshold:
                        continue
                    
                    text_results.append({
                        'id': f'surya_{idx}',
                        'text': text_content,
                        'confidence': float(confidence),
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'center': [
                            int((x1 + x2) // 2),
                            int((y1 + y2) // 2)
                        ],
                        'language': languages[0] if languages else 'auto'  # Primary language
                    })
            
            print(f" SuryaOCR extracted {len(text_results)} text regions")
            return text_results
            
        except Exception as e:
            print(f"L SuryaOCR processing failed: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @modal.method()
    def detect_text_regions(self, image_b64: str, threshold: float = 0.6) -> Dict[str, Any]:
        """
        Detect text regions only (without recognition)
        
        Args:
            image_b64: Base64 encoded image
            threshold: Detection confidence threshold
            
        Returns:
            Text detection results with bounding boxes
        """
        start_time = time.time()
        
        try:
            if not self.det_model or not self.det_processor:
                raise RuntimeError("SuryaOCR detection model not loaded")
            
            image = self._decode_image(image_b64)
            
            from surya.detection import batch_text_detection
            
            # Run text detection only
            line_predictions = batch_text_detection([image], self.det_model, self.det_processor)
            
            text_regions = []
            if line_predictions and len(line_predictions) > 0:
                prediction = line_predictions[0]
                
                for idx, text_line in enumerate(prediction.bboxes):
                    bbox = text_line.bbox
                    confidence = text_line.confidence if hasattr(text_line, 'confidence') else 0.9
                    
                    if confidence >= threshold:
                        x1, y1, x2, y2 = bbox
                        text_regions.append({
                            'id': f'region_{idx}',
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(confidence),
                            'center': [int((x1 + x2) // 2), int((y1 + y2) // 2)]
                        })
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'service': 'isa-vision-ocr',
                'function': 'text_detection',
                'text_regions': text_regions,
                'region_count': len(text_regions),
                'processing_time': processing_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'service': 'isa-vision-ocr',
                'function': 'text_detection',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    @modal.method()
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'isa-vision-ocr',
            'provider': 'ISA',
            'models_loaded': {
                'detection': self.det_model is not None,
                'recognition': self.rec_model is not None
            },
            'model_name': 'SuryaOCR Detection + Recognition',
            'languages_supported': 90,
            'timestamp': time.time(),
            'gpu': 'T4',
            'memory_usage': '8GB',
            'request_count': self.request_count
        }
    
    @modal.method()
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get service usage statistics for billing"""
        avg_processing_time = (
            self.total_processing_time / self.request_count 
            if self.request_count > 0 else 0
        )
        total_cost = (self.total_processing_time / 3600) * 0.40
        
        return {
            'service': 'isa-vision-ocr',
            'provider': 'ISA',
            'stats': {
                'total_requests': self.request_count,
                'total_gpu_seconds': round(self.total_processing_time, 3),
                'avg_processing_time': round(avg_processing_time, 3),
                'total_cost_usd': round(total_cost, 6),
                'container_id': os.environ.get('MODAL_TASK_ID', 'unknown')
            }
        }
    
    def _decode_image(self, image_b64: str) -> Image.Image:
        """Decode base64 image"""
        try:
            # Handle data URL format
            if image_b64.startswith('data:image'):
                image_b64 = image_b64.split(',')[1]
            
            # Clean up base64 string
            image_b64 = image_b64.strip().replace('\n', '').replace('\r', '').replace(' ', '')
            
            # Decode base64
            image_data = base64.b64decode(image_b64)
            print(f" Decoded image size: {len(image_data)} bytes")
            
            # Open with PIL
            image = Image.open(io.BytesIO(image_data))
            print(f" Image format: {image.format}, size: {image.size}, mode: {image.mode}")
            
            return image.convert('RGB')
            
        except Exception as e:
            print(f"L Image decode error: {e}")
            raise e

# Auto-registration function
@app.function()
async def register_service():
    """Auto-register this service in the model registry"""
    try:
        import sys
        from pathlib import Path
        
        # Add project root to path for imports
        project_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        try:
            from isa_model.core.models.model_manager import ModelManager
            from isa_model.core.models.model_repo import ModelType, ModelCapability
        except ImportError:
            print(" Could not import model manager - registration skipped")
            return {"success": False, "error": "Model manager not available"}
        
        # Use ModelManager to register this service
        model_manager = ModelManager()
        
        # Register the ISA service in the registry
        success = model_manager.registry.register_model(
            model_id="isa-surya-ocr-service",
            model_type=ModelType.VISION,
            capabilities=[
                ModelCapability.OCR,
                ModelCapability.TEXT_DETECTION,
                ModelCapability.IMAGE_ANALYSIS
            ],
            metadata={
                "description": "ISA SuryaOCR multilingual text extraction service",
                "provider": "ISA",
                "service_name": "isa-vision-ocr",
                "service_type": "modal",
                "deployment_type": "modal_gpu",
                "endpoint": "https://isa-vision-ocr.modal.run",
                "underlying_model": "SuryaOCR Detection + Recognition",
                "gpu_requirement": "T4",
                "memory_mb": 8192,
                "max_containers": 20,
                "cost_per_hour_usd": 0.40,
                "auto_registered": True,
                "registered_by": "isa_vision_ocr_service.py",
                "is_service": True,
                "optimized": True,
                "billing_enabled": True,
                "languages_supported": 90,
                "multilingual": True
            }
        )
        
        if success:
            print(" OCR service auto-registered successfully")
        else:
            print(" OCR service registration failed")
            
        return {"success": success}
        
    except Exception as e:
        print(f"L Auto-registration error: {e}")
        return {"success": False, "error": str(e)}

# Deployment script
@app.function()
def deploy_info():
    """Deployment information"""
    return {
        "service": "ISA Vision OCR Detection",
        "model": "SuryaOCR Detection + Recognition (90+ languages)",
        "gpu_requirement": "T4",
        "memory_requirement": "8GB",
        "deploy_command": "modal deploy isa_vision_ocr_service.py"
    }

# Quick deployment function
@app.function()
def deploy_service():
    """Deploy this service instantly"""
    import subprocess
    import os
    
    print("= Deploying ISA Vision OCR Service...")
    try:
        # Get the current file path
        current_file = __file__
        
        # Run modal deploy command
        result = subprocess.run(
            ["modal", "deploy", current_file],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(" Deployment completed successfully!")
        print(f"= Output: {result.stdout}")
        return {"success": True, "output": result.stdout}
        
    except subprocess.CalledProcessError as e:
        print(f"L Deployment failed: {e}")
        print(f"= Error: {e.stderr}")
        return {"success": False, "error": str(e), "stderr": e.stderr}

if __name__ == "__main__":
    print("= ISA Vision OCR Service - Modal Deployment")
    print("Deploy with: modal deploy isa_vision_ocr_service.py")
    print("Or call: modal run isa_vision_ocr_service.py::deploy_service")
    print("Note: Uses SuryaOCR for 90+ language support")
    print("\n= Service will auto-register in model registry upon deployment")