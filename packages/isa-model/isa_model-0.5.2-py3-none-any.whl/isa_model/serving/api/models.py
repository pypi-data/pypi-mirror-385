#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ISA Model API - Pydantic Models (OpenAI-Compatible)
===================================================

Standard request/response models aligned with OpenAI, Claude, Gemini, and Grok APIs.
Following best practices from major LLM providers for maximum compatibility.

References:
- OpenAI Chat Completions API: https://platform.openai.com/docs/api-reference/chat
- Anthropic Claude Messages API: https://docs.anthropic.com/claude/reference/messages
- Google Gemini API: https://ai.google.dev/gemini-api/docs
- xAI Grok API: https://docs.x.ai/docs

All models are OpenAI-compatible by default, with extensions for provider-specific features.
"""

from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field


# =============================================================================
# Base Models - Shared across all APIs
# =============================================================================

class CompletionUsage(BaseModel):
    """
    Token usage statistics (OpenAI-compatible)

    NOTE: Billing/cost is NOT included in API responses.
    Billing is handled separately via event-driven architecture (isa-common).
    Usage events are published to NATS and processed by the billing service.

    This matches the behavior of major providers (OpenAI, Anthropic, Google, xAI).
    """
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(..., description="Number of tokens in the completion")
    total_tokens: int = Field(..., description="Total tokens (prompt + completion)")

    # Optional detailed breakdowns (OpenAI extended fields)
    completion_tokens_details: Optional[Dict[str, Any]] = Field(None, description="Detailed completion token breakdown")
    prompt_tokens_details: Optional[Dict[str, Any]] = Field(None, description="Detailed prompt token breakdown")


# =============================================================================
# Chat Completion Models - Non-Streaming (OpenAI-Compatible)
# =============================================================================

class FunctionCall(BaseModel):
    """Function call information (deprecated, use tool_calls)"""
    name: str = Field(..., description="Function name")
    arguments: str = Field(..., description="Function arguments as JSON string")


class ChatCompletionMessageToolCall(BaseModel):
    """Tool call in a message"""
    id: str = Field(..., description="Tool call ID")
    type: Literal["function"] = Field("function", description="Tool type")
    function: FunctionCall = Field(..., description="Function call details")


class ChatCompletionMessage(BaseModel):
    """Message in a chat completion (OpenAI format)"""
    role: Literal["assistant", "user", "system", "tool", "function"] = Field(..., description="Message role")
    content: Optional[str] = Field(None, description="Message content")

    # Optional fields for advanced features
    refusal: Optional[str] = Field(None, description="Refusal message if model refuses")
    function_call: Optional[FunctionCall] = Field(None, description="[Deprecated] Function call")
    tool_calls: Optional[List[ChatCompletionMessageToolCall]] = Field(None, description="Tool calls made by model")
    audio: Optional[Dict[str, Any]] = Field(None, description="Audio response data")
    annotations: Optional[List[Dict[str, Any]]] = Field(None, description="Message annotations")


class ChatCompletionChoice(BaseModel):
    """A single choice in a chat completion"""
    index: int = Field(..., description="Choice index")
    message: ChatCompletionMessage = Field(..., description="Completion message")
    finish_reason: Optional[Literal["stop", "length", "tool_calls", "content_filter", "function_call"]] = Field(
        None,
        description="Why generation stopped"
    )
    logprobs: Optional[Dict[str, Any]] = Field(None, description="Log probabilities")


class ChatCompletion(BaseModel):
    """
    Chat completion response (OpenAI-compatible)

    This model matches OpenAI's ChatCompletion format and is compatible with:
    - OpenAI GPT models
    - xAI Grok models
    - Other OpenAI-compatible APIs
    """
    id: str = Field(..., description="Unique completion ID")
    object: Literal["chat.completion"] = Field("chat.completion", description="Object type")
    created: int = Field(..., description="Unix timestamp of creation")
    model: str = Field(..., description="Model used")
    choices: List[ChatCompletionChoice] = Field(..., description="Completion choices")

    # Optional fields
    usage: Optional[CompletionUsage] = Field(None, description="Token usage statistics")
    system_fingerprint: Optional[str] = Field(None, description="System configuration fingerprint")
    service_tier: Optional[str] = Field(None, description="Service tier used")

    # ISA Model extensions (not in OpenAI standard)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


# =============================================================================
# Chat Completion Chunk Models - Streaming (OpenAI-Compatible)
# =============================================================================

class ChoiceDeltaFunctionCall(BaseModel):
    """Function call delta in streaming"""
    name: Optional[str] = Field(None, description="Function name")
    arguments: Optional[str] = Field(None, description="Function arguments (partial)")


class ChoiceDeltaToolCall(BaseModel):
    """Tool call delta in streaming"""
    index: int = Field(..., description="Tool call index")
    id: Optional[str] = Field(None, description="Tool call ID")
    type: Optional[Literal["function"]] = Field(None, description="Tool type")
    function: Optional[ChoiceDeltaFunctionCall] = Field(None, description="Function details")


class ChoiceDelta(BaseModel):
    """
    Delta object in streaming chunks

    Contains incremental updates to the message being generated.
    Only the changed fields are included in each chunk.
    """
    role: Optional[Literal["developer", "system", "user", "assistant", "tool"]] = Field(None, description="Role (usually only in first chunk)")
    content: Optional[str] = Field(None, description="Content chunk (incremental text)")

    # Optional fields for advanced features
    refusal: Optional[str] = Field(None, description="Refusal chunk")
    function_call: Optional[ChoiceDeltaFunctionCall] = Field(None, description="[Deprecated] Function call delta")
    tool_calls: Optional[List[ChoiceDeltaToolCall]] = Field(None, description="Tool call deltas")
    audio: Optional[Dict[str, Any]] = Field(None, description="Audio delta")


class ChatCompletionChunkChoice(BaseModel):
    """A single choice in a streaming chunk"""
    index: int = Field(..., description="Choice index")
    delta: ChoiceDelta = Field(..., description="Incremental changes")
    finish_reason: Optional[Literal["stop", "length", "tool_calls", "content_filter", "function_call"]] = Field(
        None,
        description="Why generation stopped (only in final chunk)"
    )
    logprobs: Optional[Dict[str, Any]] = Field(None, description="Log probabilities")


class ChatCompletionChunk(BaseModel):
    """
    Streaming chunk response (OpenAI SSE format)

    Each chunk represents an incremental update in the Server-Sent Events stream.
    The delta field contains only the new/changed content since the last chunk.

    Example SSE format:
        data: {"id": "chatcmpl-123", "object": "chat.completion.chunk", ...}

        data: [DONE]
    """
    id: str = Field(..., description="Unique completion ID (same across all chunks)")
    object: Literal["chat.completion.chunk"] = Field("chat.completion.chunk", description="Object type")
    created: int = Field(..., description="Unix timestamp (same across all chunks)")
    model: str = Field(..., description="Model used")
    choices: List[ChatCompletionChunkChoice] = Field(..., description="Choice deltas")

    # Optional fields
    usage: Optional[CompletionUsage] = Field(None, description="Token usage (only in final chunk with stream_options)")
    system_fingerprint: Optional[str] = Field(None, description="System configuration fingerprint")
    service_tier: Optional[str] = Field(None, description="Service tier used")


# =============================================================================
# Request Models
# =============================================================================

class ChatMessage(BaseModel):
    """Message in a chat request"""
    role: Literal["system", "user", "assistant", "tool", "function"] = Field(..., description="Message role")
    content: Union[str, List[Dict[str, Any]]] = Field(..., description="Message content (text or multimodal)")
    name: Optional[str] = Field(None, description="Optional name for message author")
    tool_call_id: Optional[str] = Field(None, description="Tool call ID (for tool role)")
    tool_calls: Optional[List[ChatCompletionMessageToolCall]] = Field(None, description="Tool calls (for assistant)")


class FunctionDefinition(BaseModel):
    """Function definition for function calling"""
    name: str = Field(..., description="Function name")
    description: Optional[str] = Field(None, description="Function description")
    parameters: Optional[Dict[str, Any]] = Field(None, description="JSON schema for parameters")
    strict: Optional[bool] = Field(None, description="Require strict schema adherence")


class ToolDefinition(BaseModel):
    """Tool definition"""
    type: Literal["function"] = Field("function", description="Tool type")
    function: FunctionDefinition = Field(..., description="Function definition")


class ResponseFormat(BaseModel):
    """Response format specification"""
    type: Literal["text", "json_object", "json_schema"] = Field(..., description="Response format type")
    json_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for structured output")


class StreamOptions(BaseModel):
    """Streaming options"""
    include_usage: bool = Field(False, description="Include usage in final chunk")


class ChatCompletionRequest(BaseModel):
    """
    Chat completion request (OpenAI-compatible)

    Compatible with:
    - OpenAI Chat Completions API
    - xAI Grok API
    - Any OpenAI-compatible endpoint
    """
    model: str = Field(..., description="Model to use")
    messages: List[ChatMessage] = Field(..., description="Conversation messages")

    # Generation parameters
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nucleus sampling")
    n: Optional[int] = Field(1, ge=1, description="Number of completions to generate")
    stream: Optional[bool] = Field(False, description="Enable streaming")
    stream_options: Optional[StreamOptions] = Field(None, description="Streaming configuration")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum tokens to generate")
    max_completion_tokens: Optional[int] = Field(None, ge=1, description="Maximum completion tokens")

    # Advanced parameters
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Frequency penalty")
    logit_bias: Optional[Dict[str, float]] = Field(None, description="Token logit biases")
    logprobs: Optional[bool] = Field(None, description="Return log probabilities")
    top_logprobs: Optional[int] = Field(None, ge=0, le=20, description="Number of top logprobs")

    # Function calling & tools
    functions: Optional[List[FunctionDefinition]] = Field(None, description="[Deprecated] Available functions")
    function_call: Optional[Union[str, Dict[str, str]]] = Field(None, description="[Deprecated] Function call control")
    tools: Optional[List[ToolDefinition]] = Field(None, description="Available tools")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Tool choice control")
    parallel_tool_calls: Optional[bool] = Field(None, description="Allow parallel tool calls")

    # Response format
    response_format: Optional[ResponseFormat] = Field(None, description="Response format specification")

    # Other
    seed: Optional[int] = Field(None, description="Random seed for determinism")
    user: Optional[str] = Field(None, description="User identifier")
    service_tier: Optional[str] = Field(None, description="Service tier preference")

    # ISA Model extensions
    provider: Optional[str] = Field(None, description="Provider hint (openai, cerebras, yyds, etc.)")


# =============================================================================
# Unified API Models (ISA Model specific)
# =============================================================================

class UnifiedRequest(BaseModel):
    """
    Unified request format for ISA Model API

    This is our internal format that can handle all service types.
    It gets converted to provider-specific formats internally.
    """
    input_data: Union[str, List[Dict[str, Any]], Dict[str, Any]] = Field(..., description="Input data")
    task: str = Field(..., description="Task type (chat, analyze, generate, etc.)")
    service_type: str = Field(..., description="Service type (text, vision, audio, image, embedding)")

    # Model selection
    model: Optional[str] = Field(None, description="Model name")
    provider: Optional[str] = Field(None, description="Provider name")

    # Common parameters (mapped to provider-specific params)
    temperature: Optional[float] = Field(None, description="Temperature")
    max_tokens: Optional[int] = Field(None, description="Max tokens")
    stream: Optional[bool] = Field(False, description="Enable streaming")

    # Function calling
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Tools/functions")
    response_format: Optional[Dict[str, Any]] = Field(None, description="Response format")

    # Additional parameters (service-specific)
    voice: Optional[str] = Field(None, description="Voice for TTS")
    size: Optional[str] = Field(None, description="Size for image generation")
    quality: Optional[str] = Field(None, description="Quality setting")

    # Metadata
    user_id: Optional[str] = Field(None, description="User ID for tracking")


class UnifiedResponse(BaseModel):
    """
    Unified response format for ISA Model API

    This wraps provider responses in a consistent format while
    preserving provider-specific details in metadata.

    NOTE: Billing/cost information is NOT included in responses.
    Billing is handled via event-driven architecture (isa-common),
    matching the pattern used by AWS, OpenAI, and other major cloud providers.
    """
    success: bool = Field(..., description="Whether request succeeded")
    result: Optional[Any] = Field(None, description="Result data (format varies by service)")
    error: Optional[str] = Field(None, description="Error message if failed")

    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    # Common metadata fields (embedded in metadata dict for flexibility)
    request_id: Optional[str] = Field(None, description="Request ID")
    model_used: Optional[str] = Field(None, description="Actual model used")
    provider: Optional[str] = Field(None, description="Provider used")
    task: Optional[str] = Field(None, description="Task performed")
    service_type: Optional[str] = Field(None, description="Service type")
    execution_time_ms: Optional[float] = Field(None, description="Execution time in milliseconds")

    # Usage statistics (token counts only, no billing/cost)
    usage: Optional[CompletionUsage] = Field(None, description="Token usage statistics")


# =============================================================================
# Embedding Models (OpenAI-Compatible)
# =============================================================================

class EmbeddingObject(BaseModel):
    """Single embedding object"""
    object: Literal["embedding"] = Field("embedding", description="Object type")
    embedding: List[float] = Field(..., description="Embedding vector")
    index: int = Field(..., description="Index in batch")


class EmbeddingResponse(BaseModel):
    """Embedding response (OpenAI-compatible)"""
    object: Literal["list"] = Field("list", description="Object type")
    data: List[EmbeddingObject] = Field(..., description="Embedding objects")
    model: str = Field(..., description="Model used")
    usage: CompletionUsage = Field(..., description="Token usage")


# =============================================================================
# Audio Models (OpenAI-Compatible)
# =============================================================================

class TranscriptionResponse(BaseModel):
    """Speech-to-text response"""
    text: str = Field(..., description="Transcribed text")
    language: Optional[str] = Field(None, description="Detected language")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")
    segments: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed segments")


# =============================================================================
# Image Models (OpenAI-Compatible)
# =============================================================================

class ImageObject(BaseModel):
    """Single generated image"""
    url: Optional[str] = Field(None, description="Image URL")
    b64_json: Optional[str] = Field(None, description="Base64 encoded image")
    revised_prompt: Optional[str] = Field(None, description="Revised prompt used")


class ImageGenerationResponse(BaseModel):
    """Image generation response (OpenAI-compatible)"""
    created: int = Field(..., description="Unix timestamp")
    data: List[ImageObject] = Field(..., description="Generated images")


# Export all models
__all__ = [
    # Base models
    "CompletionUsage",

    # Chat completion (non-streaming)
    "ChatCompletionMessage",
    "ChatCompletionChoice",
    "ChatCompletion",

    # Chat completion chunk (streaming)
    "ChoiceDelta",
    "ChatCompletionChunkChoice",
    "ChatCompletionChunk",

    # Request models
    "ChatMessage",
    "ChatCompletionRequest",
    "ToolDefinition",
    "FunctionDefinition",
    "ResponseFormat",
    "StreamOptions",

    # Unified models
    "UnifiedRequest",
    "UnifiedResponse",

    # Other service models
    "EmbeddingResponse",
    "EmbeddingObject",
    "TranscriptionResponse",
    "ImageGenerationResponse",
    "ImageObject",
]
