"""
ISA HunyuanVideo Service

SOTA open-source video generation service using HunyuanVideo (13B parameters)
- Text-to-Video generation with cinematic quality
- Superior motion accuracy and physics simulation
- Beats Runway Gen-3 in benchmarks
"""

import modal
import time
import json
import os
import logging
import base64
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path

# Define Modal application
app = modal.App("isa-video-hunyuan")

# Define Modal container image with HunyuanVideo dependencies
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install([
        "torch>=2.0.0",
        "torchvision>=0.15.0", 
        "torchaudio>=2.0.0",
        "transformers>=4.35.0",
        "diffusers>=0.24.0",
        "accelerate>=0.24.0",
        "huggingface_hub>=0.19.0",
        "opencv-python>=4.8.0",
        "pillow>=10.0.0",
        "numpy>=1.24.0",
        "imageio>=2.31.0",
        "imageio-ffmpeg>=0.4.8",
        "ffmpeg-python>=0.2.0",
        "requests>=2.31.0",
        "httpx>=0.26.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "safetensors>=0.4.0",
        "xformers>=0.0.22",  # For memory efficiency
        "einops>=0.7.0",
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

# HunyuanVideo Service - Optimized for A100 GPU
@app.cls(
    gpu="A100",              # 80GB A100 for 13B model
    image=image,
    memory=32768,            # 32GB RAM
    timeout=3600,            # 60 minutes for video generation
    scaledown_window=300,    # 5 minutes idle timeout
    min_containers=0,        # Scale to zero
    max_containers=5,        # Support up to 5 concurrent containers
    secrets=[modal.Secret.from_name("huggingface-secret")],  # Optional HF token
)
class ISAVideoHunyuanService:
    """
    ISA HunyuanVideo Service
    
    SOTA 13B parameter video generation model:
    - Model: Tencent/HunyuanVideo
    - Architecture: Diffusion Transformer
    - Performance: Beats Runway Gen-3
    - Capabilities: Text-to-Video, cinematic quality
    """
        
    @modal.enter()
    def load_models(self):
        """Load HunyuanVideo model and dependencies"""
        print("Loading HunyuanVideo (13B parameters)...")
        start_time = time.time()
        
        # Initialize instance variables
        self.pipeline = None
        self.logger = logging.getLogger(__name__)
        self.request_count = 0
        self.total_processing_time = 0.0
        
        try:
            import torch
            from diffusers import HunyuanVideoPipeline
            
            print("Loading HunyuanVideo pipeline...")
            
            # Load HunyuanVideo pipeline with optimizations
            self.pipeline = HunyuanVideoPipeline.from_pretrained(
                "tencent/HunyuanVideo",
                torch_dtype=torch.bfloat16,
                use_safetensors=True,
                variant="bf16"
            )
            
            # Enable memory efficient attention
            if hasattr(self.pipeline, 'enable_xformers_memory_efficient_attention'):
                self.pipeline.enable_xformers_memory_efficient_attention()
            
            # Enable CPU offloading for memory efficiency
            self.pipeline.enable_model_cpu_offload()
            
            # Enable VAE slicing for memory efficiency
            if hasattr(self.pipeline.vae, 'enable_slicing'):
                self.pipeline.vae.enable_slicing()
                
            # Enable VAE tiling for large videos
            if hasattr(self.pipeline.vae, 'enable_tiling'):
                self.pipeline.vae.enable_tiling()
            
            load_time = time.time() - start_time
            print(f"HunyuanVideo loaded successfully in {load_time:.2f}s")
            
            # Model loading status
            self.models_loaded = True
            
        except Exception as e:
            print(f"Model loading failed: {e}")
            import traceback
            traceback.print_exc()
            self.models_loaded = False
    
    @modal.method()
    def generate_video(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_frames: int = 49,
        height: int = 720,
        width: int = 1280,
        fps: int = 15,
        num_inference_steps: int = 30,
        guidance_scale: float = 6.0,
        seed: Optional[int] = None,
        output_format: str = "mp4"
    ) -> Dict[str, Any]:
        """
        Generate video using HunyuanVideo
        
        Args:
            prompt: Text description for video generation
            negative_prompt: What to avoid in generation
            num_frames: Number of frames (default 49, max 129)
            height: Video height (default 720, max 1024)
            width: Video width (default 1280, max 1920) 
            fps: Frames per second (default 15)
            num_inference_steps: Denoising steps (default 30)
            guidance_scale: How closely to follow prompt (default 6.0)
            seed: Random seed for reproducibility
            output_format: Output format ('mp4' or 'gif')
            
        Returns:
            Video generation results with metadata
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Validate model loading status
            if not self.models_loaded or not self.pipeline:
                raise RuntimeError("HunyuanVideo model not loaded")
            
            # Validate parameters
            num_frames = min(max(num_frames, 9), 129)  # Clamp to valid range
            height = min(max(height, 480), 1024)       # Clamp to valid range
            width = min(max(width, 640), 1920)         # Clamp to valid range
            
            # Set random seed if provided
            if seed is not None:
                import torch
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(seed)
            
            print(f"Generating video: {prompt[:100]}...")
            print(f"Parameters: {num_frames} frames, {width}x{height}, {fps}fps")
            
            # Generate video using HunyuanVideo
            video_frames = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_frames=num_frames,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=None if seed is None else torch.Generator().manual_seed(seed)
            ).frames[0]
            
            # Save video to temporary file
            with tempfile.NamedTemporaryFile(suffix=f".{output_format}", delete=False) as tmp_file:
                if output_format.lower() == "mp4":
                    self._save_video_mp4(video_frames, tmp_file.name, fps)
                elif output_format.lower() == "gif":
                    self._save_video_gif(video_frames, tmp_file.name, fps)
                else:
                    raise ValueError(f"Unsupported output format: {output_format}")
                
                # Read video file and encode to base64
                with open(tmp_file.name, "rb") as f:
                    video_data = f.read()
                    video_b64 = base64.b64encode(video_data).decode('utf-8')
                
                # Clean up temp file
                os.unlink(tmp_file.name)
            
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            # Calculate cost (A100 GPU: ~$2.00/hour)
            gpu_cost = (processing_time / 3600) * 2.00
            
            result = {
                'success': True,
                'service': 'isa-video-hunyuan',
                'operation': 'video_generation',
                'provider': 'ISA',
                'video_b64': video_b64,
                'video_format': output_format,
                'prompt': prompt,
                'model': 'HunyuanVideo-13B',
                'architecture': 'Diffusion Transformer',
                'parameters': {
                    'num_frames': num_frames,
                    'height': height,
                    'width': width,
                    'fps': fps,
                    'inference_steps': num_inference_steps,
                    'guidance_scale': guidance_scale,
                    'seed': seed
                },
                'video_info': {
                    'duration_seconds': num_frames / fps,
                    'total_frames': num_frames,
                    'resolution': f"{width}x{height}",
                    'file_size_bytes': len(video_data)
                },
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"video_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round(gpu_cost, 4),
                    'gpu_type': 'A100'
                },
                'model_info': {
                    'model_name': 'HunyuanVideo',
                    'provider': 'ISA',
                    'architecture': 'Diffusion Transformer',
                    'parameters': '13B',
                    'gpu': 'A100',
                    'performance': 'SOTA 2024 (beats Runway Gen-3)',
                    'container_id': os.environ.get('MODAL_TASK_ID', 'unknown')
                }
            }
            
            # Output JSON results
            print("=== JSON_RESULT_START ===")
            print(json.dumps({k: v for k, v in result.items() if k != 'video_b64'}, default=str))
            print("=== JSON_RESULT_END ===")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_result = {
                'success': False,
                'service': 'isa-video-hunyuan',
                'operation': 'video_generation',
                'provider': 'ISA', 
                'error': str(e),
                'processing_time': processing_time,
                'billing': {
                    'request_id': f"video_{self.request_count}_{int(time.time())}",
                    'gpu_seconds': processing_time,
                    'estimated_cost_usd': round((processing_time / 3600) * 2.00, 4),
                    'gpu_type': 'A100'
                }
            }
            
            print("=== JSON_RESULT_START ===")
            print(json.dumps(error_result, default=str))
            print("=== JSON_RESULT_END ===")
            
            return error_result
    
    def _save_video_mp4(self, frames, output_path: str, fps: int):
        """Save video frames as MP4"""
        try:
            import imageio
            
            # Convert frames to numpy arrays if needed
            if hasattr(frames[0], 'numpy'):
                frames = [frame.numpy() for frame in frames]
            
            # Write MP4 video
            imageio.mimsave(
                output_path, 
                frames, 
                fps=fps,
                codec='libx264',
                ffmpeg_params=['-pix_fmt', 'yuv420p']
            )
            
        except Exception as e:
            print(f"Failed to save MP4: {e}")
            raise
    
    def _save_video_gif(self, frames, output_path: str, fps: int):
        """Save video frames as GIF"""
        try:
            import imageio
            
            # Convert frames to numpy arrays if needed
            if hasattr(frames[0], 'numpy'):
                frames = [frame.numpy() for frame in frames]
            
            # Write GIF
            imageio.mimsave(
                output_path,
                frames,
                fps=fps,
                loop=0
            )
            
        except Exception as e:
            print(f"Failed to save GIF: {e}")
            raise
    
    @modal.method()
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'isa-video-hunyuan',
            'provider': 'ISA',
            'models_loaded': self.models_loaded,
            'model': 'HunyuanVideo-13B',
            'architecture': 'Diffusion Transformer', 
            'timestamp': time.time(),
            'gpu': 'A100',
            'memory_usage': '32GB',
            'request_count': self.request_count,
            'performance': 'SOTA 2024 (beats Runway Gen-3)'
        }

# Deployment functions
@app.function()
def deploy_info():
    """Deployment information"""
    return {
        'service': 'isa-video-hunyuan',
        'version': '1.0.0',
        'description': 'ISA HunyuanVideo service - SOTA 13B parameter video generation',
        'model': 'HunyuanVideo-13B',
        'architecture': 'Diffusion Transformer',
        'gpu': 'A100',
        'performance': 'Beats Runway Gen-3',
        'deployment_time': time.time()
    }

@app.function()
def register_service():
    """Register service to model repository"""
    try:
        from isa_model.core.models.model_repo import ModelRepository
        
        repo = ModelRepository()
        
        # Register video generation service
        repo.register_model({
            'model_id': 'isa-hunyuan-video-service',
            'model_type': 'video',
            'provider': 'isa',
            'endpoint': 'https://isa-video-hunyuan.modal.run',
            'capabilities': ['text_to_video', 'video_generation', 'cinematic_quality'],
            'pricing': {'gpu_type': 'A100', 'cost_per_hour': 2.00},
            'metadata': {
                'model': 'HunyuanVideo-13B',
                'architecture': 'Diffusion Transformer',
                'parameters': '13B',
                'performance': 'SOTA 2024',
                'max_resolution': '1920x1024',
                'max_frames': 129,
                'supported_formats': ['mp4', 'gif']
            }
        })
        
        print("HunyuanVideo service registered successfully")
        return {'status': 'registered'}
        
    except Exception as e:
        print(f"Service registration failed: {e}")
        return {'status': 'failed', 'error': str(e)}

if __name__ == "__main__":
    print("ISA HunyuanVideo Service - Modal Deployment")
    print("Deploy with: modal deploy isa_video_hunyuan_service.py")
    print()
    print("Model: HunyuanVideo (13B parameters)")
    print("Architecture: Diffusion Transformer")
    print("Performance: SOTA 2024 (beats Runway Gen-3)")
    print("GPU: A100 (80GB)")
    print()
    print("Usage:")
    print("service.generate_video('A cat walking in a garden', num_frames=49, width=1280, height=720)")