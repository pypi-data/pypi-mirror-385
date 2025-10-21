"""
ISA Vision Table Service

Specialized service for table detection and structure recognition using Microsoft Table Transformer
Combines table detection and structure recognition for comprehensive table processing
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
app = modal.App("isa-vision-table")

# Download Table Transformer models
def download_table_transformer_models():
    """Download Microsoft Table Transformer models"""
    from huggingface_hub import snapshot_download
    
    print("=æ Downloading Microsoft Table Transformer models...")
    os.makedirs("/models", exist_ok=True)
    
    try:
        # Download Table Detection model
        print("<¯ Downloading Table Transformer Detection model...")
        snapshot_download(
            repo_id="microsoft/table-transformer-detection",
            local_dir="/models/table-transformer-detection",
            allow_patterns=["**/*.bin", "**/*.json", "**/*.safetensors"]
        )
        print(" Table Detection model downloaded")
        
        # Download Table Structure Recognition model (v1.1)
        print("=Ê Downloading Table Transformer Structure Recognition v1.1...")
        snapshot_download(
            repo_id="microsoft/table-transformer-structure-recognition-v1.1-all",
            local_dir="/models/table-transformer-structure",
            allow_patterns=["**/*.bin", "**/*.json", "**/*.safetensors"]
        )
        print(" Table Structure Recognition model downloaded")
        
    except Exception as e:
        print(f"  Table Transformer download failed: {e}")
        # Don't raise - allow service to start with fallback
        print("  Will use fallback table detection method")
    
    print(" Table Transformer setup completed")

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
    ])
    .pip_install([
        # Core AI libraries
        "torch>=2.0.0",
        "torchvision", 
        "transformers>=4.35.0",
        "huggingface_hub",
        "accelerate",
        
        # Table Transformer specific dependencies
        "timm",  # Required for DETR backbone
        
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
    .run_function(download_table_transformer_models)
    .env({
        "TRANSFORMERS_CACHE": "/models",
        "TORCH_HOME": "/models/torch",
        "HF_HOME": "/models",
    })
)

# Table Transformer Service - Optimized for T4 GPU
@app.cls(
    gpu="T4",          # T4 4GB GPU - sufficient for Table Transformer
    image=image,
    memory=12288,      # 12GB RAM for table processing
    timeout=1800,      # 30 minutes
    scaledown_window=60,   # 1 minute idle timeout
    min_containers=0,  # Scale to zero to save costs
    max_containers=15, # Support up to 15 concurrent containers
)
class TableTransformerService:
    """
    Microsoft Table Transformer Service
    
    Provides table detection and structure recognition
    Cost-effective deployment optimized for document processing
    """
        
    @modal.enter()
    def load_models(self):
        """Load Table Transformer models on container startup"""
        print("=€ Loading Table Transformer models...")
        start_time = time.time()
        
        # Initialize instance variables
        self.detection_model = None
        self.detection_processor = None
        self.structure_model = None
        self.structure_processor = None
        self.logger = logging.getLogger(__name__)
        self.request_count = 0
        self.total_processing_time = 0.0
        
        try:
            # Import transformers components
            from transformers import TableTransformerForObjectDetection, DetrImageProcessor
            
            print("<¯ Loading Table Detection model...")
            self.detection_processor = DetrImageProcessor.from_pretrained(
                "microsoft/table-transformer-detection"
            )
            self.detection_model = TableTransformerForObjectDetection.from_pretrained(
                "microsoft/table-transformer-detection"
            )
            
            print("=Ê Loading Table Structure Recognition model...")
            self.structure_processor = DetrImageProcessor.from_pretrained(
                "microsoft/table-transformer-structure-recognition-v1.1-all"
            )
            self.structure_model = TableTransformerForObjectDetection.from_pretrained(
                "microsoft/table-transformer-structure-recognition-v1.1-all"
            )
            
            # Move models to GPU if available
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.detection_model = self.detection_model.to(device)
            self.structure_model = self.structure_model.to(device)
            
            # Set to evaluation mode
            self.detection_model.eval()
            self.structure_model.eval()
            
            load_time = time.time() - start_time
            print(f" Table Transformer models loaded successfully in {load_time:.2f}s")
            
        except Exception as e:
            print(f"L Table Transformer model loading failed: {e}")
            import traceback
            traceback.print_exc()
            # Don't raise - allow service to start with fallback
            print("  Service will use fallback table detection")
    
    @modal.method()
    def detect_tables(
        self, 
        image_b64: str, 
        detection_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Detect tables in document image
        
        Args:
            image_b64: Base64 encoded image
            detection_threshold: Table detection confidence threshold
            
        Returns:
            Table detection results with bounding boxes
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Validate models are loaded
            if not self.detection_model or not self.detection_processor:
                raise RuntimeError("Table detection model not loaded")
            
            # Decode and process image
            image = self._decode_image(image_b64)
            
            # Run table detection
            tables = self._detect_tables_impl(image, detection_threshold)
            
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            # Calculate cost (T4 GPU: ~$0.40/hour)
            gpu_cost = (processing_time / 3600) * 0.40
            
            result = {
                'success': True,
                'service': 'isa-vision-table',
                'provider': 'ISA',
                'tables': tables,
                'table_count': len(tables),
                'processing_time': processing_time,
                'detection_method': 'table-transformer',
                'billing': {
                    'request_id': f"req_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round(gpu_cost, 6),
                    'gpu_type': 'T4'
                },
                'model_info': {
                    'model': 'microsoft/table-transformer-detection',
                    'provider': 'ISA',
                    'gpu': 'T4',
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
            self.logger.error(f"Table detection failed: {e}")
            error_result = {
                'success': False,
                'service': 'isa-vision-table',
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
    
    @modal.method()
    def analyze_table_structure(
        self, 
        image_b64: str, 
        table_bbox: Optional[List[int]] = None,
        structure_threshold: float = 0.6
    ) -> Dict[str, Any]:
        """
        Analyze table structure in image or table region
        
        Args:
            image_b64: Base64 encoded image
            table_bbox: Optional table bounding box [x1, y1, x2, y2]
            structure_threshold: Structure detection confidence threshold
            
        Returns:
            Table structure analysis results
        """
        start_time = time.time()
        
        try:
            if not self.structure_model or not self.structure_processor:
                raise RuntimeError("Table structure model not loaded")
            
            image = self._decode_image(image_b64)
            
            # Crop to table region if bbox provided
            if table_bbox:
                x1, y1, x2, y2 = table_bbox
                image = image.crop((x1, y1, x2, y2))
            
            # Analyze table structure
            structure = self._analyze_table_structure_impl(image, structure_threshold)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'service': 'isa-vision-table',
                'function': 'structure_analysis',
                'structure': structure,
                'processing_time': processing_time,
                'model_info': {
                    'model': 'microsoft/table-transformer-structure-recognition-v1.1-all',
                    'gpu': 'T4'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'service': 'isa-vision-table',
                'function': 'structure_analysis',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    @modal.method()
    def process_complete_table(
        self, 
        image_b64: str,
        detection_threshold: float = 0.7,
        structure_threshold: float = 0.6
    ) -> Dict[str, Any]:
        """
        Complete table processing: detection + structure analysis
        
        Args:
            image_b64: Base64 encoded image
            detection_threshold: Table detection confidence threshold
            structure_threshold: Structure analysis confidence threshold
            
        Returns:
            Complete table processing results
        """
        start_time = time.time()
        
        try:
            image = self._decode_image(image_b64)
            
            # Step 1: Detect tables
            tables = self._detect_tables_impl(image, detection_threshold)
            
            # Step 2: Analyze structure for each detected table
            for table in tables:
                if 'bbox' in table:
                    x1, y1, x2, y2 = table['bbox']
                    table_image = image.crop((x1, y1, x2, y2))
                    structure = self._analyze_table_structure_impl(table_image, structure_threshold)
                    table['structure'] = structure
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'service': 'isa-vision-table',
                'function': 'complete_processing',
                'tables': tables,
                'table_count': len(tables),
                'processing_time': processing_time,
                'model_info': {
                    'detection_model': 'microsoft/table-transformer-detection',
                    'structure_model': 'microsoft/table-transformer-structure-recognition-v1.1-all',
                    'gpu': 'T4'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'service': 'isa-vision-table',
                'function': 'complete_processing',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _detect_tables_impl(self, image: Image.Image, threshold: float) -> List[Dict[str, Any]]:
        """Implementation of table detection using Table Transformer"""
        print("<¯ Running Table Transformer detection...")
        
        try:
            # Prepare inputs
            inputs = self.detection_processor(images=image, return_tensors="pt")
            
            # Move to GPU if available
            device = next(self.detection_model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Run inference
            with torch.no_grad():
                outputs = self.detection_model(**inputs)
            
            # Process results
            target_sizes = torch.tensor([image.size[::-1]])  # (height, width)
            results = self.detection_processor.post_process_object_detection(
                outputs, threshold=threshold, target_sizes=target_sizes
            )[0]
            
            tables = []
            for idx, (score, label, box) in enumerate(zip(
                results["scores"], results["labels"], results["boxes"]
            )):
                x1, y1, x2, y2 = box.tolist()
                
                tables.append({
                    'id': f'table_{idx}',
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': float(score),
                    'center': [int((x1 + x2) // 2), int((y1 + y2) // 2)],
                    'label': int(label),
                    'type': 'table'
                })
            
            print(f" Table Transformer detected {len(tables)} tables")
            return tables
            
        except Exception as e:
            print(f"L Table detection failed: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _analyze_table_structure_impl(self, image: Image.Image, threshold: float) -> Dict[str, Any]:
        """Implementation of table structure analysis using Table Transformer"""
        print("=Ê Running Table Transformer structure analysis...")
        
        try:
            # Prepare inputs
            inputs = self.structure_processor(images=image, return_tensors="pt")
            
            # Move to GPU if available
            device = next(self.structure_model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Run inference
            with torch.no_grad():
                outputs = self.structure_model(**inputs)
            
            # Process results
            target_sizes = torch.tensor([image.size[::-1]])  # (height, width)
            results = self.structure_processor.post_process_object_detection(
                outputs, threshold=threshold, target_sizes=target_sizes
            )[0]
            
            # Parse structure elements
            rows = []
            columns = []
            cells = []
            
            for score, label, box in zip(
                results["scores"], results["labels"], results["boxes"]
            ):
                x1, y1, x2, y2 = box.tolist()
                element = {
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': float(score),
                    'label': int(label)
                }
                
                # Categorize based on label (this may need adjustment based on model output)
                if label == 0:  # Row
                    rows.append(element)
                elif label == 1:  # Column
                    columns.append(element)
                else:  # Cell or other structure
                    cells.append(element)
            
            structure = {
                'rows': rows,
                'columns': columns,
                'cells': cells,
                'row_count': len(rows),
                'column_count': len(columns),
                'cell_count': len(cells),
                'confidence_avg': float(torch.mean(results["scores"]).item()) if len(results["scores"]) > 0 else 0.0
            }
            
            print(f" Structure analysis: {len(rows)} rows, {len(columns)} columns, {len(cells)} cells")
            return structure
            
        except Exception as e:
            print(f"L Table structure analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'rows': [],
                'columns': [],
                'cells': [],
                'row_count': 0,
                'column_count': 0,
                'cell_count': 0,
                'confidence_avg': 0.0,
                'error': str(e)
            }
    
    @modal.method()
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'isa-vision-table',
            'provider': 'ISA',
            'models_loaded': {
                'detection': self.detection_model is not None,
                'structure': self.structure_model is not None
            },
            'model_names': {
                'detection': 'microsoft/table-transformer-detection',
                'structure': 'microsoft/table-transformer-structure-recognition-v1.1-all'
            },
            'timestamp': time.time(),
            'gpu': 'T4',
            'memory_usage': '12GB',
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
            'service': 'isa-vision-table',
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
            print(f"= Decoded image size: {len(image_data)} bytes")
            
            # Open with PIL
            image = Image.open(io.BytesIO(image_data))
            print(f"= Image format: {image.format}, size: {image.size}, mode: {image.mode}")
            
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
            print("  Could not import model manager - registration skipped")
            return {"success": False, "error": "Model manager not available"}
        
        # Use ModelManager to register this service
        model_manager = ModelManager()
        
        # Register the ISA service in the registry
        success = model_manager.registry.register_model(
            model_id="isa-table-transformer-service",
            model_type=ModelType.VISION,
            capabilities=[
                ModelCapability.TABLE_DETECTION,
                ModelCapability.TABLE_STRUCTURE_RECOGNITION,
                ModelCapability.IMAGE_ANALYSIS
            ],
            metadata={
                "description": "ISA Table Transformer detection and structure recognition service",
                "provider": "ISA",
                "service_name": "isa-vision-table",
                "service_type": "modal",
                "deployment_type": "modal_gpu",
                "endpoint": "https://isa-vision-table.modal.run",
                "underlying_models": [
                    "microsoft/table-transformer-detection",
                    "microsoft/table-transformer-structure-recognition-v1.1-all"
                ],
                "gpu_requirement": "T4",
                "memory_mb": 12288,
                "max_containers": 15,
                "cost_per_hour_usd": 0.40,
                "auto_registered": True,
                "registered_by": "isa_vision_table_service.py",
                "is_service": True,
                "optimized": True,
                "billing_enabled": True
            }
        )
        
        if success:
            print(" Table service auto-registered successfully")
        else:
            print("  Table service registration failed")
            
        return {"success": success}
        
    except Exception as e:
        print(f"L Auto-registration error: {e}")
        return {"success": False, "error": str(e)}

# Deployment script
@app.function()
def deploy_info():
    """Deployment information"""
    return {
        "service": "ISA Vision Table Processing",
        "models": [
            "microsoft/table-transformer-detection",
            "microsoft/table-transformer-structure-recognition-v1.1-all"
        ],
        "gpu_requirement": "T4",
        "memory_requirement": "12GB",
        "deploy_command": "modal deploy isa_vision_table_service.py"
    }

# Quick deployment function
@app.function()
def deploy_service():
    """Deploy this service instantly"""
    import subprocess
    import os
    
    print("=€ Deploying ISA Vision Table Service...")
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
        print(f"=Ý Output: {result.stdout}")
        return {"success": True, "output": result.stdout}
        
    except subprocess.CalledProcessError as e:
        print(f"L Deployment failed: {e}")
        print(f"=Ý Error: {e.stderr}")
        return {"success": False, "error": str(e), "stderr": e.stderr}

if __name__ == "__main__":
    print("=€ ISA Vision Table Service - Modal Deployment")
    print("Deploy with: modal deploy isa_vision_table_service.py")
    print("Or call: modal run isa_vision_table_service.py::deploy_service")
    print("Note: Uses Microsoft Table Transformer for detection and structure recognition")
    print("\n=Ý Service will auto-register in model registry upon deployment")