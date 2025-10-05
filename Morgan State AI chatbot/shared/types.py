from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

# Enums for standardized values
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ThreadStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class SystemStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class KnowledgeCategory(str, Enum):
    DEPARTMENT_INFO = "department_info"
    FACULTY_STAFF = "faculty_staff"
    ACADEMICS = "academics"
    COURSES = "courses"
    PROGRAMS = "programs"
    STUDENT_RESOURCES = "student_resources"
    ORGANIZATIONS = "organizations"
    CAREER_PREP = "career_prep"
    ADMINISTRATIVE = "administrative"
    REGISTRATION = "registration"
    ADVISING = "advising"
    GENERAL = "general"

class VoiceService(str, Enum):
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"

class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"
    GUEST = "guest"

# Base Models
class BaseMessage(BaseModel):
    """Base message model for chat interactions"""
    id: Optional[str] = None
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class ChatMessage(BaseMessage):
    """Extended message model with additional fields"""
    thread_id: Optional[str] = None
    status: MessageStatus = MessageStatus.COMPLETED
    sources_used: List[str] = Field(default_factory=list)
    related_questions: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    processing_time: Optional[float] = None

class ThreadMetadata(BaseModel):
    """Thread metadata model"""
    thread_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message: str = ""
    title: str = "New Conversation"
    status: ThreadStatus = ThreadStatus.ACTIVE
    tags: List[str] = Field(default_factory=list)
    category: Optional[KnowledgeCategory] = None

class VectorDocument(BaseModel):
    """Vector document model for knowledge base"""
    id: str
    content: str
    category: KnowledgeCategory
    source: str
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None
    last_updated: Optional[datetime] = None

class ServiceHealth(BaseModel):
    """Service health status model"""
    service_name: str
    status: SystemStatus
    last_check: datetime
    response_time: Optional[float] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class SystemHealth(BaseModel):
    """Overall system health model"""
    status: SystemStatus
    timestamp: datetime
    services: Dict[str, ServiceHealth]
    uptime: Optional[float] = None
    version: Optional[str] = None

class AdminUser(BaseModel):
    """Admin user model"""
    username: str
    role: UserRole = UserRole.ADMIN
    created_at: datetime
    last_login: Optional[datetime] = None
    permissions: List[str] = Field(default_factory=list)
    is_active: bool = True

class BackupInfo(BaseModel):
    """Backup information model"""
    backup_name: str
    created_at: datetime
    created_by: str
    size: int
    components: List[str]
    status: str
    file_path: Optional[str] = None
    description: Optional[str] = None

class AnalyticsData(BaseModel):
    """Analytics data model"""
    total_conversations: int = 0
    total_messages: int = 0
    average_response_time: float = 0.0
    popular_questions: List[Dict[str, Any]] = Field(default_factory=list)
    error_rate: float = 0.0
    uptime_percentage: float = 100.0
    active_users: int = 0
    peak_usage_time: Optional[str] = None

class VoiceSettings(BaseModel):
    """Voice configuration model"""
    voice: VoiceService = VoiceService.ALLOY
    speed: float = Field(1.0, ge=0.25, le=4.0)
    volume: float = Field(1.0, ge=0.0, le=1.0)
    enabled: bool = True
    auto_play: bool = False

class ChatSettings(BaseModel):
    """Chat configuration model"""
    max_tokens: int = Field(500, ge=1, le=4000)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    include_related_questions: bool = True
    category_filter: Optional[KnowledgeCategory] = None
    voice_settings: Optional[VoiceSettings] = None

class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(APIResponse):
    """Error response model"""
    success: bool = False
    error_details: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None

class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any]
    total: int
    page: int = 1
    page_size: int = 20
    has_next: bool = False
    has_previous: bool = False

# Union types for flexibility
MessageContent = Union[str, Dict[str, Any]]
EmbeddingVector = List[float]
Metadata = Dict[str, Any]

# Type aliases for common patterns
ThreadID = str
MessageID = str
UserID = str
DocumentID = str
RequestID = str

# Configuration types
class DatabaseConfig(BaseModel):
    """Database configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "prefer"

class OpenAIConfig(BaseModel):
    """OpenAI service configuration"""
    api_key: str
    model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-ada-002"
    max_tokens: int = 500
    temperature: float = 0.7
    timeout: int = 30

class PineconeConfig(BaseModel):
    """Pinecone service configuration"""
    api_key: str
    environment: str
    index_name: str
    dimension: int = 1536
    metric: str = "cosine"

class SecurityConfig(BaseModel):
    """Security configuration"""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    admin_username: str
    admin_password_hash: str

# Custom exceptions as types
class MorganAIError(Exception):
    """Base exception for Morgan AI"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(MorganAIError):
    """Validation error"""
    pass

class AuthenticationError(MorganAIError):
    """Authentication error"""
    pass

class ServiceUnavailableError(MorganAIError):
    """Service unavailable error"""
    pass

class RateLimitError(MorganAIError):
    """Rate limit exceeded error"""
    pass