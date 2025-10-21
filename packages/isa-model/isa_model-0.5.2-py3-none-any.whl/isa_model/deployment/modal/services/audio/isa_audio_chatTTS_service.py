"""
ISA ChatTTS Service

ChatTTS text-to-speech service optimized for dialogue scenarios
- High-quality Chinese and English speech synthesis
- Support for prosody control (laughter, pauses, etc.)
- Fast inference and deployment
- Professional dialogue scene optimization
"""

import modal
import time
import json
import os
import logging
import base64
import tempfile
import io
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import numpy as np

# Define Modal application
app = modal.App("isa-audio-chatTTS")

# Define Modal container image with ChatTTS dependencies
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install([
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "transformers>=4.41.0",
        "accelerate>=0.26.0",
        "numpy>=1.24.0",
        "soundfile>=0.12.0",
        "librosa>=0.10.0",
        "scipy>=1.11.0",
        "omegaconf>=2.3.0",
        "hydra-core>=1.3.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
        "httpx>=0.26.0",
        "python-dotenv>=1.0.0",
        "ChatTTS",                 # ChatTTS main package
        "pyopenjtalk",             # For better text processing
        "pypinyin",                # For Chinese pronunciation
        "jieba",                   # Chinese word segmentation
        "opencc-python-reimplemented",  # Chinese text conversion
        "vocos",                   # Neural vocoder
        "vector-quantize-pytorch", # Vector quantization
        "einops",                  # Tensor operations
        "pydub",                   # Audio processing
        "ffmpeg-python",           # Audio conversion
    ])
    .apt_install([
        "ffmpeg",
        "libsndfile1",
        "libsox-dev",
        "sox",
        "espeak-ng",
        "libmecab-dev",
        "mecab-ipadic-utf8",
        "git-lfs"
    ])
    .env({
        "TRANSFORMERS_CACHE": "/models",
        "TORCH_HOME": "/models/torch", 
        "HF_HOME": "/models",
        "CUDA_VISIBLE_DEVICES": "0",
        "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:512"
    })
)

