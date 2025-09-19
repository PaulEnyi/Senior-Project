from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    """Enumeration of possible message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageType(str, Enum):
    """Enumeration of message types"""
    TEXT = "text"
    VOICE = "voice"
    ERROR = "error"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    """Individual chat message model"""
    id: str = Field(..., description="Unique message identifier")
    role: MessageRole = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content", min_length=1, max_length=10000)
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Type of message")
    
    # Optional fields for enhanced functionality
    sources_used: Optional[List[str]] = Field(default=None, description="Sources referenced in response")
    related_questions: Optional[List[str]] = Field(default=None, description="Related question suggestions")
    confidence_score: Optional[float] = Field(default=None, description="AI confidence in response", ge=0.0, le=1.0)
    response_time: Optional[float] = Field(default=None, description="Time taken to generate response", ge=0.0)
    
    # Voice-related fields
    voice_duration: Optional[float] = Field(default=None, description="Duration of voice message in seconds")
    voice_transcription: Optional[str] = Field(default=None, description="Transcription of voice input")
    
    # Error handling
    error: Optional[bool] = Field(default=False, description="Whether message contains an error")
    error_code: Optional[str] = Field(default=None, description="Error code if applicable")
    error_details: Optional[str] = Field(default=None, description="Detailed error information")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional message metadata")

    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ChatRequest(BaseModel):
    """Request model for sending chat messages"""
    message: str = Field(..., description="User message content", min_length=1, max_length=2000)
    thread_id: Optional[str] = Field(default=None, description="Conversation thread ID")
    category_filter: Optional[str] = Field(default=None, description="Knowledge base category filter")
    include_related_questions: bool = Field(default=True, description="Include related question suggestions")
    include_sources: bool = Field(default=True, description="Include source citations")
    voice_input: bool = Field(default=False, description="Whether input was from voice")
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class ChatResponse(BaseModel):
    """Response model for chat API"""
    response: str = Field(..., description="AI assistant response")
    message_id: str = Field(..., description="Unique message ID")
    thread_id: str = Field(..., description="Conversation thread ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    # Enhanced response data
    sources_used: List[str] = Field(default=[], description="Sources referenced in response")
    related_questions: List[str] = Field(default=[], description="Suggested related questions")
    confidence_score: Optional[float] = Field(default=None, description="AI confidence score", ge=0.0, le=1.0)
    response_time: float = Field(..., description="Response generation time", ge=0.0)
    
    # Voice features
    audio_url: Optional[str] = Field(default=None, description="URL for TTS audio")
    audio_duration: Optional[float] = Field(default=None, description="Duration of TTS audio")
    
    # Status information
    status: str = Field(default="success", description="Response status")
    category_used: Optional[str] = Field(default=None, description="Knowledge base category used")

class ChatHistoryRequest(BaseModel):
    """Request model for retrieving chat history"""
    thread_id: str = Field(..., description="Thread ID to retrieve")
    limit: int = Field(default=50, description="Maximum messages to retrieve", gt=0, le=1000)
    offset: int = Field(default=0, description="Number of messages to skip", ge=0)
    include_system_messages: bool = Field(default=False, description="Include system messages")
    
class ChatHistoryResponse(BaseModel):
    """Response model for chat history"""
    thread_id: str = Field(..., description="Thread ID")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    total_messages: int = Field(..., description="Total messages in thread")
    has_more: bool = Field(..., description="Whether more messages are available")

class QuickQuestion(BaseModel):
    """Model for predefined quick questions"""
    id: str = Field(..., description="Question ID")
    question: str = Field(..., description="Question text")
    category: str = Field(..., description="Question category")
    priority: int = Field(default=0, description="Display priority", ge=0)
    usage_count: int = Field(default=0, description="How often this question is used")

class ChatAnalytics(BaseModel):
    """Model for chat analytics data"""
    total_messages: int = Field(..., description="Total messages processed")
    total_threads: int = Field(..., description="Total conversation threads")
    average_response_time: float = Field(..., description="Average response time in seconds")
    popular_questions: List[QuickQuestion] = Field(..., description="Most asked questions")
    category_usage: Dict[str, int] = Field(..., description="Usage count by category")
    error_rate: float = Field(..., description="Percentage of errors", ge=0.0, le=100.0)
    user_satisfaction: Optional[float] = Field(default=None, description="Average satisfaction score")

class ChatFeedback(BaseModel):
    """Model for user feedback on responses"""
    message_id: str = Field(..., description="ID of message being rated")
    thread_id: str = Field(..., description="Thread ID")
    rating: int = Field(..., description="Rating (1-5)", ge=1, le=5)
    feedback_type: str = Field(..., description="Type of feedback (helpful, accurate, etc.)")
    comment: Optional[str] = Field(default=None, description="Optional feedback comment")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Feedback timestamp")

class ChatSettings(BaseModel):
    """Model for user chat preferences"""
    voice_enabled: bool = Field(default=True, description="Enable voice features")
    tts_voice: str = Field(default="alloy", description="Preferred TTS voice")
    auto_play_tts: bool = Field(default=False, description="Auto-play TTS responses")
    show_sources: bool = Field(default=True, description="Show source citations")
    show_related_questions: bool = Field(default=True, description="Show related questions")
    theme: str = Field(default="light", description="UI theme preference")
    language: str = Field(default="en", description="Preferred language")

class ChatError(BaseModel):
    """Model for chat error responses"""
    error: bool = Field(default=True, description="Error flag")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(default=None, description="Technical error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")