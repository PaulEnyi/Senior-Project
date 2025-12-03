from typing import Any, Optional, Dict

class ChatbotException(Exception):
    """Base exception for chatbot errors"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class OpenAIException(ChatbotException):
    """Exception for OpenAI API errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=503, details=details)

class PineconeException(ChatbotException):
    """Exception for Pinecone errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=503, details=details)

class AuthenticationException(ChatbotException):
    """Exception for authentication errors"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)

class AuthorizationException(ChatbotException):
    """Exception for authorization errors"""
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)

class ValidationException(ChatbotException):
    """Exception for validation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)

class ResourceNotFoundException(ChatbotException):
    """Exception for resource not found errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)

class RateLimitException(ChatbotException):
    """Exception for rate limit errors"""
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=429, details=details)

class KnowledgeBaseException(ChatbotException):
    """Exception for knowledge base operations"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)

class VoiceProcessingException(ChatbotException):
    """Exception for voice processing errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)