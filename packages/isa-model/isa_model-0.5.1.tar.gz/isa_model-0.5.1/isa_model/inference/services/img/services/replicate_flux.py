#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Replicate FLUX Schnell Service
Specialized service for text-to-image generation using FLUX Schnell model
"""

import os
import logging
from typing import Dict, Any, Optional
import replicate

from ..base_image_gen_service import BaseImageGenService

logger = logging.getLogger(__name__)

class ReplicateFluxService(BaseImageGenService):
    """
    Replicate FLUX Schnell Service - $3 per 1000 images
    Ultra-fast text-to-image generation for rapid prototyping
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
            self.model_path = "black-forest-labs/flux-schnell"
            
            # Statistics
            self.total_generation_count = 0
            
            logger.info(f"Initialized ReplicateFluxService with model '{self.model_name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize Replicate FLUX client: {e}")
            raise ValueError(f"Failed to initialize Replicate FLUX client: {e}") from e

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 4,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image from text prompt using FLUX Schnell"""

        # Extract user_id from kwargs for billing
        self._current_user_id = kwargs.get('user_id')

        input_data = {
            "prompt": prompt,
            "go_fast": True,
            "megapixels": "1",
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "output_format": "jpg",
            "output_quality": 90,
            "num_inference_steps": num_inference_steps
        }

        return await self._generate_internal(input_data)

    async def _generate_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal generation method"""
        try:
            logger.info(f"Starting FLUX generation with prompt: {input_data.get('prompt', '')[:50]}...")
            
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
                    operation="text_to_image",
                    input_tokens=0,
                    output_tokens=0,
                    input_units=1,  # Input prompt
                    output_units=len(urls),  # Generated images count
                    metadata={
                        "model": self.model_name,
                        "prompt": input_data.get("prompt", "")[:100],
                        "generation_type": "t2i",
                        "image_count": len(urls),
                        "cost_usd": cost
                    }
                )
            
            # Return URLs
            result = {
                "urls": urls,
                "url": urls[0] if urls else None,
                "format": input_data.get("output_format", "jpg"),
                "aspect_ratio": input_data.get("aspect_ratio", "1:1"),
                "count": len(urls),
                "cost_usd": cost,
                "metadata": {
                    "model": self.model_name,
                    "input": input_data,
                    "generation_count": len(urls)
                }
            }
            
            logger.info(f"FLUX generation completed: {len(urls)} images, cost: ${cost:.6f}")
            return result
            
        except Exception as e:
            logger.error(f"FLUX generation failed: {e}")
            raise

    def _calculate_cost(self, image_count: int) -> float:
        """Calculate generation cost - $3 per 1000 images"""
        return (image_count / 1000) * 3.0

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        total_cost = (self.total_generation_count / 1000) * 3.0
        
        return {
            "total_generation_count": self.total_generation_count,
            "total_cost_usd": total_cost,
            "cost_per_1000_images": 3.0,
            "model": self.model_name
        }

    def get_supported_aspect_ratios(self) -> list[str]:
        """Get supported aspect ratios"""
        return ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "name": self.model_name,
            "type": "text_to_image",
            "cost_per_1000_images": 3.0,
            "supports_negative_prompt": False,
            "max_inference_steps": 4,
            "supported_formats": ["jpg", "png", "webp"],
            "supported_aspect_ratios": self.get_supported_aspect_ratios()
        }

    async def load(self) -> None:
        """Load service"""
        if not self.api_token:
            raise ValueError("Missing Replicate API token")
        logger.info(f"Replicate FLUX service ready with model: {self.model_name}")

    async def unload(self) -> None:
        """Unload service"""
        logger.info(f"Unloading Replicate FLUX service: {self.model_name}")

    async def close(self):
        """Close service"""
        await self.unload()

    async def generate_images(
        self, 
        prompt: str,
        num_images: int = 1,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 4,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> list[Dict[str, Any]]:
        """Generate multiple images"""
        results = []
        for i in range(num_images):
            current_seed = seed + i if seed else None
            result = await self.generate_image(
                prompt=prompt,
                go_fast=True,
                megapixels="1",
                num_outputs=1,
                aspect_ratio="1:1",
                output_format="jpg",
                output_quality=90,
                num_inference_steps=num_inference_steps
            )
            results.append(result)
        return results

    def get_supported_sizes(self) -> list[Dict[str, int]]:
        """Get supported image sizes"""
        return [
            {"width": 512, "height": 512},
            {"width": 768, "height": 768},
            {"width": 1024, "height": 1024},
        ]

    async def image_to_image(self, prompt: str, init_image, strength: float = 0.8, negative_prompt=None, num_inference_steps: int = 20, guidance_scale: float = 7.5, seed=None) -> Dict[str, Any]:
        """Not supported by FLUX Schnell - text-to-image only"""
        raise NotImplementedError("FLUX Schnell only supports text-to-image generation")