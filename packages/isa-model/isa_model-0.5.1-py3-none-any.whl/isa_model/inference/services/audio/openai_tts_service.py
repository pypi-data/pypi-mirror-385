from typing import Dict, Any, List, Optional
import tempfile
import os
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from isa_model.inference.services.audio.base_tts_service import BaseTTSService
import logging

logger = logging.getLogger(__name__)

class OpenAITTSService(BaseTTSService):
    """OpenAI TTS service with unified architecture"""
    
    def __init__(self, provider_name: str, model_name: str = "tts-1", **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        # Get configuration from centralized config manager
        provider_config = self.get_provider_config()
        
        # Initialize AsyncOpenAI client with provider configuration
        try:
            if not provider_config.get("api_key"):
                raise ValueError("OpenAI API key not found in provider configuration")
            
            self._client = AsyncOpenAI(
                api_key=provider_config["api_key"],
                base_url=provider_config.get("base_url", "https://api.openai.com/v1"),
                organization=provider_config.get("organization")
            )
            
            logger.info(f"Initialized OpenAITTSService with model '{self.model_name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ValueError(f"Failed to initialize OpenAI client. Check your API key configuration: {e}") from e
        
        self.language = provider_config.get('language', None)
    
    @property
    def client(self) -> AsyncOpenAI:
        """获取底层的 OpenAI 客户端"""
        return self._client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def transcribe(self, audio_data: bytes) -> Dict[str, Any]:
        """转写音频数据
        
        Args:
            audio_data: 音频二进制数据
            
        Returns:
            Dict[str, Any]: 包含转写文本的字典
        """
        try:
            # 创建临时文件存储音频数据
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                # 以二进制模式打开文件用于 API 请求
                with open(temp_file.name, 'rb') as audio_file:
                    # 只在有效的 ISO-639-1 语言代码时包含 language 参数
                    params = {
                        'model': self.model_name,
                        'file': audio_file,
                    }
                    if self.language and isinstance(self.language, str):
                        params['language'] = self.language
                        
                    response = await self._client.audio.transcriptions.create(**params)
                    
                # 清理临时文件
                os.unlink(temp_file.name)
                
                # 返回包含转写文本的字典
                return {
                    "text": response.text
                }
                
        except Exception as e:
            logger.error(f"Error in audio transcription: {e}")
            raise

    # 实现BaseTTSService的抽象方法
    async def synthesize_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        format: str = "mp3",
        **kwargs
    ) -> Dict[str, Any]:
        """Synthesize speech from text using OpenAI TTS"""
        try:
            # Extract user_id from kwargs for billing
            self._current_user_id = kwargs.get('user_id')
            response = await self._client.audio.speech.create(
                model="tts-1",
                voice=voice or "alloy",  # type: ignore
                input=text,
                response_format=format,  # type: ignore
                speed=speed
            )
            
            audio_data = response.content
            
            # Estimate audio duration for billing (rough estimation: ~150 words per minute)
            words = len(text.split())
            estimated_duration_seconds = (words / 150.0) * 60.0 / speed
            
            # Track usage for billing (OpenAI TTS is token-based: $15 per 1M characters)
            if self._current_user_id:
                await self._publish_billing_event(
                    user_id=self._current_user_id,
                    service_type="audio_tts",
                    operation="synthesize_speech",
                    input_tokens=len(text),  # Characters as input tokens
                    output_tokens=0,
                    input_units=len(text),  # Text length
                    output_units=estimated_duration_seconds,  # Audio duration in seconds
                    metadata={
                        "model": self.model_name,
                        "voice": voice or "alloy",
                        "speed": speed,
                        "format": format,
                        "text_length": len(text),
                        "estimated_duration_seconds": estimated_duration_seconds
                    }
                )
            
            # For HTTP API compatibility, encode audio data as base64
            import base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return {
                "audio_data_base64": audio_base64,  # Base64 encoded for JSON compatibility
                "format": format,
                "duration": estimated_duration_seconds,
                "sample_rate": 24000  # Default for OpenAI TTS
            }
            
        except Exception as e:
            logger.error(f"Error in speech synthesis: {e}")
            raise

    async def invoke(
        self,
        text: Optional[str] = None,
        task: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Unified invoke method for TTS service.
        Follows OpenAI pattern: text → audio
        """
        if text is None:
            raise ValueError("Text is required for TTS (text-to-speech)")

        return await self.synthesize_speech(text=text, **kwargs)

    async def synthesize_speech_to_file(
        self, 
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        format: str = "mp3"
    ) -> Dict[str, Any]:
        """Synthesize speech and save to file"""
        result = await self.synthesize_speech(text, voice, speed, pitch, format)
        
        with open(output_path, 'wb') as f:
            f.write(result["audio_data"])
        
        return {
            "file_path": output_path,
            "duration": result["duration"],
            "sample_rate": result["sample_rate"]
        }

    async def synthesize_speech_batch(
        self, 
        texts: List[str],
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        format: str = "mp3"
    ) -> List[Dict[str, Any]]:
        """Synthesize speech for multiple texts"""
        results = []
        for text in texts:
            result = await self.synthesize_speech(text, voice, speed, pitch, format)
            results.append(result)
        return results

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available OpenAI voices"""
        return [
            {"id": "alloy", "name": "Alloy", "language": "en-US", "gender": "neutral", "age": "adult"},
            {"id": "echo", "name": "Echo", "language": "en-US", "gender": "male", "age": "adult"},
            {"id": "fable", "name": "Fable", "language": "en-US", "gender": "neutral", "age": "adult"},
            {"id": "onyx", "name": "Onyx", "language": "en-US", "gender": "male", "age": "adult"},
            {"id": "nova", "name": "Nova", "language": "en-US", "gender": "female", "age": "adult"},
            {"id": "shimmer", "name": "Shimmer", "language": "en-US", "gender": "female", "age": "adult"}
        ]

    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return ["mp3", "opus", "aac", "flac"]

    def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific voice"""
        voices = {voice["id"]: voice for voice in self.get_available_voices()}
        voice_info = voices.get(voice_id, {})
        
        if voice_info:
            voice_info.update({
                "description": f"OpenAI {voice_info['name']} voice",
                "sample_rate": 24000
            })
        
        return voice_info

    async def close(self):
        """Cleanup resources"""
        if hasattr(self._client, 'close'):
            await self._client.close()