# ChatTTS Service - Optimized for A10G GPU
@app.cls(
    gpu="A10G",              # 24GB A10G for ChatTTS
    image=image,
    memory=16384,            # 16GB RAM
    timeout=1800,            # 30 minutes
    scaledown_window=300,    # 5 minutes idle timeout
    min_containers=0,        # Scale to zero
    max_containers=8,        # Support multiple concurrent requests
    # secrets=[modal.Secret.from_name("huggingface-secret")],  # Optional HF token
)
class ISAudioChatTTSService:
    """
    ISA ChatTTS Service
    
    ChatTTS text-to-speech service:
    - Model: ChatTTS (2DFN-AI/ChatTTS)
    - Architecture: Transformer-based TTS
    - Capabilities: Chinese/English TTS, prosody control, dialogue optimization
    - Performance: Fast inference, high-quality output
    """
        
    @modal.enter()
    def load_models(self):
        """Load ChatTTS model and dependencies"""
        print("Loading ChatTTS model...")
        start_time = time.time()
        
        # Initialize instance variables
        self.chat_tts = None
        self.logger = logging.getLogger(__name__)
        self.request_count = 0
        self.total_processing_time = 0.0
        
        try:
            import torch
            import ChatTTS
            
            # Initialize ChatTTS
            self.chat_tts = ChatTTS.Chat()
            
            # Load models - use HF models for better stability
            print("Loading ChatTTS models from HuggingFace...")
            self.chat_tts.load(
                compile=False,  # Disable compilation for compatibility
                source="huggingface"  # Use HuggingFace models
            )
            
            # Remove default params that might cause issues
            self.default_params = {}
            
            # Test model with a simple generation
            print("Testing ChatTTS model...")
            test_text = "Hello world, this is a test."
            test_audio = self.chat_tts.infer([test_text], use_decoder=True)
            
            if test_audio and len(test_audio) > 0:
                print("ChatTTS model test successful")
                self.models_loaded = True
            else:
                print("ChatTTS model test failed")
                self.models_loaded = False
                
            load_time = time.time() - start_time
            print(f"ChatTTS loaded successfully in {load_time:.2f}s")
            
        except Exception as e:
            print(f"ChatTTS loading failed: {e}")
            import traceback
            traceback.print_exc()
            self.models_loaded = False
            self.chat_tts = None
    
    @modal.method()
    def synthesize_speech(
        self,
        text: str,
        speaker_id: Optional[str] = None,
        language: str = "auto",
        speed: float = 1.0,
        temperature: float = 0.3,
        top_p: float = 0.7,
        top_k: int = 20,
        audio_seed: int = 2,
        text_seed: int = 42,
        enable_enhancement: bool = True,
        output_format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Synthesize speech using ChatTTS
        
        Args:
            text: Text to synthesize
            speaker_id: Optional speaker ID for voice consistency
            language: Language code ("zh", "en", "auto")
            speed: Speech speed multiplier (0.5-2.0)
            temperature: Sampling temperature (0.01-1.0)
            top_p: Top-p sampling (0.1-1.0)
            top_k: Top-k sampling (1-100)
            audio_seed: Audio generation seed
            text_seed: Text processing seed
            enable_enhancement: Enable audio enhancement
            output_format: Output format ("wav", "mp3", "flac")
            
        Returns:
            Speech synthesis results
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Validate model loading status
            if not self.models_loaded or not self.chat_tts:
                raise RuntimeError("ChatTTS model not loaded")
            
            # Validate input parameters
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            # Preprocess text
            processed_text = self._preprocess_text(text, language)
            
            print(f"Synthesizing: '{processed_text[:50]}...'")
            
            # Generate speech using correct ChatTTS API
            import torch
            import ChatTTS
            
            with torch.no_grad():
                # Sample random speaker if speaker_id is provided
                if speaker_id:
                    spk_emb = self.chat_tts.sample_random_speaker()
                else:
                    spk_emb = None
                
                # Configure inference parameters using correct API
                params_infer_code = ChatTTS.Chat.InferCodeParams(
                    spk_emb=spk_emb,
                    temperature=temperature,
                    top_P=top_p,
                    top_K=top_k
                )
                
                # Configure text refinement parameters
                params_refine_text = ChatTTS.Chat.RefineTextParams(
                    prompt='[oral_2][laugh_0][break_4]'  # Default prosody control
                )
                
                # Generate audio with proper parameters
                audio_data = self.chat_tts.infer(
                    [processed_text],
                    use_decoder=True,
                    params_infer_code=params_infer_code,
                    params_refine_text=params_refine_text
                )
            
            if not audio_data or len(audio_data) == 0:
                raise RuntimeError("Speech synthesis failed - no audio generated")
            
            # Process audio output
            audio_array = audio_data[0]  # Get first (and only) audio
            
            # Apply speed adjustment
            if speed != 1.0:
                audio_array = self._adjust_speed(audio_array, speed)
            
            # Apply enhancement if enabled
            if enable_enhancement:
                audio_array = self._enhance_audio(audio_array)
            
            # Convert to desired format and encode
            audio_b64 = self._encode_audio(audio_array, output_format)
            
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            # Calculate cost (A10G GPU: ~$1.20/hour)
            gpu_cost = (processing_time / 3600) * 1.20
            
            # Calculate audio metrics
            sample_rate = 24000  # ChatTTS default sample rate
            duration = len(audio_array) / sample_rate
            
            result = {
                'success': True,
                'service': 'isa-audio-chatTTS',
                'operation': 'speech_synthesis',
                'provider': 'ISA',
                'audio_b64': audio_b64,
                'text': text,
                'processed_text': processed_text,
                'model': 'ChatTTS',
                'architecture': 'Transformer-based TTS',
                'parameters': {
                    'speaker_id': speaker_id,
                    'language': language,
                    'speed': speed,
                    'temperature': temperature,
                    'top_p': top_p,
                    'top_k': top_k,
                    'audio_seed': audio_seed,
                    'text_seed': text_seed,
                    'enhancement': enable_enhancement,
                    'output_format': output_format
                },
                'audio_info': {
                    'sample_rate': sample_rate,
                    'duration': round(duration, 2),
                    'channels': 1,
                    'format': output_format,
                    'quality': 'high'
                },
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"tts_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round(gpu_cost, 4),
                    'gpu_type': 'A10G'
                },
                'model_info': {
                    'model_name': 'ChatTTS',
                    'provider': 'ISA',
                    'architecture': 'Transformer-based TTS',
                    'specialization': 'dialogue_optimized',
                    'gpu': 'A10G',
                    'capabilities': ['chinese_tts', 'english_tts', 'prosody_control', 'dialogue_tts'],
                    'container_id': os.environ.get('MODAL_TASK_ID', 'unknown')
                }
            }
            
            # Output JSON results
            print("=== JSON_RESULT_START ===")
            print(json.dumps(result, default=str, ensure_ascii=False))
            print("=== JSON_RESULT_END ===")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_result = {
                'success': False,
                'service': 'isa-audio-chatTTS',
                'operation': 'speech_synthesis',
                'provider': 'ISA',
                'error': str(e),
                'text': text,
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"tts_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round((processing_time / 3600) * 1.20, 4),
                    'gpu_type': 'A10G'
                }
            }
            
            print("=== JSON_RESULT_START ===")
            print(json.dumps(error_result, default=str, ensure_ascii=False))
            print("=== JSON_RESULT_END ===")
            
            return error_result
    
    @modal.method()
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'isa-audio-chatTTS',
            'provider': 'ISA',
            'models_loaded': self.models_loaded,
            'model': 'ChatTTS',
            'architecture': 'Transformer-based TTS',
            'timestamp': time.time(),
            'gpu': 'A10G',
            'memory_usage': '16GB',
            'request_count': self.request_count,
            'capabilities': ['chinese_tts', 'english_tts', 'prosody_control', 'dialogue_tts']
        }
    
    # ==================== UTILITY METHODS ====================
    
    def _preprocess_text(self, text: str, language: str) -> str:
        """Preprocess text for TTS"""
        # Basic text cleaning
        text = text.strip()
        
        # Language-specific preprocessing
        if language == "zh" or self._is_chinese(text):
            return self._preprocess_chinese(text)
        elif language == "en" or self._is_english(text):
            return self._preprocess_english(text)
        else:
            # Auto-detect and process
            if self._is_chinese(text):
                return self._preprocess_chinese(text)
            else:
                return self._preprocess_english(text)
    
    def _preprocess_chinese(self, text: str) -> str:
        """Preprocess Chinese text"""
        try:
            # Traditional to Simplified conversion
            from opencc import OpenCC
            cc = OpenCC('t2s')
            text = cc.convert(text)
            return text
        except:
            return text
    
    def _preprocess_english(self, text: str) -> str:
        """Preprocess English text"""
        # Basic normalization
        text = text.replace('&', ' and ')
        text = text.replace('@', ' at ')
        text = text.replace('#', ' number ')
        text = text.replace('%', ' percent ')
        return text
    
    def _is_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters"""
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False
    
    def _is_english(self, text: str) -> bool:
        """Check if text is primarily English"""
        english_chars = sum(1 for char in text if char.isalpha() and ord(char) < 128)
        total_chars = sum(1 for char in text if char.isalpha())
        return total_chars > 0 and english_chars / total_chars > 0.8
    
    def _get_speaker_embedding(self, speaker_id: Optional[str]) -> Optional[Any]:
        """Get speaker embedding for voice consistency"""
        if not speaker_id:
            return None
        
        try:
            import torch
            # Sample a random speaker embedding
            rand_spk = self.chat_tts.sample_random_speaker()
            return rand_spk
        except Exception as e:
            print(f"Speaker embedding error: {e}")
            return None
    
    def _adjust_speed(self, audio: np.ndarray, speed: float) -> np.ndarray:
        """Adjust audio speed"""
        try:
            import librosa
            return librosa.effects.time_stretch(audio, rate=speed)
        except:
            return audio
    
    def _enhance_audio(self, audio: np.ndarray) -> np.ndarray:
        """Apply audio enhancement"""
        try:
            import scipy.signal
            # Simple audio enhancement
            audio = scipy.signal.wiener(audio)
            audio = audio / np.max(np.abs(audio))
            return audio
        except:
            return audio
    
    def _encode_audio(self, audio: np.ndarray, format: str) -> str:
        """Encode audio to base64"""
        try:
            import soundfile as sf
            import io
            
            # Convert to 16-bit PCM
            audio_int16 = (audio * 32767).astype(np.int16)
            
            # Save to bytes
            buffer = io.BytesIO()
            sf.write(buffer, audio_int16, 24000, format=format.upper())
            buffer.seek(0)
            
            # Encode to base64
            audio_b64 = base64.b64encode(buffer.read()).decode('utf-8')
            return audio_b64
            
        except Exception as e:
            print(f"Audio encoding error: {e}")
            return ""

# Deployment functions
@app.function()
def deploy_info():
    """Deployment information"""
    return {
        'service': 'isa-audio-chatTTS',
        'version': '1.0.0',
        'description': 'ISA ChatTTS service - Dialogue-optimized TTS',
        'model': 'ChatTTS',
        'architecture': 'Transformer-based TTS',
        'gpu': 'A10G',
        'capabilities': ['chinese_tts', 'english_tts', 'prosody_control', 'dialogue_tts'],
        'deployment_time': time.time()
    }

@app.function()
def register_service():
    """Register service to model repository"""
    try:
        from isa_model.core.models.model_repo import ModelRepository
        
        repo = ModelRepository()
        
        # Register ChatTTS service
        repo.register_model({
            'model_id': 'isa-chatTTS-service',
            'model_type': 'audio',
            'provider': 'isa',
            'endpoint': 'https://isa-audio-chatTTS.modal.run',
            'capabilities': ['chinese_tts', 'english_tts', 'prosody_control', 'dialogue_tts'],
            'pricing': {'gpu_type': 'A10G', 'cost_per_hour': 1.20},
            'metadata': {
                'model': 'ChatTTS',
                'architecture': 'Transformer-based TTS',
                'specialization': 'dialogue_optimized',
                'languages': ['zh', 'en'],
                'sample_rate': 24000,
                'max_text_length': 1000
            }
        })
        
        print("ChatTTS service registered successfully")
        return {'status': 'registered'}
        
    except Exception as e:
        print(f"Service registration failed: {e}")
        return {'status': 'failed', 'error': str(e)}

if __name__ == "__main__":
    print("ISA ChatTTS Service - Modal Deployment")
    print("Deploy with: modal deploy isa_audio_chatTTS_service.py")
    print()
    print("Model: ChatTTS")
    print("Architecture: Transformer-based TTS")
    print("Capabilities: Chinese/English TTS, prosody control, dialogue optimization")
    print("GPU: A10G (24GB)")
    print()
    print("Usage:")
    print("# Speech synthesis")
    print("service.synthesize_speech('Hello world!', language='en')")
    print("# Health check")
    print("service.health_check()")