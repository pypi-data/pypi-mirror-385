import logging
from typing import Dict, Any, List, Optional, BinaryIO
import replicate
from tenacity import retry, stop_after_attempt, wait_exponential

from isa_model.inference.services.audio.base_tts_service import BaseTTSService

logger = logging.getLogger(__name__)

class ReplicateTTSService(BaseTTSService):
    """
    Replicate Text-to-Speech service using Kokoro model with unified architecture.
    High-quality voice synthesis with multiple voice options.
    """
    
    def __init__(self, provider_name: str, model_name: str = "jaaari/kokoro-82m:f559560eb822dc509045f3921a1921234918b91739db4bf3daab2169b71c7a13", **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        # Get configuration from centralized config manager
        provider_config = self.get_provider_config()
        
        # Set up Replicate API token from provider configuration
        try:
            self.api_token = provider_config.get('api_key') or provider_config.get('replicate_api_token')
            if not self.api_token:
                raise ValueError("Replicate API token not found in provider configuration")
            
            # Set environment variable for replicate library
            import os
            os.environ['REPLICATE_API_TOKEN'] = self.api_token
            
            # Available voices for Kokoro model
            self.available_voices = [
                "af_bella", "af_nicole", "af_sarah", "af_sky", "am_adam", "am_michael"
            ]
            
            # Default settings
            self.default_voice = "af_nicole"
            self.default_speed = 1.0
            
            logger.info(f"Initialized ReplicateTTSService with model '{self.model_name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize Replicate client: {e}")
            raise ValueError(f"Failed to initialize Replicate client: {e}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def synthesize_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        format: str = "wav",
        **kwargs
    ) -> Dict[str, Any]:
        """Synthesize speech from text using Kokoro model"""
        try:
            # Extract user_id from kwargs for billing
            self._current_user_id = kwargs.get('user_id')
            # Validate and set voice
            selected_voice = voice or self.default_voice
            if selected_voice not in self.available_voices:
                logger.warning(f"Voice '{selected_voice}' not available, using default '{self.default_voice}'")
                selected_voice = self.default_voice
            
            # Prepare input parameters
            input_params = {
                "text": text,
                "voice": selected_voice,
                "speed": max(0.5, min(2.0, speed))  # Clamp speed between 0.5 and 2.0
            }
            
            logger.info(f"Synthesizing speech with voice '{selected_voice}' and speed {speed}")
            
            # Run the model
            output = await replicate.async_run(self.model_name, input=input_params)
            
            # Handle different output formats
            try:
                if isinstance(output, str):
                    audio_url = output
                elif hasattr(output, 'url'):
                    # Handle FileOutput object
                    audio_url = str(getattr(output, 'url', output))
                elif isinstance(output, list) and len(output) > 0:
                    first_output = output[0]
                    if hasattr(first_output, 'url'):
                        audio_url = str(getattr(first_output, 'url', first_output))
                    else:
                        audio_url = str(first_output)
                else:
                    # Convert to string as fallback
                    audio_url = str(output)
            except Exception:
                # Safe fallback
                audio_url = str(output)
            
            # Estimate audio duration for billing (rough estimation: ~150 words per minute)
            words = len(text.split())
            estimated_duration_seconds = (words / 150.0) * 60.0 / speed
            
            # Track usage for billing
            if self._current_user_id:
                await self._publish_billing_event(
                    user_id=self._current_user_id,
                    service_type="audio_tts",
                    operation="synthesize_speech",
                    input_tokens=0,
                    output_tokens=0,
                    input_units=len(text),  # Text length
                    output_units=estimated_duration_seconds,  # Audio duration in seconds
                    metadata={
                        "model": self.model_name,
                        "voice": selected_voice,
                        "speed": speed,
                        "text_length": len(text),
                        "estimated_duration_seconds": estimated_duration_seconds
                    }
                )
            
            # Download audio data for return format consistency
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(audio_url) as response:
                    response.raise_for_status()
                    audio_data = await response.read()
            
            result = {
                "audio_data": audio_data,
                "format": "wav",  # Kokoro typically outputs WAV
                "duration": estimated_duration_seconds,
                "sample_rate": 22050,
                "audio_url": audio_url,  # Keep URL for reference
                "metadata": {
                    "model": self.model_name,
                    "provider": "replicate",
                    "voice": selected_voice,
                    "speed": speed,
                    "voice_options": self.available_voices
                }
            }
            
            logger.info(f"Speech synthesis completed: {audio_url}")
            return result

        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise

    async def invoke(
        self,
        text: Optional[str] = None,
        task: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Unified invoke method for Replicate TTS service.
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
        format: str = "wav"
    ) -> Dict[str, Any]:
        """Synthesize speech and save to file"""
        try:
            # Get synthesis result
            result = await self.synthesize_speech(text, voice, speed, pitch, format)
            audio_data = result["audio_data"]
            
            # Save audio data to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            return {
                "file_path": output_path,
                "duration": result["duration"],
                "sample_rate": result["sample_rate"],
                "file_size": len(audio_data)
            }
            
        except Exception as e:
            logger.error(f"Error saving audio to file: {e}")
            raise
    
    async def synthesize_speech_batch(
        self, 
        texts: List[str], 
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        format: str = "wav"
    ) -> List[Dict[str, Any]]:
        """Synthesize multiple texts"""
        results = []
        
        for text in texts:
            try:
                result = await self.synthesize_speech(text, voice, speed)
                results.append(result)
            except Exception as e:
                logger.error(f"Error synthesizing text '{text[:50]}...': {e}")
                results.append({
                    "audio_url": None,
                    "text": text,
                    "voice": voice or self.default_voice,
                    "speed": speed,
                    "error": str(e)
                })
        
        return results
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices"""
        voices = []
        for voice in self.available_voices:
            voice_info = self.get_voice_info(voice)
            voices.append({
                "id": voice,
                "name": voice.replace("_", " ").title(),
                "language": "en-US",
                "gender": voice_info.get("gender", "unknown"),
                "age": "adult"
            })
        return voices
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return ["wav", "mp3"]  # Kokoro typically outputs WAV
    
    def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """Get information about a specific voice"""
        if voice_id not in self.available_voices:
            return {"error": f"Voice '{voice_id}' not available"}
        
        # Voice metadata (you can expand this with more details)
        voice_info = {
            "af_bella": {"id": "af_bella", "name": "Bella", "gender": "female", "language": "en-US", "description": "Warm, friendly female voice", "sample_rate": 22050},
            "af_nicole": {"id": "af_nicole", "name": "Nicole", "gender": "female", "language": "en-US", "description": "Clear, professional female voice", "sample_rate": 22050},
            "af_sarah": {"id": "af_sarah", "name": "Sarah", "gender": "female", "language": "en-US", "description": "Gentle, expressive female voice", "sample_rate": 22050},
            "af_sky": {"id": "af_sky", "name": "Sky", "gender": "female", "language": "en-US", "description": "Bright, energetic female voice", "sample_rate": 22050},
            "am_adam": {"id": "am_adam", "name": "Adam", "gender": "male", "language": "en-US", "description": "Deep, authoritative male voice", "sample_rate": 22050},
            "am_michael": {"id": "am_michael", "name": "Michael", "gender": "male", "language": "en-US", "description": "Smooth, conversational male voice", "sample_rate": 22050}
        }
        
        return voice_info.get(voice_id, {"id": voice_id, "gender": "unknown", "language": "en-US", "description": "Voice information not available", "sample_rate": 22050})
    
    async def close(self):
        """Cleanup resources"""
        logger.info("ReplicateTTSService resources cleaned up") 