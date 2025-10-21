from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, BinaryIO
import aiohttp
import asyncio
import tempfile
import os
import logging
from io import BytesIO
from isa_model.inference.services.base_service import BaseService

logger = logging.getLogger(__name__)

class BaseSTTService(BaseService):
    """Base class for Speech-to-Text services with unified task dispatch and URL support"""
    
    async def _prepare_audio_input(self, audio_input: Union[str, BinaryIO, bytes]) -> Union[str, BinaryIO]:
        """
        Prepare audio input by handling URLs, file paths, bytes data, and file objects
        
        Args:
            audio_input: Audio input (URL, file path, bytes data, or file object)
            
        Returns:
            Prepared audio input (local file path or file object)
        """
        if isinstance(audio_input, bytes):
            # Handle bytes data from API uploads
            logger.info(f"Converting bytes data to temporary file ({len(audio_input)} bytes)")
            return await self._save_bytes_to_temp_file(audio_input)
        elif isinstance(audio_input, str):
            # Check if it's a URL
            if audio_input.startswith(('http://', 'https://')):
                logger.info(f"Downloading audio from URL: {audio_input}")
                return await self._download_audio_url(audio_input)
            else:
                # Regular file path or base64 string
                return audio_input
        else:
            # Already a file object
            return audio_input
    
    async def _prepare_audio_input_with_context(self, audio_input: Union[str, BinaryIO, bytes], context: Dict[str, Any]) -> Union[str, BinaryIO]:
        """
        Prepare audio input with additional context from kwargs
        
        Args:
            audio_input: Audio input (URL, file path, bytes data, or file object)
            context: Additional context including filename, content_type
            
        Returns:
            Prepared audio input (local file path or file object)
        """
        if isinstance(audio_input, bytes):
            # Handle bytes data from API uploads
            filename = context.get('filename')
            content_type = context.get('content_type')
            logger.info(f"Converting bytes data to temporary file ({len(audio_input)} bytes), filename={filename}, content_type={content_type}")
            return await self._save_bytes_to_temp_file(audio_input, filename, content_type)
        else:
            return await self._prepare_audio_input(audio_input)
    
    async def _download_audio_url(self, url: str) -> str:
        """
        Download audio file from URL to temporary file
        
        Args:
            url: HTTP/HTTPS URL to audio file
            
        Returns:
            Path to downloaded temporary file
            
        Raises:
            Exception: If download fails
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download audio: HTTP {response.status}")
                    
                    # Get content type to determine file extension
                    content_type = response.headers.get('Content-Type', '')
                    file_ext = self._get_file_extension_from_content_type(content_type)
                    
                    # Create temporary file
                    temp_file = tempfile.NamedTemporaryFile(
                        delete=False, 
                        suffix=file_ext,
                        prefix='audio_download_'
                    )
                    
                    # Download and save
                    async for chunk in response.content.iter_chunked(8192):
                        temp_file.write(chunk)
                    
                    temp_file.close()
                    logger.info(f"Downloaded audio to temporary file: {temp_file.name}")
                    return temp_file.name
                    
        except Exception as e:
            logger.error(f"Failed to download audio from URL {url}: {e}")
            raise Exception(f"Audio URL download failed: {e}") from e
    
    def _get_file_extension_from_content_type(self, content_type: str) -> str:
        """Get appropriate file extension from Content-Type header"""
        content_type_map = {
            'audio/mpeg': '.mp3',
            'audio/mp3': '.mp3',
            'audio/wav': '.wav',
            'audio/wave': '.wav',
            'audio/x-wav': '.wav',
            'audio/flac': '.flac',
            'audio/ogg': '.ogg',
            'audio/m4a': '.m4a',
            'audio/mp4': '.mp4',
            'audio/webm': '.webm'
        }
        return content_type_map.get(content_type.lower(), '.audio')
    
    async def _save_bytes_to_temp_file(self, audio_bytes: bytes, filename: Optional[str] = None, content_type: Optional[str] = None) -> str:
        """
        Save audio bytes data to temporary file
        
        Args:
            audio_bytes: Audio data as bytes
            filename: Optional filename to determine extension
            content_type: Optional content type to determine extension
            
        Returns:
            Path to temporary file containing audio data
        """
        try:
            # Determine file extension from filename or content type
            suffix = '.mp3'  # Default
            if filename and '.' in filename:
                suffix = '.' + filename.split('.')[-1]
            elif content_type:
                suffix = self._get_file_extension_from_content_type(content_type)
            
            # Create temporary file with proper audio extension
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
                prefix='audio_bytes_'
            )
            
            # Write bytes data
            temp_file.write(audio_bytes)
            temp_file.close()
            
            logger.info(f"Saved {len(audio_bytes)} bytes to temporary file: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Failed to save audio bytes to temporary file: {e}")
            raise Exception(f"Audio bytes save failed: {e}") from e
    
    def _cleanup_temp_file(self, file_path: str):
        """Clean up temporary downloaded file"""
        try:
            if file_path and file_path.startswith(tempfile.gettempdir()):
                os.unlink(file_path)
                logger.debug(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary file {file_path}: {e}")
    
    async def invoke(
        self, 
        audio_input: Union[str, BinaryIO, bytes, List[Union[str, BinaryIO, bytes]]],
        task: Optional[str] = None,
        **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        统一的任务分发方法 - Base类提供通用实现
        
        Args:
            audio_input: 音频输入，可以是:
                - str: 音频文件路径
                - BinaryIO: 音频文件对象
                - List: 多个音频文件（批量处理）
            task: 任务类型，支持多种STT任务
            **kwargs: 任务特定的附加参数
            
        Returns:
            Dict or List[Dict] containing task results
        """
        task = task or "transcribe"
        
        # ==================== 语音转文本类任务 ====================
        if task == "transcribe":
            if isinstance(audio_input, list):
                # Prepare all audio inputs (handle URLs)
                prepared_inputs = []
                for audio in audio_input:
                    prepared_input = await self._prepare_audio_input_with_context(audio, kwargs)
                    prepared_inputs.append(prepared_input)
                return await self.transcribe_batch(
                    prepared_inputs,
                    kwargs.get("language"),
                    kwargs.get("prompt")
                )
            else:
                # Prepare single audio input (handle URLs)
                prepared_input = await self._prepare_audio_input_with_context(audio_input, kwargs)
                return await self.transcribe(
                    prepared_input,
                    kwargs.get("language"),
                    kwargs.get("prompt")
                )
        elif task == "translate":
            if isinstance(audio_input, list):
                raise ValueError("translate task requires single audio input")
            prepared_input = await self._prepare_audio_input_with_context(audio_input, kwargs)
            return await self.translate(prepared_input)
        elif task == "batch_transcribe":
            if not isinstance(audio_input, list):
                audio_input = [audio_input]
            # Prepare all audio inputs (handle URLs)
            prepared_inputs = []
            for audio in audio_input:
                prepared_input = await self._prepare_audio_input_with_context(audio, kwargs)
                prepared_inputs.append(prepared_input)
            return await self.transcribe_batch(
                prepared_inputs,
                kwargs.get("language"),
                kwargs.get("prompt")
            )
        elif task == "detect_language":
            if isinstance(audio_input, list):
                raise ValueError("detect_language task requires single audio input")
            prepared_input = await self._prepare_audio_input_with_context(audio_input, kwargs)
            return await self.detect_language(prepared_input)
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support task: {task}")
    
    def get_supported_tasks(self) -> List[str]:
        """
        获取支持的任务列表
        
        Returns:
            List of supported task names
        """
        return ["transcribe", "translate", "batch_transcribe", "detect_language"]
    
    @abstractmethod
    async def transcribe(
        self, 
        audio_file: Union[str, BinaryIO, bytes], 
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file: Path to audio file or file-like object
            language: Language code (e.g., 'en', 'es', 'fr')
            prompt: Optional prompt to guide transcription
            
        Returns:
            Dict containing transcription results with keys:
            - text: The transcribed text
            - language: Detected/specified language
            - confidence: Confidence score (if available)
            - segments: Time-segmented transcription (if available)
        """
        pass
    
    @abstractmethod
    async def translate(
        self, 
        audio_file: Union[str, BinaryIO, bytes]
    ) -> Dict[str, Any]:
        """
        Translate audio file to English text
        
        Args:
            audio_file: Path to audio file or file-like object
            
        Returns:
            Dict containing translation results with keys:
            - text: The translated text (in English)
            - detected_language: Original language detected
            - confidence: Confidence score (if available)
        """
        pass
    
    @abstractmethod
    async def transcribe_batch(
        self, 
        audio_files: List[Union[str, BinaryIO, bytes]], 
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Transcribe multiple audio files
        
        Args:
            audio_files: List of audio file paths or file-like objects
            language: Language code (e.g., 'en', 'es', 'fr')
            prompt: Optional prompt to guide transcription
            
        Returns:
            List of transcription results
        """
        pass
    
    @abstractmethod
    async def detect_language(self, audio_file: Union[str, BinaryIO, bytes]) -> Dict[str, Any]:
        """
        Detect language of audio file
        
        Args:
            audio_file: Path to audio file or file-like object
            
        Returns:
            Dict containing language detection results with keys:
            - language: Detected language code
            - confidence: Confidence score
            - alternatives: List of alternative languages with scores
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported audio formats
        
        Returns:
            List of supported file extensions (e.g., ['mp3', 'wav', 'flac'])
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes
        
        Returns:
            List of supported language codes (e.g., ['en', 'es', 'fr'])
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass
