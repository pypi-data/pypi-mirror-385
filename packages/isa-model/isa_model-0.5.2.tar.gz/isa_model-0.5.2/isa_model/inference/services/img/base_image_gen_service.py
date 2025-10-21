from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, BinaryIO
from isa_model.inference.services.base_service import BaseService

class BaseImageGenService(BaseService):
    """Base class for image generation services with unified task dispatch"""
    
    async def invoke(
        self, 
        prompt: str,
        task: Optional[str] = None,
        **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        统一的任务分发方法 - Base类提供通用实现
        
        Args:
            prompt: 文本提示词
            task: 任务类型，支持多种图像生成任务
            **kwargs: 任务特定的附加参数
            
        Returns:
            Dict or List[Dict] containing generation results
        """
        task = task or "generate"
        
        # ==================== 图像生成类任务 ====================
        if task == "generate":
            num_images = kwargs.get("num_images", 1)
            if num_images == 1:
                return await self.generate_image(
                    prompt,
                    kwargs.get("negative_prompt"),
                    kwargs.get("width", 512),
                    kwargs.get("height", 512),
                    kwargs.get("num_inference_steps", 4),
                    kwargs.get("guidance_scale", 7.5),
                    kwargs.get("seed")
                )
            else:
                return await self.generate_images(
                    prompt,
                    num_images,
                    kwargs.get("negative_prompt"),
                    kwargs.get("width", 512),
                    kwargs.get("height", 512),
                    kwargs.get("num_inference_steps", 4),
                    kwargs.get("guidance_scale", 7.5),
                    kwargs.get("seed")
                )
        elif task == "generate_batch":
            return await self.generate_images(
                prompt,
                kwargs.get("num_images", 4),
                kwargs.get("negative_prompt"),
                kwargs.get("width", 512),
                kwargs.get("height", 512),
                kwargs.get("num_inference_steps", 4),
                kwargs.get("guidance_scale", 7.5),
                kwargs.get("seed")
            )
        elif task == "img2img":
            init_image = kwargs.get("init_image")
            if not init_image:
                raise ValueError("img2img task requires init_image parameter")
            return await self.image_to_image(
                prompt,
                init_image,
                kwargs.get("strength", 0.8),
                kwargs.get("negative_prompt"),
                kwargs.get("num_inference_steps", 4),
                kwargs.get("guidance_scale", 7.5),
                kwargs.get("seed")
            )
        elif task == "face_swap":
            target_image = kwargs.get("target_image")
            if not target_image:
                raise ValueError("face_swap task requires target_image parameter")
            if hasattr(self, 'face_swap'):
                return await self.face_swap(
                    swap_image=prompt,  # prompt contains the swap_image URL
                    target_image=target_image,
                    **{k: v for k, v in kwargs.items() if k != 'target_image'}
                )
            else:
                raise NotImplementedError(f"{self.__class__.__name__} does not support face_swap")
        elif task == "generate_sticker":
            if hasattr(self, 'generate_sticker'):
                return await self.generate_sticker(prompt, **kwargs)
            else:
                raise NotImplementedError(f"{self.__class__.__name__} does not support generate_sticker")
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support task: {task}")
    
    def get_supported_tasks(self) -> List[str]:
        """
        获取支持的任务列表
        
        Returns:
            List of supported task names
        """
        return ["generate", "generate_batch", "img2img"]
    
    @abstractmethod
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
        """
        Generate a single image from text prompt
        
        Args:
            prompt: Text description of the desired image
            negative_prompt: Text describing what to avoid in the image
            width: Image width in pixels
            height: Image height in pixels
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow the prompt
            seed: Random seed for reproducible results
            
        Returns:
            Dict containing generation results with keys:
            - image_data: Binary image data or PIL Image
            - format: Image format (e.g., 'png', 'jpg')
            - width: Actual image width
            - height: Actual image height
            - seed: Seed used for generation
        """
        pass
    
    @abstractmethod
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
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images from text prompt
        
        Args:
            prompt: Text description of the desired image
            num_images: Number of images to generate
            negative_prompt: Text describing what to avoid in the image
            width: Image width in pixels
            height: Image height in pixels
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow the prompt
            seed: Random seed for reproducible results
            
        Returns:
            List of generation result dictionaries
        """
        pass
    
    @abstractmethod
    async def image_to_image(
        self,
        prompt: str,
        init_image: Union[str, BinaryIO],
        strength: float = 0.8,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 4,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate image based on existing image and prompt
        
        Args:
            prompt: Text description of desired modifications
            init_image: Path to initial image or image data
            strength: How much to transform the initial image (0.0-1.0)
            negative_prompt: Text describing what to avoid
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow the prompt
            seed: Random seed for reproducible results
            
        Returns:
            Dict containing generation results
        """
        pass
    
    @abstractmethod
    def get_supported_sizes(self) -> List[Dict[str, int]]:
        """
        Get list of supported image dimensions
        
        Returns:
            List of dictionaries with 'width' and 'height' keys
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the image generation model
        
        Returns:
            Dict containing model information:
            - name: Model name
            - max_width: Maximum supported width
            - max_height: Maximum supported height
            - supports_negative_prompt: Whether negative prompts are supported
            - supports_img2img: Whether image-to-image is supported
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass
