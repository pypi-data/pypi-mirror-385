from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, BinaryIO
from pathlib import Path
import logging
import json
import shutil
import os

logger = logging.getLogger(__name__)

class ModelStorage(ABC):
    """Base class for model storage implementations"""
    
    @abstractmethod
    async def save_model(self, model_id: str, model_path: str, metadata: Dict[str, Any]) -> bool:
        """Save model files and metadata"""
        pass
    
    @abstractmethod
    async def load_model(self, model_id: str) -> Optional[Path]:
        """Load model files"""
        pass
    
    @abstractmethod
    async def delete_model(self, model_id: str) -> bool:
        """Delete model files and metadata"""
        pass
    
    @abstractmethod
    async def get_metadata(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model metadata"""
        pass
    
    @abstractmethod
    async def list_models(self) -> Dict[str, Dict[str, Any]]:
        """List all stored models with their metadata"""
        pass

class LocalModelStorage(ModelStorage):
    """Local file system based model storage"""
    
    def __init__(self, base_dir: str = "./models", auto_create: bool = False):
        self.base_dir = Path(base_dir)
        self.models_dir = self.base_dir / "models"
        self.metadata_file = self.base_dir / "model_metadata.json"
        self.auto_create = auto_create
        if auto_create:
            self._ensure_directories()
        self._load_metadata()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_metadata(self):
        """Load model metadata from file"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Save model metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    async def save_model(self, model_id: str, model_path: str, metadata: Dict[str, Any]) -> bool:
        """Save model files and metadata"""
        try:
            model_dir = self.models_dir / model_id
            source_path = Path(model_path)
            
            # Copy model files
            if source_path.is_file():
                model_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, model_dir / source_path.name)
            else:
                shutil.copytree(source_path, model_dir, dirs_exist_ok=True)
            
            # Update metadata
            self.metadata[model_id] = {
                **metadata,
                "storage_path": str(model_dir),
                "saved_at": str(Path(model_dir).stat().st_mtime)
            }
            self._save_metadata()
            
            logger.info(f"Saved model {model_id} to {model_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save model {model_id}: {e}")
            return False
    
    async def load_model(self, model_id: str) -> Optional[Path]:
        """Load model files"""
        try:
            model_dir = self.models_dir / model_id
            if not model_dir.exists():
                logger.warning(f"Model {model_id} not found at {model_dir}")
                return None
            
            return model_dir
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            return None
    
    async def delete_model(self, model_id: str) -> bool:
        """Delete model files and metadata"""
        try:
            model_dir = self.models_dir / model_id
            if model_dir.exists():
                shutil.rmtree(model_dir)
            
            if model_id in self.metadata:
                del self.metadata[model_id]
                self._save_metadata()
            
            logger.info(f"Deleted model {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete model {model_id}: {e}")
            return False
    
    async def get_metadata(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model metadata"""
        return self.metadata.get(model_id)
    
    async def list_models(self) -> Dict[str, Dict[str, Any]]:
        """List all stored models with their metadata"""
        return self.metadata 