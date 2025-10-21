"""
Enhanced Inference Logger with required methods for ISA Model Client

Provides compatibility methods that were previously in InfluxDB logger
"""

import logging
from typing import Optional, Dict, Any


class InferenceLogger:
    """
    Wrapper for standard Python Logger with inference-specific methods
    
    Provides compatibility with ISA Model Client expectations while
    using Loki for centralized logging.
    """
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self.log_detailed_requests = False  # Set to True to log full request/response data
        
    def log_inference_start(
        self,
        request_id: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        task: Optional[str] = None,
        input_data: Optional[Any] = None,
        **kwargs
    ):
        """Log the start of an inference request"""
        msg = f"Inference started: {request_id}"
        if model:
            msg += f" | Model: {model}"
        if provider:
            msg += f" | Provider: {provider}"
        if task:
            msg += f" | Task: {task}"
        
        self._logger.info(msg)
        
    def log_inference_complete(
        self,
        request_id: str,
        status: str = "completed",
        execution_time_ms: Optional[int] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        cost_usd: Optional[float] = None,
        output_data: Optional[Any] = None,
        error_message: Optional[str] = None,
        error_code: Optional[str] = None,
        **kwargs
    ):
        """Log the completion of an inference request"""
        msg = f"Inference {status}: {request_id}"
        
        if execution_time_ms is not None:
            msg += f" | Time: {execution_time_ms}ms"
        if input_tokens or output_tokens or total_tokens:
            msg += f" | Tokens: in={input_tokens}, out={output_tokens}, total={total_tokens}"
        if cost_usd is not None:
            msg += f" | Cost: ${cost_usd:.6f}"
        if error_message:
            msg += f" | Error: {error_message}"
        if error_code:
            msg += f" | Code: {error_code}"
        
        if status == "failed":
            self._logger.error(msg)
        else:
            self._logger.info(msg)
    
    def log_token_usage(
        self,
        request_id: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        **kwargs
    ):
        """Log token usage for an inference request"""
        msg = f"Token usage for {request_id}: "
        msg += f"input={input_tokens}, output={output_tokens}, total={total_tokens}"
        self._logger.debug(msg)
    
    def log_error(
        self,
        request_id: str,
        error_message: str,
        error_type: Optional[str] = None,
        **kwargs
    ):
        """Log an error during inference"""
        msg = f"Error in {request_id}: {error_message}"
        if error_type:
            msg += f" | Type: {error_type}"
        self._logger.error(msg)
    
    # Delegate standard logging methods to underlying logger
    def debug(self, msg, *args, **kwargs):
        return self._logger.debug(msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        return self._logger.info(msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        return self._logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        return self._logger.error(msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        return self._logger.critical(msg, *args, **kwargs)
    
    def __getattr__(self, name):
        """Delegate any other attribute access to the underlying logger"""
        return getattr(self._logger, name)

