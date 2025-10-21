from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, Callable, AsyncGenerator
from enum import Enum
import asyncio
from isa_model.inference.services.base_service import BaseService


class RealtimeEventType(Enum):
    """Realtime API event types"""
    # Session events
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"
    
    # Input audio events
    INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"
    INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer.commit"
    INPUT_AUDIO_BUFFER_CLEAR = "input_audio_buffer.clear"
    INPUT_AUDIO_BUFFER_COMMITTED = "input_audio_buffer.committed"
    INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"
    INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"
    
    # Conversation events
    CONVERSATION_ITEM_CREATE = "conversation.item.create"
    CONVERSATION_ITEM_CREATED = "conversation.item.created"
    CONVERSATION_ITEM_DELETE = "conversation.item.delete"
    CONVERSATION_ITEM_DELETED = "conversation.item.deleted"
    CONVERSATION_ITEM_TRUNCATE = "conversation.item.truncate"
    CONVERSATION_ITEM_TRUNCATED = "conversation.item.truncated"
    
    # Response events
    RESPONSE_CREATE = "response.create"
    RESPONSE_CREATED = "response.created"
    RESPONSE_DONE = "response.done"
    RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
    RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
    RESPONSE_CONTENT_PART_ADDED = "response.content_part.added"
    RESPONSE_CONTENT_PART_DONE = "response.content_part.done"
    RESPONSE_TEXT_DELTA = "response.text.delta"
    RESPONSE_TEXT_DONE = "response.text.done"
    RESPONSE_AUDIO_TRANSCRIPT_DELTA = "response.audio_transcript.delta"
    RESPONSE_AUDIO_TRANSCRIPT_DONE = "response.audio_transcript.done"
    RESPONSE_AUDIO_DELTA = "response.audio.delta"
    RESPONSE_AUDIO_DONE = "response.audio.done"
    RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA = "response.function_call_arguments.delta"
    RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE = "response.function_call_arguments.done"
    
    # Rate limit events
    RATE_LIMITS_UPDATED = "rate_limits.updated"
    
    # Error events
    ERROR = "error"


class BaseRealtimeService(BaseService):
    """Base class for Realtime API services"""
    
    def __init__(self, provider_name: str, model_name: str, **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        self.session_id: Optional[str] = None
        self.websocket = None
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.is_connected = False
        
    async def invoke(
        self, 
        task: str,
        **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        统一的任务分发方法 - 支持实时对话任务
        
        Args:
            task: 任务类型，支持多种实时对话任务
            **kwargs: 任务特定的附加参数
            
        Returns:
            Dict containing task results
        """
        if task == "create_session":
            return await self.create_session(**kwargs)
        elif task == "connect":
            return await self.connect_websocket(**kwargs)
        elif task == "send_audio":
            if not kwargs.get("audio_data"):
                raise ValueError("audio_data is required for send_audio task")
            return await self.send_audio_message(kwargs["audio_data"], **kwargs)
        elif task == "send_text":
            if not kwargs.get("text"):
                raise ValueError("text is required for send_text task")
            return await self.send_text_message(kwargs["text"], **kwargs)
        elif task == "listen":
            return await self.listen_for_responses(**kwargs)
        elif task == "audio_chat":
            return await self.simple_audio_chat(**kwargs)
        elif task == "text_chat":
            return await self.simple_text_chat(**kwargs)
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support task: {task}")
    
    def get_supported_tasks(self) -> List[str]:
        """获取支持的任务列表"""
        return [
            "create_session", "connect", "send_audio", "send_text", 
            "listen", "audio_chat", "text_chat"
        ]
    
    @abstractmethod
    async def create_session(
        self, 
        instructions: str = "You are a helpful assistant.",
        modalities: Optional[List[str]] = None,
        voice: str = "alloy",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new realtime session"""
        pass
    
    @abstractmethod
    async def connect_websocket(self, **kwargs) -> bool:
        """Connect to the realtime WebSocket"""
        pass
    
    @abstractmethod
    async def send_audio_message(
        self, 
        audio_data: bytes,
        format: str = "pcm16",
        **kwargs
    ) -> Dict[str, Any]:
        """Send audio data to the realtime session"""
        pass
    
    @abstractmethod
    async def send_text_message(
        self, 
        text: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Send text message to the realtime session"""
        pass
    
    @abstractmethod
    async def listen_for_responses(
        self,
        message_handler: Optional[Callable] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Listen for responses from the realtime session"""
        pass
    
    @abstractmethod
    async def simple_audio_chat(
        self, 
        audio_data: bytes, 
        instructions: str = "You are a helpful assistant. Respond in audio.",
        voice: str = "alloy",
        **kwargs
    ) -> Dict[str, Any]:
        """Simple audio chat - send audio, get audio response"""
        pass
    
    @abstractmethod
    async def simple_text_chat(
        self, 
        text: str, 
        instructions: str = "You are a helpful assistant.",
        voice: str = "alloy",
        **kwargs
    ) -> Dict[str, Any]:
        """Simple text chat - send text, get audio/text response"""
        pass
    
    def add_event_handler(self, event_type: Union[str, RealtimeEventType], handler: Callable):
        """Add event handler for specific event type"""
        event_name = event_type.value if isinstance(event_type, RealtimeEventType) else event_type
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
    
    def remove_event_handler(self, event_type: Union[str, RealtimeEventType], handler: Callable):
        """Remove event handler"""
        event_name = event_type.value if isinstance(event_type, RealtimeEventType) else event_type
        if event_name in self.event_handlers:
            self.event_handlers[event_name].remove(handler)
    
    async def _handle_event(self, event: Dict[str, Any]):
        """Handle incoming events"""
        event_type = event.get("type")
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(f"Error in event handler for {event_type}: {e}")
    
    @abstractmethod
    def get_supported_voices(self) -> List[str]:
        """Get list of supported voice options"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        pass
    
    @abstractmethod
    def get_session_limits(self) -> Dict[str, Any]:
        """Get session limits and constraints"""
        pass
    
    @abstractmethod
    async def update_session(self, **kwargs) -> Dict[str, Any]:
        """Update session configuration"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the realtime session"""
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass