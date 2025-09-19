from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
import logging
from typing import Union

logger = logging.getLogger(__name__)

class MorganAIChatbotException(Exception):
    """Base exception class for Morgan AI Chatbot"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class OpenAIServiceException(MorganAIChatbotException):
    """Exception raised when OpenAI API calls fail"""
    pass

class PineconeServiceException(MorganAIChatbotException):
    """Exception raised when Pinecone operations fail"""
    pass

class KnowledgeBaseException(MorganAIChatbotException):
    """Exception raised when knowledge base operations fail"""
    pass

class ThreadManagementException(MorganAIChatbotException):
    """Exception raised when thread operations fail"""
    pass

class VoiceProcessingException(MorganAIChatbotException):
    """Exception raised when voice processing fails"""
    pass

class AuthenticationException(MorganAIChatbotException):
    """Exception raised when authentication fails"""
    pass

class RateLimitException(MorganAIChatbotException):
    """Exception raised when rate limits are exceeded"""
    pass

# Custom exception handlers
async def morgan_ai_exception_handler(request: Request, exc: MorganAIChatbotException):
    """Handle custom Morgan AI exceptions"""
    logger.error(f"Morgan AI Exception: {exc.message} (Code: {exc.error_code})")
    
    # Determine HTTP status code based on exception type
    status_code = 500
    if isinstance(exc, AuthenticationException):
        status_code = 401
    elif isinstance(exc, RateLimitException):
        status_code = 429
    elif isinstance(exc, (OpenAIServiceException, PineconeServiceException)):
        status_code = 503  # Service Unavailable
    elif isinstance(exc, (KnowledgeBaseException, ThreadManagementException)):
        status_code = 422  # Unprocessable Entity
    elif isinstance(exc, VoiceProcessingException):
        status_code = 400  # Bad Request
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "type": exc.__class__.__name__
        }
    )

async def validation_exception_handler(request: Request, exc: Exception):
    """Handle validation errors with custom format"""
    logger.error(f"Validation error: {str(exc)}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Invalid input data",
            "details": str(exc),
            "type": "ValidationError"
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "An unexpected error occurred. Please try again later.",
            "type": "InternalServerError"
        }
    )

# HTTP exception handler override for consistent error format
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Override default HTTP exception handler for consistent format"""
    
    # Special handling for rate limiting
    if exc.status_code == 429:
        return JSONResponse(
            status_code=429,
            content={
                "error": True,
                "message": "Too many requests. Please slow down and try again later.",
                "type": "RateLimitError"
            }
        )
    
    # Use default handler but log the error
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    
    return await http_exception_handler(request, exc)

# Error response helper functions
def create_error_response(
    message: str,
    error_code: str = None,
    details: Union[str, dict] = None
) -> dict:
    """Create a standardized error response"""
    response = {
        "error": True,
        "message": message,
    }
    
    if error_code:
        response["error_code"] = error_code
    
    if details:
        response["details"] = details
    
    return response

def create_success_response(
    data: Union[str, dict, list] = None,
    message: str = "Success"
) -> dict:
    """Create a standardized success response"""
    response = {
        "error": False,
        "message": message,
    }
    
if data is not None:
    response["data"] = data
    
return response