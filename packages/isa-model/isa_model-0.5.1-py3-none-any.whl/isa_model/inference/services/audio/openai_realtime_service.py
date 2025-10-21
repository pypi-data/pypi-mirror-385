import logging
import json
import asyncio
import base64
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from isa_model.inference.services.audio.base_realtime_service import BaseRealtimeService, RealtimeEventType
from isa_model.core.types import ServiceType

logger = logging.getLogger(__name__)

class OpenAIRealtimeService(BaseRealtimeService):
    """
    OpenAI Realtime API service for real-time audio conversations.
    Uses gpt-4o-mini-realtime-preview model for interactive audio chat.
    """
    
    def __init__(self, provider_name: str = "openai", model_name: str = "gpt-4o-realtime-preview-2024-10-01", **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        
        provider_config = self.get_provider_config()
        self.api_key = provider_config.get('api_key') or self.get_api_key()
        self.base_url = provider_config.get('api_base_url', 'https://api.openai.com/v1')
        self.websocket_url = f"wss://api.openai.com/v1/realtime?model={self.model_name}"
        
        # Default session configuration based on latest API
        self.default_config = {
            "modalities": ["text", "audio"],
            "instructions": "You are a helpful assistant.",
            "voice": "alloy",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "whisper-1"
            },
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 200
            },
            "tools": [],
            "tool_choice": "auto",
            "temperature": 0.8,
            "max_response_output_tokens": "inf"
        }
        
        # Session limits based on API documentation
        self.session_limits = {
            "max_context_tokens": 128000,
            "max_session_time_minutes": 15,
            "audio_tokens_per_minute": 800
        }
        
        logger.info(f"Initialized OpenAIRealtimeService with model '{self.model_name}'")
        
        # Add default event handlers for common events
        self._setup_default_handlers()
    
    async def create_session(
        self,
        instructions: str = "You are a helpful assistant.",
        modalities: Optional[List[str]] = None,
        voice: str = "alloy",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new realtime session"""
        try:
            # Extract user_id from kwargs for billing
            self._current_user_id = kwargs.pop('user_id', None)

            # Prepare session configuration
            session_config = self.default_config.copy()
            session_config.update({
                "instructions": instructions,
                "modalities": modalities if modalities is not None else ["text", "audio"],
                "voice": voice,
                **kwargs
            })

            # Store session config for WebSocket connection
            self.session_config = session_config

            # Generate a session ID (WebSocket-based, no REST endpoint)
            import uuid
            self.session_id = str(uuid.uuid4())

            # Track session creation for billing
            if self._current_user_id:
                await self._publish_billing_event(
                    user_id=self._current_user_id,
                    service_type=ServiceType.AUDIO_REALTIME,
                    operation="create_session",
                    metadata={
                        "session_id": self.session_id,
                        "model": self.model_name,
                        "modalities": session_config["modalities"]
                    }
                )
            
            return {
                "id": self.session_id,
                "model": self.model_name,
                "modalities": session_config["modalities"],
                "instructions": instructions,
                "voice": voice,
                "status": "created"
            }
                        
        except Exception as e:
            logger.error(f"Error creating realtime session: {e}")
            raise
    
    async def connect_websocket(self, **kwargs) -> bool:
        """Connect to the realtime WebSocket"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            self.client_session = aiohttp.ClientSession()
            self.websocket = await self.client_session.ws_connect(
                self.websocket_url, 
                headers=headers
            )
            
            # Send session.update event to configure the session
            if hasattr(self, 'session_config'):
                await self._send_event({
                    "type": "session.update",
                    "session": self.session_config
                })
            
            self.is_connected = True
            logger.info(f"Connected to realtime WebSocket with model {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to WebSocket: {e}")
            self.is_connected = False
            raise
    
    async def send_audio_message(
        self, 
        audio_data: bytes,
        format: str = "pcm16",
        **kwargs
    ) -> Dict[str, Any]:
        """Send audio data to the realtime session"""
        try:
            if not self.is_connected or not self.websocket:
                raise RuntimeError("WebSocket not connected")
                
            # Convert audio data to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Send audio buffer append event
            await self._send_event({
                "type": RealtimeEventType.INPUT_AUDIO_BUFFER_APPEND.value,
                "audio": audio_base64
            })
            
            # Commit the audio buffer
            await self._send_event({
                "type": RealtimeEventType.INPUT_AUDIO_BUFFER_COMMIT.value
            })
            
            return {
                "status": "sent",
                "audio_size_bytes": len(audio_data),
                "format": format
            }
            
        except Exception as e:
            logger.error(f"Error sending audio message: {e}")
            raise
    
    async def send_text_message(
        self, 
        text: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Send text message to the realtime session"""
        try:
            if not self.is_connected or not self.websocket:
                raise RuntimeError("WebSocket not connected")
                
            # Create conversation item
            await self._send_event({
                "type": RealtimeEventType.CONVERSATION_ITEM_CREATE.value,
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": text
                        }
                    ]
                }
            })
            
            # Trigger response creation
            await self._send_event({
                "type": RealtimeEventType.RESPONSE_CREATE.value
            })
            
            return {
                "status": "sent",
                "text": text,
                "message_length": len(text)
            }
            
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
            raise
    
    async def listen_for_responses(
        self,
        message_handler: Optional[Callable] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Listen for responses from the realtime session"""
        try:
            if not self.is_connected or not self.websocket:
                raise RuntimeError("WebSocket not connected")
                
            async for msg in self.websocket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        event = json.loads(msg.data)
                        event_type = event.get("type")
                        
                        # Handle built-in event processing
                        await self._handle_event(event)
                        
                        # Yield specific response types
                        if event_type == RealtimeEventType.RESPONSE_AUDIO_DELTA.value:
                            audio_data = event.get("delta", "")
                            yield {
                                "type": "audio_delta",
                                "data": audio_data,
                                "format": "pcm16",
                                "raw_event": event
                            }
                        elif event_type == RealtimeEventType.RESPONSE_TEXT_DELTA.value:
                            text_data = event.get("delta", "")
                            yield {
                                "type": "text_delta",
                                "data": text_data,
                                "raw_event": event
                            }
                        elif event_type == RealtimeEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA.value:
                            transcript_data = event.get("delta", "")
                            yield {
                                "type": "transcript_delta",
                                "data": transcript_data,
                                "raw_event": event
                            }
                        elif event_type == RealtimeEventType.RESPONSE_DONE.value:
                            # Response completed
                            response = event.get("response", {})
                            usage = response.get("usage", {})

                            # Track usage for billing
                            if self._current_user_id:
                                await self._publish_billing_event(
                                    user_id=self._current_user_id,
                                    service_type=ServiceType.AUDIO_REALTIME,
                                    operation="realtime_response",
                                    input_tokens=usage.get("input_tokens", 0),
                                    output_tokens=usage.get("output_tokens", 0),
                                    metadata={
                                        "response_id": response.get("id"),
                                        "model": self.model_name,
                                        "status": response.get("status")
                                    }
                                )
                            
                            yield {
                                "type": "response_done",
                                "response": response,
                                "usage": usage,
                                "raw_event": event
                            }
                        elif event_type == RealtimeEventType.ERROR.value:
                            logger.error(f"Realtime API error: {event}")
                            yield {
                                "type": "error",
                                "error": event.get("error", {}),
                                "raw_event": event
                            }
                        
                        # Call custom message handler if provided
                        if message_handler:
                            await message_handler(event)
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing WebSocket message: {e}")
                        continue
                        
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {self.websocket.exception()}")
                    yield {
                        "type": "websocket_error",
                        "error": str(self.websocket.exception())
                    }
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    logger.info("WebSocket connection closed")
                    self.is_connected = False
                    break
                    
        except Exception as e:
            logger.error(f"Error listening for responses: {e}")
            raise
    
    async def simple_audio_chat(
        self, 
        audio_data: bytes, 
        instructions: str = "You are a helpful assistant. Respond in audio.",
        voice: str = "alloy",
        **kwargs
    ) -> Dict[str, Any]:
        """Simple audio chat - send audio, get audio response"""
        try:
            # Create session
            session = await self.create_session(
                instructions=instructions,
                modalities=["audio"],
                voice=voice
            )
            session_id = session["id"]
            
            # Connect to WebSocket
            await self.connect_websocket()
            
            try:
                # Send audio
                await self.send_audio_message(audio_data)
                
                # Collect response
                audio_chunks = []
                transcript_chunks = []
                usage_info = {}
                
                async for response in self.listen_for_responses():
                    if response["type"] == "audio_delta":
                        audio_chunks.append(response["data"])
                    elif response["type"] == "transcript_delta":
                        transcript_chunks.append(response["data"])
                    elif response["type"] == "response_done":
                        usage_info = response["usage"]
                        break
                    elif response["type"] == "error":
                        raise Exception(f"Realtime API error: {response['error']}")
                
                # Combine chunks
                full_audio = "".join(audio_chunks)
                full_transcript = "".join(transcript_chunks)
                
                return {
                    "audio_response": full_audio,
                    "transcript": full_transcript,
                    "session_id": session_id,
                    "usage": usage_info,
                    "format": "pcm16"
                }
                
            finally:
                await self.disconnect()
                
        except Exception as e:
            logger.error(f"Error in simple audio chat: {e}")
            raise
    
    async def simple_text_chat(
        self, 
        text: str, 
        instructions: str = "You are a helpful assistant.",
        voice: str = "alloy",
        **kwargs
    ) -> Dict[str, Any]:
        """Simple text chat - send text, get audio/text response"""
        try:
            # Create session
            session = await self.create_session(
                instructions=instructions,
                modalities=["text", "audio"],
                voice=voice
            )
            session_id = session["id"]
            
            # Connect to WebSocket
            await self.connect_websocket()
            
            try:
                # Send text
                await self.send_text_message(text)
                
                # Collect response
                text_response = ""
                audio_chunks = []
                transcript_chunks = []
                usage_info = {}
                
                async for response in self.listen_for_responses():
                    if response["type"] == "text_delta":
                        text_response += response["data"]
                    elif response["type"] == "audio_delta":
                        audio_chunks.append(response["data"])
                    elif response["type"] == "transcript_delta":
                        transcript_chunks.append(response["data"])
                    elif response["type"] == "response_done":
                        usage_info = response["usage"]
                        break
                    elif response["type"] == "error":
                        raise Exception(f"Realtime API error: {response['error']}")
                
                # Combine chunks
                full_audio = "".join(audio_chunks)
                full_transcript = "".join(transcript_chunks)
                
                return {
                    "text_response": text_response,
                    "audio_response": full_audio,
                    "transcript": full_transcript,
                    "session_id": session_id,
                    "usage": usage_info,
                    "format": "pcm16"
                }
                
            finally:
                await self.disconnect()
                
        except Exception as e:
            logger.error(f"Error in simple text chat: {e}")
            raise
    
    def get_supported_voices(self) -> List[str]:
        """Get list of supported voice options"""
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return ["pcm16", "g711_ulaw", "g711_alaw"]
    
    def get_session_limits(self) -> Dict[str, Any]:
        """Get session limits and constraints"""
        return self.session_limits.copy()
    
    async def update_session(self, **kwargs) -> Dict[str, Any]:
        """Update session configuration"""
        try:
            if not self.is_connected or not self.websocket:
                raise RuntimeError("WebSocket not connected")
                
            # Update session config
            session_update = {k: v for k, v in kwargs.items() if k in self.default_config}
            
            if session_update:
                await self._send_event({
                    "type": "session.update",
                    "session": session_update
                })
                
                # Update local config
                if hasattr(self, 'session_config'):
                    self.session_config.update(session_update)
            
            return {
                "status": "updated",
                "updated_fields": list(session_update.keys())
            }
            
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the realtime session"""
        try:
            if self.websocket and not self.websocket.closed:
                await self.websocket.close()
            
            if hasattr(self, 'client_session') and self.client_session:
                await self.client_session.close()
                
            self.is_connected = False
            self.websocket = None
            
            logger.info("Disconnected from realtime session")
            
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
    
    async def _send_event(self, event: Dict[str, Any]):
        """Send an event to the WebSocket"""
        if not self.websocket or self.websocket.closed:
            raise RuntimeError("WebSocket not connected")
            
        event_json = json.dumps(event)
        await self.websocket.send_str(event_json)
        logger.debug(f"Sent event: {event.get('type')}")
    
    def _setup_default_handlers(self):
        """Setup default event handlers for common events"""
        
        async def handle_session_created(event):
            logger.info(f"Session created: {event.get('session', {}).get('id')}")
            
        async def handle_session_updated(event):
            logger.info(f"Session updated: {event.get('session', {})}")
            
        async def handle_input_audio_buffer_committed(event):
            logger.debug(f"Audio buffer committed: {event.get('item_id', 'unknown')}")
            
        async def handle_input_audio_buffer_speech_started(event):
            logger.debug(f"Speech started: {event.get('audio_start_ms', 0)}ms")
            
        async def handle_input_audio_buffer_speech_stopped(event):
            logger.debug(f"Speech stopped: {event.get('audio_end_ms', 0)}ms")
            
        async def handle_conversation_item_created(event):
            item = event.get('item', {})
            logger.debug(f"Conversation item created: {item.get('type')} - {item.get('id')}")
            
        async def handle_response_created(event):
            response = event.get('response', {})
            logger.debug(f"Response created: {response.get('id')}")
            
        async def handle_rate_limits_updated(event):
            limits = event.get('rate_limits', [])
            logger.debug(f"Rate limits updated: {limits}")
            
        async def handle_error(event):
            error = event.get('error', {})
            logger.error(f"Realtime API error: {error.get('message')} (Code: {error.get('code')})")
        
        # Register default handlers
        self.add_event_handler(RealtimeEventType.SESSION_CREATED, handle_session_created)
        self.add_event_handler(RealtimeEventType.SESSION_UPDATED, handle_session_updated)
        self.add_event_handler(RealtimeEventType.INPUT_AUDIO_BUFFER_COMMITTED, handle_input_audio_buffer_committed)
        self.add_event_handler(RealtimeEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED, handle_input_audio_buffer_speech_started)
        self.add_event_handler(RealtimeEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED, handle_input_audio_buffer_speech_stopped)
        self.add_event_handler(RealtimeEventType.CONVERSATION_ITEM_CREATED, handle_conversation_item_created)
        self.add_event_handler(RealtimeEventType.RESPONSE_CREATED, handle_response_created)
        self.add_event_handler(RealtimeEventType.RATE_LIMITS_UPDATED, handle_rate_limits_updated)
        self.add_event_handler(RealtimeEventType.ERROR, handle_error)
    
    async def close(self):
        """Cleanup resources"""
        await self.disconnect() 