from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, BinaryIO
import logging

from isa_model.inference.services.base_service import BaseService
from isa_model.inference.services.vision.helpers.image_utils import (
    get_image_data, prepare_image_base64, prepare_image_data_url, 
    get_image_mime_type, get_image_dimensions, validate_image_format
)

logger = logging.getLogger(__name__)

class BaseVisionService(BaseService):
    """Base class for vision understanding services with common task implementations"""
    
    async def invoke(
        self, 
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        task: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一的任务分发方法 - 基于6个核心任务的设计
        
        Args:
            image: Path to image file or image data
            prompt: Optional text prompt/question about the image
            task: Core task type (analyze, describe, extract, detect, classify, compare)
            **kwargs: Additional task-specific parameters including:
                - target: Sub-task specification (e.g., "text"/"table" for extract, "objects"/"ui" for detect)
                - max_tokens: Maximum tokens for text generation
                - confidence_threshold: Confidence threshold for detection
                - categories: Categories for classification
                - image2: Second image for comparison
            
        Returns:
            Dict containing task results
        """
        task = task or "analyze"
        
        # Core task dispatch with parameterized sub-tasks
        if task == "analyze" and hasattr(self, 'analyze_image'):
            return await self.analyze_image(image, prompt, kwargs.get("max_tokens", 1000))
            
        elif task == "describe" and hasattr(self, 'describe_image'):
            return await self.describe_image(image, kwargs.get("detail_level", "medium"))
            
        elif task == "extract":
            # Extract with target specification
            target = kwargs.get("target", "text")
            if target == "table" and hasattr(self, 'extract_table_data'):
                return await self.extract_table_data(image, kwargs.get("table_format", "json"))
            elif hasattr(self, 'extract_text'):
                return await self.extract_text(image)
            else:
                raise NotImplementedError(f"{self.__class__.__name__} does not support extract task")
                
        elif task == "detect":
            # Detect with target specification
            target = kwargs.get("target", "objects")
            if target == "ui" and hasattr(self, 'detect_ui_elements'):
                return await self.detect_ui_elements(image, 
                    kwargs.get("element_types"), 
                    kwargs.get("confidence_threshold", 0.5))
            elif target == "coordinates" and hasattr(self, 'get_object_coordinates'):
                return await self.get_object_coordinates(image, kwargs.get("object_name", ""))
            elif hasattr(self, 'detect_objects'):
                return await self.detect_objects(image, kwargs.get("confidence_threshold", 0.5))
            else:
                raise NotImplementedError(f"{self.__class__.__name__} does not support detect task")
                
        elif task == "classify" and hasattr(self, 'classify_image'):
            return await self.classify_image(image, kwargs.get("categories"))
            
        elif task == "compare" and hasattr(self, 'compare_images'):
            return await self.compare_images(image, kwargs.get("image2"))
            
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support task: {task}")
    
    async def analyze_image(
        self, 
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        通用图像分析 - Provider可选实现
        
        Args:
            image: Path to image file or image data
            prompt: Optional text prompt/question about the image
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict containing analysis results with keys:
            - text: Description or answer about the image
            - confidence: Confidence score (if available)
            - detected_objects: List of detected objects (if available)
            - metadata: Additional metadata about the analysis
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support analyze_image task")

    
    
    
    async def close(self):
        """Cleanup resources - default implementation does nothing"""
        pass
    
    def get_supported_tasks(self) -> List[str]:
        """
        获取provider支持的核心任务列表
        
        Returns:
            List of core task names (analyze, describe, extract, detect, classify, compare)
        """
        supported = []
        
        # Check core task support based on implemented methods
        task_method_map = {
            'analyze': 'analyze_image',
            'describe': 'describe_image',
            'extract': 'extract_text',  # Basic extract support
            'detect': 'detect_objects',  # Basic detect support
            'classify': 'classify_image',
            'compare': 'compare_images'
        }
        
        for task_name, method_name in task_method_map.items():
            if hasattr(self, method_name):
                try:
                    # Check if method is actually implemented (not just raising NotImplementedError)
                    import inspect
                    method = getattr(self, method_name)
                    if callable(method):
                        source = inspect.getsource(method)
                        # If it's not just raising NotImplementedError, consider it supported
                        if not ('raise NotImplementedError' in source and len(source.split('\n')) < 10):
                            supported.append(task_name)
                except:
                    # If we can't inspect, assume it's supported if the method exists
                    supported.append(task_name)
                
        return supported
    
    # ==================== COMMON TASK IMPLEMENTATIONS ====================
    # 为每个provider提供可选的默认实现，provider可以覆盖这些方法
    
    async def analyze_images(
        self, 
        images: List[Union[str, BinaryIO]],
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        批量图像分析 - Provider可选实现
        默认实现：如果provider支持analyze_image，则逐个调用
        """
        if hasattr(self, 'analyze_image'):
            results = []
            for image in images:
                try:
                    result = await self.analyze_image(image, prompt, max_tokens)
                    results.append(result)
                except NotImplementedError:
                    raise NotImplementedError(f"{self.__class__.__name__} does not support analyze_images task")
            return results
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support analyze_images task")
    
    async def describe_image(
        self, 
        image: Union[str, BinaryIO],
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        图像描述 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support describe_image task")
    
    async def extract_text(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """
        文本提取(OCR) - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support extract_text task")
    
    async def detect_objects(
        self, 
        image: Union[str, BinaryIO],
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        物体检测 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support detect_objects task")
    
    async def get_object_coordinates(
        self,
        image: Union[str, BinaryIO],
        object_name: str
    ) -> Dict[str, Any]:
        """
        获取对象坐标 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support get_object_coordinates task")
    
    async def classify_image(
        self, 
        image: Union[str, BinaryIO],
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        图像分类 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support classify_image task")
    
    async def compare_images(
        self, 
        image1: Union[str, BinaryIO],
        image2: Union[str, BinaryIO]
    ) -> Dict[str, Any]:
        """
        图像比较 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support compare_images task")
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的图像格式 - Provider应该实现
        """
        return ['jpg', 'jpeg', 'png', 'gif', 'webp']  # 通用格式
    
    def get_max_image_size(self) -> Dict[str, int]:
        """
        获取最大图像尺寸 - Provider应该实现
        """
        return {"width": 2048, "height": 2048, "file_size_mb": 10}  # 通用限制
    
    # ==================== UTILITY METHODS ====================
    
    def _parse_coordinates_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本响应中解析对象坐标 - 使用统一的解析工具
        """
        from isa_model.inference.services.vision.helpers.image_utils import parse_coordinates_from_text
        return parse_coordinates_from_text(text)
    
    def _parse_center_coordinates_from_text(self, text: str) -> tuple[bool, Optional[List[int]], str]:
        """
        从结构化文本响应中解析中心坐标 - 使用统一的解析工具
        """
        from isa_model.inference.services.vision.helpers.image_utils import parse_center_coordinates_from_text
        return parse_center_coordinates_from_text(text)
