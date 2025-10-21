from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, Tuple
import asyncio
import logging
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

from isa_model.inference.services.base_service import BaseService

logger = logging.getLogger(__name__)

class BaseMLService(BaseService, ABC):
    """Base class for traditional ML model services"""
    
    def __init__(self, provider: 'BaseProvider', model_name: str):
        super().__init__(provider, model_name)
        self.model = None
        self.model_info = {}
        self.feature_names = []
        self.target_names = []
        self.preprocessing_pipeline = None
        
    @abstractmethod
    async def load_model(self, model_path: str) -> None:
        """Load the ML model from file"""
        pass
    
    @abstractmethod
    async def predict(self, features: Union[np.ndarray, pd.DataFrame, List]) -> Dict[str, Any]:
        """Make predictions"""
        pass
    
    @abstractmethod
    async def predict_proba(self, features: Union[np.ndarray, pd.DataFrame, List]) -> Dict[str, Any]:
        """Get prediction probabilities (for classification models)"""
        pass
    
    async def batch_predict(self, features_batch: List[Union[np.ndarray, pd.DataFrame, List]]) -> List[Dict[str, Any]]:
        """Batch predictions for multiple inputs"""
        results = []
        for features in features_batch:
            result = await self.predict(features)
            results.append(result)
        return results
    
    async def explain_prediction(self, features: Union[np.ndarray, pd.DataFrame, List]) -> Dict[str, Any]:
        """Explain model predictions (if supported)"""
        return {"explanation": "Feature importance explanation not implemented for this model"}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "name": self.model_name,
            "type": "traditional_ml",
            "provider": self.provider.name if self.provider else "unknown",
            "feature_count": len(self.feature_names),
            "model_info": self.model_info,
            "supports_probability": hasattr(self.model, 'predict_proba') if self.model else False
        }
    
    def _preprocess_features(self, features: Union[np.ndarray, pd.DataFrame, List]) -> np.ndarray:
        """Preprocess input features"""
        if isinstance(features, list):
            features = np.array(features)
        elif isinstance(features, pd.DataFrame):
            features = features.values
            
        if self.preprocessing_pipeline:
            features = self.preprocessing_pipeline.transform(features)
            
        return features
    
    async def close(self):
        """Cleanup resources"""
        self.model = None
        logger.info(f"ML service {self.model_name} closed")