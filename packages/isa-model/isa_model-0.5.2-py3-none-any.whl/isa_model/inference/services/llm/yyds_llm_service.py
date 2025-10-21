import logging
from typing import Dict, Any, List, Union, AsyncGenerator, Optional

# (�� OpenAI �
from openai import AsyncOpenAI

from isa_model.inference.services.llm.base_llm_service import BaseLLMService

logger = logging.getLogger(__name__)

class YydsLLMService(BaseLLMService):
    """YYDS LLM service implementation with unified invoke interface"""
    
    def __init__(self, provider_name: str, model_name: str = "claude-sonnet-4-20250514", **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        # Get configuration from centralized config manager
        provider_config = self.get_provider_config()
        
        # Initialize AsyncOpenAI client with provider configuration
        try:
            if not provider_config.get("api_key"):
                raise ValueError("YYDS API key not found in provider configuration")
            
            self.client = AsyncOpenAI(
                api_key=provider_config["api_key"],
                base_url=provider_config.get("base_url") or provider_config.get("api_base_url", "https://api.yyds.com/v1"),
                organization=provider_config.get("organization")
            )
            
            logger.info(f"Initialized YydsLLMService with model {self.model_name} and endpoint {self.client.base_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize YYDS client: {e}")
            raise ValueError(f"Failed to initialize YYDS client. Check your API key configuration: {e}") from e
            
        self.last_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "requests_count": 0}
        
    
    def _create_bound_copy(self) -> 'YydsLLMService':
        """Create a copy of this service for tool binding"""
        bound_service = YydsLLMService(self.provider_name, self.model_name)
        bound_service._bound_tools = self._bound_tools.copy()
        return bound_service
    
    def bind_tools(self, tools: List[Any], **kwargs) -> 'YydsLLMService':
        """
        Bind tools to this LLM service for function calling
        
        Args:
            tools: List of tools (functions, dicts, or LangChain tools)
            **kwargs: Additional arguments for tool binding
            
        Returns:
            New LLM service instance with tools bound
        """
        # Create a copy of this service
        bound_service = self._create_bound_copy()
        
        # Use base class method to bind tools
        bound_service._bound_tools = tools
        
        return bound_service
    
    async def astream(self, input_data: Union[str, List[Dict[str, str]], Any], **kwargs) -> AsyncGenerator[str, None]:
        """
        True streaming method - yields tokens one by one as they arrive

        Args:
            input_data: Same as ainvoke
            **kwargs: Additional parameters (will filter out unsupported ones)

        Yields:
            Individual tokens as they arrive from the API
        """
        # Extract user_id before removing other params
        user_id = kwargs.pop('user_id', None)
        # Remove parameters that yyds doesn't support
        kwargs.pop('show_reasoning', None)  # OpenAI-specific parameter
        try:
            # Use adapter manager to prepare messages
            messages = self._prepare_messages(input_data)
            
            # Prepare request kwargs
            provider_config = self.get_provider_config()
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": provider_config.get("temperature", 0.7),
                "max_tokens": provider_config.get("max_tokens", 1024),
                "stream": True
            }
            
            # Add tools if bound using adapter manager
            tool_schemas = await self._prepare_tools_for_request()
            if tool_schemas:
                kwargs["tools"] = tool_schemas
                kwargs["tool_choice"] = "auto"
            
            # Stream tokens one by one
            content_chunks = []
            try:
                stream = await self.client.chat.completions.create(**kwargs)
                async for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        content_chunks.append(content)
                        yield content
                
                # Track usage after streaming is complete
                full_content = "".join(content_chunks)
                await self._track_streaming_usage(messages, full_content, user_id=user_id)
                
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                raise
            
        except Exception as e:
            logger.error(f"Error in astream: {e}")
            raise
    
    async def ainvoke(self, input_data: Union[str, List[Dict[str, str]], Any], **kwargs) -> Union[str, Any]:
        """Unified invoke method for all input types"""
        # Extract user_id before removing other params
        user_id = kwargs.pop('user_id', None)
        # Remove parameters that yyds doesn't support
        kwargs.pop('show_reasoning', None)  # OpenAI-specific parameter
        kwargs.pop('task', None)  # Handled internally
        try:
            # Use adapter manager to prepare messages
            messages = self._prepare_messages(input_data)
            
            # Prepare request kwargs
            provider_config = self.get_provider_config()
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": provider_config.get("temperature", 0.7),
                "max_tokens": provider_config.get("max_tokens", 1024)
            }
            
            # Add tools if bound using adapter manager
            tool_schemas = await self._prepare_tools_for_request()
            if tool_schemas:
                kwargs["tools"] = tool_schemas
                kwargs["tool_choice"] = "auto"
            
            # Handle streaming vs non-streaming
            if self.streaming:
                # TRUE STREAMING MODE - collect all chunks from the stream
                content_chunks = []
                async for token in self.astream(input_data):
                    content_chunks.append(token)
                content = "".join(content_chunks)
                
                return self._format_response(content, input_data)
            else:
                # Non-streaming mode
                response = await self.client.chat.completions.create(**kwargs)
                message = response.choices[0].message
                
                # Update usage tracking
                if response.usage:
                    self._update_token_usage(response.usage)
                    await self._track_billing(response.usage, user_id=user_id)
                
                # Handle tool calls if present - let adapter process the complete message
                if message.tool_calls:
                    # Pass the complete message object to adapter for proper tool_calls handling
                    return self._format_response(message, input_data)
                
                # Return appropriate format based on input type
                return self._format_response(message.content or "", input_data)
            
        except Exception as e:
            logger.error(f"Error in ainvoke: {e}")
            raise
    
    async def _track_streaming_usage(self, messages: List[Dict[str, str]], content: str, user_id: Optional[str] = None):
        """Track usage for streaming requests (estimated)"""
        # Create a mock usage object for tracking
        class MockUsage:
            def __init__(self):
                self.prompt_tokens = len(str(messages)) // 4  # Rough estimate
                self.completion_tokens = len(content) // 4   # Rough estimate
                self.total_tokens = self.prompt_tokens + self.completion_tokens

        usage = MockUsage()
        self._update_token_usage(usage)
        await self._track_billing(usage, user_id=user_id)
    
    async def _stream_response(self, kwargs: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Handle streaming responses - DEPRECATED: Use astream() instead"""
        kwargs["stream"] = True
        
        async def stream_generator():
            try:
                stream = await self.client.chat.completions.create(**kwargs)
                async for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                raise
        
        return stream_generator()
    
    
    def _update_token_usage(self, usage):
        """Update token usage statistics"""
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
    
    async def _track_billing(self, usage, user_id: Optional[str] = None):
        """Track billing information using unified billing system"""
        provider_config = self.get_provider_config()
        await self._track_llm_usage(
            user_id=user_id or "anonymous",
            operation="chat",
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            metadata={
                "temperature": provider_config.get("temperature", 0.7),
                "max_tokens": provider_config.get("max_tokens", 1024)
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
            "max_tokens": provider_config.get("max_tokens", 1024),
            "supports_streaming": True,
            "supports_functions": True,
            "provider": "yyds",
            "pricing": {
                "input_tokens_per_1k": 0.0045,
                "output_tokens_per_1k": 0.0225,
                "currency": "USD"
            }
        }
    
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
        
    async def close(self):
        """Close the backend client"""
        await self.client.close()