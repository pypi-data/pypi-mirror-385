"""
Automated HuggingFace to Modal Deployment Service

This service automatically generates and deploys HuggingFace models to Modal
with optimized configurations based on model type and architecture.
"""

import os
import json
import time
import requests
import tempfile
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from huggingface_hub import HfApi, model_info
import logging

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for a HuggingFace model deployment"""
    model_id: str
    model_type: str  # text, vision, audio, image, embedding
    architecture: str
    parameters: str
    gpu_requirements: str
    memory_gb: int
    container_memory_mb: int
    python_version: str = "3.10"
    dependencies: List[str] = None
    capabilities: List[str] = None
    max_tokens: int = 2048
    estimated_cost_per_hour: float = 0.0

class ModalDeployer:
    """
    Service to automatically deploy HuggingFace models to Modal
    """
    
    def __init__(self):
        self.hf_api = HfApi()
        self.supported_architectures = {
            # Text/LLM models
            'llama': {'type': 'text', 'gpu': 'A100', 'memory': 32768, 'cost': 4.0},
            'mistral': {'type': 'text', 'gpu': 'A100', 'memory': 24576, 'cost': 4.0},
            'qwen': {'type': 'text', 'gpu': 'A100', 'memory': 24576, 'cost': 4.0},
            'gemma': {'type': 'text', 'gpu': 'A10G', 'memory': 16384, 'cost': 1.2},
            'phi': {'type': 'text', 'gpu': 'A10G', 'memory': 16384, 'cost': 1.2},
            'gpt': {'type': 'text', 'gpu': 'A100', 'memory': 32768, 'cost': 4.0},
            
            # Vision models
            'clip': {'type': 'vision', 'gpu': 'A10G', 'memory': 16384, 'cost': 1.2},
            'blip': {'type': 'vision', 'gpu': 'A10G', 'memory': 16384, 'cost': 1.2},
            'qwen2_vl': {'type': 'vision', 'gpu': 'A100', 'memory': 32768, 'cost': 4.0},
            'llava': {'type': 'vision', 'gpu': 'A100', 'memory': 24576, 'cost': 4.0},
            'fuyu': {'type': 'vision', 'gpu': 'A100', 'memory': 32768, 'cost': 4.0},
            
            # Audio models
            'whisper': {'type': 'audio', 'gpu': 'A10G', 'memory': 8192, 'cost': 1.2},
            'wav2vec2': {'type': 'audio', 'gpu': 'A10G', 'memory': 8192, 'cost': 1.2},
            'musicgen': {'type': 'audio', 'gpu': 'A100', 'memory': 16384, 'cost': 4.0},
            'bark': {'type': 'audio', 'gpu': 'A100', 'memory': 16384, 'cost': 4.0},
            
            # Image generation models
            'stable-diffusion': {'type': 'image', 'gpu': 'A100', 'memory': 16384, 'cost': 4.0},
            'flux': {'type': 'image', 'gpu': 'A100', 'memory': 24576, 'cost': 4.0},
            'dall-e': {'type': 'image', 'gpu': 'A100', 'memory': 16384, 'cost': 4.0},
            
            # Embedding models
            'sentence-transformers': {'type': 'embedding', 'gpu': 'A10G', 'memory': 8192, 'cost': 1.2},
            'e5': {'type': 'embedding', 'gpu': 'A10G', 'memory': 8192, 'cost': 1.2},
            'bge': {'type': 'embedding', 'gpu': 'A10G', 'memory': 8192, 'cost': 1.2},
        }
        
    def analyze_model(self, model_id: str) -> ModelConfig:
        """
        Analyze a HuggingFace model and determine deployment configuration
        
        Args:
            model_id: HuggingFace model ID (e.g., "microsoft/DialoGPT-medium")
            
        Returns:
            ModelConfig with deployment settings
        """
        try:
            # Get model information from HuggingFace
            info = model_info(model_id)
            
            # Extract model details
            architecture = self._detect_architecture(model_id, info)
            model_type = self._determine_model_type(model_id, info, architecture)
            parameters = self._estimate_parameters(info)
            
            # Get deployment requirements based on architecture
            requirements = self.supported_architectures.get(
                architecture.lower(), 
                {'type': 'text', 'gpu': 'A10G', 'memory': 16384, 'cost': 1.2}
            )
            
            # Generate capabilities based on model type and tags
            capabilities = self._generate_capabilities(model_type, info)
            
            # Generate dependencies based on model type
            dependencies = self._generate_dependencies(model_type, architecture, info)
            
            return ModelConfig(
                model_id=model_id,
                model_type=model_type,
                architecture=architecture,
                parameters=parameters,
                gpu_requirements=requirements['gpu'],
                memory_gb=requirements['memory'] // 1024,
                container_memory_mb=requirements['memory'],
                dependencies=dependencies,
                capabilities=capabilities,
                estimated_cost_per_hour=requirements['cost']
            )
            
        except Exception as e:
            logger.error(f"Error analyzing model {model_id}: {e}")
            raise
    
    def _detect_architecture(self, model_id: str, info) -> str:
        """Detect model architecture from model ID and metadata"""
        model_id_lower = model_id.lower()
        
        # Check for specific architectures in model ID
        for arch in self.supported_architectures.keys():
            if arch.replace('_', '-') in model_id_lower or arch.replace('-', '_') in model_id_lower:
                return arch
        
        # Check model tags and config
        if hasattr(info, 'tags'):
            for tag in info.tags:
                tag_lower = tag.lower()
                for arch in self.supported_architectures.keys():
                    if arch in tag_lower:
                        return arch
        
        # Check config architectures
        if hasattr(info, 'config') and info.config:
            config_str = str(info.config).lower()
            for arch in self.supported_architectures.keys():
                if arch in config_str:
                    return arch
        
        # Default fallback
        return 'transformers'
    
    def _determine_model_type(self, model_id: str, info, architecture: str) -> str:
        """Determine the primary model type"""
        model_id_lower = model_id.lower()
        
        # Check for specific model types in ID
        if any(x in model_id_lower for x in ['vision', 'clip', 'blip', 'llava', 'qwen2-vl', 'fuyu']):
            return 'vision'
        elif any(x in model_id_lower for x in ['whisper', 'wav2vec', 'audio', 'speech', 'tts', 'stt']):
            return 'audio'
        elif any(x in model_id_lower for x in ['stable-diffusion', 'sd-', 'flux', 'dall-e', 'imagen']):
            return 'image'
        elif any(x in model_id_lower for x in ['embed', 'sentence-transformer', 'e5-', 'bge-']):
            return 'embedding'
        
        # Check tags
        if hasattr(info, 'tags'):
            for tag in info.tags:
                tag_lower = tag.lower()
                if tag_lower in ['computer-vision', 'image-classification', 'object-detection']:
                    return 'vision'
                elif tag_lower in ['automatic-speech-recognition', 'text-to-speech', 'audio']:
                    return 'audio'
                elif tag_lower in ['text-to-image', 'image-generation']:
                    return 'image'
                elif tag_lower in ['sentence-similarity', 'feature-extraction']:
                    return 'embedding'
        
        # Use architecture mapping
        if architecture in self.supported_architectures:
            return self.supported_architectures[architecture]['type']
        
        return 'text'  # Default
    
    def _estimate_parameters(self, info) -> str:
        """Estimate model parameters from model info"""
        if hasattr(info, 'config') and info.config:
            config = info.config
            if isinstance(config, dict):
                # Try different parameter estimation methods
                if 'num_parameters' in config:
                    params = config['num_parameters']
                elif 'd_model' in config and 'n_layer' in config:
                    # Transformer estimation
                    d_model = config.get('d_model', 768)
                    n_layer = config.get('n_layer', 12)
                    vocab_size = config.get('vocab_size', 50000)
                    params = (d_model * d_model * 4 * n_layer) + (vocab_size * d_model)
                else:
                    return 'Unknown'
                
                # Format parameters
                if params > 1e9:
                    return f"{params/1e9:.1f}B"
                elif params > 1e6:
                    return f"{params/1e6:.0f}M"
                else:
                    return f"{params/1e3:.0f}K"
        
        return 'Unknown'
    
    def _generate_capabilities(self, model_type: str, info) -> List[str]:
        """Generate capabilities list based on model type"""
        base_capabilities = {
            'text': ['text_generation', 'chat', 'completion'],
            'vision': ['image_analysis', 'image_understanding', 'visual_question_answering'],
            'audio': ['speech_recognition', 'audio_processing'],
            'image': ['image_generation', 'text_to_image'],
            'embedding': ['text_embedding', 'similarity_search', 'semantic_search']
        }
        
        capabilities = base_capabilities.get(model_type, ['general_ai'])
        
        # Add specific capabilities based on tags
        if hasattr(info, 'tags'):
            for tag in info.tags:
                if tag == 'conversational':
                    capabilities.append('chat')
                elif tag == 'question-answering':
                    capabilities.append('question_answering')
                elif tag == 'summarization':
                    capabilities.append('text_summarization')
                elif tag == 'translation':
                    capabilities.append('translation')
        
        return list(set(capabilities))
    
    def _generate_dependencies(self, model_type: str, architecture: str, info) -> List[str]:
        """Generate Python dependencies based on model type and architecture"""
        base_deps = [
            "torch>=2.0.0",
            "transformers>=4.35.0",
            "accelerate>=0.24.0",
            "numpy>=1.24.0",
            "requests>=2.31.0",
            "httpx>=0.26.0",
            "pydantic>=2.0.0",
        ]
        
        type_deps = {
            'vision': [
                "Pillow>=10.0.0",
                "opencv-python>=4.8.0",
                "torchvision>=0.15.0",
            ],
            'audio': [
                "librosa>=0.10.0",
                "soundfile>=0.12.0",
                "torchaudio>=2.0.0",
            ],
            'image': [
                "diffusers>=0.21.0",
                "Pillow>=10.0.0",
                "controlnet-aux>=0.3.0",
            ],
            'embedding': [
                "sentence-transformers>=2.2.0",
                "faiss-cpu>=1.7.0",
            ]
        }
        
        arch_deps = {
            'whisper': ["openai-whisper>=20231117"],
            'stable-diffusion': ["diffusers>=0.21.0", "controlnet-aux>=0.3.0"],
            'qwen2_vl': ["qwen-vl-utils", "av", "decord"],
            'llava': ["llava>=1.1.0"],
        }
        
        deps = base_deps.copy()
        deps.extend(type_deps.get(model_type, []))
        deps.extend(arch_deps.get(architecture, []))
        
        return list(set(deps))
    
    def generate_modal_service(self, config: ModelConfig) -> str:
        """
        Generate Modal deployment code for a HuggingFace model
        
        Args:
            config: Model configuration
            
        Returns:
            Generated Python code for Modal deployment
        """
        service_name = config.model_id.replace('/', '_').replace('-', '_').lower()
        
        template = f'''"""
{config.model_id} Modal Service

