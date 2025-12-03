from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    """Chat message model"""
    message_id: Optional[str] = Field(None, description="Unique message ID")
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")
    user_id: Optional[str] = Field(None, description="User ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        use_enum_values = True

class ChatThread(BaseModel):
    """Chat thread model"""
    thread_id: str = Field(..., description="Unique thread ID")
    user_id: str = Field(..., description="User ID")
    title: Optional[str] = Field(None, description="Thread title")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    message_count: int = Field(default=0, description="Number of messages")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    is_active: bool = Field(default=True, description="Thread active status")

class ChatResponse(BaseModel):
    """Chat response model"""
    thread_id: str = Field(..., description="Thread ID")
    message: str = Field(..., description="Response message")
    sources: Optional[List[str]] = Field(default_factory=list, description="Information sources")
    timestamp: datetime = Field(..., description="Response timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Response metadata")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Response confidence score")

class ChatFeedback(BaseModel):
    """Chat feedback model"""
    message_id: str = Field(..., description="Message ID")
    thread_id: str = Field(..., description="Thread ID")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    comment: Optional[str] = Field(None, description="Feedback comment")
    user_id: str = Field(..., description="User ID")
    timestamp: datetime = Field(..., description="Feedback timestamp")

class ThreadSummary(BaseModel):
    """Thread summary model"""
    thread_id: str = Field(..., description="Thread ID")
    title: Optional[str] = Field(None, description="Thread title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(..., description="Total messages")
    last_message: Optional[str] = Field(None, description="Last message preview")
    is_active: bool = Field(default=True, description="Thread status")

class SearchResult(BaseModel):
    """Search result model"""
    thread_id: str = Field(..., description="Thread ID")
    message_id: str = Field(..., description="Message ID")
    content: str = Field(..., description="Message content")
    role: MessageRole = Field(..., description="Message role")
    timestamp: datetime = Field(..., description="Message timestamp")
    relevance_score: Optional[float] = Field(None, description="Search relevance score")
    highlight: Optional[str] = Field(None, description="Highlighted search match")

class ConversationContext(BaseModel):
    """Conversation context model"""
    thread_id: str = Field(..., description="Thread ID")
    user_id: str = Field(..., description="User ID")
    recent_messages: List[ChatMessage] = Field(default_factory=list, description="Recent messages")
    user_profile: Optional[Dict[str, Any]] = Field(None, description="User profile data")
    session_metadata: Optional[Dict[str, Any]] = Field(None, description="Session metadata")