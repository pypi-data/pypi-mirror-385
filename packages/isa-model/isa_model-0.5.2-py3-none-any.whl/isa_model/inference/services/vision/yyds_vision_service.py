from typing import Dict, Any, Union, List, Optional, BinaryIO
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from isa_model.inference.services.vision.base_vision_service import BaseVisionService
from isa_model.inference.services.vision.helpers.image_utils import prepare_image_base64
from isa_model.inference.services.vision.helpers.vision_prompts import VisionPromptMixin
from isa_model.core.types import ServiceType
import logging

logger = logging.getLogger(__name__)

class YydsVisionService(BaseVisionService, VisionPromptMixin):
    """YYDS Vision service using centralized config management"""
    
    def __init__(self, provider_name: str, model_name: str = "gpt-4o-mini", **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        # Get configuration from centralized config manager
        provider_config = self.get_provider_config()
        
        # Initialize AsyncOpenAI client with centralized configuration
        try:
            if not provider_config.get("api_key"):
                raise ValueError("YYDS API key not found in provider configuration")
            
            self._client = AsyncOpenAI(
                api_key=provider_config["api_key"],
                base_url=provider_config.get("api_base_url", "https://api.openai.com/v1"),
                organization=provider_config.get("organization")
            )
            
            logger.info(f"Initialized YydsVisionService with model {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize YYDS client: {e}")
            raise ValueError(f"Failed to initialize YYDS client. Check your API key configuration: {e}") from e
        
        self.max_tokens = provider_config.get('max_tokens', 1000)
        self.temperature = provider_config.get('temperature', 0.7)
    
    @property
    def client(self) -> AsyncOpenAI:
        """Get the underlying OpenAI client"""
        return self._client
    
    
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def analyze_image(
        self,
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze image and provide description or answer questions

        Args:
            image: Path to image file, URL, or image data
            prompt: Optional text prompt/question about the image
            max_tokens: Maximum tokens in response

        Returns:
            Dict containing analysis results
        """
        try:
            # Extract user_id from kwargs for billing
            self._current_user_id = kwargs.get('user_id')

            # Use unified image processing from image_utils
            base64_image = prepare_image_base64(image)
            
            # Use default prompt if none provided
            if prompt is None:
                prompt = "Please describe what you see in this image in detail."
            
            # Use the standard chat completions API with vision
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "auto"
                            }
                        },
                    ],
                }
            ]
            
            # Use max_completion_tokens for newer models like gpt-4o-mini
            completion_params = {
                "model": self.model_name,
                "messages": messages,  # type: ignore
                "temperature": self.temperature
            }
            
            # Check if model uses new parameter name
            # All newer models (gpt-4o, gpt-4.1, o1, etc.) use max_completion_tokens
            if any(prefix in self.model_name for prefix in ["gpt-4o", "gpt-4.1", "o1"]):
                completion_params["max_completion_tokens"] = max_tokens
            else:
                completion_params["max_tokens"] = max_tokens
            
            response = await self._client.chat.completions.create(**completion_params)  # type: ignore
            
            # Track usage for billing
            if response.usage and self._current_user_id:
                await self._publish_billing_event(
                    user_id=self._current_user_id,
                    service_type=ServiceType.VISION,
                    operation="image_analysis",
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    metadata={"prompt": prompt[:100] if prompt else "", "model": self.model_name}
                )
            
            content = response.choices[0].message.content or ""
            
            # 尝试解析JSON响应（对于结构化任务）
            try:
                import json
                # 检查响应是否是JSON格式
                if content.strip().startswith('{') and content.strip().endswith('}'):
                    parsed_json = json.loads(content)
                    return {
                        "text": content,
                        "parsed_data": parsed_json,
                        "confidence": 1.0,
                        "metadata": {
                            "model": self.model_name,
                            "prompt": prompt[:100],
                            "tokens_used": response.usage.total_tokens if response.usage else 0,
                            "response_format": "json"
                        }
                    }
            except json.JSONDecodeError:
                pass
            
            # 标准文本响应
            return {
                "text": content,
                "confidence": 1.0,  # OpenAI doesn't provide confidence scores
                "detected_objects": [],  # Populated by specific detection methods
                "metadata": {
                    "model": self.model_name,
                    "prompt": prompt[:100],
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "response_format": "text"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in image analysis: {e}")
            raise
    
    # ==================== 基于提示词的智能功能实现 ====================
    # YYDS通过改变提示词就能实现大部分Vision功能
    # 使用统一的VisionPromptMixin提供标准提示词
    
    # 重写其他方法以使用智能提示词
    async def describe_image(
        self, 
        image: Union[str, BinaryIO],
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        图像描述 - 使用专门提示词
        """
        prompt = self.get_task_prompt("describe", detail_level=detail_level)
        return await self.analyze_image(image, prompt, max_tokens=1000)
    
    async def extract_text(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """
        文本提取(OCR) - 使用专门提示词
        """
        prompt = self.get_task_prompt("extract_text")
        
        return await self.analyze_image(image, prompt, max_tokens=1000)
    
    async def detect_objects(
        self, 
        image: Union[str, BinaryIO],
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        物体检测 - 使用专门提示词
        """
        prompt = self.get_task_prompt("detect_objects", confidence_threshold=confidence_threshold)
        
        return await self.analyze_image(image, prompt, max_tokens=1000)
    
    async def detect_ui_elements(
        self,
        image: Union[str, BinaryIO],
        element_types: Optional[List[str]] = None,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        UI元素检测 - 使用专门提示词
        """
        prompt = self.get_task_prompt("detect_ui_elements", element_types=element_types, confidence_threshold=confidence_threshold)
        
        return await self.analyze_image(image, prompt, max_tokens=1000)
    
    async def detect_document_elements(
        self,
        image: Union[str, BinaryIO],
        element_types: Optional[List[str]] = None,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        文档元素检测 - 使用专门提示词  
        """
        prompt = self.get_task_prompt("detect_document_elements", element_types=element_types, confidence_threshold=confidence_threshold)
        
        return await self.analyze_image(image, prompt)
    
    async def classify_image(
        self, 
        image: Union[str, BinaryIO],
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        图像分类 - 使用专门提示词
        """
        prompt = self.get_task_prompt("classify", categories=categories)
        
        return await self.analyze_image(image, prompt)
    
    async def get_object_coordinates(
        self,
        image: Union[str, BinaryIO],
        object_name: str
    ) -> Dict[str, Any]:
        """
        获取对象坐标 - 使用专门提示词
        """
        prompt = self.get_task_prompt("get_coordinates", object_name=object_name)
        
        return await self.analyze_image(image, prompt)
    
    async def extract_table_data(
        self,
        image: Union[str, BinaryIO],
        table_format: str = "json",
        preserve_formatting: bool = True
    ) -> Dict[str, Any]:
        """
        表格数据结构化抽取 - 使用专门的表格抽取提示词
        """
        prompt = self.get_task_prompt("extract_table_data", table_format=table_format, preserve_formatting=preserve_formatting)
        
        return await self.analyze_image(image, prompt)
    
    async def close(self):
        """Clean up resources"""
        if hasattr(self._client, 'close'):
            await self._client.close()