Automatically generated deployment for {config.model_id}
- Model Type: {config.model_type}
- Architecture: {config.architecture}
- Parameters: {config.parameters}
- Capabilities: {', '.join(config.capabilities)}
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
app = modal.App("isa-{service_name}")

# Define Modal container image
image = (
    modal.Image.debian_slim(python_version="{config.python_version}")
    .pip_install([
{self._format_dependencies(config.dependencies)}
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
    .env({{
        "TRANSFORMERS_CACHE": "/models",
        "TORCH_HOME": "/models/torch",
        "HF_HOME": "/models",
        "CUDA_VISIBLE_DEVICES": "0",
        "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:512"
    }})
)

# Model Service
@app.cls(
    gpu="{config.gpu_requirements}",
    image=image,
    memory={config.container_memory_mb},
    timeout=1800,
    scaledown_window=300,
    min_containers=0,
    max_containers=5,
)
class {service_name.title().replace('_', '')}Service:
    """
    {config.model_id} Service
    
    Model: {config.model_id}
    Architecture: {config.architecture}
    Parameters: {config.parameters}
    Capabilities: {', '.join(config.capabilities)}
    """
        
    @modal.enter()
    def load_model(self):
        """Load {config.model_id} model and dependencies"""
        print("Loading {config.model_id}...")
        start_time = time.time()
        
        self.model = None
        self.tokenizer = None
        self.processor = None
        self.logger = logging.getLogger(__name__)
        self.request_count = 0
        self.total_processing_time = 0.0
        
        try:
            import torch
            from transformers import AutoModel, AutoTokenizer, AutoProcessor
            
            model_name = "{config.model_id}"
            
            print(f"Loading model: {{model_name}}")
            
            # Load tokenizer/processor
            try:
                self.processor = AutoProcessor.from_pretrained(model_name)
                print("✅ Processor loaded")
            except:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                print("✅ Tokenizer loaded")
            
            # Load model with optimizations
            self.model = AutoModel.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
                use_cache=True
            )
            
            self.model.eval()
            
            # Try to compile model for faster inference
            try:
                self.model = torch.compile(self.model, mode="reduce-overhead")
                print("✅ Model compiled for faster inference")
            except Exception as e:
                print(f"⚠️ Model compilation failed: {{e}}")
                
            load_time = time.time() - start_time
            print(f"{config.model_id} loaded successfully in {{load_time:.2f}}s")
            
            self.models_loaded = True
            
        except Exception as e:
            print(f"Model loading failed: {{e}}")
            import traceback
            traceback.print_exc()
            self.models_loaded = False

{self._generate_inference_methods(config)}

    @modal.method()
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {{
            'status': 'healthy',
            'service': 'isa-{service_name}',
            'provider': 'ISA',
            'models_loaded': self.models_loaded,
            'model': '{config.model_id}',
            'architecture': '{config.architecture}',
            'timestamp': time.time(),
            'gpu': '{config.gpu_requirements}',
            'memory_usage': '{config.memory_gb}GB',
            'request_count': self.request_count,
            'capabilities': {config.capabilities}
        }}

# Deployment functions
@app.function()
def deploy_info():
    """Deployment information"""
    return {{
        'service': 'isa-{service_name}',
        'version': '1.0.0',
        'description': 'ISA {config.model_id} service',
        'model': '{config.model_id}',
        'architecture': '{config.architecture}',
        'gpu': '{config.gpu_requirements}',
        'capabilities': {config.capabilities},
        'deployment_time': time.time()
    }}

if __name__ == "__main__":
    print("ISA {config.model_id} Service - Modal Deployment")
    print("Deploy with: modal deploy {service_name}_service.py")
    print()
    print("Model: {config.model_id}")
    print("Architecture: {config.architecture}")
    print("Parameters: {config.parameters}")
    print("GPU: {config.gpu_requirements}")
    print("Capabilities: {', '.join(config.capabilities)}")
'''
        
        return template
    
    def _format_dependencies(self, dependencies: List[str]) -> str:
        """Format dependencies for template"""
        formatted = []
        for dep in dependencies:
            formatted.append(f'        "{dep}",')
        return '\n'.join(formatted)
    
    def _generate_inference_methods(self, config: ModelConfig) -> str:
        """Generate inference methods based on model type"""
        methods = {
            'text': self._text_generation_method,
            'vision': self._vision_analysis_method,
            'audio': self._audio_processing_method,
            'image': self._image_generation_method,
            'embedding': self._embedding_method
        }
        
        return methods.get(config.model_type, self._generic_inference_method)(config)
    
    def _text_generation_method(self, config: ModelConfig) -> str:
        return '''
    @modal.method()
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Dict[str, Any]:
        """Generate text using the model"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            if not self.models_loaded or not self.model:
                raise RuntimeError("Model not loaded")
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                padding=True, 
                truncation=True
            ).to("cuda")
            
            # Generate response
            import torch
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:], 
                skip_special_tokens=True
            )
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'text': response,
                'processing_time': processing_time,
                'model': self.model.config.name_or_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }'''
    
    def _vision_analysis_method(self, config: ModelConfig) -> str:
        return '''
    @modal.method()
    def analyze_image(
        self,
        image_b64: str,
        prompt: str = "Describe this image.",
        max_tokens: int = 512
    ) -> Dict[str, Any]:
        """Analyze image using the model"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            if not self.models_loaded or not self.model:
                raise RuntimeError("Model not loaded")
            
            # Decode image
            image_data = base64.b64decode(image_b64)
            
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                tmp_file.write(image_data)
                tmp_file.flush()
                
                from PIL import Image
                image = Image.open(tmp_file.name)
                
                # Process inputs
                if self.processor:
                    inputs = self.processor(text=prompt, images=image, return_tensors="pt")
                else:
                    # Fallback for models without processor
                    inputs = self.tokenizer(prompt, return_tensors="pt")
                
                inputs = inputs.to("cuda")
                
                # Generate response
                import torch
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        do_sample=True
                    )
                
                # Decode response
                if self.processor:
                    response = self.processor.decode(outputs[0], skip_special_tokens=True)
                else:
                    response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                os.unlink(tmp_file.name)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'text': response,
                'processing_time': processing_time,
                'model': self.model.config.name_or_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }'''
    
    def _audio_processing_method(self, config: ModelConfig) -> str:
        return '''
    @modal.method()
    def process_audio(
        self,
        audio_b64: str,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """Process audio using the model"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            if not self.models_loaded or not self.model:
                raise RuntimeError("Model not loaded")
            
            # Decode audio
            audio_data = base64.b64decode(audio_b64)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file.flush()
                
                # Process audio
                if self.processor:
                    inputs = self.processor(tmp_file.name, return_tensors="pt")
                else:
                    import librosa
                    audio, sr = librosa.load(tmp_file.name)
                    inputs = self.tokenizer(audio, return_tensors="pt")
                
                inputs = inputs.to("cuda")
                
                # Generate response
                import torch
                with torch.no_grad():
                    outputs = self.model.generate(**inputs)
                
                # Decode response
                if self.processor:
                    response = self.processor.decode(outputs[0], skip_special_tokens=True)
                else:
                    response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                os.unlink(tmp_file.name)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'text': response,
                'processing_time': processing_time,
                'model': self.model.config.name_or_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }'''
    
    def _image_generation_method(self, config: ModelConfig) -> str:
        return '''
    @modal.method()
    def generate_image(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 20
    ) -> Dict[str, Any]:
        """Generate image using the model"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            if not self.models_loaded or not self.model:
                raise RuntimeError("Model not loaded")
            
            # Generate image
            image = self.model(
                prompt=prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps
            ).images[0]
            
            # Convert to base64
            import io
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'image': image_b64,
                'processing_time': processing_time,
                'model': self.model.config.name_or_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }'''
    
    def _embedding_method(self, config: ModelConfig) -> str:
        return '''
    @modal.method()
    def embed_text(
        self,
        text: Union[str, List[str]]
    ) -> Dict[str, Any]:
        """Generate embeddings for text"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            if not self.models_loaded or not self.model:
                raise RuntimeError("Model not loaded")
            
            # Generate embeddings
            if hasattr(self.model, 'encode'):
                embeddings = self.model.encode(text)
            else:
                inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
                inputs = inputs.to("cuda")
                
                import torch
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'embeddings': embeddings.tolist(),
                'processing_time': processing_time,
                'model': self.model.config.name_or_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }'''
    
    def _generic_inference_method(self, config: ModelConfig) -> str:
        return '''
    @modal.method()
    def inference(
        self,
        input_data: str,
        task: str = "generate",
        **kwargs
    ) -> Dict[str, Any]:
        """Generic inference method"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            if not self.models_loaded or not self.model:
                raise RuntimeError("Model not loaded")
            
            # Process input
            if self.processor:
                inputs = self.processor(input_data, return_tensors="pt")
            else:
                inputs = self.tokenizer(input_data, return_tensors="pt")
            
            inputs = inputs.to("cuda")
            
            # Generate response
            import torch
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **kwargs)
            
            # Decode response
            if self.processor:
                response = self.processor.decode(outputs[0], skip_special_tokens=True)
            else:
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'output': response,
                'processing_time': processing_time,
                'model': self.model.config.name_or_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }'''
    
    def deploy_model(self, model_id: str, deploy: bool = False) -> Dict[str, Any]:
        """
        Analyze and optionally deploy a HuggingFace model to Modal
        
        Args:
            model_id: HuggingFace model ID
            deploy: Whether to actually deploy to Modal
            
        Returns:
            Deployment result with service code
        """
        try:
            # Analyze model
            config = self.analyze_model(model_id)
            
            # Generate Modal service code
            service_code = self.generate_modal_service(config)
            
            # Save service code to file
            service_name = model_id.replace('/', '_').replace('-', '_').lower()
            output_dir = Path("/Users/xenodennis/Documents/Fun/isA_Model/isa_model/deployment/cloud/modal")
            output_file = output_dir / f"auto_{service_name}_service.py"
            
            with open(output_file, 'w') as f:
                f.write(service_code)
            
            result = {
                'success': True,
                'model_id': model_id,
                'config': config.__dict__,
                'service_file': str(output_file),
                'service_code': service_code,
                'estimated_cost_per_hour': config.estimated_cost_per_hour,
                'deployment_command': f"modal deploy {output_file}",
                'deployed': False
            }
            
            # Optional: Actually deploy to Modal
            if deploy:
                try:
                    import subprocess
                    deployment_result = subprocess.run(
                        ['modal', 'deploy', str(output_file)],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if deployment_result.returncode == 0:
                        result['deployed'] = True
                        result['deployment_output'] = deployment_result.stdout
                    else:
                        result['deployment_error'] = deployment_result.stderr
                        
                except Exception as e:
                    result['deployment_error'] = str(e)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model_id': model_id
            }

# Example usage
if __name__ == "__main__":
    deployer = HuggingFaceModalDeployer()
    
    # Example: Deploy a text model
    result = deployer.deploy_model("microsoft/DialoGPT-medium")
    print(json.dumps(result, indent=2, default=str))