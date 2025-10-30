from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ThreadStatus(str, Enum):
    """Thread status enumeration"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    RESOLVED = "resolved"

class ThreadType(str, Enum):
    """Thread type enumeration"""
    GENERAL = "general"
    ACADEMIC = "academic"
    CAREER = "career"
    TECHNICAL = "technical"
    REGISTRATION = "registration"
    SUPPORT = "support"

class Thread(BaseModel):
    """Thread model"""
    thread_id: str = Field(..., description="Unique thread ID")
    user_id: str = Field(..., description="User ID")
    title: Optional[str] = Field(None, description="Thread title")
    type: ThreadType = Field(default=ThreadType.GENERAL, description="Thread type")
    status: ThreadStatus = Field(default=ThreadStatus.ACTIVE, description="Thread status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(default=0, description="Total messages")
    unread_count: int = Field(default=0, description="Unread messages")
    tags: Optional[List[str]] = Field(default_factory=list, description="Thread tags")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Thread metadata")
    
    class Config:
        use_enum_values = True

class ThreadCreate(BaseModel):
    """Thread creation request"""
    title: Optional[str] = Field(None, description="Thread title")
    type: ThreadType = Field(default=ThreadType.GENERAL, description="Thread type")
    initial_message: str = Field(..., description="First message")
    tags: Optional[List[str]] = Field(default_factory=list, description="Thread tags")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Thread metadata")

class ThreadUpdate(BaseModel):
    """Thread update request"""
    title: Optional[str] = Field(None, description="Thread title")
    type: Optional[ThreadType] = Field(None, description="Thread type")
    status: Optional[ThreadStatus] = Field(None, description="Thread status")
    tags: Optional[List[str]] = Field(None, description="Thread tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Thread metadata")

class ThreadList(BaseModel):
    """Thread list response"""
    threads: List[Thread] = Field(..., description="List of threads")
    total: int = Field(..., description="Total thread count")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=20, description="Page size")
    has_more: bool = Field(default=False, description="More threads available")

class ThreadStatistics(BaseModel):
    """Thread statistics model"""
    user_id: str = Field(..., description="User ID")
    total_threads: int = Field(..., description="Total threads")
    active_threads: int = Field(..., description="Active threads")
    archived_threads: int = Field(..., description="Archived threads")
    total_messages: int = Field(..., description="Total messages")
    avg_messages_per_thread: float = Field(..., description="Average messages per thread")
    most_active_type: Optional[ThreadType] = Field(None, description="Most active thread type")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")

class ThreadExport(BaseModel):
    """Thread export model"""
    thread: Thread = Field(..., description="Thread information")
    messages: List[Dict[str, Any]] = Field(..., description="Thread messages")
    export_date: datetime = Field(..., description="Export timestamp")
    format: str = Field(default="json", description="Export format")