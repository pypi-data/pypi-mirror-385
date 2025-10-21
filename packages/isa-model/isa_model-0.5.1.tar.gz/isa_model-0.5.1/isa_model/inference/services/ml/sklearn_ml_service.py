import asyncio
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Union
from pathlib import Path
import logging

from .base_ml_service import BaseMLService

logger = logging.getLogger(__name__)

class SklearnService(BaseMLService):
    """Service for scikit-learn models"""
    
    async def load_model(self, model_path: str) -> None:
        """Load scikit-learn model from joblib file"""
        try:
            model_path = Path(model_path)
            
            # Load model
            self.model = joblib.load(model_path)
            
            # Try to load additional metadata if available
            metadata_path = model_path.parent / f"{model_path.stem}_metadata.json"
            if metadata_path.exists():
                import json
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.feature_names = metadata.get('feature_names', [])
                    self.target_names = metadata.get('target_names', [])
                    self.model_info = metadata.get('model_info', {})
            
            # Try to load preprocessing pipeline
            preprocessing_path = model_path.parent / f"{model_path.stem}_preprocessing.joblib"
            if preprocessing_path.exists():
                self.preprocessing_pipeline = joblib.load(preprocessing_path)
                
            logger.info(f"Loaded sklearn model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load sklearn model {model_path}: {e}")
            raise
    
    async def predict(self, features: Union[np.ndarray, pd.DataFrame, List]) -> Dict[str, Any]:
        """Make predictions with the sklearn model"""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        try:
            # Preprocess features
            processed_features = self._preprocess_features(features)
            
            # Make prediction
            prediction = self.model.predict(processed_features)
            
            # Handle single vs batch predictions
            if prediction.ndim == 0:
                prediction = [prediction.item()]
            elif prediction.ndim == 1:
                prediction = prediction.tolist()
            
            result = {
                "predictions": prediction,
                "model_name": self.model_name,
                "feature_count": processed_features.shape[1] if processed_features.ndim > 1 else len(processed_features)
            }
            
            # Add feature names if available
            if self.feature_names:
                result["feature_names"] = self.feature_names
                
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    async def predict_proba(self, features: Union[np.ndarray, pd.DataFrame, List]) -> Dict[str, Any]:
        """Get prediction probabilities"""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        if not hasattr(self.model, 'predict_proba'):
            raise ValueError("Model does not support probability predictions")
        
        try:
            processed_features = self._preprocess_features(features)
            probabilities = self.model.predict_proba(processed_features)
            
            if probabilities.ndim == 1:
                probabilities = [probabilities.tolist()]
            else:
                probabilities = probabilities.tolist()
            
            result = {
                "probabilities": probabilities,
                "classes": getattr(self.model, 'classes_', []).tolist(),
                "model_name": self.model_name
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Probability prediction failed: {e}")
            raise
    
    async def explain_prediction(self, features: Union[np.ndarray, pd.DataFrame, List]) -> Dict[str, Any]:
        """Explain predictions using feature importance"""
        try:
            processed_features = self._preprocess_features(features)
            
            explanation = {
                "model_name": self.model_name,
                "explanation_type": "feature_importance"
            }
            
            # Get feature importance if available
            if hasattr(self.model, 'feature_importances_'):
                importance = self.model.feature_importances_.tolist()
                explanation["feature_importance"] = importance
                
                if self.feature_names:
                    explanation["feature_importance_named"] = dict(zip(self.feature_names, importance))
            
            # Get coefficients for linear models
            elif hasattr(self.model, 'coef_'):
                coef = self.model.coef_
                if coef.ndim > 1:
                    coef = coef[0]  # Take first class for binary classification
                explanation["coefficients"] = coef.tolist()
                
                if self.feature_names:
                    explanation["coefficients_named"] = dict(zip(self.feature_names, coef))
            
            return explanation
            
        except Exception as e:
            logger.error(f"Explanation failed: {e}")
            return {"error": str(e)}