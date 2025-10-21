#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ISA LLM Service - Modal deployment for HuggingFace trained models
Provides inference API for custom trained models
"""

import os
import logging
from typing import Dict, Any, List, Optional
import modal

# Modal app configuration
app = modal.App("isa-llm-inference")

# GPU configuration for inference
GPU_CONFIG = modal.gpu.A10G()

# Base image with HuggingFace transformers
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        "torch>=2.0.0",
        "transformers>=4.35.0", 
        "accelerate>=0.20.0",
        "huggingface_hub>=0.17.0",
        "peft>=0.5.0",  # For LoRA models
        "bitsandbytes>=0.41.0",  # For quantization
        "sentencepiece>=0.1.99",  # For tokenizers
    ])
)

logger = logging.getLogger(__name__)

@app.cls(
    image=image,
    gpu=GPU_CONFIG,
    cpu=2.0,
    memory=16384,  # 16GB memory
    timeout=300,   # 5 minute timeout
    container_idle_timeout=60,  # Keep warm for 1 minute
    allow_concurrent_inputs=5,  # Allow concurrent requests
)
class ISALLMService:
    """
    ISA LLM Service for inference on HuggingFace trained models
    Designed to work with models trained through ISA training pipeline
    """
    
    def __init__(self):
        """Initialize the service (runs on container startup)"""
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        # Model will be loaded when first requested
        self.model = None
        self.tokenizer = None
        self.current_model_id = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"ISA LLM Service initialized on {self.device}")
    
    def _load_model(self, model_id: str, hf_token: str = None):
        """Load a specific model"""
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        if self.current_model_id == model_id and self.model is not None:
            logger.info(f"Model {model_id} already loaded")
            return
        
        logger.info(f"Loading model: {model_id}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                token=hf_token,
                trust_remote_code=True
            )
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with GPU optimization
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                token=hf_token,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            self.current_model_id = model_id
            logger.info(f"Successfully loaded model {model_id}")
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            raise
    
    @modal.method
    def generate_text(
        self,
        prompt: str,
        model_id: str,
        hf_token: str = None,
        max_length: int = 100,
        temperature: float = 0.7,
        do_sample: bool = True,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using the specified model
        
        Args:
            prompt: Input text prompt
            model_id: HuggingFace model ID (e.g., "xenobordom/dialogpt-isa-trained-xxx")
            hf_token: HuggingFace token for private models
            max_length: Maximum generation length
            temperature: Sampling temperature
            do_sample: Whether to use sampling
            top_p: Top-p sampling parameter
            repetition_penalty: Repetition penalty
            **kwargs: Additional generation parameters
            
        Returns:
            Dictionary containing generated text and metadata
        """
        import torch
        import time
        
        start_time = time.time()
        
        try:
            # Load model if needed
            self._load_model(model_id, hf_token)
            
            if self.model is None or self.tokenizer is None:
                raise RuntimeError("Model not properly loaded")
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=inputs["input_ids"].shape[1] + max_length,
                    temperature=temperature,
                    do_sample=do_sample,
                    top_p=top_p,
                    repetition_penalty=repetition_penalty,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    **kwargs
                )
            
            # Decode generated text
            full_text = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            
            # Extract only the new generated part
            generated_text = full_text
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "text": generated_text,
                "full_text": full_text,
                "prompt": prompt,
                "model_id": model_id,
                "provider": "ISA",
                "service": "isa-llm",
                "generation_config": {
                    "max_length": max_length,
                    "temperature": temperature,
                    "do_sample": do_sample,
                    "top_p": top_p,
                    "repetition_penalty": repetition_penalty
                },
                "metadata": {
                    "processing_time": processing_time,
                    "device": str(self.device),
                    "input_tokens": inputs["input_ids"].shape[1],
                    "output_tokens": outputs.shape[1]
                }
            }
            
        except Exception as e:
            logger.error(f"Error during text generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt,
                "model_id": model_id,
                "provider": "ISA",
                "service": "isa-llm"
            }
    
    @modal.method
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        hf_token: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat completion with conversation history
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model_id: HuggingFace model ID
            hf_token: HuggingFace token
            **kwargs: Additional generation parameters
            
        Returns:
            Dictionary containing generated response and metadata
        """
        try:
            # Convert messages to a single prompt
            conversation = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    conversation += f"User: {content}\n"
                elif role == "assistant":
                    conversation += f"Assistant: {content}\n"
                elif role == "system":
                    conversation += f"System: {content}\n"
            
            conversation += "Assistant: "
            
            # Generate response
            result = self.generate_text(
                prompt=conversation,
                model_id=model_id,
                hf_token=hf_token,
                **kwargs
            )
            
            # Format as chat response
            if result.get("success"):
                result["role"] = "assistant"
                result["conversation"] = conversation
                result["messages"] = messages
            
            return result
            
        except Exception as e:
            logger.error(f"Error during chat completion: {e}")
            return {
                "success": False,
                "error": str(e),
                "messages": messages,
                "model_id": model_id,
                "provider": "ISA",
                "service": "isa-llm"
            }
    
    @modal.method
    def get_model_info(self, model_id: str, hf_token: str = None) -> Dict[str, Any]:
        """Get information about the loaded model"""
        try:
            # Load model if needed
            self._load_model(model_id, hf_token)
            
            if self.model is None:
                return {
                    "success": False,
                    "error": "Model not loaded"
                }
            
            # Get model config
            config = self.model.config
            
            # Count parameters
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            
            return {
                "success": True,
                "model_id": model_id,
                "provider": "ISA",
                "service": "isa-llm",
                "architecture": config.model_type if hasattr(config, 'model_type') else "unknown",
                "vocab_size": config.vocab_size if hasattr(config, 'vocab_size') else None,
                "hidden_size": config.hidden_size if hasattr(config, 'hidden_size') else None,
                "num_layers": getattr(config, 'num_layers', getattr(config, 'n_layer', None)),
                "num_attention_heads": getattr(config, 'num_attention_heads', getattr(config, 'n_head', None)),
                "total_parameters": total_params,
                "trainable_parameters": trainable_params,
                "device": str(self.device),
                "dtype": str(next(self.model.parameters()).dtype)
            }
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @modal.method
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        import torch
        
        try:
            gpu_available = torch.cuda.is_available()
            gpu_count = torch.cuda.device_count() if gpu_available else 0
            
            return {
                "success": True,
                "status": "healthy",
                "service": "isa-llm",
                "provider": "ISA",
                "device": str(self.device),
                "gpu_available": gpu_available,
                "gpu_count": gpu_count,
                "current_model": self.current_model_id,
                "memory_info": {
                    "allocated": torch.cuda.memory_allocated() if gpu_available else 0,
                    "cached": torch.cuda.memory_reserved() if gpu_available else 0
                } if gpu_available else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "error": str(e)
            }

# Deployment functions
@app.function(
    image=image,
    schedule=modal.Cron("0 2 * * *"),  # Deploy daily at 2 AM
    timeout=300
)
def deploy_service():
    """Deploy the ISA LLM service"""
    print("ISA LLM Service deployed successfully!")
    return {"status": "deployed", "service": "isa-llm"}

# Local testing function
@app.local_entrypoint()
def test_service():
    """Test the ISA LLM service locally"""
    
    # Test with our trained model
    test_model_id = "xenobordom/dialogpt-isa-trained-1755493402"
    test_prompt = "你好"
    
    # Get HF token from environment
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("❌ HF_TOKEN not found in environment")
        return
    
    print(f"🧪 Testing ISA LLM Service with model: {test_model_id}")
    
    # Create service instance
    service = ISALLMService()
    
    # Test health check
    print("📋 Testing health check...")
    health = service.health_check.remote()
    print(f"Health: {health}")
    
    # Test model info
    print("📊 Testing model info...")
    info = service.get_model_info.remote(test_model_id, hf_token)
    print(f"Model info: {info}")
    
    # Test text generation
    print("🤖 Testing text generation...")
    result = service.generate_text.remote(
        prompt=test_prompt,
        model_id=test_model_id,
        hf_token=hf_token,
        max_length=30,
        temperature=0.7
    )
    print(f"Generation result: {result}")
    
    # Test chat completion
    print("💬 Testing chat completion...")
    messages = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！很高兴见到你。"},
        {"role": "user", "content": "你能帮我做什么？"}
    ]
    chat_result = service.chat_completion.remote(
        messages=messages,
        model_id=test_model_id,
        hf_token=hf_token,
        max_length=30
    )
    print(f"Chat result: {chat_result}")
    
    print("✅ ISA LLM Service test completed!")

if __name__ == "__main__":
    # For local development
    test_service()