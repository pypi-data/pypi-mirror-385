#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenAI DALL-E Image Generation Service
Supports DALL-E 2 and DALL-E 3 models
"""

import os
import logging
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI

from ..base_image_gen_service import BaseImageGenService

logger = logging.getLogger(__name__)

class OpenAIDALLEService(BaseImageGenService):
    """
    OpenAI DALL-E image generation service
    Supports both DALL-E 2 and DALL-E 3
    """

    def __init__(self, provider_name: str, model_name: str = "dall-e-3", **kwargs):
        super().__init__(provider_name, model_name, **kwargs)

        # Get configuration from centralized config manager
        provider_config = self.get_provider_config()

        # Initialize AsyncOpenAI client
        try:
            if not provider_config.get("api_key"):
                raise ValueError("OpenAI API key not found in provider configuration")

            self.client = AsyncOpenAI(
                api_key=provider_config["api_key"],
                base_url=provider_config.get("base_url", "https://api.openai.com/v1"),
                organization=provider_config.get("organization")
            )

            logger.info(f"Initialized OpenAIDALLEService with model '{self.model_name}'")

        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ValueError(f"Failed to initialize OpenAI client: {e}") from e

        self.total_generation_count = 0

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a single image using DALL-E

        Args:
            prompt: Text description of desired image
            negative_prompt: Not supported by DALL-E (ignored)
            width: Image width (must match DALL-E specs)
            height: Image height (must match DALL-E specs)
            num_inference_steps: Not used by DALL-E (ignored)
            guidance_scale: Not used by DALL-E (ignored)
            seed: Not supported by DALL-E (ignored)

        Returns:
            Dict with image_url and metadata
        """
        try:
            # Extract user_id from kwargs for billing
            self._current_user_id = getattr(self, '_current_user_id', None)

            # Determine size based on model
            if self.model_name == "dall-e-3":
                # DALL-E 3 supports: 1024x1024, 1792x1024, 1024x1792
                if width == height == 1024:
                    size = "1024x1024"
                elif width == 1792 and height == 1024:
                    size = "1792x1024"
                elif width == 1024 and height == 1792:
                    size = "1024x1792"
                else:
                    # Default to square
                    size = "1024x1024"
                    logger.warning(f"Unsupported size {width}x{height} for DALL-E 3, using 1024x1024")
            else:
                # DALL-E 2 supports: 256x256, 512x512, 1024x1024
                if width == height:
                    if width >= 1024:
                        size = "1024x1024"
                    elif width >= 512:
                        size = "512x512"
                    else:
                        size = "256x256"
                else:
                    size = "1024x1024"
                    logger.warning(f"DALL-E 2 only supports square images, using 1024x1024")

            # Generate image
            response = await self.client.images.generate(
                model=self.model_name,
                prompt=prompt,
                n=1,
                size=size,
                response_format="url"
            )

            # Track generation count
            self.total_generation_count += 1

            # Get image URL
            image_url = response.data[0].url

            # Calculate cost based on model and size
            cost = self._calculate_cost(size)

            # Track usage for billing
            if self._current_user_id:
                await self._publish_billing_event(
                    user_id=self._current_user_id,
                    service_type="image_generation",
                    operation="generate",
                    input_tokens=len(prompt.split()),
                    output_tokens=0,
                    input_units=1,
                    output_units=1,
                    metadata={
                        "model": self.model_name,
                        "size": size,
                        "prompt_length": len(prompt),
                        "cost_usd": cost
                    }
                )

            result = {
                "image_url": image_url,
                "revised_prompt": getattr(response.data[0], 'revised_prompt', None),  # DALL-E 3 feature
                "metadata": {
                    "model": self.model_name,
                    "provider": "openai",
                    "size": size,
                    "cost_usd": cost
                }
            }

            logger.info(f"DALL-E image generated: {image_url}, cost: ${cost:.4f}")
            return result

        except Exception as e:
            logger.error(f"DALL-E generation failed: {e}")
            raise

    def _calculate_cost(self, size: str) -> float:
        """
        Calculate cost based on DALL-E pricing

        DALL-E 3:
        - 1024×1024: $0.040/image (standard), $0.080/image (HD)
        - 1024×1792, 1792×1024: $0.080/image (standard), $0.120/image (HD)

        DALL-E 2:
        - 1024×1024: $0.020/image
        - 512×512: $0.018/image
        - 256×256: $0.016/image
        """
        if self.model_name == "dall-e-3":
            if size == "1024x1024":
                return 0.040  # Standard quality
            else:  # 1792x1024 or 1024x1792
                return 0.080  # Standard quality
        else:  # dall-e-2
            if size == "1024x1024":
                return 0.020
            elif size == "512x512":
                return 0.018
            else:  # 256x256
                return 0.016

    async def generate_images(
        self,
        prompt: str,
        num_images: int = 1,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Generate multiple images"""
        # DALL-E 3 only supports n=1, so we generate sequentially
        results = []
        for _ in range(num_images):
            result = await self.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                seed=seed
            )
            results.append(result)
        return results

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        avg_cost = 0.040 if self.model_name == "dall-e-3" else 0.020
        total_cost = self.total_generation_count * avg_cost

        return {
            "total_generation_count": self.total_generation_count,
            "total_cost_usd": total_cost,
            "avg_cost_per_image": avg_cost,
            "model": self.model_name
        }

    def get_supported_sizes(self) -> List[Dict[str, int]]:
        """Get supported image sizes"""
        if self.model_name == "dall-e-3":
            return [
                {"width": 1024, "height": 1024},
                {"width": 1792, "height": 1024},
                {"width": 1024, "height": 1792},
            ]
        else:  # dall-e-2
            return [
                {"width": 256, "height": 256},
                {"width": 512, "height": 512},
                {"width": 1024, "height": 1024},
            ]

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "name": self.model_name,
            "type": "text_to_image",
            "supports_negative_prompt": False,
            "supports_hd_quality": self.model_name == "dall-e-3",
            "supports_style": self.model_name == "dall-e-3",
            "max_prompt_length": 4000,
            "supported_sizes": self.get_supported_sizes()
        }

    async def image_to_image(
        self,
        input_image: str,
        prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Image-to-image transformation (not supported by DALL-E)
        DALL-E only supports text-to-image generation
        """
        raise NotImplementedError("DALL-E does not support image-to-image transformation. Use generate_image instead.")

    async def load(self) -> None:
        """Load service"""
        logger.info(f"OpenAI DALL-E service ready with model: {self.model_name}")

    async def unload(self) -> None:
        """Unload service"""
        logger.info(f"Unloading OpenAI DALL-E service: {self.model_name}")

    async def close(self):
        """Close service"""
        await self.unload()
