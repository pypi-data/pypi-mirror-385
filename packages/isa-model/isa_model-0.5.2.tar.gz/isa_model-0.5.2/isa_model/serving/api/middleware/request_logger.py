"""
Request Logger Middleware

Logs all incoming requests and responses for monitoring
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import json
from typing import Callable

logger = logging.getLogger(__name__)

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log HTTP requests and responses
    """
    
    def __init__(self, app, log_body: bool = False):
        super().__init__(app)
        self.log_body = log_body
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details
        """
        start_time = time.time()
        
        # Log request
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client": request.client.host if request.client else None,
            "timestamp": start_time
        }
        
        # Optionally log request body (be careful with large images)
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) < 1024:  # Only log small bodies
                    request_info["body_size"] = len(body)
                else:
                    request_info["body_size"] = len(body)
                    request_info["body_preview"] = "Large body truncated"
            except Exception as e:
                request_info["body_error"] = str(e)
        
        logger.info(f"Request: {json.dumps(request_info, default=str)}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            response_info = {
                "status_code": response.status_code,
                "processing_time": process_time,
                "url": str(request.url),
                "method": request.method
            }
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            if response.status_code >= 400:
                logger.warning(f"Response: {json.dumps(response_info, default=str)}")
            else:
                logger.info(f"Response: {json.dumps(response_info, default=str)}")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            error_info = {
                "error": str(e),
                "processing_time": process_time,
                "url": str(request.url),
                "method": request.method
            }
            logger.error(f"Request error: {json.dumps(error_info, default=str)}")
            raise