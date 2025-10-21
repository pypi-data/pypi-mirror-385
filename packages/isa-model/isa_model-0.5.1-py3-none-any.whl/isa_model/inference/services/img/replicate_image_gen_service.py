#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Replicate Image Generation Service (Orchestrator)
Delegates to specialized services: FLUX, FLUX Kontext, Sticker Maker, Face Swap
"""

import logging
from typing import Dict, Any, Optional, Union

from .base_image_gen_service import BaseImageGenService
from .services.replicate_flux import ReplicateFluxService
from .services.replicate_flux_kontext import ReplicateFluxKontextService
from .services.replicate_sticker_maker import ReplicateStickerMakerService
from .services.replicate_face_swap import ReplicateFaceSwapService

logger = logging.getLogger(__name__)

class ReplicateImageGenService(BaseImageGenService):
    """
    Replicate Image Generation Service (Orchestrator)
    Delegates to specialized services based on model type:
    - flux-schnell: Text-to-image generation
    - flux-kontext-pro: Image-to-image generation
    - sticker-maker: Sticker generation
    - face-swap: Face swapping
    """
    
    def __init__(self, provider_name: str, model_name: str, **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        # Initialize the appropriate specialized service
        self._delegate_service = self._create_delegate_service()
        
        logger.info(f"Initialized ReplicateImageGenService orchestrator with model '{self.model_name}'")

    def _create_delegate_service(self) -> BaseImageGenService:
        """Create the appropriate specialized service based on model name"""
        if "flux-schnell" in self.model_name:
            return ReplicateFluxService(self.provider_name, self.model_name)
        elif "flux-kontext-pro" in self.model_name:
            return ReplicateFluxKontextService(self.provider_name, self.model_name)
        elif "sticker-maker" in self.model_name:
            return ReplicateStickerMakerService(self.provider_name, self.model_name)
        elif "face-swap" in self.model_name:
            return ReplicateFaceSwapService(self.provider_name, self.model_name)
        else:
            # Default to FLUX for unknown models
            return ReplicateFluxService(self.provider_name, self.model_name)

    async def generate_image(
        self, 
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 4,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate single image - delegates to appropriate service"""
        if hasattr(self._delegate_service, 'generate_image'):
            return await self._delegate_service.generate_image(
                prompt, negative_prompt, width, height, 
                num_inference_steps, guidance_scale, seed
            )
        else:
            raise NotImplementedError(f"generate_image not supported by {type(self._delegate_service).__name__}")

    async def image_to_image(
        self,
        prompt: str,
        init_image: Union[str, Any],
        strength: float = 0.8,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Image-to-image generation - delegates to appropriate service"""
        if hasattr(self._delegate_service, 'image_to_image'):
            return await self._delegate_service.image_to_image(
                prompt, init_image, strength, negative_prompt,
                num_inference_steps, guidance_scale, seed
            )
        else:
            raise NotImplementedError(f"image_to_image not supported by {type(self._delegate_service).__name__}")

    async def generate_sticker(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate sticker - delegates to sticker maker service"""
        if hasattr(self._delegate_service, 'generate_sticker'):
            return await self._delegate_service.generate_sticker(prompt, **kwargs)
        else:
            raise NotImplementedError(f"generate_sticker not supported by {type(self._delegate_service).__name__}")

    async def face_swap(
        self,
        swap_image: Union[str, Any],
        target_image: Union[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Face swap - delegates to face swap service"""
        if hasattr(self._delegate_service, 'face_swap'):
            return await self._delegate_service.face_swap(swap_image, target_image, **kwargs)
        else:
            raise NotImplementedError(f"face_swap not supported by {type(self._delegate_service).__name__}")

    # Delegation methods for common functionality
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics - delegates to service"""
        return self._delegate_service.get_generation_stats()

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information - delegates to service"""
        return self._delegate_service.get_model_info()

    async def load(self) -> None:
        """Load service - delegates to service"""
        await self._delegate_service.load()

    async def unload(self) -> None:
        """Unload service - delegates to service"""
        await self._delegate_service.unload()

    async def close(self):
        """Close service - delegates to service"""
        await self._delegate_service.close()

    # Abstract method implementations for delegation
    async def generate_images(self, prompt: str, num_images: int = 1, negative_prompt=None, width: int = 512, height: int = 512, num_inference_steps: int = 20, guidance_scale: float = 7.5, seed=None) -> list[Dict[str, Any]]:
        """Generate multiple images - delegates to service"""
        if hasattr(self._delegate_service, 'generate_images'):
            return await self._delegate_service.generate_images(prompt, num_images, negative_prompt, width, height, num_inference_steps, guidance_scale, seed)
        else:
            raise NotImplementedError(f"generate_images not supported by {type(self._delegate_service).__name__}")

    def get_supported_sizes(self) -> list[Dict[str, int]]:
        """Get supported sizes - delegates to service"""
        if hasattr(self._delegate_service, 'get_supported_sizes'):
            return self._delegate_service.get_supported_sizes()
        else:
            return [{"width": 512, "height": 512}, {"width": 1024, "height": 1024}]

