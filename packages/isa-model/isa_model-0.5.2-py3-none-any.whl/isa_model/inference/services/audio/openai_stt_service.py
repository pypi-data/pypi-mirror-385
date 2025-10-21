import logging
import os
import aiohttp
from typing import Dict, Any, List, Union, Optional, BinaryIO
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from isa_model.inference.services.audio.base_stt_service import BaseSTTService

logger = logging.getLogger(__name__)

class OpenAISTTService(BaseSTTService):
    """
    OpenAI Speech-to-Text service using whisper-1 model.
    Supports transcription and translation to English.
    Uses the new unified architecture with centralized config management.
    """
    
    def __init__(self, provider_name: str, model_name: str = "whisper-1", **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        # Get provider configuration from centralized config manager
        provider_config = self.get_provider_config()
        
        # Initialize AsyncOpenAI client with provider configuration
        try:
            api_key = self.get_api_key()
            
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=provider_config.get("api_base_url", "https://api.openai.com/v1"),
                organization=provider_config.get("organization")
            )
            
            logger.info(f"Initialized OpenAISTTService with model '{self.model_name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ValueError(f"Failed to initialize OpenAI client. Check your API key configuration: {e}") from e
        
        # Model configurations
        self.max_file_size = provider_config.get('max_file_size', 25 * 1024 * 1024)  # 25MB
        self.supported_formats = ['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm']
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def transcribe(self, audio_file: Union[str, BinaryIO, bytes], language: Optional[str] = None, prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio file to text using OpenAI's Whisper model.

        Args:
            audio_file: Path to audio file or file-like object
            language: Optional language code for better accuracy
            **kwargs: Additional parameters for the transcription API

        Returns:
            Dict containing transcription result and metadata
        """
        try:
            # Extract user_id from kwargs for billing
            self._current_user_id = kwargs.get('user_id')
            # Prepare request parameters
            transcription_params = {
                "model": self.model_name,
                "response_format": "verbose_json"
            }
            
            if language:
                transcription_params["language"] = language
            
            # Add optional parameters
            if prompt:
                transcription_params["prompt"] = prompt
            
            # Handle file input - support bytes, base64 strings, file paths, and file objects
            if isinstance(audio_file, bytes):
                # Handle bytes data directly
                logger.info(f"Processing bytes audio data ({len(audio_file)} bytes)")
                from io import BytesIO
                audio_buffer = BytesIO(audio_file)
                
                # Use filename from kwargs if provided, otherwise default to .mp3
                filename = kwargs.get('filename', 'audio.mp3')
                if filename and not filename.endswith(('.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm', '.mp4')):
                    filename += '.mp3'  # Add extension if missing
                audio_buffer.name = filename
                logger.info(f"Using filename: {filename}")
                transcription = await self.client.audio.transcriptions.create(
                    file=audio_buffer,
                    **transcription_params
                )
            elif isinstance(audio_file, str):
                # Check if it's a URL, base64 string, or file path
                if audio_file.startswith(('http://', 'https://')):
                    # Fetch audio from URL
                    logger.info(f"Fetching audio from URL: {audio_file}")
                    async with aiohttp.ClientSession() as session:
                        async with session.get(audio_file) as response:
                            if response.status == 200:
                                audio_data = await response.read()
                                from io import BytesIO
                                audio_buffer = BytesIO(audio_data)
                                # Extract filename from URL or use default
                                filename = audio_file.split('/')[-1] if '/' in audio_file else 'audio.wav'
                                if not filename.endswith(('.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm', '.mp4')):
                                    filename += '.wav'
                                audio_buffer.name = filename
                                logger.info(f"Downloaded {len(audio_data)} bytes from URL")
                                transcription = await self.client.audio.transcriptions.create(
                                    file=audio_buffer,
                                    **transcription_params
                                )
                            else:
                                raise ValueError(f"Failed to fetch audio from URL: HTTP {response.status}")
                elif len(audio_file) > 100 and not os.path.exists(audio_file):
                    # Likely a base64 string
                    try:
                        import base64
                        from io import BytesIO
                        logger.info(f"Attempting to decode base64 audio data (length: {len(audio_file)})")
                        audio_data = base64.b64decode(audio_file)
                        audio_buffer = BytesIO(audio_data)
                        audio_buffer.name = "audio.wav"  # OpenAI needs a filename hint
                        logger.info(f"Successfully decoded base64 to {len(audio_data)} bytes")
                        transcription = await self.client.audio.transcriptions.create(
                            file=audio_buffer,
                            **transcription_params
                        )
                    except Exception as e:
                        # If base64 decoding fails, treat as file path
                        logger.error(f"Base64 decoding failed: {e}, treating as file path")
                        with open(audio_file, "rb") as f:
                            transcription = await self.client.audio.transcriptions.create(
                                file=f,
                                **transcription_params
                            )
                else:
                    # Regular file path
                    with open(audio_file, "rb") as f:
                        transcription = await self.client.audio.transcriptions.create(
                            file=f,
                            **transcription_params
                        )
            else:
                transcription = await self.client.audio.transcriptions.create(
                    file=audio_file,
                    **transcription_params
                )
            
            # Extract usage information for billing
            result = {
                "text": transcription.text,
                "language": getattr(transcription, 'language', language),
                "duration": getattr(transcription, 'duration', None),
                "segments": getattr(transcription, 'segments', []),
                "usage": {
                    "input_units": getattr(transcription, 'duration', 1),  # Duration in seconds
                    "output_tokens": len(transcription.text.split()) if transcription.text else 0
                }
            }
            
            # Track usage for billing
            if self._current_user_id:
                await self._publish_billing_event(
                    user_id=self._current_user_id,
                    service_type="audio_stt",
                    operation="transcribe",
                    input_units=result["usage"]["input_units"],
                    output_tokens=result["usage"]["output_tokens"],
                    metadata={
                        "language": result.get("language"),
                        "model_name": self.model_name,
                        "provider": self.provider_name
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    async def invoke(
        self,
        audio_input: Optional[Union[str, BinaryIO, bytes]] = None,
        task: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Unified invoke method for STT service.
        Follows OpenAI pattern: audio → text
        """
        if audio_input is None:
            raise ValueError("Audio input is required for STT (speech-to-text)")

        # STT always does transcription (or translation if specified)
        if task == "translate":
            return await self.translate(audio_file=audio_input, **kwargs)
        else:
            return await self.transcribe(audio_file=audio_input, **kwargs)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def translate(self, audio_file: Union[str, BinaryIO, bytes], **kwargs) -> Dict[str, Any]:
        """
        Translate audio file to English text using OpenAI's Whisper model.

        Args:
            audio_file: Path to audio file or file-like object
            **kwargs: Additional parameters for the translation API

        Returns:
            Dict containing translation result and metadata
        """
        try:
            # Extract user_id from kwargs for billing
            self._current_user_id = kwargs.get('user_id')
            # Prepare request parameters
            translation_params = {
                "model": self.model_name,
                "response_format": "verbose_json"
            }
            
            # No additional parameters for translation
            
            # Handle file input
            if isinstance(audio_file, str):
                with open(audio_file, "rb") as f:
                    translation = await self.client.audio.translations.create(
                        file=f,
                        **translation_params
                    )
            else:
                translation = await self.client.audio.translations.create(
                    file=audio_file,
                    **translation_params
                )
            
            # Extract usage information for billing
            result = {
                "text": translation.text,
                "language": "en",  # Translation is always to English
                "duration": getattr(translation, 'duration', None),
                "segments": getattr(translation, 'segments', []),
                "usage": {
                    "input_units": getattr(translation, 'duration', 1),  # Duration in seconds
                    "output_tokens": len(translation.text.split()) if translation.text else 0
                }
            }
            
            # Track usage for billing
            if self._current_user_id:
                await self._publish_billing_event(
                    user_id=self._current_user_id,
                    service_type="audio_stt",
                    operation="translate",
                    input_units=result["usage"]["input_units"],
                    output_tokens=result["usage"]["output_tokens"],
                    metadata={
                        "target_language": "en",
                        "model_name": self.model_name,
                        "provider": self.provider_name
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

    async def transcribe_batch(self, audio_files: List[Union[str, BinaryIO, bytes]], language: Optional[str] = None, prompt: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Transcribe multiple audio files in batch.
        
        Args:
            audio_files: List of audio file paths or file-like objects
            language: Optional language code for better accuracy
            **kwargs: Additional parameters for the transcription API
            
        Returns:
            List of transcription results
        """
        results = []
        for audio_file in audio_files:
            try:
                result = await self.transcribe(audio_file, language, prompt)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to transcribe {audio_file}: {e}")
                results.append({
                    "error": str(e),
                    "file": str(audio_file),
                    "text": None
                })
        
        return results

    async def detect_language(self, audio_file: Union[str, BinaryIO, bytes]) -> Dict[str, Any]:
        """
        Detect the language of an audio file.
        
        Args:
            audio_file: Path to audio file or file-like object
            **kwargs: Additional parameters
            
        Returns:
            Dict containing detected language and confidence
        """
        try:
            # Use transcription with language detection - need to access client directly
            transcription = await self.client.audio.transcriptions.create(
                file=audio_file if not isinstance(audio_file, str) else open(audio_file, "rb"),
                model=self.model_name,
                response_format="verbose_json"
            )
            
            result = {
                "text": transcription.text,
                "language": getattr(transcription, 'language', "unknown")
            }
            
            return {
                "language": result.get("language", "unknown"),
                "confidence": 1.0,  # OpenAI doesn't provide confidence scores
                "text_sample": result.get("text", "")[:100] if result.get("text") else ""
            }
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                "language": "unknown",
                "confidence": 0.0,
                "error": str(e)
            }

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported audio formats.
        
        Returns:
            List of supported file extensions
        """
        return self.supported_formats
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes for OpenAI Whisper.
        
        Returns:
            List of supported language codes
        """
        return [
            'af', 'ar', 'hy', 'az', 'be', 'bs', 'bg', 'ca', 'zh', 'hr', 'cs', 'da',
            'nl', 'en', 'et', 'fi', 'fr', 'gl', 'de', 'el', 'he', 'hi', 'hu', 'is',
            'id', 'it', 'ja', 'kn', 'kk', 'ko', 'lv', 'lt', 'mk', 'ms', 'mr', 'mi',
            'ne', 'no', 'fa', 'pl', 'pt', 'ro', 'ru', 'sr', 'sk', 'sl', 'es', 'sw',
            'sv', 'tl', 'ta', 'th', 'tr', 'uk', 'ur', 'vi', 'cy'
        ]

    def get_max_file_size(self) -> int:
        """
        Get maximum file size limit in bytes.
        
        Returns:
            Maximum file size in bytes
        """
        return self.max_file_size

    async def close(self):
        """Cleanup resources"""
        if hasattr(self.client, 'close'):
            await self.client.close()
        logger.info("OpenAI STT service closed")