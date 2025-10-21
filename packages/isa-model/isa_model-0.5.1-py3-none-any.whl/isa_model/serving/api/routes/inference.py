"""
Inference API Route - Direct AI Service Access
===============================================

Clean architecture:
- Uses AIFactory directly (no ISAModelClient middleman)
- OpenAI-compatible responses with SSE streaming
- Event-driven billing via isa-common (no cost in responses)
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
import logging
import json
import time
import uuid

# Direct AI service access
from isa_model.inference.ai_factory import AIFactory

# OpenAI-compatible Pydantic models
from ..models import (
    UnifiedRequest,
    UnifiedResponse,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChoiceDelta,
    CompletionUsage
)

# Middleware
from ..middleware.auth import require_read_access
from ..middleware.security import rate_limit_standard, sanitize_input

logger = logging.getLogger(__name__)
router = APIRouter()

# Valid providers
VALID_PROVIDERS = {"openai", "yyds", "cerebras", "ollama", "isa", "replicate", "anthropic"}

# Global AI Factory instance
_ai_factory = None


def get_ai_factory() -> AIFactory:
    """Get or create AI Factory singleton"""
    global _ai_factory
    if _ai_factory is None:
        _ai_factory = AIFactory()
    return _ai_factory


# =============================================================================
# Helper Functions
# =============================================================================

def should_stream(service_type: str, task: str, stream: bool, has_tools: bool) -> bool:
    """Determine if response should be streamed"""
    is_text_chat = (service_type == "text" and task == "chat")
    return is_text_chat and not has_tools and stream


async def stream_llm_tokens(
    factory: AIFactory,
    input_data,
    model: str,
    provider: str,
    user_id: str,
    **kwargs
):
    """Stream LLM tokens"""
    llm_service = factory.get_llm(model_name=model, provider=provider)
    llm_service._current_user_id = user_id

    # Use astream method (correct method name)
    async for token in llm_service.astream(input_data, **kwargs):
        yield token


async def generate_openai_sse_stream(
    factory: AIFactory,
    request: UnifiedRequest,
    user_id: str,
    params: dict
):
    """Generate OpenAI-compatible SSE stream"""
    chunk_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created_ts = int(time.time())
    model_used = request.model or "unknown"

    async def stream_generator():
        try:
            token_count = 0

            # Stream tokens
            async for item in stream_llm_tokens(
                factory,
                request.input_data,
                request.model,
                request.provider,
                user_id,
                **params
            ):
                # astream yields Union[str, Dict] - handle both
                if isinstance(item, str):
                    # Token chunk
                    token_count += 1
                    chunk = ChatCompletionChunk(
                        id=chunk_id,
                        object="chat.completion.chunk",
                        created=created_ts,
                        model=model_used,
                        choices=[
                            ChatCompletionChunkChoice(
                                index=0,
                                delta=ChoiceDelta(content=item),
                                finish_reason=None
                            )
                        ]
                    )
                    yield f"data: {chunk.model_dump_json()}\n\n"
                else:
                    # Final result dict (with tool_calls, etc.) - skip for now
                    logger.debug(f"Skipping non-string item in stream: {type(item)}")
                    continue

            # Final chunk
            final_chunk = ChatCompletionChunk(
                id=chunk_id,
                object="chat.completion.chunk",
                created=created_ts,
                model=model_used,
                choices=[
                    ChatCompletionChunkChoice(
                        index=0,
                        delta=ChoiceDelta(),
                        finish_reason="stop"
                    )
                ],
                usage=CompletionUsage(
                    prompt_tokens=0,
                    completion_tokens=token_count,
                    total_tokens=token_count
                )
            )
            yield f"data: {final_chunk.model_dump_json()}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            error_chunk = {
                "id": chunk_id,
                "object": "error",
                "error": {"message": str(e), "type": "server_error"}
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"

        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/")
async def api_info():
    """API information"""
    return {
        "service": "inference_api",
        "version": "2.0.0",
        "architecture": "direct_ai_factory_access",
        "features": [
            "OpenAI-compatible streaming (SSE)",
            "Event-driven billing (isa-common)",
            "Multi-provider support",
            "No ISAModelClient middleman"
        ],
        "supported_services": ["text", "vision", "audio", "image", "embedding"]
    }


@router.post("/invoke")
@rate_limit_standard()
async def invoke_ai_service(
    request: Request,
    user: dict = Depends(require_read_access)
):
    """
    Main inference endpoint - calls AI services directly via AIFactory

    OpenAI-compatible format:
    - Streaming: SSE with ChatCompletionChunk
    - Non-streaming: Standard JSON response
    - Billing: Event-driven (no cost in response)
    """
    try:
        factory = get_ai_factory()

        # Parse and validate request
        json_body = await request.json()
        req = UnifiedRequest(**json_body)

        # Sanitize inputs
        if isinstance(req.input_data, str):
            req.input_data = sanitize_input(req.input_data)

        # Validate provider
        if req.provider and req.provider not in VALID_PROVIDERS:
            return UnifiedResponse(
                success=False,
                error=f"Invalid provider: {req.provider}",
                metadata={"valid_providers": sorted(VALID_PROVIDERS)}
            )

        # Build params dict from individual request fields (OpenAI-style)
        params = {}
        if req.temperature is not None:
            params["temperature"] = req.temperature
        if req.max_tokens is not None:
            params["max_tokens"] = req.max_tokens
        if req.response_format is not None:
            params["response_format"] = req.response_format
        if req.tools is not None:
            params["tools"] = req.tools

        # Get user_id from auth user or request body (for testing)
        user_id = user.get("user_id") if user else None
        if not user_id and req.user_id:
            user_id = req.user_id

        # TEXT/LLM SERVICE
        if req.service_type == "text":
            # Check if streaming
            if should_stream(req.service_type, req.task, req.stream, bool(req.tools)):
                return await generate_openai_sse_stream(factory, req, user_id, params)

            # Non-streaming
            llm_service = factory.get_llm(model_name=req.model, provider=req.provider)
            llm_service._current_user_id = user_id

            # Use ainvoke (standard async method)
            result = await llm_service.ainvoke(req.input_data, **params)

            return UnifiedResponse(
                success=True,
                result=result,
                metadata={
                    "model_used": req.model,
                    "provider": req.provider,
                    "service_type": "text",
                    "task": req.task
                }
            )

        # VISION SERVICE
        elif req.service_type == "vision":
            vision_service = factory.get_vision(model_name=req.model, provider=req.provider)
            vision_service._current_user_id = user_id

            result = await vision_service.analyze_image(req.input_data, **params)

            return UnifiedResponse(
                success=True,
                result=result,
                metadata={
                    "model_used": req.model,
                    "provider": req.provider,
                    "service_type": "vision"
                }
            )

        # AUDIO - TTS
        elif req.service_type == "audio" and req.task == "tts":
            tts_service = factory.get_tts(model_name=req.model, provider=req.provider)
            tts_service._current_user_id = user_id

            result = await tts_service.invoke(text=req.input_data, task=req.task, **params)

            return UnifiedResponse(
                success=True,
                result=result,
                metadata={
                    "model_used": req.model,
                    "provider": req.provider,
                    "service_type": "audio",
                    "task": "tts"
                }
            )

        # AUDIO - STT
        elif req.service_type == "audio" and req.task == "stt":
            stt_service = factory.get_stt(model_name=req.model, provider=req.provider)
            stt_service._current_user_id = user_id

            result = await stt_service.invoke(audio_input=req.input_data, task=req.task, **params)

            return UnifiedResponse(
                success=True,
                result=result,
                metadata={
                    "model_used": req.model,
                    "provider": req.provider,
                    "service_type": "audio",
                    "task": "stt"
                }
            )

        # IMAGE GENERATION
        elif req.service_type == "image":
            img_service = factory.get_img(type="t2i", model_name=req.model, provider=req.provider)
            img_service._current_user_id = user_id

            result = await img_service.invoke(prompt=req.input_data, task=req.task, **params)

            return UnifiedResponse(
                success=True,
                result=result,
                metadata={
                    "model_used": req.model,
                    "provider": req.provider,
                    "service_type": "image"
                }
            )

        # EMBEDDING
        elif req.service_type == "embedding":
            embed_service = factory.get_embed(model_name=req.model, provider=req.provider)
            embed_service._current_user_id = user_id

            result = await embed_service.invoke(input_data=req.input_data, task=req.task, **params)

            return UnifiedResponse(
                success=True,
                result=result,
                metadata={
                    "model_used": req.model,
                    "provider": req.provider,
                    "service_type": "embedding"
                }
            )

        else:
            return UnifiedResponse(
                success=False,
                error=f"Unsupported service_type: {req.service_type}",
                metadata={}
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Inference failed: {e}", exc_info=True)
        return UnifiedResponse(
            success=False,
            error=str(e),
            metadata={"error_type": type(e).__name__}
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        factory = get_ai_factory()
        return {
            "status": "healthy",
            "version": "2.0.0",
            "architecture": "direct_ai_factory"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/models")
async def list_models(service_type: str = None):
    """List available models"""
    try:
        # TODO: Add Redis caching here using isa_common
        models = [
            {"service_type": "text", "provider": "openai", "model_id": "gpt-4o-mini"},
            {"service_type": "text", "provider": "openai", "model_id": "gpt-4o"},
            {"service_type": "text", "provider": "cerebras", "model_id": "gpt-oss-120b"},
            {"service_type": "text", "provider": "yyds", "model_id": "gpt-5"},
            {"service_type": "vision", "provider": "openai", "model_id": "gpt-4o-mini"},
            {"service_type": "audio", "provider": "openai", "model_id": "whisper-1"},
            {"service_type": "audio", "provider": "openai", "model_id": "tts-1"},
            {"service_type": "embedding", "provider": "openai", "model_id": "text-embedding-3-small"},
            {"service_type": "image", "provider": "replicate", "model_id": "flux-1.1-pro"}
        ]

        if service_type:
            models = [m for m in models if m["service_type"] == service_type]

        return {
            "success": True,
            "models": models,
            "total_count": len(models),
            "service_type_filter": service_type
        }
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return {
            "success": False,
            "error": str(e),
            "models": []
        }
