from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, BinaryIO
from isa_model.inference.services.base_service import BaseService

class BaseTTSService(BaseService):
    """Base class for Text-to-Speech services with unified task dispatch"""
    
    async def invoke(
        self, 
        text: Union[str, List[str]],
        task: Optional[str] = None,
        **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        统一的任务分发方法 - Base类提供通用实现
        
        Args:
            text: 输入文本，可以是:
                - str: 单个文本
                - List[str]: 多个文本（批量处理）
            task: 任务类型，支持多种TTS任务
            **kwargs: 任务特定的附加参数
            
        Returns:
            Dict or List[Dict] containing task results
        """
        task = task or "synthesize"
        
        # ==================== 语音合成类任务 ====================
        if task == "synthesize":
            if isinstance(text, list):
                return await self.synthesize_speech_batch(
                    text, 
                    kwargs.get("voice"),
                    kwargs.get("speed", 1.0),
                    kwargs.get("pitch", 1.0),
                    kwargs.get("format", "mp3")
                )
            else:
                return await self.synthesize_speech(
                    text,
                    kwargs.get("voice"),
                    kwargs.get("speed", 1.0),
                    kwargs.get("pitch", 1.0),
                    kwargs.get("format", "mp3")
                )
        elif task == "synthesize_to_file":
            if not kwargs.get("output_path"):
                raise ValueError("output_path is required for synthesize_to_file task")
            if isinstance(text, list):
                raise ValueError("synthesize_to_file task requires single text input")
            return await self.synthesize_speech_to_file(
                text,
                kwargs["output_path"],
                kwargs.get("voice"),
                kwargs.get("speed", 1.0),
                kwargs.get("pitch", 1.0),
                kwargs.get("format", "mp3")
            )
        elif task == "batch_synthesize":
            if not isinstance(text, list):
                text = [text]
            return await self.synthesize_speech_batch(
                text,
                kwargs.get("voice"),
                kwargs.get("speed", 1.0),
                kwargs.get("pitch", 1.0),
                kwargs.get("format", "mp3")
            )
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support task: {task}")
    
    def get_supported_tasks(self) -> List[str]:
        """
        获取支持的任务列表
        
        Returns:
            List of supported task names
        """
        return ["synthesize", "synthesize_to_file", "batch_synthesize"]
    
    @abstractmethod
    async def synthesize_speech(
        self, 
        text: str, 
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        format: str = "mp3"
    ) -> Dict[str, Any]:
        """
        Synthesize speech from text
        
        Args:
            text: Input text to convert to speech
            voice: Voice ID or name to use
            speed: Speech speed multiplier (0.5-2.0)
            pitch: Pitch adjustment (-1.0 to 1.0)
            format: Audio format ('mp3', 'wav', 'ogg')
            
        Returns:
            Dict containing synthesis results with keys:
            - audio_data: Binary audio data
            - format: Audio format
            - duration: Audio duration in seconds
            - sample_rate: Audio sample rate
        """
        pass
    
    @abstractmethod
    async def synthesize_speech_to_file(
        self, 
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        format: str = "mp3"
    ) -> Dict[str, Any]:
        """
        Synthesize speech and save directly to file
        
        Args:
            text: Input text to convert to speech
            output_path: Path to save the audio file
            voice: Voice ID or name to use
            speed: Speech speed multiplier (0.5-2.0)
            pitch: Pitch adjustment (-1.0 to 1.0)
            format: Audio format ('mp3', 'wav', 'ogg')
            
        Returns:
            Dict containing synthesis results with keys:
            - file_path: Path to saved audio file
            - duration: Audio duration in seconds
            - sample_rate: Audio sample rate
        """
        pass
    
    @abstractmethod
    async def synthesize_speech_batch(
        self, 
        texts: List[str],
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        format: str = "mp3"
    ) -> List[Dict[str, Any]]:
        """
        Synthesize speech for multiple texts
        
        Args:
            texts: List of input texts to convert to speech
            voice: Voice ID or name to use
            speed: Speech speed multiplier (0.5-2.0)
            pitch: Pitch adjustment (-1.0 to 1.0)
            format: Audio format ('mp3', 'wav', 'ogg')
            
        Returns:
            List of synthesis result dictionaries
        """
        pass
    
    @abstractmethod
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices
        
        Returns:
            List of voice information dictionaries with keys:
            - id: Voice identifier
            - name: Human-readable voice name
            - language: Language code (e.g., 'en-US', 'es-ES')
            - gender: Voice gender ('male', 'female', 'neutral')
            - age: Voice age category ('adult', 'child', 'elderly')
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported audio formats
        
        Returns:
            List of supported file extensions (e.g., ['mp3', 'wav', 'ogg'])
        """
        pass
    
    @abstractmethod
    def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific voice
        
        Args:
            voice_id: Voice identifier
            
        Returns:
            Dict containing voice information:
            - id: Voice identifier
            - name: Human-readable voice name
            - language: Language code
            - gender: Voice gender
            - description: Voice description
            - sample_rate: Default sample rate
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass
