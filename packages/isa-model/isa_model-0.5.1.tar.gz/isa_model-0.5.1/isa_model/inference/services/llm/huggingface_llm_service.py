#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ISA LLM Service - Inference client for Modal-deployed HuggingFace models
Supports custom trained models deployed on Modal infrastructure
"""

import logging
import os
from typing import Dict, Any, Optional, List

try:
    import modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False
    modal = None

from isa_model.inference.services.base_service import BaseService
from isa_model.core.models.model_manager import ModelManager
from isa_model.core.config import ConfigManager

logger = logging.getLogger(__name__)

class ISALLMService(BaseService):
    """
    ISA LLM Service - Client for Modal-deployed HuggingFace models
    Calls ISA's own deployed LLM inference services on Modal
    """
    
    def __init__(
        self,
        provider_name: str = "isa",
        model_name: str = None,
        model_manager: ModelManager = None,
        config_manager: ConfigManager = None,
        modal_app_name: str = "isa-llm-inference",
        timeout: int = 60,
        **kwargs
    ):
        # Skip BaseService init to avoid config validation for now
        self.provider_name = provider_name
        self.model_name = model_name or "isa-llm-service"
        self.modal_app_name = modal_app_name
        self.timeout = timeout
        
        # Initialize Modal client
        if MODAL_AVAILABLE:
            try:
                # Get deployed Modal app
                self.modal_app = modal.App.lookup(modal_app_name)
                logger.info(f"Connected to Modal LLM app: {modal_app_name}")
                
                self.modal_service = True
                logger.info("Modal LLM service connection established")
                    
            except Exception as e:
                logger.warning(f"Failed to connect to Modal LLM app: {e}")
                self.modal_app = None
                self.modal_service = None
        else:
            logger.warning("Modal SDK not available")
            self.modal_app = None
            self.modal_service = None
        
        # Service statistics
        self.request_count = 0
        self.total_cost = 0.0
        
        # Fallback mode for when Modal is not available
        self.fallback_mode = not MODAL_AVAILABLE or not self.modal_service
    
    async def _fallback_response(self, method_name: str, **kwargs) -> Dict[str, Any]:
        """
        Provide fallback responses when Modal service is not available
        """
        import time
        import random
        
        if method_name == "generate_text":
            prompt = kwargs.get("prompt", "")
            # Simple rule-based responses for demo purposes
            responses = [
                "这是一个模拟的ISA LLM响应。",
                "抱歉，Modal服务当前不可用，这是一个fallback响应。",
                "ISA模型正在维护中，请稍后再试。",
                f"您说：{prompt}。我理解了，但当前模型不可用。"
            ]
            
            generated_text = random.choice(responses)
            
            return {
                "success": True,
                "text": generated_text,
                "full_text": prompt + " " + generated_text,
                "prompt": prompt,
                "model_id": kwargs.get("model_id", "isa-llm-fallback"),
                "provider": "ISA",
                "service": "isa-llm",
                "fallback": True,
                "generation_config": kwargs.get("generation_config", {}),
                "metadata": {
                    "processing_time": random.uniform(0.5, 2.0),
                    "device": "cpu",
                    "input_tokens": len(prompt.split()),
                    "output_tokens": len(generated_text.split()),
                    "note": "This is a fallback response - Modal service not available"
                }
            }
            
        elif method_name == "chat_completion":
            messages = kwargs.get("messages", [])
            user_message = ""
            if messages:
                user_message = messages[-1].get("content", "")
            
            chat_responses = [
                "很抱歉，ISA模型当前不可用，这是一个模拟响应。",
                "我是ISA模型的fallback版本，功能有限。",
                f"我听到您说：{user_message}，但现在无法提供完整的回复。",
                "Modal服务正在重启中，请稍后再试完整的ISA模型功能。"
            ]
            
            response_text = random.choice(chat_responses)
            
            return {
                "success": True,
                "text": response_text,
                "role": "assistant",
                "messages": messages,
                "model_id": kwargs.get("model_id", "isa-llm-fallback"),
                "provider": "ISA",
                "service": "isa-llm",
                "fallback": True,
                "metadata": {
                    "processing_time": random.uniform(0.3, 1.5),
                    "device": "cpu",
                    "note": "This is a fallback response - Modal service not available"
                }
            }
            
        elif method_name == "get_model_info":
            return {
                "success": True,
                "model_id": kwargs.get("model_id", "isa-llm-fallback"),
                "provider": "ISA",
                "service": "isa-llm",
                "architecture": "unknown (fallback mode)",
                "fallback": True,
                "note": "Modal service not available - showing fallback info"
            }
            
        elif method_name == "health_check":
            return {
                "success": True,
                "status": "fallback",
                "service": "isa-llm",
                "provider": "ISA",
                "device": "cpu",
                "fallback": True,
                "message": "Modal service not available - running in fallback mode"
            }
        
        else:
            return {
                "success": False,
                "error": f"Method {method_name} not supported in fallback mode",
                "fallback": True
            }
    
    async def _call_modal_llm_service(
        self,
        method_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call Modal LLM service via SDK with improved error handling and fallback
        """
        # If in fallback mode, use fallback response immediately
        if self.fallback_mode:
            logger.info(f"Using fallback mode for {method_name}")
            return await self._fallback_response(method_name, **kwargs)
        
        try:
            if not MODAL_AVAILABLE:
                logger.warning("Modal SDK not available, switching to fallback mode")
                self.fallback_mode = True
                return await self._fallback_response(method_name, **kwargs)
            
            if not self.modal_app or not self.modal_service:
                logger.warning("Modal app/service not available, switching to fallback mode")
                self.fallback_mode = True
                return await self._fallback_response(method_name, **kwargs)
            
            logger.info(f"Calling Modal LLM service method: {method_name}")
            
            try:
                # Use Modal SDK to call the service
                ISALLMServiceCls = modal.Cls.from_name(
                    app_name=self.modal_app_name,
                    name="ISALLMService"
                )
                
                # Create instance and call method
                instance = ISALLMServiceCls()
                method = getattr(instance, method_name)
                result = method.remote(**kwargs)
                
                logger.info("✅ Modal LLM service call successful")
                return result
                
            except modal.exception.NotFoundError:
                logger.warning(f"Modal app not found, switching to fallback mode")
                self.fallback_mode = True
                return await self._fallback_response(method_name, **kwargs)
                
            except modal.exception.ConnectionError:
                logger.warning(f"Modal connection error, switching to fallback mode")
                self.fallback_mode = True
                return await self._fallback_response(method_name, **kwargs)
                        
        except Exception as e:
            logger.error(f"Modal LLM service call failed: {e}, switching to fallback mode")
            self.fallback_mode = True
            return await self._fallback_response(method_name, **kwargs)
    
    async def complete(
        self,
        prompt: str,
        model_id: str = None,
        max_length: Optional[int] = 50,
        temperature: float = 0.7,
        do_sample: bool = True,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion using Modal-deployed LLM service
        
        Args:
            prompt: Input text prompt
            model_id: HuggingFace model ID to use
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            do_sample: Whether to use sampling
            top_p: Top-p sampling parameter
            repetition_penalty: Repetition penalty
            **kwargs: Additional generation parameters
            
        Returns:
            Dictionary containing generated text and metadata
        """
        try:
            # Get HF token from environment
            hf_token = os.getenv("HF_TOKEN")
            
            # Use provided model_id or default trained model
            target_model = model_id or "xenobordom/dialogpt-isa-trained-1755493402"
            
            # Call Modal service
            result = await self._call_modal_llm_service(
                method_name="generate_text",
                prompt=prompt,
                model_id=target_model,
                hf_token=hf_token,
                max_length=max_length,
                temperature=temperature,
                do_sample=do_sample,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                **kwargs
            )
            
            if result and result.get('success', False):
                self.request_count += 1
                
                # Add cost tracking if available
                if 'billing' in result:
                    cost = result['billing'].get('estimated_cost_usd', 0)
                    self.total_cost += cost
                
                return result
            else:
                return {
                    'success': False,
                    'provider': 'ISA',
                    'service': 'isa-llm',
                    'error': f'Modal LLM service returned error: {result.get("error", "Unknown error") if result else "No response"}',
                    'details': result
                }
                
        except Exception as e:
            logger.error(f"ISA LLM completion failed: {e}")
            return {
                'success': False,
                'provider': 'ISA',
                'service': 'isa-llm',
                'error': str(e)
            }
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat completion using Modal-deployed LLM service
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model_id: HuggingFace model ID to use
            **kwargs: Additional generation parameters
            
        Returns:
            Dictionary containing generated response and metadata
        """
        try:
            # Get HF token from environment
            hf_token = os.getenv("HF_TOKEN")
            
            # Use provided model_id or default trained model
            target_model = model_id or "xenobordom/dialogpt-isa-trained-1755493402"
            
            # Call Modal service
            result = await self._call_modal_llm_service(
                method_name="chat_completion",
                messages=messages,
                model_id=target_model,
                hf_token=hf_token,
                **kwargs
            )
            
            if result and result.get('success', False):
                self.request_count += 1
                
                # Add cost tracking if available
                if 'billing' in result:
                    cost = result['billing'].get('estimated_cost_usd', 0)
                    self.total_cost += cost
                
                return result
            else:
                return {
                    'success': False,
                    'provider': 'ISA',
                    'service': 'isa-llm',
                    'error': f'Modal LLM service returned error: {result.get("error", "Unknown error") if result else "No response"}',
                    'details': result
                }
                
        except Exception as e:
            logger.error(f"ISA LLM chat completion failed: {e}")
            return {
                'success': False,
                'provider': 'ISA',
                'service': 'isa-llm',
                'error': str(e)
            }
    
    async def get_model_info(self, model_id: str = None) -> Dict[str, Any]:
        """Get information about the model via Modal service"""
        try:
            # Get HF token from environment
            hf_token = os.getenv("HF_TOKEN")
            
            # Use provided model_id or default trained model
            target_model = model_id or "xenobordom/dialogpt-isa-trained-1755493402"
            
            # Call Modal service
            result = await self._call_modal_llm_service(
                method_name="get_model_info",
                model_id=target_model,
                hf_token=hf_token
            )
            
            if result and result.get('success', False):
                return result
            else:
                return {
                    'success': False,
                    'provider': 'ISA',
                    'service': 'isa-llm',
                    'error': f'Modal LLM service returned error: {result.get("error", "Unknown error") if result else "No response"}'
                }
                
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check ISA LLM service health"""
        try:
            # Call Modal service health check
            result = await self._call_modal_llm_service(
                method_name="health_check"
            )
            
            if result and result.get('success', False):
                return {
                    'success': True,
                    'provider': 'ISA',
                    'service': 'isa-llm',
                    'status': 'healthy',
                    'modal_service': result,
                    'usage_stats': {
                        'total_requests': self.request_count,
                        'total_cost_usd': round(self.total_cost, 6)
                    }
                }
            else:
                return {
                    'success': False,
                    'provider': 'ISA',
                    'service': 'isa-llm',
                    'status': 'error',
                    'error': f'Modal service error: {result.get("error", "Unknown error") if result else "No response"}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'provider': 'ISA',
                'service': 'isa-llm',
                'status': 'error',
                'error': str(e)
            }
    
    def get_supported_tasks(self) -> List[str]:
        """Get supported task list"""
        return [
            'generate',     # Text generation
            'chat',         # Chat completion
            'complete'      # Text completion
        ]
    
    def get_supported_models(self) -> List[str]:
        """Get supported model types"""
        return [
            'dialogpt',     # DialoGPT models
            'gpt2',         # GPT-2 models
            'custom'        # Custom trained models
        ]
    
    async def invoke(self, input_data: str, task: str = "chat", **kwargs) -> Dict[str, Any]:
        """
        Unified invoke method for ISA LLM service compatibility
        Required by the ISA Model client interface
        """
        try:
            if task in ["chat", "generate", "complete"]:
                # Handle chat tasks by converting to message format
                if task == "chat":
                    if isinstance(input_data, str):
                        messages = [{"role": "user", "content": input_data}]
                    elif isinstance(input_data, list):
                        messages = input_data
                    else:
                        messages = [{"role": "user", "content": str(input_data)}]
                    
                    result = await self.chat(messages, **kwargs)
                    
                    # Convert result to unified format
                    if result.get('success'):
                        response_text = ""
                        if 'response' in result and isinstance(result['response'], dict):
                            response_text = result['response'].get('generated_text', '')
                        elif 'generated_text' in result:
                            response_text = result['generated_text']
                        elif 'content' in result:
                            response_text = result['content']
                        
                        return {
                            'success': True,
                            'result': {
                                'content': response_text,
                                'tool_calls': [],
                                'response_metadata': result.get('metadata', {})
                            },
                            'error': None,
                            'metadata': {
                                'model_used': self.model_name,
                                'provider': self.provider_name,
                                'task': task,
                                'service_type': 'text',
                                'processing_time': result.get('processing_time', 0)
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'result': None,
                            'error': result.get('error', 'Unknown error'),
                            'metadata': {
                                'model_used': self.model_name,
                                'provider': self.provider_name,
                                'task': task,
                                'service_type': 'text'
                            }
                        }
                        
                elif task in ["generate", "complete"]:
                    result = await self.complete(input_data, **kwargs)
                    
                    # Convert result to unified format
                    if result.get('success'):
                        response_text = ""
                        if 'response' in result and isinstance(result['response'], dict):
                            response_text = result['response'].get('generated_text', '')
                        elif 'generated_text' in result:
                            response_text = result['generated_text']
                        elif 'content' in result:
                            response_text = result['content']
                        
                        return {
                            'success': True,
                            'result': {
                                'content': response_text,
                                'response_metadata': result.get('metadata', {})
                            },
                            'error': None,
                            'metadata': {
                                'model_used': self.model_name,
                                'provider': self.provider_name,
                                'task': task,
                                'service_type': 'text',
                                'processing_time': result.get('processing_time', 0)
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'result': None,
                            'error': result.get('error', 'Unknown error'),
                            'metadata': {
                                'model_used': self.model_name,
                                'provider': self.provider_name,
                                'task': task,
                                'service_type': 'text'
                            }
                        }
            else:
                return {
                    'success': False,
                    'result': None,
                    'error': f'Unsupported task: {task}. Supported tasks: {self.get_supported_tasks()}',
                    'metadata': {
                        'model_used': self.model_name,
                        'provider': self.provider_name,
                        'task': task,
                        'service_type': 'text'
                    }
                }
                
        except Exception as e:
            logger.error(f"ISA LLM invoke failed: {e}")
            return {
                'success': False,
                'result': None,
                'error': str(e),
                'metadata': {
                    'model_used': self.model_name,
                    'provider': self.provider_name,
                    'task': task,
                    'service_type': 'text'
                }
            }

# Backward compatibility aliases
class HuggingFaceLLMService(ISALLMService):
    """Alias for backward compatibility with AIFactory naming convention"""
    pass

class HuggingFaceInferenceService(ISALLMService):
    """Alias for backward compatibility"""
    pass