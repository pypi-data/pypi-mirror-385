#!/usr/bin/env python3
"""
VGG16 Vision Service
Computer vision service using VGG16 for image classification
Based on the aircraft damage detection notebook implementation
"""

import os
import numpy as np
from typing import Dict, List, Any, Optional, Union, BinaryIO
import logging
from PIL import Image
import io

from .base_vision_service import BaseVisionService

logger = logging.getLogger(__name__)

def _lazy_import_vgg16_deps():
    """Lazy import VGG16 dependencies"""
    try:
        import tensorflow as tf
        from tensorflow.keras.applications import VGG16
        from tensorflow.keras.layers import Dense, Dropout, Flatten
        from tensorflow.keras.models import Sequential, Model
        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.preprocessing.image import ImageDataGenerator
        
        return {
            'tf': tf,
            'VGG16': VGG16,
            'Dense': Dense,
            'Dropout': Dropout,
            'Flatten': Flatten,
            'Sequential': Sequential,
            'Model': Model,
            'Adam': Adam,
            'ImageDataGenerator': ImageDataGenerator,
            'available': True
        }
    except ImportError as e:
        logger.warning(f"VGG16 dependencies not available: {e}")
        return {'available': False}

class VGG16VisionService(BaseVisionService):
    """
    VGG16-based vision service for image classification
    Provides an alternative implementation to VLM-based classification
    """
    
    def __init__(self, model_path: Optional[str] = None, class_names: Optional[List[str]] = None):
        """
        Initialize VGG16 vision service
        
        Args:
            model_path: Path to trained VGG16 model
            class_names: List of class names for classification
        """
        super().__init__()
        
        self.model_path = model_path
        self.class_names = class_names or ["class_0", "class_1"]
        self.model = None
        self.input_shape = (224, 224, 3)
        
        # Lazy load dependencies
        self.vgg16_components = _lazy_import_vgg16_deps()
        
        if not self.vgg16_components['available']:
            raise ImportError("TensorFlow and VGG16 dependencies are required")
        
        # Load model if path provided
        if model_path and os.path.exists(model_path):
            self._load_model(model_path)
    
    def _load_model(self, model_path: str):
        """Load trained VGG16 model"""
        try:
            tf = self.vgg16_components['tf']
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"VGG16 model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Error loading VGG16 model: {e}")
            raise
    
    def _preprocess_image(self, image: Union[str, BinaryIO]) -> np.ndarray:
        """
        Preprocess image for VGG16 input
        
        Args:
            image: Image path or binary data
            
        Returns:
            Preprocessed image array
        """
        try:
            # Handle different image input types
            if isinstance(image, str):
                # File path
                pil_image = Image.open(image).convert('RGB')
            elif hasattr(image, 'read'):
                # Binary IO
                image_data = image.read()
                pil_image = Image.open(io.BytesIO(image_data)).convert('RGB')
            else:
                raise ValueError("Unsupported image format")
            
            # Resize to VGG16 input size
            pil_image = pil_image.resize((self.input_shape[0], self.input_shape[1]))
            
            # Convert to array and normalize
            image_array = np.array(pil_image) / 255.0
            
            # Add batch dimension
            image_batch = np.expand_dims(image_array, axis=0)
            
            return image_batch, image_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise
    
    async def classify_image(self, 
                           image: Union[str, BinaryIO], 
                           categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Classify image using trained VGG16 model
        
        Args:
            image: Image path or binary data
            categories: Optional list of categories (uses model's classes if None)
            
        Returns:
            Classification results
        """
        try:
            if self.model is None:
                return {
                    "error": "No trained model available. Please load a model first.",
                    "service": "VGG16VisionService"
                }
            
            # Preprocess image
            image_batch, image_array = self._preprocess_image(image)
            
            # Make prediction
            predictions = self.model.predict(image_batch, verbose=0)
            
            # Use provided categories or default class names
            class_names = categories or self.class_names
            
            # Process predictions based on model output
            if len(predictions[0]) == 1:  # Binary classification
                predicted_class_idx = int(predictions[0] > 0.5)
                confidence = float(predictions[0][0]) if predicted_class_idx == 1 else float(1 - predictions[0][0])
                
                # Create probability distribution
                probabilities = {
                    class_names[0]: float(1 - predictions[0][0]),
                    class_names[1]: float(predictions[0][0])
                }
            else:  # Multiclass classification
                predicted_class_idx = np.argmax(predictions[0])
                confidence = float(predictions[0][predicted_class_idx])
                
                # Create probability distribution
                probabilities = {
                    class_names[i]: float(predictions[0][i]) 
                    for i in range(min(len(class_names), len(predictions[0])))
                }
            
            predicted_class = class_names[predicted_class_idx] if predicted_class_idx < len(class_names) else f"class_{predicted_class_idx}"
            
            return {
                "task": "classify",
                "service": "VGG16VisionService",
                "predicted_class": predicted_class,
                "confidence": confidence,
                "probabilities": probabilities,
                "model_type": "VGG16",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error classifying image: {e}")
            return {
                "error": str(e),
                "service": "VGG16VisionService",
                "success": False
            }
    
    async def analyze_image(self, 
                          image: Union[str, BinaryIO], 
                          prompt: Optional[str] = None,
                          max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Analyze image using VGG16 classification
        
        Args:
            image: Image path or binary data
            prompt: Optional prompt (used to guide interpretation)
            max_tokens: Not used for classification
            
        Returns:
            Analysis results
        """
        # For VGG16, analysis is essentially classification
        classification_result = await self.classify_image(image)
        
        if classification_result.get("success"):
            # Create analysis text based on classification
            predicted_class = classification_result["predicted_class"]
            confidence = classification_result["confidence"]
            
            analysis_text = f"The image has been classified as '{predicted_class}' with {confidence:.2%} confidence."
            
            if prompt:
                analysis_text += f" Analysis context: {prompt}"
            
            return {
                "task": "analyze",
                "service": "VGG16VisionService",
                "text": analysis_text,
                "confidence": confidence,
                "classification": classification_result,
                "success": True
            }
        else:
            return classification_result
    
    def set_class_names(self, class_names: List[str]):
        """Set class names for classification"""
        self.class_names = class_names
    
    def load_trained_model(self, model_path: str, class_names: Optional[List[str]] = None):
        """
        Load a trained VGG16 model
        
        Args:
            model_path: Path to the trained model
            class_names: Optional class names
        """
        self._load_model(model_path)
        if class_names:
            self.set_class_names(class_names)
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            "service_name": "VGG16VisionService",
            "model_type": "VGG16",
            "capabilities": ["classify", "analyze"],
            "model_loaded": self.model is not None,
            "input_shape": self.input_shape,
            "class_names": self.class_names,
            "dependencies_available": self.vgg16_components['available']
        }