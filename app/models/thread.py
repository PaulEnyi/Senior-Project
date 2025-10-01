from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

class ThreadStatus(str, Enum):
    """Enumeration of possible thread statuses"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PAUSED = "paused"

class MessageRole(str, Enum):
    """Enumeration of message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageType(str, Enum):
    """Enumeration of message types"""
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    ERROR = "error"

class ThreadMessage(BaseModel):
    """Model for individual messages within a thread"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str = Field(..., description="ID of the thread this message belongs to")
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content", min_length=1)
    message_type: MessageType = Field(default=MessageType.TEXT, description="Type of message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the message was created")
    
    # Optional fields for enhanced functionality
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional message metadata")
    sources_used: Optional[List[str]] = Field(default_factory=list, description="Knowledge sources used for AI responses")
    related_questions: Optional[List[str]] = Field(default_factory=list, description="Suggested related questions")
    response_time: Optional[float] = Field(None, description="Time taken to generate response (for AI messages)")
    error_info: Optional[Dict[str, Any]] = Field(None, description="Error information if message failed")
    
    # Voice-specific fields
    audio_duration: Optional[float] = Field(None, description="Duration of audio message in seconds")
    voice_model: Optional[str] = Field(None, description="Voice model used for TTS")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    @validator('content')
    def validate_content(cls, v):
        """Ensure content is not empty after stripping whitespace"""
        if not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """Ensure metadata doesn't contain sensitive information"""
        if v is None:
            return {}
        
        # Remove any potentially sensitive keys
        sensitive_keys = ['password', 'token', 'api_key', 'secret']
        return {k: val for k, val in v.items() if k.lower() not in sensitive_keys}

class ThreadMetadata(BaseModel):
    """Model for thread metadata and statistics"""
    
    total_messages: int = Field(default=0, description="Total number of messages in thread")
    user_messages: int = Field(default=0, description="Number of user messages")
    assistant_messages: int = Field(default=0, description="Number of assistant messages")
    
    # Timing information
    first_message_at: Optional[datetime] = Field(None, description="Timestamp of first message")
    last_message_at: Optional[datetime] = Field(None, description="Timestamp of last message")
    last_activity: Optional[datetime] = Field(None, description="Last activity in thread")
    
    # Usage statistics
    average_response_time: Optional[float] = Field(None, description="Average AI response time")
    total_tokens_used: Optional[int] = Field(None, description="Total tokens used in thread")
    voice_messages_count: int = Field(default=0, description="Number of voice messages")
    
    # Content categorization
    primary_topics: List[str] = Field(default_factory=list, description="Main topics discussed")
    knowledge_sources: List[str] = Field(default_factory=list, description="Knowledge sources referenced")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class ConversationThread(BaseModel):
    """Model for conversation threads"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique thread identifier")
    title: str = Field(default="New Conversation", description="Thread title", max_length=200)
    status: ThreadStatus = Field(default=ThreadStatus.ACTIVE, description="Current thread status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Thread creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Thread configuration
    max_messages: int = Field(default=100, description="Maximum number of messages to keep")
    auto_archive_days: Optional[int] = Field(30, description="Days after which to auto-archive")
    
    # User/session information
    user_id: Optional[str] = Field(None, description="User identifier if available")
    session_id: Optional[str] = Field(None, description="Session identifier")
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="User IP address")
    
    # Thread metadata and statistics
    metadata: ThreadMetadata = Field(default_factory=ThreadMetadata, description="Thread statistics")
    
    # Custom fields for Morgan State context
    department_context: str = Field(default="computer_science", description="Department context")
    student_level: Optional[str] = Field(None, description="Student level (freshman, sophomore, etc.)")
    primary_interest: Optional[str] = Field(None, description="Primary area of interest")
    
    # Tags and categorization
    tags: List[str] = Field(default_factory=list, description="Thread tags for categorization")
    is_archived: bool = Field(default=False, description="Whether thread is archived")
    archive_reason: Optional[str] = Field(None, description="Reason for archiving")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    @validator('title')
    def validate_title(cls, v):
        """Ensure title is reasonable length and not empty"""
        v = v.strip()
        if not v:
            v = "New Conversation"
        return v[:200]  # Truncate to max length
    
    @validator('tags')
    def validate_tags(cls, v):
        """Ensure tags are reasonable"""
        if v is None:
            return []
        # Remove duplicates, limit number, and clean up
        cleaned_tags = []
        for tag in v[:10]:  # Limit to 10 tags
            tag = str(tag).strip().lower()
            if tag and len(tag) <= 50 and tag not in cleaned_tags:
                cleaned_tags.append(tag)
        return cleaned_tags
    
    def update_metadata(self, message: ThreadMessage) -> None:
        """Update thread metadata when a new message is added"""
        self.metadata.total_messages += 1
        
        if message.role == MessageRole.USER:
            self.metadata.user_messages += 1
        elif message.role == MessageRole.ASSISTANT:
            self.metadata.assistant_messages += 1
            
            # Update response time statistics
            if message.response_time:
                if self.metadata.average_response_time is None:
                    self.metadata.average_response_time = message.response_time
                else:
                    # Running average
                    total_responses = self.metadata.assistant_messages
                    current_sum = self.metadata.average_response_time * (total_responses - 1)
                    self.metadata.average_response_time = (current_sum + message.response_time) / total_responses
        
        # Update timing
        if self.metadata.first_message_at is None:
            self.metadata.first_message_at = message.timestamp
        
        self.metadata.last_message_at = message.timestamp
        self.metadata.last_activity = datetime.utcnow()
        
        # Update voice message count
        if message.message_type == MessageType.VOICE:
            self.metadata.voice_messages_count += 1
        
        # Update knowledge sources
        if message.sources_used:
            for source in message.sources_used:
                if source not in self.metadata.knowledge_sources:
                    self.metadata.knowledge_sources.append(source)
        
        # Update timestamp
        self.updated_at = datetime.utcnow()
    
    def should_auto_archive(self) -> bool:
        """Check if thread should be auto-archived"""
        if not self.auto_archive_days or self.is_archived:
            return False
        
        if not self.metadata.last_activity:
            return False
        
        days_inactive = (datetime.utcnow() - self.metadata.last_activity).days
        return days_inactive >= self.auto_archive_days
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the thread for display purposes"""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "message_count": self.metadata.total_messages,
            "last_activity": self.metadata.last_activity,
            "tags": self.tags,
            "department_context": self.department_context,
            "is_archived": self.is_archived
        }

