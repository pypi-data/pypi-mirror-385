#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Replicate Face Swap Service
Specialized service for face swapping using the easel/advanced-face-swap model
"""

import os
import logging
from typing import Dict, Any, Union, Optional
import replicate

from ..base_image_gen_service import BaseImageGenService

logger = logging.getLogger(__name__)

class ReplicateFaceSwapService(BaseImageGenService):
    """
    Replicate Face Swap Service - $0.04 per generation
    Advanced face swapping with hair source control and gender options
    """
    
    def __init__(self, provider_name: str, model_name: str, **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        # Get configuration from centralized config manager
        provider_config = self.get_provider_config()
        
        try:
            self.api_token = provider_config.get("api_key") or provider_config.get("replicate_api_token")
            
            if not self.api_token:
                raise ValueError("Replicate API token not found in provider configuration")
            
            # Set API token
            os.environ["REPLICATE_API_TOKEN"] = self.api_token
            
            # Model path
            self.model_path = "easel/advanced-face-swap"
            
            # Statistics
            self.total_generation_count = 0
            
            logger.info(f"Initialized ReplicateFaceSwapService with model '{self.model_name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize Replicate Face Swap client: {e}")
            raise ValueError(f"Failed to initialize Replicate Face Swap client: {e}") from e

    async def face_swap(
        self,
        swap_image: Union[str, Any],
        target_image: Union[str, Any],
        hair_source: str = "target",
        user_gender: str = "default",
        user_b_gender: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """Perform face swap between two images"""

        # Extract user_id from kwargs for billing
        self._current_user_id = kwargs.get('user_id')

        input_data = {
            "swap_image": swap_image,
            "target_image": target_image,
            "hair_source": hair_source,
            "user_gender": user_gender,
            "user_b_gender": user_b_gender
        }

        return await self._generate_internal(input_data)

    async def _generate_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal generation method"""
        try:
            logger.info("Starting face swap generation...")
            
            # Call Replicate API
            output = await replicate.async_run(self.model_path, input=input_data)
            
            # Process output - convert FileOutput objects to URL strings
            if isinstance(output, list):
                raw_urls = output
            else:
                raw_urls = [output]
            
            # Convert to string URLs
            urls = []
            for url in raw_urls:
                if hasattr(url, 'url'):
                    urls.append(str(url.url))
                else:
                    urls.append(str(url))

            # Update statistics
            self.total_generation_count += len(urls)
            
            # Calculate cost
            cost = self._calculate_cost(len(urls))
            
            # Track billing information
            if self._current_user_id:
                await self._publish_billing_event(
                    user_id=self._current_user_id,
                    service_type="image_generation",
                    operation="face_swap",
                    input_tokens=0,
                    output_tokens=0,
                    input_units=2,  # Two input images
                    output_units=len(urls),  # Generated images count
                    metadata={
                        "model": self.model_name,
                        "generation_type": "face_swap",
                        "image_count": len(urls),
                        "cost_usd": cost,
                        "hair_source": input_data.get("hair_source", "target")
                    }
                )
            
            # Return URLs
            result = {
                "urls": urls,
                "url": urls[0] if urls else None,
                "format": "jpg",  # Default format
                "count": len(urls),
                "cost_usd": cost,
                "metadata": {
                    "model": self.model_name,
                    "input": input_data,
                    "generation_count": len(urls)
                }
            }
            
            logger.info(f"Face swap completed: {len(urls)} images, cost: ${cost:.6f}")
            return result
            
        except Exception as e:
            logger.error(f"Face swap failed: {e}")
            raise

    def _calculate_cost(self, image_count: int) -> float:
        """Calculate generation cost - $0.04 per generation"""
        return image_count * 0.04

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        total_cost = self.total_generation_count * 0.04
        
        return {
            "total_generation_count": self.total_generation_count,
            "total_cost_usd": total_cost,
            "cost_per_generation": 0.04,
            "model": self.model_name
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "name": self.model_name,
            "type": "face_swap",
            "cost_per_generation": 0.04,
            "supports_hair_source": True,
            "supports_gender_control": True,
            "hair_source_options": ["target", "swap"],
            "gender_options": ["default", "male", "female"]
        }

    async def load(self) -> None:
        """Load service"""
        if not self.api_token:
            raise ValueError("Missing Replicate API token")
        logger.info(f"Replicate Face Swap service ready with model: {self.model_name}")

    async def unload(self) -> None:
        """Unload service"""
        logger.info(f"Unloading Replicate Face Swap service: {self.model_name}")

    async def close(self):
        """Close service"""
        await self.unload()

    # Abstract method implementations (not supported by face swap)
    async def generate_image(self, prompt: str, negative_prompt=None, width: int = 512, height: int = 512, num_inference_steps: int = 20, guidance_scale: float = 7.5, seed=None) -> Dict[str, Any]:
        """Not supported - use face_swap instead"""
        raise NotImplementedError("Face swap requires two images - use face_swap method")

    async def generate_images(self, prompt: str, num_images: int = 1, negative_prompt=None, width: int = 512, height: int = 512, num_inference_steps: int = 20, guidance_scale: float = 7.5, seed=None) -> list[Dict[str, Any]]:
        """Not supported - use face_swap instead"""
        raise NotImplementedError("Face swap requires two images - use face_swap method")

    async def image_to_image(self, prompt: str, init_image, strength: float = 0.8, negative_prompt=None, num_inference_steps: int = 20, guidance_scale: float = 7.5, seed=None) -> Dict[str, Any]:
        """Not supported - use face_swap instead"""
        raise NotImplementedError("Face swap requires specific face swap method")

    def get_supported_sizes(self) -> list[Dict[str, int]]:
        """Get supported image sizes"""
        return [{"width": 512, "height": 512}, {"width": 768, "height": 768}, {"width": 1024, "height": 1024}]