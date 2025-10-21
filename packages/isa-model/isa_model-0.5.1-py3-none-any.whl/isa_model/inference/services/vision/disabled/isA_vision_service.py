"""
ISA Vision Service

Connects to self-hosted Modal UI detection service
Provides vision capabilities using our deployed models
"""

import modal
import base64
import io
import logging
from typing import Dict, Any, List, Union, Optional, BinaryIO
from PIL import Image

from .base_vision_service import BaseVisionService

logger = logging.getLogger(__name__)

class ISAVisionService(BaseVisionService):
    """ISA Vision Service using Modal backend"""
    
    def __init__(self, provider, model_name: str):
        super().__init__(provider, model_name)
        self.ui_app = None
        self.doc_app = None
        self.table_app = None
        self._initialize_modal_connections()
    
    def _initialize_modal_connections(self):
        """Initialize connections to Modal services"""
        try:
            # Connect to UI detection service
            self.ui_app = modal.App.lookup("isa-vision-ui", create_if_missing=False)
            logger.info(" Connected to UI detection service")
        except Exception as e:
            logger.warning(f"� UI service not available: {e}")
            self.ui_app = None
        
        try:
            # Connect to document analysis service (when deployed)
            self.doc_app = modal.App.lookup("isa-vision-doc", create_if_missing=False)
            logger.info(" Connected to document analysis service")
        except Exception as e:
            logger.warning(f"� Document service not available: {e}")
            self.doc_app = None
        
        try:
            # Connect to table extraction service
            self.table_app = modal.App.lookup("qwen-vision-table", create_if_missing=False)
            logger.info("✅ Connected to table extraction service")
        except Exception as e:
            logger.warning(f"⚠️ Table extraction service not available: {e}")
            self.table_app = None
    
    async def invoke(
        self, 
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        task: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Unified invoke method for all vision operations
        """
        if task == "detect_ui" or task == "ui_analysis":
            return await self.detect_objects(image, **kwargs)
        elif task == "extract_text" or task == "ocr":
            return await self.extract_text(image)
        elif task == "analyze_document":
            return await self._analyze_document(image)
        elif task == "extract_table" or task == "table_extraction":
            return await self.extract_table_data(image, **kwargs)
        else:
            return await self.analyze_image(image, prompt, **kwargs)
    
    async def analyze_image(
        self, 
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Analyze image using UI detection service"""
        
        if not self.ui_app:
            return {
                'error': 'UI detection service not available',
                'success': False
            }
        
        try:
            # Convert image to base64
            image_b64 = self._encode_image(image)
            
            # Call Modal UI detection service using from_name (new API)
            ui_detector = modal.Cls.from_name("isa-vision-ui", "UIDetectionService")
            result = ui_detector().detect_ui_elements.remote(image_b64)
            
            if result.get('success'):
                return {
                    'success': True,
                    'service': 'isa-vision',
                    'text': f"Detected {result.get('element_count', 0)} UI elements",
                    'detected_objects': result.get('ui_elements', []),
                    'confidence': 0.9,
                    'metadata': {
                        'processing_time': result.get('processing_time'),
                        'detection_method': result.get('detection_method'),
                        'model_info': result.get('model_info')
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'service': 'isa-vision'
                }
                
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'service': 'isa-vision'
            }
    
    async def analyze_images(
        self, 
        images: List[Union[str, BinaryIO]],
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> List[Dict[str, Any]]:
        """Analyze multiple images"""
        results = []
        for image in images:
            result = await self.analyze_image(image, prompt, max_tokens)
            results.append(result)
        return results
    
    async def describe_image(
        self, 
        image: Union[str, BinaryIO],
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """Generate description using UI detection"""
        result = await self.analyze_image(image)
        
        if result.get('success'):
            objects = result.get('detected_objects', [])
            description = f"This appears to be a user interface with {len(objects)} interactive elements. "
            
            if objects:
                element_types = list(set([obj.get('type', 'element') for obj in objects]))
                description += f"The interface contains: {', '.join(element_types)}."
            
            return {
                'success': True,
                'description': description,
                'objects': objects,
                'scene': 'User Interface',
                'colors': ['unknown']  # Could be enhanced with color detection
            }
        else:
            return result
    
    async def extract_text(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Extract text using document analysis service"""
        
        if not self.doc_app:
            # Fallback to UI service for basic text detection
            return await self._extract_text_fallback(image)
        
        try:
            # Convert image to base64
            image_b64 = self._encode_image(image)
            
            # Call Modal document analysis service using from_name (new API)
            doc_analyzer = modal.Cls.from_name("isa-vision-doc", "DocumentAnalysisService")
            result = doc_analyzer().extract_text.remote(image_b64)
            
            if result.get('success'):
                text_results = result.get('text_results', [])
                all_text = ' '.join([item.get('text', '') for item in text_results])
                
                return {
                    'success': True,
                    'service': 'isa-vision-doc',
                    'text': all_text,
                    'confidence': sum([item.get('confidence', 0) for item in text_results]) / len(text_results) if text_results else 0,
                    'bounding_boxes': [item.get('bbox') for item in text_results],
                    'language': 'auto-detected',
                    'metadata': {
                        'processing_time': result.get('processing_time'),
                        'text_count': result.get('text_count')
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'OCR failed'),
                    'service': 'isa-vision-doc'
                }
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'service': 'isa-vision-doc'
            }
    
    async def detect_objects(
        self, 
        image: Union[str, BinaryIO],
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Detect UI elements using UI detection service"""
        
        result = await self.analyze_image(image)
        
        if result.get('success'):
            objects = result.get('detected_objects', [])
            # Filter by confidence threshold
            filtered_objects = [obj for obj in objects if obj.get('confidence', 0) >= confidence_threshold]
            
            return {
                'success': True,
                'service': 'isa-vision-ui',
                'objects': filtered_objects,
                'count': len(filtered_objects),
                'bounding_boxes': [obj.get('bbox') for obj in filtered_objects],
                'metadata': result.get('metadata', {})
            }
        else:
            return result
    
    async def get_object_coordinates(
        self,
        image: Union[str, BinaryIO],
        object_name: str
    ) -> Dict[str, Any]:
        """Get coordinates of specific UI element"""
        
        detection_result = await self.detect_objects(image)
        
        if not detection_result.get('success'):
            return detection_result
        
        objects = detection_result.get('objects', [])
        
        # Look for object by name/type
        for obj in objects:
            obj_type = obj.get('type', '').lower()
            obj_content = obj.get('content', '').lower()
            
            if object_name.lower() in obj_type or object_name.lower() in obj_content:
                return {
                    'success': True,
                    'found': True,
                    'center_coordinates': obj.get('center', [0, 0]),
                    'confidence': obj.get('confidence', 0),
                    'description': f"Found {obj.get('type')} at center coordinates",
                    'object_info': obj
                }
        
        return {
            'success': True,
            'found': False,
            'center_coordinates': [0, 0],
            'confidence': 0,
            'description': f"Object '{object_name}' not found in image"
        }
    
    async def classify_image(
        self, 
        image: Union[str, BinaryIO],
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Classify image type"""
        
        result = await self.analyze_image(image)
        
        if result.get('success'):
            objects = result.get('detected_objects', [])
            
            # Simple classification based on detected UI elements
            if objects:
                category = "user_interface"
                confidence = 0.9
            else:
                category = "unknown"
                confidence = 0.1
            
            return {
                'success': True,
                'category': category,
                'confidence': confidence,
                'all_predictions': [
                    {'category': category, 'confidence': confidence}
                ]
            }
        else:
            return result
    
    async def compare_images(
        self, 
        image1: Union[str, BinaryIO],
        image2: Union[str, BinaryIO]
    ) -> Dict[str, Any]:
        """Compare two images based on UI elements"""
        
        result1 = await self.analyze_image(image1)
        result2 = await self.analyze_image(image2)
        
        if not (result1.get('success') and result2.get('success')):
            return {
                'success': False,
                'error': 'Failed to analyze one or both images'
            }
        
        objects1 = result1.get('detected_objects', [])
        objects2 = result2.get('detected_objects', [])
        
        # Simple comparison based on element counts and types
        count_diff = abs(len(objects1) - len(objects2))
        types1 = set([obj.get('type') for obj in objects1])
        types2 = set([obj.get('type') for obj in objects2])
        
        common_types = types1.intersection(types2)
        unique_types = types1.symmetric_difference(types2)
        
        similarity_score = len(common_types) / max(len(types1.union(types2)), 1)
        
        return {
            'success': True,
            'similarity_score': similarity_score,
            'differences': f"Different element types: {list(unique_types)}",
            'common_elements': f"Common element types: {list(common_types)}",
            'metadata': {
                'elements_count_1': len(objects1),
                'elements_count_2': len(objects2),
                'count_difference': count_diff
            }
        }
    
    def get_supported_formats(self) -> List[str]:
        """Get supported image formats"""
        return ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff']
    
    def get_max_image_size(self) -> Dict[str, int]:
        """Get maximum image dimensions"""
        return {'width': 4096, 'height': 4096}
    
    async def close(self):
        """Cleanup resources"""
        # Modal connections don't need explicit cleanup
        pass
    
    # Helper methods
    
    def _encode_image(self, image: Union[str, BinaryIO]) -> str:
        """Convert image to base64 string"""
        if isinstance(image, str):
            # File path
            with open(image, 'rb') as f:
                image_data = f.read()
        else:
            # Binary data
            if hasattr(image, 'read'):
                image_data = image.read()
            else:
                # Assume it's bytes
                image_data = bytes(image) if not isinstance(image, bytes) else image
        
        return base64.b64encode(image_data).decode('utf-8')
    
    async def _extract_text_fallback(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Fallback OCR using UI service (basic text detection)"""
        # For now, return placeholder
        return {
            'success': False,
            'error': 'OCR service not available, deploy document analysis service',
            'text': '',
            'confidence': 0,
            'service': 'isa-vision-fallback'
        }
    
    async def _analyze_document(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Analyze document with tables and OCR"""
        
        if not self.doc_app:
            return {
                'success': False,
                'error': 'Document analysis service not deployed',
                'service': 'isa-vision-doc'
            }
        
        try:
            # Convert image to base64
            image_b64 = self._encode_image(image)
            
            # Call Modal document analysis service using from_name (new API)
            doc_analyzer = modal.Cls.from_name("isa-vision-doc", "DocumentAnalysisService")
            result = doc_analyzer().analyze_document_complete.remote(image_b64)
            
            return result
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'service': 'isa-vision-doc'
            }
    
    async def extract_table_data(
        self, 
        image: Union[str, BinaryIO],
        extraction_format: str = "markdown",
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract table data using Qwen2.5-VL table extraction service"""
        
        if not self.table_app:
            return {
                'success': False,
                'error': 'Table extraction service not available',
                'service': 'isa-vision-table'
            }
        
        try:
            # Convert image to base64
            image_b64 = self._encode_image(image)
            
            # Call Modal table extraction service
            table_extractor = modal.Cls.from_name("qwen-vision-table", "QwenTableExtractionService")
            result = table_extractor().extract_table_data.remote(
                image_b64=image_b64,
                extraction_format=extraction_format,
                custom_prompt=custom_prompt
            )
            
            if result.get('success'):
                return {
                    'success': True,
                    'service': 'isa-vision-table',
                    'extracted_data': result.get('extracted_data'),
                    'raw_output': result.get('raw_output'),
                    'format': result.get('format'),
                    'processing_time': result.get('processing_time'),
                    'model_info': result.get('model_info')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Table extraction failed'),
                    'service': 'isa-vision-table'
                }
                
        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'service': 'isa-vision-table'
            }
    
    async def batch_extract_tables(
        self, 
        images: List[Union[str, BinaryIO]],
        extraction_format: str = "markdown"
    ) -> Dict[str, Any]:
        """Extract tables from multiple images"""
        
        if not self.table_app:
            return {
                'success': False,
                'error': 'Table extraction service not available',
                'service': 'isa-vision-table'
            }
        
        try:
            # Convert all images to base64
            images_b64 = [self._encode_image(image) for image in images]
            
            # Call Modal batch extraction service
            table_extractor = modal.Cls.from_name("qwen-vision-table", "QwenTableExtractionService")
            result = table_extractor().batch_extract_tables.remote(
                images_b64=images_b64,
                extraction_format=extraction_format
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Batch table extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'service': 'isa-vision-table'
            }