class ThreadCreateRequest(BaseModel):
    """Request model for creating a new thread"""
    
    title: Optional[str] = Field(None, description="Optional thread title")
    department_context: str = Field(default="computer_science", description="Department context")
    student_level: Optional[str] = Field(None, description="Student level")
    primary_interest: Optional[str] = Field(None, description="Primary area of interest")
    tags: Optional[List[str]] = Field(None, description="Initial tags")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Questions about CS Prerequisites",
                "department_context": "computer_science",
                "student_level": "sophomore",
                "primary_interest": "software_engineering",
                "tags": ["prerequisites", "planning"]
            }
        }

class ThreadUpdateRequest(BaseModel):
    """Request model for updating thread information"""
    
    title: Optional[str] = Field(None, description="New thread title")
    status: Optional[ThreadStatus] = Field(None, description="New thread status")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    student_level: Optional[str] = Field(None, description="Updated student level")
    primary_interest: Optional[str] = Field(None, description="Updated primary interest")
    
    class Config:
        use_enum_values = True

class ThreadListResponse(BaseModel):
    """Response model for thread listing"""
    
    threads: List[Dict[str, Any]] = Field(..., description="List of thread summaries")
    total_count: int = Field(..., description="Total number of threads")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of threads per page")
    has_more: bool = Field(..., description="Whether more threads are available")

class MessageCreateRequest(BaseModel):
    """Request model for creating a new message"""
    
    content: str = Field(..., description="Message content", min_length=1)
    message_type: MessageType = Field(default=MessageType.TEXT, description="Type of message")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional message metadata")
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "content": "What are the prerequisites for COSC 315?",
                "message_type": "text",
                "metadata": {
                    "source": "web_interface",
                    "user_agent": "Mozilla/5.0..."
                }
            }
        }

class ThreadAnalytics(BaseModel):
    """Model for thread analytics and insights"""
    
    thread_id: str = Field(..., description="Thread identifier")
    total_messages: int = Field(..., description="Total messages in thread")
    conversation_length: float = Field(..., description="Duration in hours")
    response_times: List[float] = Field(default_factory=list, description="AI response times")
    topics_discussed: List[str] = Field(default_factory=list, description="Main topics")
    knowledge_coverage: Dict[str, int] = Field(default_factory=dict, description="Knowledge areas covered")
    user_satisfaction_indicators: Dict[str, Any] = Field(default_factory=dict, description="Satisfaction metrics")
    
    class Config:
        schema_extra = {
            "example": {
                "thread_id": "thread_123",
                "total_messages": 24,
                "conversation_length": 2.5,
                "response_times": [1.2, 0.8, 1.5],
                "topics_discussed": ["prerequisites", "course planning", "career advice"],
                "knowledge_coverage": {
                    "academics": 15,
                    "career": 5,
                    "department_info": 4
                },
                "user_satisfaction_indicators": {
                    "positive_responses": 8,
                    "follow_up_questions": 12,
                    "completion_rate": 0.85
                }
            }
        }