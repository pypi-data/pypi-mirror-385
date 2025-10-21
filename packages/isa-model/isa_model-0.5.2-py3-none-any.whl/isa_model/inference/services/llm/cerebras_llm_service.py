import logging
import json
import asyncio
from typing import Dict, Any, List, Union, AsyncGenerator, Optional

# Conditional import for Cerebras SDK
try:
    from cerebras.cloud.sdk import Cerebras
    CEREBRAS_AVAILABLE = True
except ImportError:
    CEREBRAS_AVAILABLE = False
    Cerebras = None

from isa_model.inference.services.llm.base_llm_service import BaseLLMService
from isa_model.core.types import ServiceType
from isa_model.core.dependencies import DependencyChecker

logger = logging.getLogger(__name__)

class CerebrasLLMService(BaseLLMService):
    """
    Cerebras LLM service implementation with tool calling emulation.

    Cerebras provides ultra-fast inference but doesn't natively support function calling.
    This implementation uses prompt engineering to emulate tool calling capabilities.

    Supported models:
    - llama-4-scout-17b-16e-instruct (109B params, ~2600 tokens/sec)
    - llama3.1-8b (8B params, ~2200 tokens/sec)
    - llama-3.3-70b (70B params, ~2100 tokens/sec)
    - gpt-oss-120b (120B params, ~3000 tokens/sec)
    - qwen-3-32b (32B params, ~2600 tokens/sec)
    """

    def __init__(self, model_name: str = "llama-3.3-70b", provider_name: str = "cerebras", **kwargs):
        # Check if Cerebras SDK is available
        if not CEREBRAS_AVAILABLE:
            install_cmd = DependencyChecker.get_install_command(packages=["cerebras-cloud-sdk"])
            raise ImportError(
                f"Cerebras SDK is not installed. This is required for using Cerebras models.\n"
                f"Install with: {install_cmd}"
            )
        
        super().__init__(provider_name, model_name, **kwargs)

        # Check if this is a reasoning model (gpt-oss-120b supports CoT reasoning)
        self.is_reasoning_model = "gpt-oss" in model_name.lower()

        # Get configuration from centralized config manager
        provider_config = self.get_provider_config()

        # Initialize Cerebras client
        try:
            if not provider_config.get("api_key"):
                raise ValueError("Cerebras API key not found in provider configuration")

            self.client = Cerebras(
                api_key=provider_config["api_key"],
            )

            logger.info(f"Initialized CerebrasLLMService with model {self.model_name}")
            if self.is_reasoning_model:
                logger.info(f"Model {self.model_name} is a reasoning model with CoT support")

        except Exception as e:
            logger.error(f"Failed to initialize Cerebras client: {e}")
            raise ValueError(f"Failed to initialize Cerebras client. Check your API key configuration: {e}") from e

        self.last_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "requests_count": 0}

        # Tool calling emulation flag
        self._emulate_tool_calling = True

    def _create_bound_copy(self) -> 'CerebrasLLMService':
        """Create a copy of this service for tool binding"""
        bound_service = object.__new__(CerebrasLLMService)

        # Copy all essential attributes
        bound_service.model_name = self.model_name
        bound_service.provider_name = self.provider_name
        bound_service.client = self.client
        bound_service.last_token_usage = self.last_token_usage.copy()
        bound_service.total_token_usage = self.total_token_usage.copy()
        bound_service._bound_tools = self._bound_tools.copy() if self._bound_tools else []
        bound_service.adapter_manager = self.adapter_manager

        # Copy base class attributes
        bound_service.streaming = self.streaming
        bound_service.max_tokens = self.max_tokens
        bound_service.temperature = self.temperature
        bound_service._tool_mappings = {}
        bound_service._emulate_tool_calling = self._emulate_tool_calling

        # Copy BaseService attributes
        bound_service.config_manager = self.config_manager
        bound_service.model_manager = self.model_manager

        return bound_service

    def bind_tools(self, tools: List[Any], **kwargs) -> 'CerebrasLLMService':
        """
        Bind tools to this LLM service for emulated function calling

        Args:
            tools: List of tools (functions, dicts, or LangChain tools)
            **kwargs: Additional arguments for tool binding

        Returns:
            New LLM service instance with tools bound
        """
        bound_service = self._create_bound_copy()
        bound_service._bound_tools = tools

        return bound_service

    def _create_tool_calling_prompt(self, messages: List[Dict[str, str]], tool_schemas: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Create a prompt that instructs the model to use tools via structured output.

        This emulates OpenAI-style function calling using prompt engineering.
        """
        # Build tool descriptions
        tool_descriptions = []
        for tool in tool_schemas:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                name = func.get("name", "unknown")
                description = func.get("description", "")
                parameters = func.get("parameters", {})

                tool_desc = f"- {name}: {description}"
                if parameters.get("properties"):
                    props = []
                    for prop_name, prop_info in parameters["properties"].items():
                        prop_type = prop_info.get("type", "any")
                        prop_desc = prop_info.get("description", "")
                        props.append(f"  - {prop_name} ({prop_type}): {prop_desc}")
                    tool_desc += "\n" + "\n".join(props)

                tool_descriptions.append(tool_desc)

        # Create system message with tool instructions
        tool_system_msg = f"""You have access to the following tools:

{chr(10).join(tool_descriptions)}

IMPORTANT INSTRUCTIONS:
1. Analyze the user's request carefully
2. Select ALL APPROPRIATE tools needed to fulfill the request
3. You can call MULTIPLE tools in a single response if needed
4. When tools are needed, respond ONLY with a JSON object (no other text)
5. Choose tools based on their description and purpose

When you need to use tool(s), respond with ONLY this JSON format:
{{
  "tool_calls": [
    {{
      "id": "call_1",
      "type": "function", 
      "function": {{
        "name": "<exact_tool_name_from_list>",
        "arguments": "{{\\"param1\\": \\"value1\\", \\"param2\\": \\"value2\\"}}"
      }}
    }},
    {{
      "id": "call_2",
      "type": "function",
      "function": {{
        "name": "<another_tool_if_needed>",
        "arguments": "{{\\"param1\\": \\"value1\\"}}"
      }}
    }}
  ]
}}

Examples:
- Single tool: "Calculate 5+5" → use calculate tool once
- Multiple tools: "Weather in Paris and Tokyo" → use get_weather twice
- Multiple different tools: "Book flight and check weather" → use book_flight AND get_weather

Only respond normally WITHOUT JSON if the request does NOT require any of the available tools."""

        # Prepend or merge with existing system message
        modified_messages = messages.copy()
        if modified_messages and modified_messages[0].get("role") == "system":
            # Merge with existing system message
            modified_messages[0]["content"] = tool_system_msg + "\n\n" + modified_messages[0]["content"]
        else:
            # Add new system message
            modified_messages.insert(0, {"role": "system", "content": tool_system_msg})

        return modified_messages

    def _add_reasoning_instruction(self, messages: List[Dict[str, str]], level: str = "high") -> List[Dict[str, str]]:
        """
        Add reasoning level instruction to system message for gpt-oss-120b.

        Args:
            messages: List of message dicts
            level: Reasoning level - "low", "medium", or "high"

        Returns:
            Modified messages with reasoning instruction
        """
        # Create reasoning instruction
        reasoning_instruction = f"Reasoning: {level}"

        # Find or create system message
        modified_messages = messages.copy()

        if modified_messages and modified_messages[0].get("role") == "system":
            # Append to existing system message
            modified_messages[0]["content"] = f"{reasoning_instruction}\n\n{modified_messages[0]['content']}"
        else:
            # Insert new system message at the beginning
            modified_messages.insert(0, {
                "role": "system",
                "content": reasoning_instruction
            })

        logger.info(f"Added reasoning level '{level}' for gpt-oss-120b")
        return modified_messages

    def _parse_tool_calling_response(self, content: str) -> tuple[Optional[str], Optional[List[Dict[str, Any]]]]:
        """
        Parse the model's response to extract tool calls.

        Returns:
            (text_content, tool_calls) where tool_calls is None if no tools were called
        """
        content = content.strip()

        # Try to parse as JSON
        try:
            # Check if response contains JSON
            if content.startswith("{") and "tool_calls" in content:
                data = json.loads(content)
                tool_calls = data.get("tool_calls", [])

                if tool_calls:
                    # Convert to OpenAI format
                    formatted_calls = []
                    for call in tool_calls:
                        formatted_calls.append({
                            "id": call.get("id", f"call_{len(formatted_calls)}"),
                            "type": "function",
                            "function": {
                                "name": call.get("function", {}).get("name", ""),
                                "arguments": call.get("function", {}).get("arguments", "{}")
                            }
                        })

                    return None, formatted_calls
        except json.JSONDecodeError:
            pass

        # No tool calls found, return content as-is
        return content, None

    async def astream(self, input_data: Union[str, List[Dict[str, str]], Any], show_reasoning: bool = False, **kwargs) -> AsyncGenerator[Union[str, Dict[str, Any]], None]:
        """
        True streaming method - yields tokens one by one as they arrive

        Args:
            input_data: Same as ainvoke
            show_reasoning: If True and model supports it, enable chain-of-thought reasoning
            **kwargs: Additional parameters

        Yields:
            Individual tokens as they arrive from the API, plus final result with tool_calls
        """
        try:
            # Use adapter manager to prepare messages
            messages = self._prepare_messages(input_data)

            # Add reasoning configuration for gpt-oss-120b
            if show_reasoning and self.is_reasoning_model:
                messages = self._add_reasoning_instruction(messages, level="high")

            # Check if we have bound tools
            tool_schemas = await self._prepare_tools_for_request()
            has_tools = bool(tool_schemas)

            # Modify messages for tool calling emulation
            if has_tools:
                messages = self._create_tool_calling_prompt(messages, tool_schemas)

            # Prepare request kwargs
            provider_config = self.get_provider_config()

            # Stream tokens
            content_chunks = []

            try:
                stream = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    stream=True,
                    temperature=provider_config.get("temperature", 0.7),
                    max_tokens=provider_config.get("max_tokens", 1024),
                )

                for chunk in stream:
                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        content_chunks.append(content)

                        # Only stream content if no tools (tool responses should be complete JSON)
                        if not has_tools:
                            yield content

                # Process complete response
                full_content = "".join(content_chunks)

                # Parse for tool calls if tools are bound
                text_content, tool_calls = None, None
                if has_tools:
                    text_content, tool_calls = self._parse_tool_calling_response(full_content)
                else:
                    text_content = full_content

                # Track usage
                self._track_streaming_usage(messages, full_content)
                await asyncio.sleep(0.01)

                # Create response object
                if tool_calls:
                    # Create mock message with tool calls
                    class MockMessage:
                        def __init__(self):
                            self.content = text_content or ""
                            self.tool_calls = []
                            for tc in tool_calls:
                                mock_tc = type('MockToolCall', (), {
                                    'id': tc['id'],
                                    'function': type('MockFunction', (), {
                                        'name': tc['function']['name'],
                                        'arguments': tc['function']['arguments']
                                    })()
                                })()
                                self.tool_calls.append(mock_tc)

                    final_result = self._format_response(MockMessage(), input_data)
                else:
                    # Stream the content if we haven't already
                    if has_tools and text_content:
                        yield text_content
                    final_result = self._format_response(text_content or "", input_data)

                # Yield final result
                yield {
                    "result": final_result,
                    "billing": self._get_streaming_billing_info(),
                    "api_used": "cerebras"
                }

            except Exception as e:
                logger.error(f"Error in Cerebras streaming: {e}")
                raise

        except Exception as e:
            logger.error(f"Error in astream: {e}")
            raise

    async def ainvoke(self, input_data: Union[str, List[Dict[str, str]], Any], show_reasoning: bool = False, **kwargs) -> Union[str, Any]:
        """
        Unified invoke method for all input types with tool calling emulation

        Args:
            input_data: Input messages or text
            show_reasoning: If True and model supports it, enable chain-of-thought reasoning
            **kwargs: Additional parameters
        """
        try:
            # Extract user_id from kwargs for billing
            self._current_user_id = kwargs.get('user_id')

            # Use adapter manager to prepare messages
            messages = self._prepare_messages(input_data)

            # Add reasoning configuration for gpt-oss-120b
            if show_reasoning and self.is_reasoning_model:
                messages = self._add_reasoning_instruction(messages, level="high")

            # Check if we have bound tools
            tool_schemas = await self._prepare_tools_for_request()
            has_tools = bool(tool_schemas)

            # Modify messages for tool calling emulation
            if has_tools:
                messages = self._create_tool_calling_prompt(messages, tool_schemas)

            # Prepare request kwargs
            provider_config = self.get_provider_config()

            # Handle streaming vs non-streaming
            if self.streaming:
                # Streaming mode - collect all chunks
                content_chunks = []
                async for token in self.astream(input_data, show_reasoning=show_reasoning, **kwargs):
                    if isinstance(token, str):
                        content_chunks.append(token)
                    elif isinstance(token, dict) and "result" in token:
                        return token["result"]

                # Fallback
                content = "".join(content_chunks)
                return self._format_response(content, input_data)
            else:
                # Non-streaming mode
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=provider_config.get("temperature", 0.7),
                    max_tokens=provider_config.get("max_tokens", 1024),
                )

                content = response.choices[0].message.content or ""

                # Update usage tracking
                if response.usage:
                    self._update_token_usage(response.usage)
                    await self._track_billing(response.usage)

                # Parse for tool calls if tools are bound
                if has_tools:
                    text_content, tool_calls = self._parse_tool_calling_response(content)

                    if tool_calls:
                        # Create mock message with tool calls
                        class MockMessage:
                            def __init__(self):
                                self.content = text_content or ""
                                self.tool_calls = []
                                for tc in tool_calls:
                                    mock_tc = type('MockToolCall', (), {
                                        'id': tc['id'],
                                        'function': type('MockFunction', (), {
                                            'name': tc['function']['name'],
                                            'arguments': tc['function']['arguments']
                                        })()
                                    })()
                                    self.tool_calls.append(mock_tc)

                        return self._format_response(MockMessage(), input_data)

                # No tool calls, return content
                return self._format_response(content, input_data)

        except Exception as e:
            logger.error(f"Error in ainvoke: {e}")
            raise

    def _track_streaming_usage(self, messages: List[Dict[str, str]], content: str):
        """Track usage for streaming requests (estimated)"""
        class MockUsage:
            def __init__(self):
                self.prompt_tokens = len(str(messages)) // 4
                self.completion_tokens = len(content) // 4
                self.total_tokens = self.prompt_tokens + self.completion_tokens

        usage = MockUsage()
        self._update_token_usage(usage)

        # Fire and forget async tracking
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._track_billing(usage))
        except:
            pass

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

    async def _track_billing(self, usage):
        """Track billing information"""
        provider_config = self.get_provider_config()

        if self._current_user_id:
            await self._publish_billing_event(
                user_id=self._current_user_id,
                service_type=ServiceType.LLM,
                operation="chat",
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                metadata={
                    "temperature": provider_config.get("temperature", 0.7),
                    "max_tokens": provider_config.get("max_tokens", 1024),
                    "inference_speed": "ultra-fast"
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

        # Model specifications
        model_specs = {
            "llama-4-scout-17b-16e-instruct": {
                "params": "109B",
                "speed_tokens_per_sec": 2600,
                "description": "Llama 4 Scout - High performance instruction following"
            },
            "llama3.1-8b": {
                "params": "8B",
                "speed_tokens_per_sec": 2200,
                "description": "Llama 3.1 8B - Fast and efficient"
            },
            "llama-3.3-70b": {
                "params": "70B",
                "speed_tokens_per_sec": 2100,
                "description": "Llama 3.3 70B - Powerful reasoning"
            },
            "gpt-oss-120b": {
                "params": "120B",
                "speed_tokens_per_sec": 3000,
                "description": "OpenAI GPT OSS - Ultra-fast inference"
            },
            "qwen-3-32b": {
                "params": "32B",
                "speed_tokens_per_sec": 2600,
                "description": "Qwen 3 32B - Balanced performance"
            }
        }

        specs = model_specs.get(self.model_name, {
            "params": "Unknown",
            "speed_tokens_per_sec": 2000,
            "description": "Cerebras model"
        })

        return {
            "name": self.model_name,
            "max_tokens": provider_config.get("max_tokens", 1024),
            "supports_streaming": True,
            "supports_functions": True,  # Emulated via prompt engineering
            "supports_reasoning": self.is_reasoning_model,  # Native CoT for gpt-oss-120b
            "provider": "cerebras",
            "inference_speed_tokens_per_sec": specs["speed_tokens_per_sec"],
            "parameters": specs["params"],
            "description": specs["description"],
            "tool_calling_method": "emulated_via_prompt",
            "reasoning_method": "native_system_message" if self.is_reasoning_model else "none"
        }

    async def chat(
        self,
        input_data: Union[str, List[Dict[str, str]], Any],
        max_tokens: Optional[int] = None,
        show_reasoning: bool = False
    ) -> Dict[str, Any]:
        """
        Chat method that wraps ainvoke for compatibility with base class
        """
        try:
            response = await self.ainvoke(input_data)

            return {
                "message": response,
                "success": True,
                "metadata": {
                    "model": self.model_name,
                    "provider": self.provider_name,
                    "max_tokens": max_tokens or self.max_tokens,
                    "ultra_fast_inference": True
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
        # Cerebras SDK client doesn't have a close method
        pass

    def _get_streaming_billing_info(self) -> Dict[str, Any]:
        """Get billing information for streaming requests"""
        try:
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
                "currency": "USD"
            }
        except Exception as e:
            logger.warning(f"Failed to get streaming billing info: {e}")
            return {
                "cost_usd": 0.0,
                "error": str(e),
                "currency": "USD"
            }
