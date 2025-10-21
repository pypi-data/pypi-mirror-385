#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Improved Error Handling for ISA Model API
Provides consistent error responses and better user experience
"""

import logging
import traceback
from typing import Dict, Any, Optional, Union
from enum import Enum
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class ErrorCode(str, Enum):
    """Standard error codes for ISA Model API"""
    
    # Input/Request errors (4xx)
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    INVALID_MODEL = "INVALID_MODEL"
    INVALID_PROVIDER = "INVALID_PROVIDER"
    INVALID_SERVICE_TYPE = "INVALID_SERVICE_TYPE"
    INVALID_TASK = "INVALID_TASK"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    
    # Service errors (5xx)
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    MODEL_LOAD_FAILED = "MODEL_LOAD_FAILED"
    INFERENCE_FAILED = "INFERENCE_FAILED"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    
    # Configuration errors
    CONFIG_ERROR = "CONFIG_ERROR"
    API_KEY_MISSING = "API_KEY_MISSING"
    API_KEY_INVALID = "API_KEY_INVALID"

class ISAModelError(Exception):
    """Base exception for ISA Model errors"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.user_message = user_message or self._generate_user_message()
        super().__init__(self.message)
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly error message"""
        user_messages = {
            ErrorCode.INVALID_INPUT: "请检查您的输入数据格式是否正确。",
            ErrorCode.MISSING_PARAMETER: "请提供必需的参数。",
            ErrorCode.INVALID_MODEL: "指定的模型不存在或不可用，请选择其他模型。",
            ErrorCode.INVALID_PROVIDER: "指定的提供商不支持，请选择其他提供商。",
            ErrorCode.INVALID_SERVICE_TYPE: "不支持的服务类型，请选择text、vision、audio、image或embedding。",
            ErrorCode.INVALID_TASK: "不支持的任务类型，请查看API文档了解支持的任务。",
            ErrorCode.UNSUPPORTED_FORMAT: "不支持的文件格式，请使用支持的格式。",
            ErrorCode.FILE_TOO_LARGE: "文件太大，请压缩后重试。",
            ErrorCode.RATE_LIMIT_EXCEEDED: "请求过于频繁，请稍后再试。",
            ErrorCode.AUTHENTICATION_FAILED: "身份验证失败，请检查您的凭据。",
            ErrorCode.AUTHORIZATION_FAILED: "您没有权限执行此操作。",
            ErrorCode.SERVICE_UNAVAILABLE: "服务暂时不可用，请稍后再试。",
            ErrorCode.MODEL_LOAD_FAILED: "模型加载失败，请稍后再试或选择其他模型。",
            ErrorCode.INFERENCE_FAILED: "推理过程出现错误，请重试。",
            ErrorCode.EXTERNAL_API_ERROR: "外部服务出现问题，请稍后再试。",
            ErrorCode.DATABASE_ERROR: "数据库连接问题，请稍后再试。",
            ErrorCode.TIMEOUT_ERROR: "请求超时，请稍后再试。",
            ErrorCode.INTERNAL_ERROR: "内部服务器错误，请联系技术支持。",
            ErrorCode.CONFIG_ERROR: "配置错误，请联系管理员。",
            ErrorCode.API_KEY_MISSING: "缺少API密钥，请在配置中提供。",
            ErrorCode.API_KEY_INVALID: "API密钥无效，请检查配置。"
        }
        
        return user_messages.get(self.error_code, "出现了未知错误，请稍后再试。")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API response"""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "user_message": self.user_message,
            "status_code": self.status_code,
            "details": self.details
        }

