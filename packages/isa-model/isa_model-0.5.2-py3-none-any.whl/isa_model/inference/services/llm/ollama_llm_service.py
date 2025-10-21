import logging
import httpx
import json
from typing import Dict, Any, List, Union, AsyncGenerator, Optional, Callable
from isa_model.inference.services.llm.base_llm_service import BaseLLMService
from isa_model.core.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class OllamaLLMService(BaseLLMService):
    """Ollama LLM service with unified invoke interface and proper adapter support"""
    
    def __init__(self, provider_name: str, model_name: str = "llama3.2:3b-instruct-fp16", **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        # Get configuration from centralized config manager
        provider_config = self.get_provider_config()
        
        # Create HTTP client for Ollama API
        config_manager = ConfigManager()
        # Use Consul discovery with fallback
        default_base_url = config_manager.get_ollama_url()
        base_url = provider_config.get("base_url", default_base_url)
        timeout = provider_config.get("timeout", 60)
        
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout
        )
            
        self.last_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "requests_count": 0}
        
        
        logger.info(f"Initialized OllamaLLMService with model {model_name} at {base_url}")
    
    def _ensure_client(self):
        """Ensure the HTTP client is available and not closed"""
        if not hasattr(self, 'client') or not self.client or self.client.is_closed:
            provider_config = self.get_provider_config()
            config_manager = ConfigManager()
            # Use Consul discovery with fallback
            default_base_url = config_manager.get_ollama_url()
            base_url = provider_config.get("base_url", default_base_url)
            timeout = provider_config.get("timeout", 60)
            self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
    
    def _create_bound_copy(self) -> 'OllamaLLMService':
        """Create a copy of this service for tool binding"""
        bound_service = OllamaLLMService(self.provider_name, self.model_name)
        bound_service._bound_tools = self._bound_tools.copy()
        return bound_service
    
    def bind_tools(self, tools: List[Any], **kwargs) -> 'OllamaLLMService':
        """Bind tools to this LLM service for function calling"""
        bound_service = self._create_bound_copy()
        # Use base class method to bind tools
        bound_service._bound_tools = tools
        
        return bound_service
    
    async def ainvoke(self, input_data: Union[str, List[Dict[str, str]], Any], **kwargs) -> Union[str, Any]:
        """
        Universal async invocation method that handles different input types

        Args:
            input_data: Can be:
                - str: Simple text prompt
                - list: Message history like [{"role": "user", "content": "hello"}]
                - Any: LangChain message objects or other formats

        Returns:
            Model response (string for simple cases, object for complex cases)
        """
        # Extract user_id from kwargs
        user_id = kwargs.pop('user_id', None)
        try:
            # Ensure client is available
            self._ensure_client()
            
            # Use adapter manager to prepare messages (consistent with OpenAI service)
            messages = self._prepare_messages(input_data)
            
            # Prepare request parameters
            provider_config = self.get_provider_config()
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": self.streaming,
                "options": {
                    "temperature": provider_config.get("temperature", 0.7),
                    "top_p": provider_config.get("top_p", 0.9),
                    "num_predict": provider_config.get("max_tokens", 2048)
                }
            }
            
            # Add tools if bound using adapter manager
            tool_schemas = await self._prepare_tools_for_request()
            if tool_schemas:
                payload["tools"] = tool_schemas
            
            # Handle streaming vs non-streaming
            if self.streaming:
                # TRUE STREAMING MODE - collect all chunks from the stream
                content_chunks = []
                async for token in self.astream(input_data):
                    content_chunks.append(token)
                content = "".join(content_chunks)
                
                return self._format_response(content, input_data)
            
            # Regular request
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Update token usage if available
            if "eval_count" in result:
                self._update_token_usage(result)
                await self._track_ollama_billing(result, user_id=user_id)
            
            # Handle tool calls if present - let adapter process the complete message
            message = result["message"]
            if "tool_calls" in message and message["tool_calls"]:
                # Create message object similar to OpenAI format for adapter processing
                message_obj = type('OllamaMessage', (), {
                    'content': message.get("content", ""),
                    'tool_calls': message["tool_calls"]
                })()
                # Pass the complete message object to adapter for proper tool_calls handling
                return self._format_response(message_obj, input_data)
            
            # Return appropriate format based on input type
            return self._format_response(message.get("content", ""), input_data)
            
        except httpx.RequestError as e:
            logger.error(f"HTTP request error in ainvoke: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
    
    def _prepare_messages(self, input_data: Union[str, List[Dict[str, str]], Any]) -> List[Dict[str, str]]:
        """Use adapter manager to convert messages (consistent with OpenAI service)"""
        return self.adapter_manager.convert_messages(input_data)
    
    
    def _format_response(self, response: Union[str, Any], original_input: Any) -> Union[str, Any]:
        """Use adapter manager to format response (consistent with OpenAI service)"""
        return self.adapter_manager.format_response(response, original_input)
    
    async def chat(
        self,
        input_data: Union[str, List[Dict[str, str]], Any],
        max_tokens: Optional[int] = None,
        show_reasoning: bool = False
    ) -> Dict[str, Any]:
        """
        Chat method that wraps ainvoke for compatibility with base class
        
        Args:
            input_data: Input messages
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict containing chat response with properly formatted message object
        """
        try:
            # Call ainvoke and get the response (already processed by adapter)
            response = await self.ainvoke(input_data)
            
            # Return the response as-is (adapter already formatted it correctly)
            # For LangChain inputs, this will be an AIMessage object
            # For standard inputs, this will be a string
            return {
                "message": response,  # Use "message" to preserve object type
                "success": True,
                "metadata": {
                    "model": self.model_name,
                    "provider": self.provider_name,
                    "max_tokens": max_tokens or self.max_tokens
                }
            }
        except Exception as e:
            logger.error(f"Chat method failed: {e}")
            return {
                "message": None,
                "success": False,
                "error": str(e),
                "metadata": {
                    "model": self.model_name,
                    "provider": self.provider_name
                }
            }
    
    
    async def _stream_response(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Handle streaming responses"""
        async def stream_generator():
            try:
                async with self.client.stream("POST", "/api/chat", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                if "message" in chunk and "content" in chunk["message"]:
                                    content = chunk["message"]["content"]
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                raise
        
        return stream_generator()
    
    async def _handle_tool_calls(self, assistant_message: Dict[str, Any], original_messages: List[Dict[str, str]]) -> str:
        """Handle tool calls from the assistant using adapter manager"""
        tool_calls = assistant_message.get("tool_calls", [])
        
        # Add assistant message with tool calls to conversation
        messages = original_messages + [assistant_message]
        
        # Execute each tool call using adapter manager
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            
            try:
                # Parse arguments if they're a string
                arguments = tool_call["function"]["arguments"]
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
                
                # Use adapter manager to execute tool
                result = await self._execute_tool_call(function_name, arguments)
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": tool_call.get("id", function_name)
                })
                
            except Exception as e:
                logger.error(f"Error executing tool {function_name}: {e}")
                messages.append({
                    "role": "tool",
                    "content": f"Error executing {function_name}: {str(e)}",
                    "tool_call_id": tool_call.get("id", function_name)
                })
        
        # Get final response from the model
        return await self.ainvoke(messages)
    
    async def _track_streaming_usage(self, messages: List[Dict[str, str]], content: str, user_id: Optional[str] = None):
        """Track usage for streaming requests (estimated)"""
        # Create a mock usage object for tracking
        class MockUsage:
            def __init__(self):
                self.prompt_tokens = len(str(messages)) // 4  # Rough estimate
                self.completion_tokens = len(content) // 4   # Rough estimate
                self.total_tokens = self.prompt_tokens + self.completion_tokens

        usage = MockUsage()
        self._update_token_usage_from_mock(usage)

        # Track billing
        await self._track_llm_usage(
            user_id=user_id or "anonymous",
            operation="chat_stream",
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            metadata={
                "model": self.model_name,
                "provider": "ollama",
                "streaming": True
            }
        )
    
    def _update_token_usage_from_mock(self, usage):
        """Update token usage statistics from mock usage object"""
        self.last_token_usage = {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens
        }
        
        # Update total usage
        self.total_token_usage["prompt_tokens"] += self.last_token_usage["prompt_tokens"]
        self.total_token_usage["completion_tokens"] += self.last_token_usage["completion_tokens"]
        self.total_token_usage["total_tokens"] += self.last_token_usage["total_tokens"]
        self.total_token_usage["requests_count"] += 1

    def _update_token_usage(self, result: Dict[str, Any]):
        """Update token usage statistics"""
        self.last_token_usage = {
            "prompt_tokens": result.get("prompt_eval_count", 0),
            "completion_tokens": result.get("eval_count", 0),
            "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
        }
        
        # Update total usage
        self.total_token_usage["prompt_tokens"] += self.last_token_usage["prompt_tokens"]
        self.total_token_usage["completion_tokens"] += self.last_token_usage["completion_tokens"]
        self.total_token_usage["total_tokens"] += self.last_token_usage["total_tokens"]
        self.total_token_usage["requests_count"] += 1
    
    async def _track_ollama_billing(self, result: Dict[str, Any], user_id: Optional[str] = None):
        """Track billing information for Ollama requests"""
        prompt_tokens = result.get("prompt_eval_count", 0)
        completion_tokens = result.get("eval_count", 0)

        await self._track_llm_usage(
            user_id=user_id or "anonymous",
            operation="chat",
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            metadata={
                "model": self.model_name,
                "provider": "ollama"
            }
        )
    
    def get_token_usage(self) -> Dict[str, Any]:
        """Get total token usage statistics"""
        return self.total_token_usage
    
    def get_last_token_usage(self) -> Dict[str, int]:
        """Get token usage from last request"""
        return self.last_token_usage
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        provider_config = self.get_provider_config()
        return {
            "name": self.model_name,
            "max_tokens": provider_config.get("max_tokens", 2048),
            "supports_streaming": True,
            "supports_functions": True,
            "provider": "ollama"
        }
    
        
    async def close(self):
        """Close the HTTP client"""
        if hasattr(self, 'client') and self.client:
            try:
                if not self.client.is_closed:
                    await self.client.aclose()
            except Exception as e:
                logger.warning(f"Error closing Ollama client: {e}")

    async def astream(self, input_data: Union[str, List[Dict[str, str]], Any], **kwargs) -> AsyncGenerator[str, None]:
        """
        True streaming method that yields tokens one by one as they arrive

        Args:
            input_data: Can be:
                - str: Simple text prompt
                - list: Message history like [{"role": "user", "content": "hello"}]
                - Any: LangChain message objects or other formats

        Yields:
            Individual tokens as they arrive from the model
        """
        # Extract user_id from kwargs
        user_id = kwargs.pop('user_id', None)
        try:
            # Ensure client is available
            self._ensure_client()
            
            # Use adapter manager to prepare messages
            messages = self._prepare_messages(input_data)
            
            # Prepare request parameters for streaming
            provider_config = self.get_provider_config()
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": True,  # Force streaming for astream
                "options": {
                    "temperature": provider_config.get("temperature", 0.7),
                    "top_p": provider_config.get("top_p", 0.9),
                    "num_predict": provider_config.get("max_tokens", 2048)
                }
            }
            
            # Add tools if bound using adapter manager
            tool_schemas = await self._prepare_tools_for_request()
            if tool_schemas:
                payload["tools"] = tool_schemas
            
            # Stream tokens one by one
            content_chunks = []
            try:
                async with self.client.stream("POST", "/api/chat", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                if "message" in chunk and "content" in chunk["message"]:
                                    content = chunk["message"]["content"]
                                    if content:
                                        content_chunks.append(content)
                                        yield content
                            except json.JSONDecodeError:
                                continue
                
                # Track usage after streaming is complete (estimated)
                full_content = "".join(content_chunks)
                await self._track_streaming_usage(messages, full_content, user_id=user_id)
                
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                raise
            
        except httpx.RequestError as e:
            logger.error(f"HTTP request error in astream: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in astream: {e}")
            raise