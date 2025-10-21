#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Replicate Sticker Maker Service
Specialized service for generating stickers using the fofr/sticker-maker model
"""

import os
import logging
from typing import Dict, Any, Optional
import replicate

from ..base_image_gen_service import BaseImageGenService

logger = logging.getLogger(__name__)

class ReplicateStickerMakerService(BaseImageGenService):
    """
    Replicate Sticker Maker Service - $0.0024 per generation
    Specialized for creating cute stickers from text prompts
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
            self.model_path = "fofr/sticker-maker:4acb778eb059772225ec213948f0660867b2e03f277448f18cf1800b96a65a1a"
            
            # Statistics
            self.total_generation_count = 0
            
            logger.info(f"Initialized ReplicateStickerMakerService with model '{self.model_name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize Replicate Sticker Maker client: {e}")
            raise ValueError(f"Failed to initialize Replicate Sticker Maker client: {e}") from e

    async def generate_sticker(
        self,
        prompt: str,
        steps: int = 17,
        width: int = 1152,
        height: int = 1152,
        output_format: str = "webp",
        output_quality: int = 100,
        negative_prompt: str = "",
        number_of_images: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate sticker from text prompt"""

        # Extract user_id from kwargs for billing
        self._current_user_id = kwargs.get('user_id')

        input_data = {
            "steps": steps,
            "width": width,
            "height": height,
            "prompt": prompt,
            "output_format": output_format,
            "output_quality": output_quality,
            "negative_prompt": negative_prompt,
            "number_of_images": number_of_images
        }

        return await self._generate_internal(input_data)

    async def _generate_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal generation method"""
        try:
            logger.info(f"Starting sticker generation with prompt: {input_data.get('prompt', '')[:50]}...")
            
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
                    operation="sticker_generation",
                    input_tokens=0,
                    output_tokens=0,
                    input_units=1,  # Input prompt
                    output_units=len(urls),  # Generated stickers count
                    metadata={
                        "model": self.model_name,
                        "prompt": input_data.get("prompt", "")[:100],
                        "generation_type": "sticker",
                        "image_count": len(urls),
                        "cost_usd": cost
                    }
                )
            
            # Return URLs
            result = {
                "urls": urls,
                "url": urls[0] if urls else None,
                "format": input_data.get("output_format", "webp"),
                "width": input_data.get("width", 1152),
                "height": input_data.get("height", 1152),
                "count": len(urls),
                "cost_usd": cost,
                "metadata": {
                    "model": self.model_name,
                    "input": input_data,
                    "generation_count": len(urls)
                }
            }
            
            logger.info(f"Sticker generation completed: {len(urls)} stickers, cost: ${cost:.6f}")
            return result
            
        except Exception as e:
            logger.error(f"Sticker generation failed: {e}")
            raise

    def _calculate_cost(self, image_count: int) -> float:
        """Calculate generation cost - $0.0024 per generation"""
        return image_count * 0.0024

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        total_cost = self.total_generation_count * 0.0024
        
        return {
            "total_generation_count": self.total_generation_count,
            "total_cost_usd": total_cost,
            "cost_per_generation": 0.0024,
            "model": self.model_name
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "name": self.model_name,
            "type": "sticker_generation",
            "cost_per_generation": 0.0024,
            "supports_negative_prompt": True,
            "max_width": 1152,
            "max_height": 1152,
            "output_formats": ["webp", "jpg", "png"]
        }

    async def load(self) -> None:
        """Load service"""
        if not self.api_token:
            raise ValueError("Missing Replicate API token")
        logger.info(f"Replicate Sticker Maker service ready with model: {self.model_name}")

    async def unload(self) -> None:
        """Unload service"""
        logger.info(f"Unloading Replicate Sticker Maker service: {self.model_name}")

    async def close(self):
        """Close service"""
        await self.unload()

    async def generate_image(
        self, 
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 17,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate single sticker"""
        return await self.generate_sticker(
            prompt=prompt,
            steps=num_inference_steps,
            width=width,
            height=height,
            negative_prompt=negative_prompt or ""
        )

    async def generate_images(
        self, 
        prompt: str,
        num_images: int = 1,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 17,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> list[Dict[str, Any]]:
        """Generate multiple stickers"""
        results = []
        for i in range(num_images):
            result = await self.generate_sticker(
                prompt=prompt,
                steps=num_inference_steps,
                width=width,
                height=height,
                negative_prompt=negative_prompt or "",
                number_of_images=1
            )
            results.append(result)
        return results

    async def image_to_image(
        self,
        prompt: str,
        init_image,
        strength: float = 0.8,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 17,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Not supported by sticker maker"""
        raise NotImplementedError("Sticker maker does not support image-to-image generation")

    def get_supported_sizes(self) -> list[Dict[str, int]]:
        """Get supported image sizes"""
        return [
            {"width": 1152, "height": 1152},
            {"width": 1024, "height": 1024},
            {"width": 768, "height": 768},
        ]