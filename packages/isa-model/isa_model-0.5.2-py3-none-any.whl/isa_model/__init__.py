"""
isA_Model - A simple interface for AI model integration

Main Components:
- ISAModel: Sync OpenAI-compatible client (NEW!)
- AsyncISAModel: Async OpenAI-compatible client (NEW!)
- AIFactory: Direct service access
- ISAModelClient: Legacy unified client (deprecated, use ISAModel instead)
"""

__version__ = "0.5.0"

# New OpenAI-compatible clients (recommended)
from isa_model.inference_client import ISAModel, AsyncISAModel

# Legacy support - deprecated, use ISAModel/AsyncISAModel instead
try:
    from isa_model.client import ISAModelClient, create_client
    _legacy_available = True
except ImportError:
    ISAModelClient = None
    create_client = None
    _legacy_available = False

# Direct service access
from isa_model.inference.ai_factory import AIFactory

# Core components for advanced usage
try:
    from isa_model.core.models.model_manager import ModelManager
    from isa_model.core.config import ConfigManager
    _core_available = True
except ImportError:
    ModelManager = None
    ConfigManager = None
    _core_available = False

__all__ = [
    "ISAModel",
    "AsyncISAModel",
    "AIFactory"
]

if _legacy_available:
    __all__.extend(["ISAModelClient", "create_client"])

if _core_available:
    __all__.extend(["ModelManager", "ConfigManager"])
