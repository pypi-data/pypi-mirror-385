"""
Pricing Manager for ISA Model SDK

Centralized pricing management for all AI providers and models.
Supports external configuration, dynamic updates, and multiple pricing models.
"""

import os
import json
import yaml
import logging
from typing import Dict, Optional, Any, Union, List
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from .types import Provider

logger = logging.getLogger(__name__)


@dataclass
class ModelPricing:
    """Pricing information for a model"""
    provider: str
    model_name: str
    input_cost: float = 0.0  # Cost per input unit
    output_cost: float = 0.0  # Cost per output unit
    unit_type: str = "token"  # "token", "character", "minute", "request", "image"
    base_cost: float = 0.0  # Fixed cost per request
    infrastructure_cost_per_hour: float = 0.0  # For self-hosted models
    currency: str = "USD"
    last_updated: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PricingManager:
    """
    Manages pricing information for all AI models and providers.
    
    Features:
    - Load pricing from YAML/JSON configuration files
    - Support multiple pricing models (per token, per minute, per request, etc.)
    - Dynamic pricing updates without code changes
    - Caching for performance
    - Fallback pricing when specific models aren't found
    
    Example:
        ```python
        from isa_model.core.pricing_manager import PricingManager
        
        pricing = PricingManager()
        
        # Get pricing for a specific model
        cost = pricing.calculate_cost(
            provider="openai",
            model_name="gpt-4o-mini",
            input_units=1000,
            output_units=500
        )
        
        # Check if pricing is available
        if pricing.has_pricing("openai", "gpt-4o"):
            print("Pricing available for GPT-4o")
        ```
    """
    
    def __init__(self, pricing_config_path: Optional[Path] = None):
        """Initialize pricing manager"""
        self.pricing_data: Dict[str, Dict[str, ModelPricing]] = {}
        self.config_path = pricing_config_path
        self._last_load_time: Optional[datetime] = None
        self._cache_ttl_hours = 24  # Reload pricing daily
        
        self._load_pricing_data()
        logger.info("PricingManager initialized")
    
    def _load_pricing_data(self):
        """Load pricing data from configuration files"""
        # Try to load from specified config path first
        if self.config_path and self.config_path.exists():
            self._load_from_file(self.config_path)
            return
        
        # Try to find configuration files in common locations
        possible_paths = [
            Path.cwd() / "pricing.yaml",
            Path.cwd() / "pricing.yml",
            Path.cwd() / "pricing.json",
            Path.cwd() / "config" / "pricing.yaml",
            self._find_project_root() / "pricing.yaml",
            self._find_project_root() / "config" / "pricing.yaml",
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Loading pricing from {path}")
                self._load_from_file(path)
                self.config_path = path
                return
        
        # If no config file found, load default pricing
        logger.warning("No pricing configuration file found, loading defaults")
        self._load_default_pricing()
    
    def _find_project_root(self) -> Path:
        """Find the project root directory"""
        current = Path(__file__).parent
        while current != current.parent:
            if (current / "pyproject.toml").exists() or (current / "setup.py").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _load_from_file(self, file_path: Path):
        """Load pricing from a YAML or JSON file"""
        try:
            with open(file_path, 'r') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            self._parse_pricing_data(data)
            self._last_load_time = datetime.now()
            logger.info(f"Loaded pricing for {len(self.pricing_data)} providers")
            
        except Exception as e:
            logger.error(f"Failed to load pricing from {file_path}: {e}")
            self._load_default_pricing()
    
    def _parse_pricing_data(self, data: Dict[str, Any]):
        """Parse pricing data from configuration"""
        self.pricing_data = {}
        
        providers_data = data.get("providers", data)  # Support both formats
        
        for provider_name, models_data in providers_data.items():
            self.pricing_data[provider_name] = {}
            
            for model_name, pricing_info in models_data.items():
                if isinstance(pricing_info, dict):
                    pricing = ModelPricing(
                        provider=provider_name,
                        model_name=model_name,
                        input_cost=pricing_info.get("input", 0.0),
                        output_cost=pricing_info.get("output", 0.0),
                        unit_type=pricing_info.get("unit_type", "token"),
                        base_cost=pricing_info.get("base_cost", 0.0),
                        infrastructure_cost_per_hour=pricing_info.get("infrastructure_cost_per_hour", 0.0),
                        currency=pricing_info.get("currency", "USD"),
                        metadata=pricing_info.get("metadata", {})
                    )
                    self.pricing_data[provider_name][model_name] = pricing
    
    def _load_default_pricing(self):
        """Load default pricing data as fallback"""
        default_pricing = {
            "openai": {
                "gpt-4o-mini": {"input": 0.00000015, "output": 0.0000006, "unit_type": "token"},
                "gpt-4o": {"input": 0.000005, "output": 0.000015, "unit_type": "token"},
                "gpt-4-turbo": {"input": 0.00001, "output": 0.00003, "unit_type": "token"},
                "gpt-4": {"input": 0.00003, "output": 0.00006, "unit_type": "token"},
                "gpt-3.5-turbo": {"input": 0.0000005, "output": 0.0000015, "unit_type": "token"},
                "text-embedding-3-small": {"input": 0.00000002, "output": 0.0, "unit_type": "token"},
                "text-embedding-3-large": {"input": 0.00000013, "output": 0.0, "unit_type": "token"},
                "whisper-1": {"input": 0.006, "output": 0.0, "unit_type": "minute"},
                "dall-e-3": {"input": 0.04, "output": 0.0, "unit_type": "image"},
            },
            "anthropic": {
                "claude-3-opus": {"input": 0.000015, "output": 0.000075, "unit_type": "token"},
                "claude-3-sonnet": {"input": 0.000003, "output": 0.000015, "unit_type": "token"},
                "claude-3-haiku": {"input": 0.00000025, "output": 0.00000125, "unit_type": "token"},
            },
            "replicate": {
                "black-forest-labs/flux-dev": {"input": 0.003, "output": 0.0, "unit_type": "image"},
                "meta/meta-llama-3-70b-instruct": {"input": 0.00000065, "output": 0.00000275, "unit_type": "token"},
            },
            "ollama": {
                "default": {"input": 0.0, "output": 0.0, "unit_type": "token"},
            },
            "modal": {
                "default": {"input": 0.0, "output": 0.0, "infrastructure_cost_per_hour": 0.4, "unit_type": "token"},
            }
        }
        
        self._parse_pricing_data({"providers": default_pricing})
        logger.info("Loaded default pricing data")
    
    def get_model_pricing(self, provider: str, model_name: str) -> Optional[ModelPricing]:
        """Get pricing information for a specific model"""
        self._refresh_if_needed()
        
        provider_data = self.pricing_data.get(provider, {})
        
        # Try exact match first
        if model_name in provider_data:
            return provider_data[model_name]
        
        # Try partial matches (for versioned models)
        for available_model, pricing in provider_data.items():
            if model_name.startswith(available_model) or available_model in model_name:
                return pricing
        
        # Try default for provider
        if "default" in provider_data:
            return provider_data["default"]
        
        return None
    
    def has_pricing(self, provider: str, model_name: str) -> bool:
        """Check if pricing is available for a model"""
        return self.get_model_pricing(provider, model_name) is not None
    
    def calculate_cost(self, 
                      provider: str, 
                      model_name: str, 
                      input_units: Union[int, float] = 0,
                      output_units: Union[int, float] = 0,
                      requests: int = 1) -> float:
        """
        Calculate the cost for using a model.
        
        Args:
            provider: Provider name (e.g., "openai", "anthropic")
            model_name: Model name (e.g., "gpt-4o-mini")
            input_units: Number of input units (tokens, characters, minutes, etc.)
            output_units: Number of output units
            requests: Number of requests made
            
        Returns:
            Total cost in USD
        """
        pricing = self.get_model_pricing(provider, model_name)
        if not pricing:
            logger.warning(f"No pricing found for {provider}/{model_name}")
            return 0.0
        
        total_cost = 0.0
        
        # Calculate variable costs based on usage
        if pricing.unit_type == "token":
            # Standard per-token pricing
            total_cost += (input_units / 1000000) * pricing.input_cost  # Cost per 1M tokens
            total_cost += (output_units / 1000000) * pricing.output_cost
        elif pricing.unit_type == "character":
            # Per-character pricing (TTS)
            total_cost += (input_units / 1000) * pricing.input_cost  # Cost per 1K characters
        elif pricing.unit_type == "minute":
            # Per-minute pricing (audio)
            total_cost += input_units * pricing.input_cost
        elif pricing.unit_type == "image":
            # Per-image pricing
            total_cost += input_units * pricing.input_cost
        elif pricing.unit_type == "request":
            # Per-request pricing
            total_cost += requests * pricing.input_cost
        
        # Add base cost per request
        total_cost += requests * pricing.base_cost
        
        return total_cost
    
    def get_cheapest_model(self, 
                          provider: Optional[str] = None,
                          unit_type: str = "token",
                          min_input_units: int = 1000) -> Optional[Dict[str, Any]]:
        """
        Find the cheapest model for a given usage pattern.
        
        Args:
            provider: Specific provider to search, or None for all providers
            unit_type: Type of units to optimize for
            min_input_units: Minimum expected input units for cost calculation
            
        Returns:
            Dictionary with provider, model_name, and estimated_cost
        """
        self._refresh_if_needed()
        
        candidates = []
        
        providers_to_check = [provider] if provider else self.pricing_data.keys()
        
        for prov in providers_to_check:
            if prov not in self.pricing_data:
                continue
                
            for model_name, pricing in self.pricing_data[prov].items():
                if pricing.unit_type != unit_type:
                    continue
                
                # Calculate cost for the given usage
                estimated_cost = self.calculate_cost(
                    prov, model_name, 
                    input_units=min_input_units, 
                    output_units=min_input_units
                )
                
                candidates.append({
                    "provider": prov,
                    "model_name": model_name,
                    "estimated_cost": estimated_cost,
                    "pricing": pricing
                })
        
        if not candidates:
            return None
        
        # Sort by cost and return cheapest
        candidates.sort(key=lambda x: x["estimated_cost"])
        return candidates[0]
    
    def get_provider_summary(self, provider: str) -> Dict[str, Any]:
        """Get summary of pricing for a provider"""
        self._refresh_if_needed()
        
        if provider not in self.pricing_data:
            return {"provider": provider, "models": [], "total_models": 0}
        
        models = []
        for model_name, pricing in self.pricing_data[provider].items():
            models.append({
                "model_name": model_name,
                "unit_type": pricing.unit_type,
                "input_cost": pricing.input_cost,
                "output_cost": pricing.output_cost,
                "base_cost": pricing.base_cost
            })
        
        return {
            "provider": provider,
            "models": models,
            "total_models": len(models)
        }
    
    def update_model_pricing(self, 
                           provider: str, 
                           model_name: str, 
                           input_cost: Optional[float] = None,
                           output_cost: Optional[float] = None,
                           **kwargs):
        """Update pricing for a specific model"""
        if provider not in self.pricing_data:
            self.pricing_data[provider] = {}
        
        if model_name not in self.pricing_data[provider]:
            self.pricing_data[provider][model_name] = ModelPricing(
                provider=provider,
                model_name=model_name
            )
        
        pricing = self.pricing_data[provider][model_name]
        
        if input_cost is not None:
            pricing.input_cost = input_cost
        if output_cost is not None:
            pricing.output_cost = output_cost
        
        for key, value in kwargs.items():
            if hasattr(pricing, key):
                setattr(pricing, key, value)
        
        pricing.last_updated = datetime.now()
        logger.info(f"Updated pricing for {provider}/{model_name}")
    
    def save_pricing_config(self, file_path: Optional[Path] = None):
        """Save current pricing to configuration file"""
        if file_path is None:
            file_path = self.config_path or Path.cwd() / "pricing.yaml"
        
        # Convert pricing data to serializable format
        config_data = {"providers": {}}
        
        for provider, models in self.pricing_data.items():
            config_data["providers"][provider] = {}
            for model_name, pricing in models.items():
                config_data["providers"][provider][model_name] = {
                    "input": pricing.input_cost,
                    "output": pricing.output_cost,
                    "unit_type": pricing.unit_type,
                    "base_cost": pricing.base_cost,
                    "infrastructure_cost_per_hour": pricing.infrastructure_cost_per_hour,
                    "currency": pricing.currency,
                    "metadata": pricing.metadata
                }
        
        try:
            with open(file_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            logger.info(f"Saved pricing configuration to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save pricing configuration: {e}")
    
    def _refresh_if_needed(self):
        """Refresh pricing data if cache is stale"""
        if self._last_load_time is None:
            return
        
        time_since_load = datetime.now() - self._last_load_time
        if time_since_load > timedelta(hours=self._cache_ttl_hours):
            logger.info("Refreshing pricing data (cache expired)")
            self._load_pricing_data()
    
    def get_all_providers(self) -> List[str]:
        """Get list of all providers with pricing data"""
        self._refresh_if_needed()
        return list(self.pricing_data.keys())
    
    def get_provider_models(self, provider: str) -> List[str]:
        """Get list of models for a provider"""
        self._refresh_if_needed()
        return list(self.pricing_data.get(provider, {}).keys())


# Global pricing manager instance
pricing_manager = PricingManager()

# Convenience functions
def get_model_cost(provider: str, model_name: str, input_units: int, output_units: int) -> float:
    """Calculate cost for a model usage"""
    return pricing_manager.calculate_cost(provider, model_name, input_units, output_units)

def has_pricing(provider: str, model_name: str) -> bool:
    """Check if pricing is available"""
    return pricing_manager.has_pricing(provider, model_name)