def create_error_response(
    error: Union[Exception, ISAModelError, str],
    status_code: Optional[int] = None,
    error_code: Optional[ErrorCode] = None,
    details: Optional[Dict[str, Any]] = None,
    include_traceback: bool = False
) -> Dict[str, Any]:
    """Create standardized error response"""
    
    if isinstance(error, ISAModelError):
        response = {
            "success": False,
            "error": error.message,
            "error_code": error.error_code.value,
            "user_message": error.user_message,
            "details": error.details,
            "metadata": {
                "error_type": "ISAModelError",
                "status_code": error.status_code
            }
        }
    elif isinstance(error, Exception):
        # Convert generic exception to ISAModelError
        error_message = str(error)
        final_error_code = error_code or ErrorCode.INTERNAL_ERROR
        final_status_code = status_code or 500
        
        isa_error = ISAModelError(
            message=error_message,
            error_code=final_error_code,
            status_code=final_status_code,
            details=details
        )
        
        response = {
            "success": False,
            "error": isa_error.message,
            "error_code": isa_error.error_code.value,
            "user_message": isa_error.user_message,
            "details": isa_error.details,
            "metadata": {
                "error_type": type(error).__name__,
                "status_code": isa_error.status_code
            }
        }
        
        if include_traceback:
            response["metadata"]["traceback"] = traceback.format_exc()
            
    else:
        # String error
        final_error_code = error_code or ErrorCode.INTERNAL_ERROR
        final_status_code = status_code or 500
        
        isa_error = ISAModelError(
            message=str(error),
            error_code=final_error_code,
            status_code=final_status_code,
            details=details or {}
        )
        
        response = {
            "success": False,
            "error": isa_error.message,
            "error_code": isa_error.error_code.value,
            "user_message": isa_error.user_message,
            "details": isa_error.details,
            "metadata": {
                "error_type": "StringError",
                "status_code": isa_error.status_code
            }
        }
    
    return response

def handle_validation_error(exc: Exception) -> Dict[str, Any]:
    """Handle Pydantic validation errors"""
    details = {}
    
    if hasattr(exc, 'errors'):
        # Pydantic validation error
        validation_errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error.get('loc', []))
            message = error.get('msg', '')
            validation_errors.append({
                "field": field,
                "message": message,
                "type": error.get('type', '')
            })
        details["validation_errors"] = validation_errors
    
    return create_error_response(
        error="请求数据格式不正确",
        status_code=400,
        error_code=ErrorCode.INVALID_INPUT,
        details=details
    )

def handle_service_error(
    service_name: str,
    error: Exception,
    fallback_available: bool = False
) -> Dict[str, Any]:
    """Handle service-specific errors with context"""
    
    details = {
        "service": service_name,
        "fallback_available": fallback_available
    }
    
    # Determine error code based on service and error type
    if "connection" in str(error).lower():
        error_code = ErrorCode.EXTERNAL_API_ERROR
        if fallback_available:
            user_message = f"{service_name}服务暂时不可用，已切换到备用服务。"
        else:
            user_message = f"{service_name}服务连接失败，请稍后再试。"
    elif "timeout" in str(error).lower():
        error_code = ErrorCode.TIMEOUT_ERROR
        user_message = f"{service_name}服务响应超时，请稍后再试。"
    elif "authentication" in str(error).lower() or "api key" in str(error).lower():
        error_code = ErrorCode.API_KEY_INVALID
        user_message = f"{service_name}服务认证失败，请检查API密钥配置。"
    elif "rate limit" in str(error).lower():
        error_code = ErrorCode.RATE_LIMIT_EXCEEDED
        user_message = f"{service_name}服务请求频率过高，请稍后再试。"
    else:
        error_code = ErrorCode.SERVICE_UNAVAILABLE
        if fallback_available:
            user_message = f"{service_name}服务出现问题，已切换到备用服务。"
        else:
            user_message = f"{service_name}服务暂时不可用，请稍后再试。"
    
    return create_error_response(
        error=str(error),
        status_code=503 if not fallback_available else 200,
        error_code=error_code,
        details=details
    )

def create_http_exception(
    message: str,
    status_code: int = 500,
    error_code: Optional[ErrorCode] = None,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create HTTPException with standardized error format"""
    
    error_response = create_error_response(
        error=message,
        status_code=status_code,
        error_code=error_code,
        details=details
    )
    
    return HTTPException(
        status_code=status_code,
        detail=error_response
    )

# Convenience functions for common errors
def invalid_input_error(message: str, details: Optional[Dict] = None) -> HTTPException:
    return create_http_exception(message, 400, ErrorCode.INVALID_INPUT, details)

def model_not_found_error(model_name: str) -> HTTPException:
    return create_http_exception(
        f"模型 '{model_name}' 不存在或不可用",
        404,
        ErrorCode.INVALID_MODEL,
        {"model": model_name, "suggestion": "请查看 /api/v1/models 获取可用模型列表"}
    )

def service_unavailable_error(service_name: str, fallback: bool = False) -> HTTPException:
    status_code = 200 if fallback else 503
    return create_http_exception(
        f"{service_name}服务{'已切换到备用模式' if fallback else '暂时不可用'}",
        status_code,
        ErrorCode.SERVICE_UNAVAILABLE,
        {"service": service_name, "fallback_mode": fallback}
    )