import logging
import os
import json
import asyncio
from typing import Dict, Any, List, Union, AsyncGenerator, Optional, Callable

# 使用官方 OpenAI 库
from openai import AsyncOpenAI

from isa_model.inference.services.llm.base_llm_service import BaseLLMService
from ....core.types import ServiceType

logger = logging.getLogger(__name__)

class OpenAILLMService(BaseLLMService):
    """OpenAI LLM service implementation with unified invoke interface"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", provider_name: str = "openai", **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        # Check if this is an O-series reasoning model
        self.is_reasoning_model = model_name.startswith("o4-") or model_name.startswith("o3-")
        self.uses_completion_tokens = self.is_reasoning_model or model_name.startswith("gpt-5")
        self.requires_default_temperature = self.is_reasoning_model or model_name.startswith("gpt-5")
        self.supports_deep_research = "deep-search" in model_name or "deep-research" in model_name
        
        # Get configuration from centralized config manager
        provider_config = self.get_provider_config()
        
        # Check if reasoning summary is enabled (requires verified organization)
        self.enable_reasoning_summary = provider_config.get("enable_reasoning_summary", False)
        
        # Initialize AsyncOpenAI client with provider configuration
        try:
            if not provider_config.get("api_key"):
                raise ValueError("OpenAI API key not found in provider configuration")
            
            self.client = AsyncOpenAI(
                api_key=provider_config["api_key"],
                base_url=provider_config.get("api_base_url", "https://api.openai.com/v1"),
                organization=provider_config.get("organization"),
                timeout=10.0,  # 10 second timeout for first token (much faster than 600s default)
                max_retries=2  # Retry on timeout
            )
            
            logger.info(f"Initialized OpenAILLMService with model {self.model_name} and endpoint {self.client.base_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ValueError(f"Failed to initialize OpenAI client. Check your API key configuration: {e}") from e
            
        self.last_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "requests_count": 0}
        
        # For O-series models, track reasoning tokens separately
        if self.is_reasoning_model:
            self.last_token_usage["reasoning_tokens"] = 0
            self.total_token_usage["reasoning_tokens"] = 0
        
    
    def _create_bound_copy(self) -> 'OpenAILLMService':
        """Create a copy of this service for tool binding"""
        # Create new instance but bypass full initialization
        bound_service = object.__new__(OpenAILLMService)
        
        # Copy all essential attributes from original service
        bound_service.model_name = self.model_name
        bound_service.provider_name = self.provider_name
        bound_service.client = self.client  # Reuse the same OpenAI client
        bound_service.last_token_usage = self.last_token_usage.copy()
        bound_service.total_token_usage = self.total_token_usage.copy()
        bound_service._bound_tools = self._bound_tools.copy() if self._bound_tools else []
        bound_service.adapter_manager = self.adapter_manager  # Reuse adapter manager
        
        # Copy OpenAI-specific attributes
        bound_service.is_reasoning_model = self.is_reasoning_model
        bound_service.uses_completion_tokens = self.uses_completion_tokens
        bound_service.requires_default_temperature = self.requires_default_temperature
        bound_service.supports_deep_research = self.supports_deep_research
        
        # Copy base class attributes
        bound_service.streaming = self.streaming
        bound_service.max_tokens = self.max_tokens
        bound_service.temperature = self.temperature
        bound_service._tool_mappings = {}
        
        # Copy BaseService attributes that are needed
        bound_service.config_manager = self.config_manager
        bound_service.model_manager = self.model_manager
        
        return bound_service
    
    def bind_tools(self, tools: List[Any], **kwargs) -> 'OpenAILLMService':
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
    
    async def astream(self, input_data: Union[str, List[Dict[str, str]], Any], show_reasoning: bool = False, **extra_kwargs) -> AsyncGenerator[Union[str, Dict[str, Any]], None]:
        """
        True streaming method - yields tokens one by one as they arrive
        
        Args:
            input_data: Same as ainvoke
            show_reasoning: If True and model supports it, show reasoning process using Responses API
            
        Yields:
            Individual tokens as they arrive from the API, plus final result object with tool_calls
        """
        try:
            # Determine which API to use for streaming
            use_responses_api = (show_reasoning and self.is_reasoning_model) or self.supports_deep_research
            
            if use_responses_api:
                logger.info(f"Using Responses API streaming for {self.model_name}")
                # Use Responses API streaming
                async for chunk in self._astream_responses_api(input_data, show_reasoning, **extra_kwargs):
                    yield chunk
            else:
                logger.debug(f"Using Chat Completions API streaming for {self.model_name}")
                # Use Chat Completions API streaming
                async for chunk in self._astream_chat_completions_api(input_data, **extra_kwargs):
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Error in astream: {e}")
            raise
    
    async def _astream_responses_api(self, input_data: Union[str, List[Dict[str, str]], Any], show_reasoning: bool = False, **extra_kwargs) -> AsyncGenerator[Union[str, Dict[str, Any]], None]:
        """Stream using Responses API for reasoning models and deep research models"""
        try:
            # Use adapter manager to prepare messages
            messages = self._prepare_messages(input_data)
            
            # Prepare request kwargs for Responses API
            provider_config = self.get_provider_config()
            kwargs = {
                "model": self.model_name,
                "input": messages,  # Responses API uses 'input' instead of 'messages'
                "stream": True
            }
            
            # Responses API uses max_output_tokens
            max_tokens_value = provider_config.get("max_tokens", 1024)
            kwargs["max_output_tokens"] = max_tokens_value
            
            # Add reasoning configuration if needed (optional - requires verified organization)
            if show_reasoning and self.is_reasoning_model and self.enable_reasoning_summary:
                kwargs["reasoning"] = {"summary": "auto"}
                logger.info("Reasoning summary enabled - using verified organization features")
            elif show_reasoning and self.is_reasoning_model:
                logger.info("Reasoning visibility requested - using Responses API without summary (requires verified org)")
            
            # Deep research models require web_search_preview tool
            if self.supports_deep_research:
                kwargs["tools"] = [{"type": "web_search_preview"}]
            
            # Add any additional bound tools
            tool_schemas = await self._prepare_tools_for_request()
            if tool_schemas:
                if "tools" not in kwargs:
                    kwargs["tools"] = []
                kwargs["tools"].extend(tool_schemas)
            
            # Stream using Responses API
            content_chunks = []
            reasoning_items = []
            
            try:
                logger.info(f"Streaming with Responses API for model {self.model_name}")
                stream = await self.client.responses.create(**kwargs)
                
                async for event in stream:
                    # Handle different event types from Responses API
                    if event.type == 'response.output_text.delta':
                        # Stream text content
                        if event.delta:
                            content_chunks.append(event.delta)
                            yield event.delta
                    
                    elif event.type == 'response.reasoning.delta' and show_reasoning:
                        # Stream reasoning content (if enabled)
                        if hasattr(event, 'delta') and event.delta:
                            yield f"[思考: {event.delta}]"
                    
                    elif event.type == 'response.output_item.done':
                        # Handle completed items (reasoning, function calls, etc.)
                        if hasattr(event, 'item'):
                            if event.item.type == 'reasoning':
                                reasoning_items.append(event.item)
                            elif event.item.type == 'function_call':
                                # Handle function call completion
                                logger.debug(f"Function call completed: {event.item}")
                
                # Create final response object
                full_content = "".join(content_chunks)
                
                # Track usage for streaming
                self._track_streaming_usage(messages, full_content)
                
                # Get billing info
                await asyncio.sleep(0.01)
                billing_info = self._get_streaming_billing_info()
                
                # Format final result
                final_result = self._format_response(full_content, input_data)
                
                # Yield final result with metadata
                yield {
                    "result": final_result,
                    "billing": billing_info,
                    "reasoning_items": len(reasoning_items),
                    "api_used": "responses"
                }
                
            except Exception as e:
                logger.error(f"Error in Responses API streaming: {e}")
                raise
                
        except Exception as e:
            logger.error(f"Error in _astream_responses_api: {e}")
            raise
    
    async def _astream_chat_completions_api(self, input_data: Union[str, List[Dict[str, str]], Any], **extra_kwargs) -> AsyncGenerator[Union[str, Dict[str, Any]], None]:
        """Stream using Chat Completions API for standard models"""
        try:
            # Use adapter manager to prepare messages
            messages = self._prepare_messages(input_data)
            
            # Prepare request kwargs
            provider_config = self.get_provider_config()
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "stream": True
            }
            
            # O4 and GPT-5 models only support temperature=1 (default)
            if not self.requires_default_temperature:
                kwargs["temperature"] = provider_config.get("temperature", 0.7)
            
            # O4 and GPT-5 models use max_completion_tokens instead of max_tokens
            max_tokens_value = provider_config.get("max_tokens", 1024)
            if self.uses_completion_tokens:
                kwargs["max_completion_tokens"] = max_tokens_value
            else:
                kwargs["max_tokens"] = max_tokens_value
            
            # Add tools if bound using adapter manager
            tool_schemas = await self._prepare_tools_for_request()
            if tool_schemas:
                kwargs["tools"] = tool_schemas
                kwargs["tool_choice"] = "auto"
            
            # Add response_format if specified (for JSON mode)
            if 'response_format' in extra_kwargs:
                kwargs['response_format'] = extra_kwargs['response_format']
                logger.debug(f"Using response_format in streaming: {extra_kwargs['response_format']}")
            
            # Stream tokens and detect tool calls
            content_chunks = []
            tool_calls_accumulator = {}  # Track complete tool calls by ID
            has_tool_calls = False
            
            try:
                stream = await self.client.chat.completions.create(**kwargs)
                async for chunk in stream:
                    delta = chunk.choices[0].delta
                    
                    # Check for tool calls first
                    if hasattr(delta, 'tool_calls') and delta.tool_calls:
                        has_tool_calls = True
                        for tool_call in delta.tool_calls:
                            tool_index = getattr(tool_call, 'index', 0)  # OpenAI uses index for streaming
                            
                            # Use index as key since streaming tool calls use index
                            tool_key = f"tool_{tool_index}"
                            
                            # Initialize tool call if not seen before
                            if tool_key not in tool_calls_accumulator:
                                tool_calls_accumulator[tool_key] = {
                                    'id': getattr(tool_call, 'id', f"call_{tool_index}"),
                                    'type': 'function',
                                    'function': {
                                        'name': '',
                                        'arguments': ''
                                    }
                                }
                            
                            # Accumulate function name
                            if hasattr(tool_call, 'function') and hasattr(tool_call.function, 'name') and tool_call.function.name:
                                tool_calls_accumulator[tool_key]['function']['name'] += tool_call.function.name
                            
                            # Accumulate function arguments
                            if hasattr(tool_call, 'function') and hasattr(tool_call.function, 'arguments'):
                                if tool_call.function.arguments:
                                    tool_calls_accumulator[tool_key]['function']['arguments'] += tool_call.function.arguments
                    
                    # Handle regular content - only stream if no tool calls detected
                    elif delta.content:
                        content_chunks.append(delta.content)
                        if not has_tool_calls:  # Only yield content if no tool calls
                            yield delta.content
                
                # Always yield final result at the end
                # - If has tool_calls: complete structured response (no prior streaming)
                # - If no tool_calls: AIMessage after streaming content
                
                # Create a mock message object for adapter processing
                class MockMessage:
                    def __init__(self):
                        self.content = "".join(content_chunks) or ""
                        self.tool_calls = []
                        # Add tool_calls if any
                        if tool_calls_accumulator:
                            for tool_data in tool_calls_accumulator.values():
                                mock_tool_call = type('MockToolCall', (), {
                                    'id': tool_data['id'],
                                    'function': type('MockFunction', (), {
                                        'name': tool_data['function']['name'],
                                        'arguments': tool_data['function']['arguments']
                                    })()
                                })()
                                self.tool_calls.append(mock_tool_call)
                
                mock_message = MockMessage()
                
                logger.debug(f"Streaming complete - tool calls collected: {len(mock_message.tool_calls)}")
                for i, tc in enumerate(mock_message.tool_calls):
                    logger.debug(f"  Tool call {i+1}: {tc.function.name} with args: {tc.function.arguments}")
                
                # Format response using adapter (this handles LangChain conversion)
                final_result = self._format_response(mock_message, input_data)
                
                logger.debug(f"Final result type after adapter: {type(final_result)}")
                logger.debug(f"Final result has tool_calls: {hasattr(final_result, 'tool_calls')}")
                
                # Track usage after streaming is complete
                full_content = "".join(content_chunks)
                self._track_streaming_usage(messages, full_content)
                
                # Get billing info after tracking (wait a moment for billing to be recorded)
                await asyncio.sleep(0.01)
                billing_info = self._get_streaming_billing_info()
                
                # Yield the final result with billing info
                yield {
                    "result": final_result,
                    "billing": billing_info,
                    "api_used": "chat_completions"
                }
                
            except Exception as e:
                logger.error(f"Error in Chat Completions streaming: {e}")
                raise
            
        except Exception as e:
            logger.error(f"Error in _astream_chat_completions_api: {e}")
            raise
    
    async def ainvoke(self, input_data: Union[str, List[Dict[str, str]], Any], show_reasoning: bool = False, **extra_kwargs) -> Union[str, Any]:
        """
        Unified invoke method for all input types

        Args:
            input_data: Input messages or text
            show_reasoning: If True and model supports it, show reasoning process using Responses API
            **extra_kwargs: Additional parameters to pass to the API (e.g., response_format)
        """
        try:
            # Extract user_id from kwargs for billing (don't overwrite if already set)
            if 'user_id' in extra_kwargs:
                self._current_user_id = extra_kwargs.get('user_id')
            # Use adapter manager to prepare messages
            messages = self._prepare_messages(input_data)
            
            # Determine which API to use
            # Responses API is required for:
            # 1. Reasoning models with show_reasoning=True
            # 2. Deep research models (they only work with Responses API)
            use_responses_api = (show_reasoning and self.is_reasoning_model) or self.supports_deep_research
            
            # Prepare request kwargs
            provider_config = self.get_provider_config()
            kwargs = {
                "model": self.model_name,
                "messages": messages
            }
            
            # O4 and GPT-5 models only support temperature=1 (default)
            if not self.requires_default_temperature:
                kwargs["temperature"] = provider_config.get("temperature", 0.7)
            
            # O4 and GPT-5 models use max_completion_tokens instead of max_tokens
            max_tokens_value = provider_config.get("max_tokens", 1024)
            if self.uses_completion_tokens:
                kwargs["max_completion_tokens"] = max_tokens_value
            else:
                kwargs["max_tokens"] = max_tokens_value
            
            # Add tools if bound using adapter manager
            tool_schemas = await self._prepare_tools_for_request()
            if tool_schemas:
                kwargs["tools"] = tool_schemas
                if not use_responses_api:  # Responses API handles tool choice differently
                    kwargs["tool_choice"] = "auto"
            
            # Add response_format if specified (for JSON mode)
            if 'response_format' in extra_kwargs:
                kwargs['response_format'] = extra_kwargs['response_format']
                logger.debug(f"Using response_format: {extra_kwargs['response_format']}")
            
            # Handle streaming vs non-streaming
            if self.streaming:
                # TRUE STREAMING MODE - collect all chunks from the stream
                content_chunks = []
                async for token in self.astream(input_data, show_reasoning=show_reasoning, **extra_kwargs):
                    if isinstance(token, str):
                        content_chunks.append(token)
                    elif isinstance(token, dict) and "result" in token:
                        # Return the final result from streaming
                        return token["result"]
                
                # Fallback: join collected content
                content = "".join(content_chunks)
                return self._format_response(content, input_data)
            else:
                # Non-streaming mode - choose API based on reasoning visibility
                if use_responses_api:
                    logger.info(f"Using Responses API for model {self.model_name}")
                    
                    # Convert kwargs for Responses API
                    responses_kwargs = {
                        "model": kwargs["model"],
                        "input": kwargs["messages"]  # Responses API uses 'input' instead of 'messages'
                    }
                    
                    # Handle max tokens parameter
                    if "max_completion_tokens" in kwargs:
                        responses_kwargs["max_output_tokens"] = kwargs["max_completion_tokens"]
                    elif "max_tokens" in kwargs:
                        responses_kwargs["max_output_tokens"] = kwargs["max_tokens"]
                    
                    # Add tools if present
                    if "tools" in kwargs:
                        responses_kwargs["tools"] = kwargs["tools"]
                    
                    # Add reasoning configuration for reasoning models (requires verified organization)
                    if show_reasoning and self.is_reasoning_model and self.enable_reasoning_summary:
                        responses_kwargs["reasoning"] = {"summary": "auto"}
                        logger.info("Reasoning summary enabled - using verified organization features")
                    elif show_reasoning and self.is_reasoning_model:
                        logger.info("Reasoning visibility requested - using Responses API without summary (requires verified org)")
                    
                    # Deep research models require web_search_preview tool
                    if self.supports_deep_research:
                        if "tools" not in responses_kwargs:
                            responses_kwargs["tools"] = []
                        responses_kwargs["tools"].insert(0, {"type": "web_search_preview"})
                    
                    response = await self.client.responses.create(**responses_kwargs)
                    
                    # Handle Responses API format
                    if hasattr(response, 'output_text'):
                        # Modern Responses API format
                        content = response.output_text
                        usage_info = getattr(response, 'usage', None)
                    elif hasattr(response, 'body') and hasattr(response.body, 'response'):
                        # Legacy format
                        content = response.body.response
                        usage_info = getattr(response.body, 'usage', None)
                    else:
                        # Fallback handling
                        content = str(response)
                        usage_info = None
                    
                    # Update usage tracking if available
                    if usage_info:
                        self._update_token_usage(usage_info)
                        await self._track_billing(usage_info)
                    
                    return self._format_response(content, input_data)
                else:
                    # Standard Chat Completions API
                    response = await self.client.chat.completions.create(**kwargs)
                    message = response.choices[0].message
                    
                    # Debug: Log the raw OpenAI response
                    logger.debug(f"OpenAI response message: {message}")
                    if message.tool_calls:
                        logger.debug(f"Tool calls found: {len(message.tool_calls)}")
                        for i, tc in enumerate(message.tool_calls):
                            logger.debug(f"  Tool call {i+1}: id={tc.id}, function={tc.function.name}, args={tc.function.arguments}")
                    
                    # Update usage tracking
                    if response.usage:
                        self._update_token_usage(response.usage)
                        await self._track_billing(response.usage)
                    
                    # Handle tool calls if present - let adapter process the complete message
                    if message.tool_calls:
                        # Pass the complete message object to adapter for proper tool_calls handling
                        return self._format_response(message, input_data)
                    
                    # Return appropriate format based on input type
                    return self._format_response(message.content or "", input_data)
            
        except Exception as e:
            logger.error(f"Error in ainvoke: {e}")
            raise
    
    def _track_streaming_usage(self, messages: List[Dict[str, str]], content: str):
        """Track usage for streaming requests (estimated)"""
        # Create a mock usage object for tracking
        class MockUsage:
            def __init__(self):
                self.prompt_tokens = len(str(messages)) // 4  # Rough estimate
                self.completion_tokens = len(content) // 4   # Rough estimate  
                self.total_tokens = self.prompt_tokens + self.completion_tokens
        
        usage = MockUsage()
        self._update_token_usage(usage)
        # Fire and forget async tracking
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._track_billing(usage))
        except:
            # If no event loop, skip tracking
            pass
    
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
        # Handle different usage object structures (Chat Completions vs Responses API)
        if hasattr(usage, 'prompt_tokens'):
            # Chat Completions API format
            self.last_token_usage = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }
        elif hasattr(usage, 'input_tokens'):
            # Responses API format
            self.last_token_usage = {
                "prompt_tokens": usage.input_tokens,
                "completion_tokens": usage.output_tokens,
                "total_tokens": usage.total_tokens
            }
        else:
            # Fallback for unknown usage format
            logger.warning(f"Unknown usage format: {type(usage)}, attributes: {dir(usage)}")
            self.last_token_usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        
        # For O-series models, track reasoning tokens if available
        if self.is_reasoning_model:
            reasoning_tokens = 0
            if hasattr(usage, 'reasoning_tokens'):
                reasoning_tokens = usage.reasoning_tokens
            elif hasattr(usage, 'output_tokens_details') and hasattr(usage.output_tokens_details, 'reasoning_tokens'):
                reasoning_tokens = usage.output_tokens_details.reasoning_tokens
            
            self.last_token_usage["reasoning_tokens"] = reasoning_tokens
            if "reasoning_tokens" not in self.total_token_usage:
                self.total_token_usage["reasoning_tokens"] = 0
            self.total_token_usage["reasoning_tokens"] += reasoning_tokens
        
        # Update total usage
        self.total_token_usage["prompt_tokens"] += self.last_token_usage["prompt_tokens"]
        self.total_token_usage["completion_tokens"] += self.last_token_usage["completion_tokens"]
        self.total_token_usage["total_tokens"] += self.last_token_usage["total_tokens"]
        self.total_token_usage["requests_count"] += 1
    
    async def _track_billing(self, usage):
        """Track billing information"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"_track_billing called with user_id={self._current_user_id}")

        provider_config = self.get_provider_config()

        # Prepare metadata for tracking
        metadata = {
            "temperature": provider_config.get("temperature", 0.7),
            "max_tokens": provider_config.get("max_tokens", 1024),
            "is_reasoning_model": self.is_reasoning_model
        }

        # Add reasoning tokens if available for O-series models
        if self.is_reasoning_model and hasattr(usage, 'reasoning_tokens'):
            metadata["reasoning_tokens"] = usage.reasoning_tokens

        # Get tokens using the same logic as _update_token_usage
        if hasattr(usage, 'prompt_tokens'):
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
        elif hasattr(usage, 'input_tokens'):
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
        else:
            input_tokens = 0
            output_tokens = 0

        logger.info(f"Token usage: input={input_tokens}, output={output_tokens}")

        # Publish billing event if user_id is available
        if self._current_user_id:
            logger.info(f"About to call _publish_billing_event for user={self._current_user_id}")
            await self._publish_billing_event(
                user_id=self._current_user_id,
                service_type=ServiceType.LLM,
                operation="chat",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                metadata=metadata
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
            "supports_reasoning": self.is_reasoning_model,
            "supports_deep_research": self.supports_deep_research,
            "provider": "openai",
            "model_type": "reasoning" if self.is_reasoning_model else "standard"
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
            show_reasoning: Whether to show reasoning process (for O4 models)
            
        Returns:
            Dict containing chat response with properly formatted message object
        """
        try:
            # Call ainvoke with show_reasoning parameter
            response = await self.ainvoke(input_data, show_reasoning=show_reasoning)
            
            # Return the response as-is (adapter already formatted it correctly)
            # For LangChain inputs, this will be an AIMessage object
            # For standard inputs, this will be a string
            return {
                "message": response,  # Changed from "text" to "message" to preserve object
                "success": True,
                "metadata": {
                    "model": self.model_name,
                    "provider": self.provider_name,
                    "max_tokens": max_tokens or self.max_tokens,
                    "show_reasoning": show_reasoning,
                    "is_reasoning_model": self.is_reasoning_model
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
    
    async def deep_research(
        self,
        input_data: Union[str, List[Dict[str, str]], Any],
        research_type: Optional[str] = None,
        search_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        深度研究任务 - 专为深度研究模型设计，使用OpenAI Responses API
        
        Args:
            input_data: 研究查询或问题
            research_type: 研究类型 (academic, market, competitive, etc.)
            search_enabled: 是否启用网络搜索
            
        Returns:
            Dict containing research results
        """
        if not self.supports_deep_research:
            # Fallback to regular chat for non-deep-research models
            logger.info(f"Model {self.model_name} doesn't support deep research, falling back to regular chat")
            return await self.chat(input_data)
        
        try:
            # Prepare messages with research context
            messages = self._prepare_messages(input_data)
            
            # Add research-specific system prompt if research_type is specified
            if research_type and messages:
                research_prompts = {
                    "academic": "You are conducting academic research. Please provide thorough, well-sourced analysis with proper citations and methodical reasoning.",
                    "market": "You are conducting market research. Focus on market trends, competitive analysis, and business insights.",
                    "competitive": "You are conducting competitive analysis. Compare and contrast different approaches, solutions, or entities.",
                    "technical": "You are conducting technical research. Provide detailed technical analysis with implementation considerations."
                }
                
                if research_type in research_prompts:
                    # Insert system message at the beginning
                    system_msg = {"role": "system", "content": research_prompts[research_type]}
                    if messages[0].get("role") == "system":
                        messages[0]["content"] = research_prompts[research_type] + "\n\n" + messages[0]["content"]
                    else:
                        messages.insert(0, system_msg)
            
            # Prepare request kwargs for Responses API
            provider_config = self.get_provider_config()
            kwargs = {
                "model": self.model_name,
                "input": messages  # Responses API uses 'input' instead of 'messages'
            }
            
            # Responses API uses max_output_tokens instead of max_completion_tokens
            max_tokens_value = provider_config.get("max_tokens", 4096)
            kwargs["max_output_tokens"] = max_tokens_value
            
            # Deep research models require web_search_preview tool when search is enabled
            if search_enabled:
                kwargs["tools"] = [
                    {
                        "type": "web_search_preview"
                    }
                ]
            
            # Add any additional bound tools
            tool_schemas = await self._prepare_tools_for_request()
            if tool_schemas:
                if "tools" not in kwargs:
                    kwargs["tools"] = []
                kwargs["tools"].extend(tool_schemas)
            
            # Check if streaming is enabled
            if self.streaming:
                # Use streaming mode for deep research
                logger.info(f"Using Responses API streaming for deep research model {self.model_name}")
                kwargs["stream"] = True
                
                content_chunks = []
                stream = await self.client.responses.create(**kwargs)
                
                async for event in stream:
                    if event.type == 'response.output_text.delta':
                        if event.delta:
                            content_chunks.append(event.delta)
                
                message_content = "".join(content_chunks)
                
                # Track estimated usage for streaming
                messages = self._prepare_messages(input_data)
                self._track_streaming_usage(messages, message_content)
                
                # Format response
                formatted_response = self._format_response(message_content or "", input_data)
            else:
                # Use non-streaming mode for deep research
                logger.info(f"Using Responses API for deep research model {self.model_name}")
                response = await self.client.responses.create(**kwargs)
                
                # Extract the response content from Responses API format
                if hasattr(response, 'output_text'):
                    # Modern Responses API format
                    message_content = response.output_text
                    usage_info = getattr(response, 'usage', None)
                elif hasattr(response, 'body') and hasattr(response.body, 'response'):
                    # Legacy Responses API format
                    message_content = response.body.response
                    usage_info = getattr(response.body, 'usage', None)
                elif hasattr(response, 'choices') and response.choices:
                    # Fallback to standard format
                    message_content = response.choices[0].message.content
                    usage_info = getattr(response, 'usage', None)
                else:
                    # Handle unexpected format
                    message_content = str(response)
                    usage_info = None
                
                # Update usage tracking if available
                if usage_info:
                    self._update_token_usage(usage_info)
                    await self._track_billing(usage_info)
                
                # Format response
                formatted_response = self._format_response(message_content or "", input_data)
            
            return {
                "result": formatted_response,
                "research_type": research_type,
                "search_enabled": search_enabled,
                "success": True,
                "metadata": {
                    "model": self.model_name,
                    "provider": self.provider_name,
                    "supports_deep_research": self.supports_deep_research,
                    "reasoning_model": self.is_reasoning_model,
                    "api_used": "responses"
                }
            }
            
        except Exception as e:
            logger.error(f"Deep research failed: {e}")
            return {
                "result": None,
                "success": False,
                "error": str(e),
                "metadata": {
                    "model": self.model_name,
                    "provider": self.provider_name,
                    "api_used": "responses"
                }
            }

    async def close(self):
        """Close the backend client"""
        await self.client.close()
    
    def _get_streaming_billing_info(self) -> Dict[str, Any]:
        """Get billing information for streaming requests"""
        try:
            # Check if service has model_manager with billing_tracker
            if hasattr(self, 'model_manager') and hasattr(self.model_manager, 'billing_tracker'):
                billing_tracker = self.model_manager.billing_tracker
                
                # Get the latest usage record for this model
                model_records = [
                    record for record in billing_tracker.usage_records
                    if record.model_id == self.model_name
                ]
                
                if model_records:
                    # Get the most recent record
                    latest_record = max(model_records, key=lambda r: r.timestamp)
                    
                    return {
                        "cost_usd": latest_record.cost_usd,
                        "input_tokens": latest_record.input_tokens,
                        "output_tokens": latest_record.output_tokens,
                        "total_tokens": latest_record.total_tokens,
                        "operation": latest_record.operation,
                        "timestamp": latest_record.timestamp,
                        "currency": "USD"
                    }
            
            # Fallback: use last token usage with estimated cost
            last_usage = self.get_last_token_usage()
            estimated_cost = 0.0
            
            if hasattr(self, 'model_manager'):
                estimated_cost = self.model_manager.calculate_cost(
                    provider=self.provider_name,
                    model_name=self.model_name,
                    input_tokens=last_usage.get("prompt_tokens", 0),
                    output_tokens=last_usage.get("completion_tokens", 0)
                )
            
            return {
                "cost_usd": estimated_cost,
                "input_tokens": last_usage.get("prompt_tokens", 0),
                "output_tokens": last_usage.get("completion_tokens", 0),
                "total_tokens": last_usage.get("total_tokens", 0),
                "operation": "chat",
                "timestamp": None,
                "currency": "USD",
                "note": "Estimated from last token usage"
            }
            
        except Exception as e:
            logger.warning(f"Failed to get streaming billing info: {e}")
            return {
                "cost_usd": 0.0,
                "error": str(e),
                "currency": "USD"
            }