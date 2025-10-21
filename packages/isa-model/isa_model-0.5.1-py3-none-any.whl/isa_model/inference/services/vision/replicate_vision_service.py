from typing import Dict, Any, Union, List, Optional, BinaryIO
import base64
import os
import replicate
import re
import ast
from isa_model.inference.services.vision.base_vision_service import BaseVisionService
from isa_model.core.types import ServiceType
from isa_model.inference.services.vision.helpers.image_utils import prepare_image_data_url
from isa_model.inference.services.vision.helpers.vision_prompts import VisionPromptMixin
import logging

logger = logging.getLogger(__name__)

class ReplicateVisionService(BaseVisionService, VisionPromptMixin):
    """Enhanced Replicate Vision service supporting multiple specialized models"""
    
    # Supported model configurations
    MODELS = {
        "cogvlm": "cjwbw/cogvlm:a5092d718ea77a073e6d8f6969d5c0fb87d0ac7e4cdb7175427331e1798a34ed",
        "florence-2": "microsoft/florence-2-large:fcdb54e52322b9e6dce7a35e5d8ad173dce30b46ef49a236c1a71bc6b78b5bed",
        "omniparser": "microsoft/omniparser-v2:49cf3d41b8d3aca1360514e83be4c97131ce8f0d99abfc365526d8384caa88df",
        "yolov8": "adirik/yolov8:3b21ba0e5da47bb2c69a96f72894a31b7c1e77b3e8a7b6ba43b7eb93b7b2c4f4",
        "qwen-vl-chat": "lucataco/qwen-vl-chat:50881b153b4d5f72b3db697e2bbad23bb1277ab741c5b52d80cd6ee17ea660e9"
    }
    
    def __init__(self, provider_name: str, model_name: str = "cogvlm", **kwargs):
        # Resolve model name to full model path
        self.model_key = model_name
        resolved_model = self.MODELS.get(model_name, model_name)
        super().__init__(provider_name, resolved_model, **kwargs)
        
        # Get configuration from centralized config manager
        provider_config = self.get_provider_config()
        
        # Initialize Replicate client
        try:
            # Get API token - try different possible keys like the image gen service
            self.api_token = provider_config.get("api_token") or provider_config.get("replicate_api_token") or provider_config.get("api_key")
            
            if not self.api_token:
                raise ValueError("Replicate API token not found in provider configuration")
            
            # Set API token for replicate
            os.environ["REPLICATE_API_TOKEN"] = self.api_token
            
            logger.info(f"Initialized ReplicateVisionService with model {self.model_key} ({self.model_name})")
            
        except Exception as e:
            logger.error(f"Failed to initialize Replicate client: {e}")
            raise ValueError(f"Failed to initialize Replicate client. Check your API key configuration: {e}") from e
        
        self.temperature = provider_config.get('temperature', 0.7)
    
    def _prepare_image(self, image: Union[str, BinaryIO]) -> str:
        """Prepare image for Replicate API - convert to URL or base64"""
        if isinstance(image, str) and image.startswith(('http://', 'https://')):
            # Already a URL
            return image
        else:
            # Use unified image processing from image_utils
            return prepare_image_data_url(image)
    
    # Replicate使用base的invoke方法，不需要重写
    # 直接实现对应的标准方法即可
    
    async def analyze_image(
        self,
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze image and provide description or answer questions
        """
        try:
            # Extract user_id from kwargs for billing
            self._current_user_id = kwargs.get('user_id')

            # Prepare image for API using unified processing
            image_input = self._prepare_image(image)
            
            # Use default prompt if none provided
            if prompt is None:
                prompt = "Describe this image in detail."
            
            # Choose input format based on model type
            if self.model_key == "qwen-vl-chat":
                # Qwen-VL-Chat uses simple image + prompt format
                output = replicate.run(
                    self.model_name,
                    input={
                        "image": image_input,
                        "prompt": prompt
                    }
                )
            else:
                # CogVLM and other models use VQA format
                output = replicate.run(
                    self.model_name,
                    input={
                        "vqa": True,  # Visual Question Answering mode
                        "image": image_input,
                        "query": prompt
                    }
                )
            
            # CogVLM returns a string response
            response_text = str(output) if output else ""
            
            # Track usage for billing
            if self._current_user_id:
                await self._publish_billing_event(
                    user_id=self._current_user_id,
                    service_type=ServiceType.VISION,
                    operation="image_analysis",
                    input_tokens=len(prompt.split()) if prompt else 0,
                    output_tokens=len(response_text.split()),
                    metadata={"prompt": prompt[:100] if prompt else "", "model": self.model_name}
                )
            
            return {
                "text": response_text,
                "confidence": 1.0,  # CogVLM doesn't provide confidence scores
                "detected_objects": [],  # Would need separate object detection
                "metadata": {
                    "model": self.model_name,
                    "prompt": prompt,
                    "tokens_used": len(response_text.split())
                }
            }
            
        except Exception as e:
            logger.error(f"Error in image analysis: {e}")
            raise
    
    # ==================== 标准接口实现：检测抽取类 ====================
    
    async def detect_ui_elements(
        self,
        image: Union[str, BinaryIO],
        element_types: Optional[List[str]] = None,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        UI界面元素检测 - 使用专门模型实现
        """
        if self.model_key == "omniparser":
            return await self.run_omniparser(image, box_threshold=confidence_threshold)
        elif self.model_key == "florence-2":
            return await self.run_florence2(image, task="<OPEN_VOCABULARY_DETECTION>")
        else:
            # 使用通用物体检测作为fallback
            return await self.detect_objects(image, confidence_threshold)
    
    async def detect_document_elements(
        self,
        image: Union[str, BinaryIO],
        element_types: Optional[List[str]] = None,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        文档结构元素检测 - 使用专门模型实现
        """
        if self.model_key == "florence-2":
            # Florence-2可以检测文档结构
            return await self.run_florence2(image, task="<DETAILED_CAPTION>")
        else:
            raise NotImplementedError(f"Document detection not supported for model {self.model_key}")
    
    async def detect_objects(
        self, 
        image: Union[str, BinaryIO],
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        通用物体检测 - 实现标准接口
        """
        if self.model_key == "yolov8":
            return await self.run_yolo(image, confidence=confidence_threshold)
        elif self.model_key == "florence-2":
            return await self.run_florence2(image, task="<OD>")
        elif self.model_key == "qwen-vl-chat":
            # Qwen-VL-Chat can do object detection through prompting
            prompt = self.get_task_prompt("detect_objects", confidence_threshold=confidence_threshold)
            return await self.analyze_image(image, prompt)
        else:
            raise NotImplementedError(f"Object detection not supported for model {self.model_key}")
    
    # ==================== QWEN-VL-CHAT 智能提示词实现 ====================
    # 类似 OpenAI，qwen-vl-chat 通过提示词实现所有 Vision 功能
    
    async def describe_image(
        self, 
        image: Union[str, BinaryIO],
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        图像描述 - qwen-vl-chat通过提示词实现
        """
        if self.model_key == "qwen-vl-chat":
            prompt = self.get_task_prompt("describe", detail_level=detail_level)
            return await self.analyze_image(image, prompt)
        else:
            raise NotImplementedError(f"describe_image not supported for model {self.model_key}")
    
    async def extract_text(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """
        文本提取(OCR) - qwen-vl-chat通过提示词实现
        """
        if self.model_key == "qwen-vl-chat":
            prompt = self.get_task_prompt("extract_text")
            return await self.analyze_image(image, prompt)
        else:
            raise NotImplementedError(f"extract_text not supported for model {self.model_key}")
    
    async def classify_image(
        self, 
        image: Union[str, BinaryIO],
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        图像分类 - qwen-vl-chat通过提示词实现
        """
        if self.model_key == "qwen-vl-chat":
            prompt = self.get_task_prompt("classify", categories=categories)
            return await self.analyze_image(image, prompt)
        else:
            raise NotImplementedError(f"classify_image not supported for model {self.model_key}")
    
    async def extract_table_data(
        self,
        image: Union[str, BinaryIO],
        table_format: str = "json",
        preserve_formatting: bool = True
    ) -> Dict[str, Any]:
        """
        表格数据抽取 - qwen-vl-chat通过提示词实现
        """
        if self.model_key == "qwen-vl-chat":
            prompt = self.get_task_prompt("extract_table_data", table_format=table_format, preserve_formatting=preserve_formatting)
            return await self.analyze_image(image, prompt)
        else:
            raise NotImplementedError(f"extract_table_data not supported for model {self.model_key}")
    
    async def get_object_coordinates(
        self,
        image: Union[str, BinaryIO],
        object_name: str
    ) -> Dict[str, Any]:
        """
        获取对象坐标 - qwen-vl-chat通过提示词实现
        """
        if self.model_key == "qwen-vl-chat":
            prompt = self.get_task_prompt("get_coordinates", object_name=object_name)
            return await self.analyze_image(image, prompt)
        else:
            raise NotImplementedError(f"get_object_coordinates not supported for model {self.model_key}")
    
    # ==================== REPLICATE专门模型方法 ====================
    # 以下方法是Replicate特有的专门模型实现，不在标准接口中
    
    # ==================== MODEL-SPECIFIC METHODS ====================
    
    async def run_omniparser(
        self, 
        image: Union[str, BinaryIO],
        imgsz: int = 640,
        box_threshold: float = 0.05,
        iou_threshold: float = 0.1
    ) -> Dict[str, Any]:
        """Run OmniParser-v2 for UI element detection"""
        if self.model_key != "omniparser":
            # Switch to OmniParser model temporarily
            original_model = self.model_name
            self.model_name = self.MODELS["omniparser"]
        
        try:
            image_input = self._prepare_image(image)
            
            output = replicate.run(
                self.model_name,
                input={
                    "image": image_input,
                    "imgsz": imgsz,
                    "box_threshold": box_threshold,
                    "iou_threshold": iou_threshold
                }
            )
            
            # Parse OmniParser output format
            elements = []
            if isinstance(output, dict) and 'elements' in output:
                elements_text = output['elements']
                elements = self._parse_omniparser_elements(elements_text, image)
            
            return {
                "model": "omniparser",
                "raw_output": output,
                "parsed_elements": elements,
                "metadata": {
                    "imgsz": imgsz,
                    "box_threshold": box_threshold,
                    "iou_threshold": iou_threshold
                }
            }
            
        finally:
            if self.model_key != "omniparser":
                # Restore original model
                self.model_name = original_model
    
    async def run_florence2(
        self,
        image: Union[str, BinaryIO],
        task: str = "<OPEN_VOCABULARY_DETECTION>",
        text_input: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run Florence-2 for object detection and description"""
        if self.model_key != "florence-2":
            original_model = self.model_name
            self.model_name = self.MODELS["florence-2"]
        
        try:
            image_input = self._prepare_image(image)
            
            input_params = {
                "image": image_input,
                "task": task
            }
            if text_input:
                input_params["text_input"] = text_input
            
            output = replicate.run(self.model_name, input=input_params)
            
            # Parse Florence-2 output
            parsed_objects = []
            if isinstance(output, dict):
                parsed_objects = self._parse_florence2_output(output, image)
            
            return {
                "model": "florence-2",
                "task": task,
                "raw_output": output,
                "parsed_objects": parsed_objects,
                "metadata": {"task": task, "text_input": text_input}
            }
            
        finally:
            if self.model_key != "florence-2":
                self.model_name = original_model
    
    async def run_yolo(
        self,
        image: Union[str, BinaryIO],
        confidence: float = 0.5,
        iou_threshold: float = 0.45
    ) -> Dict[str, Any]:
        """Run YOLO for general object detection"""
        if self.model_key != "yolov8":
            original_model = self.model_name
            self.model_name = self.MODELS["yolov8"]
        
        try:
            image_input = self._prepare_image(image)
            
            output = replicate.run(
                self.model_name,
                input={
                    "image": image_input,
                    "confidence": confidence,
                    "iou_threshold": iou_threshold
                }
            )
            
            # Parse YOLO output
            detected_objects = []
            if output:
                detected_objects = self._parse_yolo_output(output, image)
            
            return {
                "model": "yolov8",
                "raw_output": output,
                "detected_objects": detected_objects,
                "metadata": {
                    "confidence": confidence,
                    "iou_threshold": iou_threshold
                }
            }
            
        finally:
            if self.model_key != "yolov8":
                self.model_name = original_model
    
    # ==================== PARSING HELPERS ====================
    
    def _parse_omniparser_elements(self, elements_text: str, image: Union[str, BinaryIO]) -> List[Dict[str, Any]]:
        """Parse OmniParser-v2 elements format"""
        elements = []
        
        # Get image dimensions for coordinate conversion
        from PIL import Image as PILImage
        if isinstance(image, str):
            img = PILImage.open(image)
        else:
            img = PILImage.open(image)
        img_width, img_height = img.size
        
        try:
            # Extract individual icon entries
            icon_pattern = r"icon (\d+): ({.*?})\n?"
            matches = re.findall(icon_pattern, elements_text, re.DOTALL)
            
            for icon_id, icon_data_str in matches:
                try:
                    icon_data = eval(icon_data_str)  # Safe since we control the source
                    
                    bbox = icon_data.get('bbox', [])
                    element_type = icon_data.get('type', 'unknown')
                    interactivity = icon_data.get('interactivity', False)
                    content = icon_data.get('content', '').strip()
                    
                    if len(bbox) == 4:
                        # Convert normalized coordinates to pixel coordinates
                        x1_norm, y1_norm, x2_norm, y2_norm = bbox
                        x1 = int(x1_norm * img_width)
                        y1 = int(y1_norm * img_height)
                        x2 = int(x2_norm * img_width)
                        y2 = int(y2_norm * img_height)
                        
                        element = {
                            'id': f'omni_icon_{icon_id}',
                            'bbox': [x1, y1, x2, y2],
                            'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                            'size': [x2 - x1, y2 - y1],
                            'type': element_type,
                            'interactivity': interactivity,
                            'content': content,
                            'confidence': 0.9
                        }
                        elements.append(element)
                        
                except Exception as e:
                    logger.warning(f"Failed to parse icon {icon_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to parse OmniParser elements: {e}")
        
        return elements
    
    def _parse_florence2_output(self, output: Dict[str, Any], image: Union[str, BinaryIO]) -> List[Dict[str, Any]]:
        """Parse Florence-2 detection output"""
        objects = []
        
        try:
            # Florence-2 typically returns nested detection data
            for key, value in output.items():
                if isinstance(value, dict) and ('bboxes' in value and 'labels' in value):
                    bboxes = value['bboxes']
                    labels = value['labels']
                    
                    for i, (label, bbox) in enumerate(zip(labels, bboxes)):
                        if len(bbox) >= 4:
                            x1, y1, x2, y2 = bbox[:4]
                            obj = {
                                'id': f'florence_{i}',
                                'label': label,
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                                'size': [int(x2 - x1), int(y2 - y1)],
                                'confidence': 0.9
                            }
                            objects.append(obj)
                            
        except Exception as e:
            logger.error(f"Failed to parse Florence-2 output: {e}")
        
        return objects
    
    def _parse_yolo_output(self, output: Any, image: Union[str, BinaryIO]) -> List[Dict[str, Any]]:
        """Parse YOLO detection output"""
        objects = []
        
        try:
            # YOLO output format varies, handle common formats
            if isinstance(output, list):
                for i, detection in enumerate(output):
                    if isinstance(detection, dict):
                        bbox = detection.get('bbox', detection.get('box', []))
                        label = detection.get('class', detection.get('label', f'object_{i}'))
                        confidence = detection.get('confidence', detection.get('score', 0.9))
                        
                        if len(bbox) >= 4:
                            x1, y1, x2, y2 = bbox[:4]
                            obj = {
                                'id': f'yolo_{i}',
                                'label': label,
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                                'size': [int(x2 - x1), int(y2 - y1)],
                                'confidence': float(confidence)
                            }
                            objects.append(obj)
                            
        except Exception as e:
            logger.error(f"Failed to parse YOLO output: {e}")
        
        return objects

    async def close(self):
        """Clean up resources"""
        # Replicate doesn't need explicit cleanup
        pass