"""
ISA Qwen2.5-VL Service

Multimodal vision-language service using Qwen2.5-VL 7B
- Image understanding and analysis
- Video understanding and analysis
- Vision-language reasoning
- High-quality visual content interpretation
"""

import modal
import time
import json
import os
import logging
import base64
import tempfile
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Define Modal application
app = modal.App("isa-vision-qwen2.5")

# Define Modal container image with Qwen2.5-VL dependencies
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install([
        "packaging",               # Required dependency
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "transformers>=4.37.0",
        "accelerate>=0.26.0",
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "requests>=2.31.0",
        "httpx>=0.26.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "qwen-vl-utils",           # Qwen VL utilities
        "av",                      # Video processing
        "decord",                  # Video decoding
        "imageio>=2.31.0",
        "imageio-ffmpeg>=0.4.8",
        "tiktoken>=0.5.0",
        "sentencepiece>=0.1.99",
        "protobuf>=3.20.0",
        # "flash-attn>=2.0.0",     # Optional - removed for easier deployment
    ])
    .apt_install([
        "ffmpeg",
        "libsm6",
        "libxext6", 
        "libxrender-dev",
        "libglib2.0-0",
        "libgl1-mesa-glx",
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

# Qwen2.5-VL Service - Optimized for performance
@app.cls(
    gpu="A100",              # Use A100 for better performance (40GB)
    image=image,
    memory=32768,            # 32GB RAM for faster processing
    timeout=1800,            # 30 minutes
    scaledown_window=300,    # 5 minutes idle timeout (longer for model warmup)
    min_containers=1,        # Keep 1 container warm
    max_containers=5,        # Limit for cost control
    # secrets=[modal.Secret.from_name("huggingface-secret")],  # Optional HF token
)
class ISAVisionQwen25Service:
    """
    ISA Qwen2.5-VL Service
    
    Multimodal vision-language model (7B parameters):
    - Model: Qwen/Qwen2.5-VL-7B-Instruct
    - Architecture: Vision Transformer + Language Model
    - Capabilities: Image understanding, Video understanding, VL reasoning
    - Performance: SOTA multimodal understanding
    """
        
    @modal.enter()
    def load_models(self):
        """Load Qwen2.5-VL model and dependencies"""
        print("Loading Qwen2.5-VL (7B parameters)...")
        start_time = time.time()
        
        # Initialize instance variables
        self.model = None
        self.processor = None
        self.logger = logging.getLogger(__name__)
        self.request_count = 0
        self.total_processing_time = 0.0
        
        try:
            import torch
            from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
            from qwen_vl_utils import process_vision_info
            
            # Store the function as instance variable for later use
            self.process_vision_info = process_vision_info
            
            model_name = "Qwen/Qwen2.5-VL-7B-Instruct"
            
            print(f"Loading Qwen2.5-VL model: {model_name}")
            
            # Load model with optimizations for speed
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16,  # Use float16 for speed
                device_map="auto",
                attn_implementation="sdpa",  # Use SDPA for better performance
                low_cpu_mem_usage=True,     # Reduce CPU memory usage
                use_cache=True              # Enable KV cache
            )
            
            # Load processor for image/video processing
            self.processor = AutoProcessor.from_pretrained(
                model_name,
                use_fast=True  # Use fast tokenizer for speed
            )
            
            # Set model to evaluation mode and optimize for inference
            self.model.eval()
            
            # Compile model for faster inference (PyTorch 2.0+)
            try:
                self.model = torch.compile(self.model, mode="reduce-overhead")
                print("✅ Model compiled for faster inference")
            except Exception as e:
                print(f"⚠️ Model compilation failed: {e}")
                
            # Enable CPU offloading for memory efficiency
            self.model.tie_weights()
            
            load_time = time.time() - start_time
            print(f"Qwen2.5-VL loaded successfully in {load_time:.2f}s")
            
            # Model loading status
            self.models_loaded = True
            
        except Exception as e:
            print(f"Model loading failed: {e}")
            import traceback
            traceback.print_exc()
            self.models_loaded = False
    
    @modal.method()
    def analyze_image(
        self,
        image_b64: str,
        prompt: str = "Describe this image in detail.",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Dict[str, Any]:
        """
        Analyze image using Qwen2.5-VL
        
        Args:
            image_b64: Base64 encoded image
            prompt: Question or instruction about the image
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Returns:
            Image analysis results
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Validate model loading status
            if not self.models_loaded or not self.model:
                raise RuntimeError("Qwen2.5-VL model not loaded")
            
            # Decode base64 image
            image_data = base64.b64decode(image_b64)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                tmp_file.write(image_data)
                tmp_file.flush()
                
                # Prepare messages for the model
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "image": tmp_file.name,
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ]
                
                # Process the conversation
                text = self.processor.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                
                # Process vision info
                image_inputs, video_inputs = self.process_vision_info(messages)
                
                # Prepare inputs
                inputs = self.processor(
                    text=[text],
                    images=image_inputs,
                    videos=video_inputs,
                    padding=True,
                    return_tensors="pt",
                )
                inputs = inputs.to("cuda")
                
                # Generate response with optimized parameters
                import torch
                with torch.no_grad():
                    generated_ids = self.model.generate(
                        **inputs,
                        max_new_tokens=min(max_tokens, 200),  # Limit max tokens for speed
                        temperature=temperature,
                        top_p=top_p,
                        do_sample=True,
                        pad_token_id=self.processor.tokenizer.eos_token_id,
                        use_cache=True,           # Enable KV cache
                        num_beams=1,              # Use greedy decoding for speed
                        early_stopping=True       # Stop early when possible
                    )
                
                # Extract generated tokens (remove input tokens)
                generated_ids_trimmed = [
                    out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                ]
                
                # Decode response
                response_text = self.processor.batch_decode(
                    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
                )[0]
                
                # Clean up temp file
                os.unlink(tmp_file.name)
            
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            # Calculate cost (A100 GPU: ~$4.00/hour)
            gpu_cost = (processing_time / 3600) * 4.00
            
            result = {
                'success': True,
                'service': 'isa-vision-qwen2.5',
                'operation': 'image_analysis',
                'provider': 'ISA',
                'text': response_text,
                'prompt': prompt,
                'model': 'Qwen2.5-VL-7B-Instruct',
                'architecture': 'Vision Transformer + Language Model',
                'modality': 'image',
                'parameters': {
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                    'top_p': top_p
                },
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"img_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round(gpu_cost, 4),
                    'gpu_type': 'A100'
                },
                'model_info': {
                    'model_name': 'Qwen2.5-VL-7B-Instruct',
                    'provider': 'ISA',
                    'architecture': 'Multimodal Vision-Language',
                    'parameters': '7B',
                    'gpu': 'A100',
                    'capabilities': ['image_understanding', 'vision_language_reasoning'],
                    'container_id': os.environ.get('MODAL_TASK_ID', 'unknown')
                }
            }
            
            # Output JSON results
            print("=== JSON_RESULT_START ===")
            print(json.dumps(result, default=str))
            print("=== JSON_RESULT_END ===")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_result = {
                'success': False,
                'service': 'isa-vision-qwen2.5',
                'operation': 'image_analysis',
                'provider': 'ISA', 
                'error': str(e),
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"img_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round((processing_time / 3600) * 1.20, 4),
                    'gpu_type': 'A100'
                }
            }
            
            print("=== JSON_RESULT_START ===")
            print(json.dumps(error_result, default=str))
            print("=== JSON_RESULT_END ===")
            
            return error_result
    
    @modal.method()
    def analyze_video(
        self,
        video_b64: str,
        prompt: str = "Describe what happens in this video.",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_frames: int = 8
    ) -> Dict[str, Any]:
        """
        Analyze video using Qwen2.5-VL
        
        Args:
            video_b64: Base64 encoded video
            prompt: Question or instruction about the video
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            max_frames: Maximum frames to sample from video
            
        Returns:
            Video analysis results
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Validate model loading status
            if not self.models_loaded or not self.model:
                raise RuntimeError("Qwen2.5-VL model not loaded")
            
            # Decode base64 video
            video_data = base64.b64decode(video_b64)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
                tmp_file.write(video_data)
                tmp_file.flush()
                
                # Prepare messages for the model
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "video",
                                "video": tmp_file.name,
                                "max_pixels": 360 * 420,
                                "fps": 1.0,
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ]
                
                # Process the conversation
                text = self.processor.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                
                # Process vision info
                image_inputs, video_inputs = self.process_vision_info(messages)
                
                # Prepare inputs
                inputs = self.processor(
                    text=[text],
                    images=image_inputs,
                    videos=video_inputs,
                    padding=True,
                    return_tensors="pt",
                )
                inputs = inputs.to("cuda")
                
                # Generate response with optimized parameters
                import torch
                with torch.no_grad():
                    generated_ids = self.model.generate(
                        **inputs,
                        max_new_tokens=min(max_tokens, 200),  # Limit max tokens for speed
                        temperature=temperature,
                        top_p=top_p,
                        do_sample=True,
                        pad_token_id=self.processor.tokenizer.eos_token_id,
                        use_cache=True,           # Enable KV cache
                        num_beams=1,              # Use greedy decoding for speed
                        early_stopping=True       # Stop early when possible
                    )
                
                # Extract generated tokens (remove input tokens)
                generated_ids_trimmed = [
                    out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                ]
                
                # Decode response
                response_text = self.processor.batch_decode(
                    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
                )[0]
                
                # Clean up temp file
                os.unlink(tmp_file.name)
            
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            # Calculate cost (A100 GPU: ~$4.00/hour)
            gpu_cost = (processing_time / 3600) * 4.00
            
            result = {
                'success': True,
                'service': 'isa-vision-qwen2.5',
                'operation': 'video_analysis',
                'provider': 'ISA',
                'text': response_text,
                'prompt': prompt,
                'model': 'Qwen2.5-VL-7B-Instruct',
                'architecture': 'Vision Transformer + Language Model',
                'modality': 'video',
                'parameters': {
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                    'top_p': top_p,
                    'max_frames': max_frames
                },
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"vid_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round(gpu_cost, 4),
                    'gpu_type': 'A100'
                },
                'model_info': {
                    'model_name': 'Qwen2.5-VL-7B-Instruct',
                    'provider': 'ISA',
                    'architecture': 'Multimodal Vision-Language',
                    'parameters': '7B',
                    'gpu': 'A100',
                    'capabilities': ['video_understanding', 'temporal_reasoning', 'vision_language_reasoning'],
                    'container_id': os.environ.get('MODAL_TASK_ID', 'unknown')
                }
            }
            
            # Output JSON results
            print("=== JSON_RESULT_START ===")
            print(json.dumps(result, default=str))
            print("=== JSON_RESULT_END ===")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_result = {
                'success': False,
                'service': 'isa-vision-qwen2.5',
                'operation': 'video_analysis',
                'provider': 'ISA', 
                'error': str(e),
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"vid_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round((processing_time / 3600) * 1.20, 4),
                    'gpu_type': 'A100'
                }
            }
            
            print("=== JSON_RESULT_START ===")
            print(json.dumps(error_result, default=str))
            print("=== JSON_RESULT_END ===")
            
            return error_result
    
    @modal.method()
    def multimodal_chat(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Dict[str, Any]:
        """
        Multimodal chat with images/videos
        
        Args:
            messages: List of chat messages with images/videos
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Returns:
            Chat response
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Validate model loading status
            if not self.models_loaded or not self.model:
                raise RuntimeError("Qwen2.5-VL model not loaded")
            
            # Process the conversation
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            # Process vision info
            image_inputs, video_inputs = self.process_vision_info(messages)
            
            # Prepare inputs
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to("cuda")
            
            # Generate response
            import torch
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            # Extract generated tokens (remove input tokens)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            # Decode response
            response_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0]
            
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            # Calculate cost (A100 GPU: ~$4.00/hour)
            gpu_cost = (processing_time / 3600) * 4.00
            
            result = {
                'success': True,
                'service': 'isa-vision-qwen2.5',
                'operation': 'multimodal_chat',
                'provider': 'ISA',
                'text': response_text,
                'model': 'Qwen2.5-VL-7B-Instruct',
                'architecture': 'Vision Transformer + Language Model',
                'modality': 'multimodal',
                'parameters': {
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                    'top_p': top_p
                },
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"chat_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round(gpu_cost, 4),
                    'gpu_type': 'A100'
                },
                'model_info': {
                    'model_name': 'Qwen2.5-VL-7B-Instruct',
                    'provider': 'ISA',
                    'architecture': 'Multimodal Vision-Language',
                    'parameters': '7B',
                    'gpu': 'A100',
                    'capabilities': ['image_understanding', 'video_understanding', 'multimodal_chat'],
                    'container_id': os.environ.get('MODAL_TASK_ID', 'unknown')
                }
            }
            
            # Output JSON results
            print("=== JSON_RESULT_START ===")
            print(json.dumps(result, default=str))
            print("=== JSON_RESULT_END ===")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_result = {
                'success': False,
                'service': 'isa-vision-qwen2.5',
                'operation': 'multimodal_chat',
                'provider': 'ISA', 
                'error': str(e),
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"chat_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round((processing_time / 3600) * 1.20, 4),
                    'gpu_type': 'A100'
                }
            }
            
            print("=== JSON_RESULT_START ===")
            print(json.dumps(error_result, default=str))
            print("=== JSON_RESULT_END ===")
            
            return error_result
    
    @modal.method()
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'isa-vision-qwen2.5',
            'provider': 'ISA',
            'models_loaded': self.models_loaded,
            'model': 'Qwen2.5-VL-7B-Instruct',
            'architecture': 'Vision Transformer + Language Model',
            'timestamp': time.time(),
            'gpu': 'A100',
            'memory_usage': '32GB',
            'request_count': self.request_count,
            'capabilities': ['image_understanding', 'video_understanding', 'multimodal_chat']
        }

# Deployment functions
@app.function()
def deploy_info():
    """Deployment information"""
    return {
        'service': 'isa-vision-qwen2.5',
        'version': '1.0.0',
        'description': 'ISA Qwen2.5-VL service - 7B multimodal vision-language model',
        'model': 'Qwen2.5-VL-7B-Instruct',
        'architecture': 'Vision Transformer + Language Model',
        'gpu': 'A10G',
        'capabilities': ['image_understanding', 'video_understanding'],
        'deployment_time': time.time()
    }

@app.function()
def register_service():
    """Register service to model repository"""
    try:
        from isa_model.core.models.model_repo import ModelRepository
        
        repo = ModelRepository()
        
        # Register multimodal vision service
        repo.register_model({
            'model_id': 'isa-qwen2.5-vl-service',
            'model_type': 'vision',
            'provider': 'isa',
            'endpoint': 'https://isa-vision-qwen2.5.modal.run',
            'capabilities': ['image_understanding', 'video_understanding', 'multimodal_chat', 'vision_language_reasoning'],
            'pricing': {'gpu_type': 'A10G', 'cost_per_hour': 1.20},
            'metadata': {
                'model': 'Qwen2.5-VL-7B-Instruct',
                'architecture': 'Vision Transformer + Language Model',
                'parameters': '7B',
                'modalities': ['image', 'video', 'text'],
                'max_tokens': 1000,
                'supported_formats': ['jpg', 'png', 'gif', 'mp4', 'avi']
            }
        })
        
        print("Qwen2.5-VL service registered successfully")
        return {'status': 'registered'}
        
    except Exception as e:
        print(f"Service registration failed: {e}")
        return {'status': 'failed', 'error': str(e)}

if __name__ == "__main__":
    print("ISA Qwen2.5-VL Service - Modal Deployment")
    print("Deploy with: modal deploy isa_vision_qwen2.5_service.py")
    print()
    print("Model: Qwen2.5-VL-7B-Instruct")
    print("Architecture: Vision Transformer + Language Model")
    print("Capabilities: Image & Video Understanding")
    print("GPU: A10G (24GB)")
    print()
    print("Usage:")
    print("# Image analysis")
    print("service.analyze_image(image_b64, 'What do you see in this image?')")
    print("# Video analysis") 
    print("service.analyze_video(video_b64, 'Describe what happens in this video')")