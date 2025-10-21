"""
Model Version Manager for Core Module

Manages model versions, lineage tracking, and lifecycle management.
Integrates with the existing ModelRegistry and provides version control
for all models in the system.

This is the central version management system that works with:
- Training module (for newly trained models)
- External model imports
- Model updates and fine-tuning
- Deployment and serving
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from ..database.supabase_client import get_supabase_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

from .model_repo import ModelRegistry, ModelType, ModelCapability

logger = logging.getLogger(__name__)


class VersionType(str, Enum):
    """Version increment types"""
    MAJOR = "major"      # Breaking changes, new architecture
    MINOR = "minor"      # New features, significant improvements  
    PATCH = "patch"      # Bug fixes, small improvements


@dataclass
class ModelVersion:
    """Model version information"""
    version_id: str                    # Unique version identifier
    model_id: str                      # Base model identifier  
    version_number: str                # Semantic version (e.g., "1.2.3")
    version_type: VersionType          # Type of version increment
    
    # Model information
    model_path: Optional[str] = None
    model_size_mb: Optional[float] = None
    model_format: Optional[str] = None
    
    # Training/source information
    source_type: Optional[str] = None  # "training", "import", "fine_tune"
    source_id: Optional[str] = None    # Training job ID, import ID, etc.
    base_model: Optional[str] = None
    dataset_source: Optional[str] = None
    
    # Performance metrics
    performance_metrics: Optional[Dict[str, float]] = None
    quality_score: Optional[float] = None
    benchmark_scores: Optional[Dict[str, float]] = None
    
    # Metadata
    description: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    # Lineage and relationships
    parent_version: Optional[str] = None
    derived_from: Optional[List[str]] = None
    children_versions: Optional[List[str]] = None
    
    # Status and flags
    status: str = "active"  # "active", "deprecated", "archived"
    is_production: bool = False
    is_default: bool = False
    
    # Core integration
    core_model_id: Optional[str] = None
    model_type: Optional[ModelType] = None
    capabilities: Optional[List[ModelCapability]] = None


class ModelVersionManager:
    """
    Central model version management system.
    
    Provides comprehensive version control for all models in the system,
    including trained models, imported models, and fine-tuned variants.
    
    Example:
        ```python
        from isa_model.core.models import ModelVersionManager
        
        version_manager = ModelVersionManager()
        
        # Create version from training
        version = version_manager.create_version_from_training(
            training_job_id="training_abc123",
            model_path="/path/to/model",
            base_model="google/gemma-2-4b-it",
            performance_metrics={"accuracy": 0.95}
        )
        
        # List all versions of a model
        versions = version_manager.list_versions("gemma_2_4b_it_chat")
        
        # Compare versions
        comparison = version_manager.compare_versions("v1.0.0", "v1.1.0")
        ```
    """
    
    def __init__(self, model_registry: Optional[ModelRegistry] = None):
        """
        Initialize version manager.
        
        Args:
            model_registry: Core model registry instance
        """
        self.model_registry = model_registry or ModelRegistry()
        
        # Initialize Supabase connection
        if SUPABASE_AVAILABLE:
            try:
                self.supabase_client = get_supabase_client()
                self.supabase_available = True
                self._ensure_version_tables()
            except Exception as e:
                logger.warning(f"Supabase not available for version management: {e}")
                self.supabase_client = None
                self.supabase_available = False
        else:
            self.supabase_client = None
            self.supabase_available = False
        
        logger.info(f"ModelVersionManager initialized (supabase: {self.supabase_available})")
    
    def create_version_from_training(self,
                                   training_job_id: str,
                                   model_path: str,
                                   base_model: str,
                                   task_type: str = "text_generation",
                                   performance_metrics: Optional[Dict[str, float]] = None,
                                   version_type: VersionType = VersionType.MINOR,
                                   description: Optional[str] = None,
                                   created_by: Optional[str] = None,
                                   tags: Optional[Dict[str, str]] = None) -> ModelVersion:
        """
        Create a new model version from a training job.
        
        Args:
            training_job_id: ID of the training job
            model_path: Path to the trained model
            base_model: Base model that was fine-tuned
            task_type: Type of task the model was trained for
            performance_metrics: Model performance metrics
            version_type: Type of version increment
            description: Version description
            created_by: User who created this version
            tags: Additional tags
            
        Returns:
            Created model version
        """
        try:
            # Generate model ID from base model and task
            model_id = self._generate_model_id(base_model, task_type)
            
            # Get next version number
            version_number = self._get_next_version(model_id, version_type)
            
            # Determine model type and capabilities
            model_type = self._infer_model_type(task_type)
            capabilities = self._infer_capabilities(task_type)
            
            # Create version
            version = ModelVersion(
                version_id=f"{model_id}:v{version_number}",
                model_id=model_id,
                version_number=version_number,
                version_type=version_type,
                model_path=model_path,
                source_type="training",
                source_id=training_job_id,
                base_model=base_model,
                performance_metrics=performance_metrics,
                description=description or f"Trained {task_type} model v{version_number}",
                tags=tags or {},
                created_at=datetime.now(),
                created_by=created_by,
                model_type=model_type,
                capabilities=capabilities
            )
            
            # Calculate quality score
            if performance_metrics:
                version.quality_score = self._calculate_quality_score(performance_metrics)
            
            # Get model size
            version.model_size_mb = self._calculate_model_size(model_path)
            
            # Save version
            success = self._save_version(version)
            if not success:
                raise Exception("Failed to save model version")
            
            # Register in core model registry
            core_model_id = self._register_in_core_registry(version)
            if core_model_id:
                version.core_model_id = core_model_id
                self._update_version(version)
            
            logger.info(f"Created model version from training: {version.version_id}")
            return version
            
        except Exception as e:
            logger.error(f"Failed to create version from training: {e}")
            raise
    
    def create_version_from_import(self,
                                 model_path: str,
                                 model_name: str,
                                 model_type: ModelType,
                                 capabilities: List[ModelCapability],
                                 version_type: VersionType = VersionType.MAJOR,
                                 description: Optional[str] = None,
                                 created_by: Optional[str] = None,
                                 tags: Optional[Dict[str, str]] = None,
                                 metadata: Optional[Dict[str, Any]] = None) -> ModelVersion:
        """
        Create a new model version from an imported model.
        
        Args:
            model_path: Path to the imported model
            model_name: Name of the model
            model_type: Type of the model
            capabilities: Model capabilities
            version_type: Type of version increment
            description: Version description
            created_by: User who imported this model
            tags: Additional tags
            metadata: Additional metadata
            
        Returns:
            Created model version
        """
        try:
            # Use model name as model ID
            model_id = self._clean_model_name(model_name)
            
            # Get next version number
            version_number = self._get_next_version(model_id, version_type)
            
            # Create version
            version = ModelVersion(
                version_id=f"{model_id}:v{version_number}",
                model_id=model_id,
                version_number=version_number,
                version_type=version_type,
                model_path=model_path,
                source_type="import",
                description=description or f"Imported {model_name} v{version_number}",
                tags=tags or {},
                created_at=datetime.now(),
                created_by=created_by,
                model_type=model_type,
                capabilities=capabilities
            )
            
            # Get model size
            version.model_size_mb = self._calculate_model_size(model_path)
            
            # Save version
            success = self._save_version(version)
            if not success:
                raise Exception("Failed to save model version")
            
            # Register in core model registry
            core_model_id = self._register_in_core_registry(version, metadata)
            if core_model_id:
                version.core_model_id = core_model_id
                self._update_version(version)
            
            logger.info(f"Created model version from import: {version.version_id}")
            return version
            
        except Exception as e:
            logger.error(f"Failed to create version from import: {e}")
            raise
    
    def get_version(self, version_id: str) -> Optional[ModelVersion]:
        """Get model version by ID."""
        try:
            return self._load_version(version_id)
        except Exception as e:
            logger.error(f"Failed to get version {version_id}: {e}")
            return None
    
    def list_versions(self,
                     model_id: Optional[str] = None,
                     status: Optional[str] = None,
                     created_by: Optional[str] = None,
                     limit: int = 50) -> List[ModelVersion]:
        """
        List model versions with filtering.
        
        Args:
            model_id: Filter by model ID
            status: Filter by status ("active", "deprecated", "archived")
            created_by: Filter by creator
            limit: Maximum number of versions
            
        Returns:
            List of model versions
        """
        try:
            return self._list_versions(model_id, status, created_by, limit)
        except Exception as e:
            logger.error(f"Failed to list versions: {e}")
            return []
    
    def get_latest_version(self, model_id: str, status: str = "active") -> Optional[ModelVersion]:
        """Get latest version of a model."""
        try:
            versions = self.list_versions(model_id=model_id, status=status, limit=1)
            return versions[0] if versions else None
        except Exception as e:
            logger.error(f"Failed to get latest version for {model_id}: {e}")
            return None
    
    def get_default_version(self, model_id: str) -> Optional[ModelVersion]:
        """Get default version of a model."""
        try:
            versions = self.list_versions(model_id=model_id, limit=100)
            default_versions = [v for v in versions if v.is_default]
            return default_versions[0] if default_versions else None
        except Exception as e:
            logger.error(f"Failed to get default version for {model_id}: {e}")
            return None
    
    def set_default_version(self, version_id: str) -> bool:
        """Set a version as the default for its model."""
        try:
            version = self.get_version(version_id)
            if not version:
                return False
            
            # Remove default flag from all versions of this model
            versions = self.list_versions(model_id=version.model_id, limit=1000)
            for v in versions:
                if v.is_default:
                    v.is_default = False
                    self._update_version(v)
            
            # Set this version as default
            version.is_default = True
            success = self._update_version(version)
            
            if success:
                logger.info(f"Set default version: {version_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to set default version {version_id}: {e}")
            return False
    
    def deprecate_version(self, version_id: str, reason: Optional[str] = None) -> bool:
        """Deprecate a model version."""
        try:
            version = self.get_version(version_id)
            if not version:
                return False
            
            version.status = "deprecated"
            if reason:
                if not version.tags:
                    version.tags = {}
                version.tags["deprecation_reason"] = reason
            
            success = self._update_version(version)
            
            if success:
                logger.info(f"Deprecated version: {version_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to deprecate version {version_id}: {e}")
            return False
    
    def compare_versions(self, version_id_1: str, version_id_2: str) -> Dict[str, Any]:
        """
        Compare two model versions.
        
        Args:
            version_id_1: First version ID
            version_id_2: Second version ID
            
        Returns:
            Comparison results
        """
        try:
            v1 = self.get_version(version_id_1)
            v2 = self.get_version(version_id_2)
            
            if not v1 or not v2:
                return {"error": "One or both versions not found"}
            
            comparison = {
                "version_1": {
                    "id": v1.version_id,
                    "number": v1.version_number,
                    "created_at": v1.created_at.isoformat() if v1.created_at else None,
                    "quality_score": v1.quality_score,
                    "model_size_mb": v1.model_size_mb,
                    "status": v1.status
                },
                "version_2": {
                    "id": v2.version_id,
                    "number": v2.version_number,
                    "created_at": v2.created_at.isoformat() if v2.created_at else None,
                    "quality_score": v2.quality_score,
                    "model_size_mb": v2.model_size_mb,
                    "status": v2.status
                },
                "differences": {}
            }
            
            # Compare quality scores
            if v1.quality_score is not None and v2.quality_score is not None:
                comparison["differences"]["quality_improvement"] = v2.quality_score - v1.quality_score
            
            # Compare model sizes
            if v1.model_size_mb is not None and v2.model_size_mb is not None:
                comparison["differences"]["size_change_mb"] = v2.model_size_mb - v1.model_size_mb
            
            # Compare performance metrics
            if v1.performance_metrics and v2.performance_metrics:
                metrics_diff = {}
                all_metrics = set(v1.performance_metrics.keys()) | set(v2.performance_metrics.keys())
                
                for metric in all_metrics:
                    val1 = v1.performance_metrics.get(metric)
                    val2 = v2.performance_metrics.get(metric)
                    
                    if val1 is not None and val2 is not None:
                        metrics_diff[metric] = {
                            "v1": val1,
                            "v2": val2,
                            "difference": val2 - val1,
                            "improvement": val2 > val1
                        }
                
                comparison["differences"]["metrics"] = metrics_diff
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare versions: {e}")
            return {"error": str(e)}
    
    def get_version_lineage(self, version_id: str, depth: int = 5) -> Dict[str, Any]:
        """
        Get version lineage tree.
        
        Args:
            version_id: Version ID to trace
            depth: Maximum depth to traverse
            
        Returns:
            Lineage information
        """
        try:
            version = self.get_version(version_id)
            if not version:
                return {"error": "Version not found"}
            
            lineage = {
                "version": version.version_id,
                "model_id": version.model_id,
                "ancestors": self._get_ancestors(version_id, depth),
                "descendants": self._get_descendants(version_id, depth)
            }
            
            return lineage
            
        except Exception as e:
            logger.error(f"Failed to get version lineage: {e}")
            return {"error": str(e)}
    
    def delete_version(self, version_id: str, force: bool = False) -> bool:
        """
        Delete a model version.
        
        Args:
            version_id: Version ID to delete
            force: Force deletion even if version is default or production
            
        Returns:
            True if successful
        """
        try:
            version = self.get_version(version_id)
            if not version:
                return False
            
            # Check if version can be deleted
            if not force:
                if version.is_default:
                    raise ValueError("Cannot delete default version. Set another version as default first.")
                if version.is_production:
                    raise ValueError("Cannot delete production version. Mark as non-production first.")
            
            # Unregister from core model registry
            if version.core_model_id:
                try:
                    self.model_registry.unregister_model(version.core_model_id)
                except Exception as e:
                    logger.warning(f"Failed to unregister from core registry: {e}")
            
            # Delete version data
            success = self._delete_version(version_id)
            
            if success:
                logger.info(f"Deleted model version: {version_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete version {version_id}: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get version management statistics."""
        try:
            all_versions = self.list_versions(limit=10000)
            
            stats = {
                "total_versions": len(all_versions),
                "unique_models": len(set(v.model_id for v in all_versions)),
                "status_breakdown": {},
                "source_breakdown": {},
                "version_type_breakdown": {},
                "average_quality_score": 0.0,
                "total_model_size_gb": 0.0
            }
            
            quality_scores = []
            total_size = 0.0
            
            for version in all_versions:
                # Count by status
                status = version.status
                stats["status_breakdown"][status] = stats["status_breakdown"].get(status, 0) + 1
                
                # Count by source type
                source = version.source_type or "unknown"
                stats["source_breakdown"][source] = stats["source_breakdown"].get(source, 0) + 1
                
                # Count by version type
                vtype = version.version_type.value
                stats["version_type_breakdown"][vtype] = stats["version_type_breakdown"].get(vtype, 0) + 1
                
                # Collect quality scores
                if version.quality_score is not None:
                    quality_scores.append(version.quality_score)
                
                # Sum model sizes
                if version.model_size_mb is not None:
                    total_size += version.model_size_mb
            
            # Calculate averages
            if quality_scores:
                stats["average_quality_score"] = sum(quality_scores) / len(quality_scores)
            
            stats["total_model_size_gb"] = total_size / 1024.0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}
    
    # Private methods
    
    def _generate_model_id(self, base_model: str, task_type: str) -> str:
        """Generate model ID from base model and task type."""
        clean_model = self._clean_model_name(base_model)
        clean_task = task_type.replace("-", "_").replace(" ", "_")
        return f"{clean_model}_{clean_task}"
    
    def _clean_model_name(self, model_name: str) -> str:
        """Clean model name for use as ID."""
        return model_name.replace("/", "_").replace("-", "_").replace(" ", "_").lower()
    
    def _get_next_version(self, model_id: str, version_type: VersionType) -> str:
        """Get next semantic version number."""
        try:
            versions = self.list_versions(model_id=model_id, limit=1000)
            
            if not versions:
                return "1.0.0"
            
            # Parse latest version number
            latest = versions[0]  # Assuming sorted by version desc
            version_parts = latest.version_number.split(".")
            
            if len(version_parts) != 3:
                return "1.0.0"
            
            major, minor, patch = map(int, version_parts)
            
            # Increment based on type
            if version_type == VersionType.MAJOR:
                major += 1
                minor = 0
                patch = 0
            elif version_type == VersionType.MINOR:
                minor += 1
                patch = 0
            else:  # PATCH
                patch += 1
            
            return f"{major}.{minor}.{patch}"
            
        except Exception:
            return "1.0.0"
    
    def _infer_model_type(self, task_type: str) -> ModelType:
        """Infer model type from task type."""
        task_lower = task_type.lower()
        
        if "embedding" in task_lower:
            return ModelType.EMBEDDING
        elif "image" in task_lower:
            return ModelType.IMAGE
        elif "audio" in task_lower:
            return ModelType.AUDIO
        elif "vision" in task_lower:
            return ModelType.VISION
        else:
            return ModelType.LLM
    
    def _infer_capabilities(self, task_type: str) -> List[ModelCapability]:
        """Infer model capabilities from task type."""
        task_lower = task_type.lower()
        capabilities = []
        
        if "chat" in task_lower or "conversation" in task_lower:
            capabilities.extend([ModelCapability.CHAT, ModelCapability.TEXT_GENERATION])
        elif "classification" in task_lower:
            capabilities.append(ModelCapability.TEXT_GENERATION)
        elif "embedding" in task_lower:
            capabilities.append(ModelCapability.EMBEDDING)
        elif "reasoning" in task_lower:
            capabilities.append(ModelCapability.REASONING)
        elif "image" in task_lower:
            if "generation" in task_lower:
                capabilities.append(ModelCapability.IMAGE_GENERATION)
            else:
                capabilities.append(ModelCapability.IMAGE_ANALYSIS)
        else:
            capabilities.append(ModelCapability.TEXT_GENERATION)
        
        return capabilities
    
    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall quality score from metrics."""
        try:
            score = 0.0
            count = 0
            
            # Common metrics (higher is better)
            for metric in ["accuracy", "f1_score", "bleu_score"]:
                if metric in metrics:
                    score += metrics[metric]
                    count += 1
            
            # Loss metrics (lower is better, so invert)
            for loss_metric in ["validation_loss", "loss"]:
                if loss_metric in metrics and metrics[loss_metric] > 0:
                    score += max(0, 1.0 - metrics[loss_metric])
                    count += 1
            
            return score / count if count > 0 else 0.5
            
        except Exception:
            return 0.5
    
    def _calculate_model_size(self, model_path: str) -> Optional[float]:
        """Calculate model size in MB."""
        try:
            import os
            
            if not os.path.exists(model_path):
                return None
            
            total_size = 0
            
            if os.path.isfile(model_path):
                total_size = os.path.getsize(model_path)
            else:
                for dirpath, dirnames, filenames in os.walk(model_path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if os.path.exists(filepath):
                            total_size += os.path.getsize(filepath)
            
            return total_size / (1024 * 1024)  # Convert to MB
            
        except Exception:
            return None
    
    def _register_in_core_registry(self, 
                                  version: ModelVersion, 
                                  additional_metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Register model version in core registry."""
        try:
            metadata = {
                "version_id": version.version_id,
                "version_number": version.version_number,
                "source_type": version.source_type,
                "source_id": version.source_id,
                "base_model": version.base_model,
                "quality_score": version.quality_score,
                "model_size_mb": version.model_size_mb,
                "created_at": version.created_at.isoformat() if version.created_at else None,
                "provider": "isa_model_core"
            }
            
            if additional_metadata:
                metadata.update(additional_metadata)
            
            success = self.model_registry.register_model(
                model_id=version.version_id,
                model_type=version.model_type,
                capabilities=version.capabilities or [],
                metadata=metadata
            )
            
            return version.version_id if success else None
            
        except Exception as e:
            logger.warning(f"Failed to register in core registry: {e}")
            return None
    
    def _ensure_version_tables(self):
        """Ensure version management tables exist."""
        if not self.supabase_available:
            return
        
        try:
            # Test if model_versions table exists
            self.supabase_client.table('model_versions').select('version_id').limit(1).execute()
        except Exception:
            logger.warning("model_versions table might not exist - would need database migration")
    
    def _save_version(self, version: ModelVersion) -> bool:
        """Save model version to storage."""
        if not self.supabase_available:
            logger.warning("No storage backend available for version management")
            return False
        
        try:
            version_data = {
                "version_id": version.version_id,
                "model_id": version.model_id,
                "version_number": version.version_number,
                "version_type": version.version_type.value,
                "model_path": version.model_path,
                "model_size_mb": version.model_size_mb,
                "model_format": version.model_format,
                "source_type": version.source_type,
                "source_id": version.source_id,
                "base_model": version.base_model,
                "dataset_source": version.dataset_source,
                "performance_metrics": json.dumps(version.performance_metrics) if version.performance_metrics else None,
                "quality_score": version.quality_score,
                "benchmark_scores": json.dumps(version.benchmark_scores) if version.benchmark_scores else None,
                "description": version.description,
                "tags": json.dumps(version.tags) if version.tags else None,
                "created_at": version.created_at.isoformat() if version.created_at else None,
                "created_by": version.created_by,
                "parent_version": version.parent_version,
                "derived_from": json.dumps(version.derived_from) if version.derived_from else None,
                "children_versions": json.dumps(version.children_versions) if version.children_versions else None,
                "status": version.status,
                "is_production": version.is_production,
                "is_default": version.is_default,
                "core_model_id": version.core_model_id,
                "model_type": version.model_type.value if version.model_type else None,
                "capabilities": json.dumps([cap.value for cap in version.capabilities]) if version.capabilities else None
            }
            
            result = self.supabase_client.table('model_versions').upsert(version_data).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Failed to save version: {e}")
            return False
    
    def _load_version(self, version_id: str) -> Optional[ModelVersion]:
        """Load model version from storage."""
        if not self.supabase_available:
            return None
        
        try:
            result = self.supabase_client.table('model_versions').select('*').eq('version_id', version_id).execute()
            
            if not result.data:
                return None
            
            return self._dict_to_version(result.data[0])
            
        except Exception as e:
            logger.error(f"Failed to load version {version_id}: {e}")
            return None
    
    def _list_versions(self,
                      model_id: Optional[str] = None,
                      status: Optional[str] = None,
                      created_by: Optional[str] = None,
                      limit: int = 50) -> List[ModelVersion]:
        """List model versions from storage."""
        if not self.supabase_available:
            return []
        
        try:
            query = self.supabase_client.table('model_versions').select('*')
            
            if model_id:
                query = query.eq('model_id', model_id)
            if status:
                query = query.eq('status', status)
            if created_by:
                query = query.eq('created_by', created_by)
            
            result = query.order('created_at', desc=True).limit(limit).execute()
            
            versions = []
            for data in result.data:
                version = self._dict_to_version(data)
                if version:
                    versions.append(version)
            
            return versions
            
        except Exception as e:
            logger.error(f"Failed to list versions: {e}")
            return []
    
    def _dict_to_version(self, data: Dict[str, Any]) -> ModelVersion:
        """Convert dictionary to ModelVersion object."""
        # Parse JSON fields
        for field in ['performance_metrics', 'benchmark_scores', 'tags', 'derived_from', 'children_versions']:
            if data.get(field) and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    data[field] = None
        
        # Parse capabilities
        if data.get('capabilities') and isinstance(data['capabilities'], str):
            try:
                cap_list = json.loads(data['capabilities'])
                data['capabilities'] = [ModelCapability(cap) for cap in cap_list]
            except (json.JSONDecodeError, ValueError):
                data['capabilities'] = None
        
        # Parse datetime
        if data.get('created_at') and isinstance(data['created_at'], str):
            try:
                data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            except ValueError:
                data['created_at'] = None
        
        # Parse enums
        if data.get('version_type') and isinstance(data['version_type'], str):
            try:
                data['version_type'] = VersionType(data['version_type'])
            except ValueError:
                data['version_type'] = VersionType.MINOR
        
        if data.get('model_type') and isinstance(data['model_type'], str):
            try:
                data['model_type'] = ModelType(data['model_type'])
            except ValueError:
                data['model_type'] = None
        
        return ModelVersion(**data)
    
    def _update_version(self, version: ModelVersion) -> bool:
        """Update existing version in storage."""
        return self._save_version(version)
    
    def _delete_version(self, version_id: str) -> bool:
        """Delete version from storage."""
        if not self.supabase_available:
            return False
        
        try:
            result = self.supabase_client.table('model_versions').delete().eq('version_id', version_id).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Failed to delete version: {e}")
            return False
    
    def _get_ancestors(self, version_id: str, depth: int) -> List[Dict[str, Any]]:
        """Get version ancestors."""
        ancestors = []
        current_version_id = version_id
        
        for _ in range(depth):
            version = self.get_version(current_version_id)
            if not version or not version.parent_version:
                break
            
            parent = self.get_version(version.parent_version)
            if not parent:
                break
            
            ancestors.append({
                "version_id": parent.version_id,
                "version_number": parent.version_number,
                "created_at": parent.created_at.isoformat() if parent.created_at else None
            })
            
            current_version_id = version.parent_version
        
        return ancestors
    
    def _get_descendants(self, version_id: str, depth: int) -> List[Dict[str, Any]]:
        """Get version descendants."""
        descendants = []
        
        def find_children(parent_id: str, current_depth: int):
            if current_depth >= depth:
                return
            
            # Find all versions where parent_version equals parent_id
            all_versions = self.list_versions(limit=1000)
            children = [v for v in all_versions if v.parent_version == parent_id]
            
            for child in children:
                descendants.append({
                    "version_id": child.version_id,
                    "version_number": child.version_number,
                    "created_at": child.created_at.isoformat() if child.created_at else None
                })
                
                # Recursively find children
                find_children(child.version_id, current_depth + 1)
        
        find_children(version_id, 0)
        return descendants