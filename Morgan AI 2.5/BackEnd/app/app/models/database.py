"""
SQLAlchemy Database Models for Morgan AI Chatbot
Defines all database tables with proper relationships, indexes, and constraints
"""

from sqlalchemy import (
    Column, String, Integer, DateTime, Text, Boolean, 
    ForeignKey, Index, JSON, LargeBinary, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role enumeration"""
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(Base):
    """
    User account table - stores all user authentication and profile data
    Contains hashed passwords (NEVER plain text), profile information, and account metadata
    """
    __tablename__ = "users"
    
    # Primary Key
    user_id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Authentication Fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt hashed password
    
    # Profile Information
    full_name = Column(String(255), nullable=True)
    student_id = Column(String(50), nullable=True, index=True)  # Morgan State student ID - NOT unique, allows NULL for non-students
    major = Column(String(100), nullable=True)
    classification = Column(String(50), nullable=True)  # Freshman, Sophomore, Junior, Senior, Graduate
    expected_graduation = Column(String(20), nullable=True)  # e.g., "Spring 2026"
    
    # Account Management
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT, index=True)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE, index=True)
    
    # WebSIS Integration (Optional)
    websis_session_id = Column(String(255), nullable=True)  # Cached WebSIS session
    websis_session_expires = Column(DateTime(timezone=True), nullable=True)
    
    # OAuth Provider Data (for social login)
    google_id = Column(String(255), nullable=True, unique=True, index=True)
    apple_id = Column(String(255), nullable=True, unique=True, index=True)
    microsoft_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Relationships
    degree_works_files = relationship("DegreeWorksFile", back_populates="user", cascade="all, delete-orphan")
    chat_threads = relationship("ChatThread", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_email_status', 'email', 'status'),
        Index('idx_user_role_status', 'role', 'status'),
        Index('idx_user_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email}, role={self.role})>"


class DegreeWorksFile(Base):
    """
    Degree Works file storage - stores uploaded PDF files and parsed academic data
    Links to User table to maintain ownership and access control
    """
    __tablename__ = "degree_works_files"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key to User
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # File Storage
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)  # Path to PDF file on disk
    file_blob = Column(LargeBinary, nullable=True)  # Alternative: store file as binary blob
    file_size = Column(Integer, nullable=True)  # File size in bytes
    file_hash = Column(String(64), nullable=True, index=True)  # SHA256 hash for deduplication
    
    # Parsed Data (JSON)
    parsed_data = Column(JSON, nullable=True)  # Complete parsed Degree Works data
    
    # Academic Information Extracted
    student_name = Column(String(255), nullable=True)
    student_id = Column(String(50), nullable=True, index=True)
    major = Column(String(100), nullable=True)
    classification = Column(String(50), nullable=True)
    gpa = Column(String(10), nullable=True)
    credits_earned = Column(Integer, nullable=True)
    credits_needed = Column(Integer, nullable=True)
    
    # Processing Status
    is_processed = Column(Boolean, default=False, nullable=False, index=True)
    processing_error = Column(Text, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="degree_works_files")
    
    # Indexes
    __table_args__ = (
        Index('idx_degree_works_user_uploaded', 'user_id', 'uploaded_at'),
        Index('idx_degree_works_processed', 'is_processed', 'uploaded_at'),
    )
    
    def __repr__(self):
        return f"<DegreeWorksFile(id={self.id}, user_id={self.user_id}, filename={self.filename})>"


class ChatThread(Base):
    """
    Chat thread/conversation storage - each user can have multiple chat sessions
    Stores thread metadata, title, and conversation context
    """
    __tablename__ = "chat_threads"
    
    # Primary Key
    thread_id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Foreign Key to User
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Thread Metadata
    title = Column(String(500), nullable=True)  # Auto-generated or user-defined title
    description = Column(Text, nullable=True)
    
    # Thread Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # Current active chat
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    
    # Message Counts
    message_count = Column(Integer, default=0, nullable=False)
    
    # Additional Metadata (JSON for flexibility)
    thread_metadata = Column(JSON, nullable=True)  # Can store: last_saved, saved_on_logout, tags, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, index=True)
    last_message_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_threads")
    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete-orphan", order_by="ChatMessage.created_at")
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_thread_user_active', 'user_id', 'is_active'),
        Index('idx_thread_user_updated', 'user_id', 'updated_at'),
        Index('idx_thread_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ChatThread(thread_id={self.thread_id}, user_id={self.user_id}, title={self.title})>"


class ChatMessage(Base):
    """
    Individual chat messages within a thread
    Stores both user messages and AI responses with full conversation context
    """
    __tablename__ = "chat_messages"
    
    # Primary Key
    message_id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Foreign Key to ChatThread
    thread_id = Column(String(36), ForeignKey('chat_threads.thread_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Message Content
    role = Column(String(20), nullable=False, index=True)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    # Message Metadata
    token_count = Column(Integer, nullable=True)  # Number of tokens in message
    model = Column(String(50), nullable=True)  # AI model used (e.g., 'gpt-4-turbo-preview')
    finish_reason = Column(String(50), nullable=True)  # 'stop', 'length', etc.
    
    # RAG Context (if applicable)
    context_used = Column(JSON, nullable=True)  # Retrieved context from Pinecone
    sources = Column(JSON, nullable=True)  # Source documents/files referenced
    
    # User Feedback
    feedback_rating = Column(Integer, nullable=True)  # 1 (thumbs down) or 2 (thumbs up)
    feedback_comment = Column(Text, nullable=True)
    feedback_submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional Metadata (JSON for flexibility)
    message_metadata = Column(JSON, nullable=True)  # Can store: latency, prompt_tokens, completion_tokens, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Relationships
    thread = relationship("ChatThread", back_populates="messages")
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_message_thread_created', 'thread_id', 'created_at'),
        Index('idx_message_thread_role', 'thread_id', 'role'),
        Index('idx_message_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ChatMessage(message_id={self.message_id}, thread_id={self.thread_id}, role={self.role})>"


class UserSession(Base):
    """
    Active user sessions for tracking logins and managing session tokens
    Helps with logout functionality and session invalidation
    """
    __tablename__ = "user_sessions"
    
    # Primary Key
    session_id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Foreign Key to User
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Session Data
    access_token = Column(String(500), nullable=False, unique=True, index=True)  # JWT token
    refresh_token = Column(String(500), nullable=True, unique=True, index=True)  # Optional refresh token
    
    # Session Metadata
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)  # Browser/device info
    device_type = Column(String(50), nullable=True)  # 'mobile', 'desktop', 'tablet'
    
    # Session Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Indexes for session management
    __table_args__ = (
        Index('idx_session_user_active', 'user_id', 'is_active'),
        Index('idx_session_expires', 'expires_at', 'is_active'),
        Index('idx_session_token', 'access_token', 'is_active'),
    )
    
    def __repr__(self):
        return f"<UserSession(session_id={self.session_id}, user_id={self.user_id}, is_active={self.is_active})>"


class AuditLog(Base):
    """
    Audit log for tracking important user actions and system events
    Helps with security monitoring and debugging
    """
    __tablename__ = "audit_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User Reference (nullable for system events)
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Event Information
    event_type = Column(String(50), nullable=False, index=True)  # 'login', 'logout', 'chat_created', etc.
    event_action = Column(String(100), nullable=False)  # Detailed action description
    event_result = Column(String(20), nullable=False, index=True)  # 'success', 'failure', 'error'
    
    # Event Details (JSON)
    event_data = Column(JSON, nullable=True)  # Additional context about the event
    
    # Request Metadata
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(String(500), nullable=True)
    request_path = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)
    
    # Error Information (if applicable)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Indexes for audit queries
    __table_args__ = (
        Index('idx_audit_user_type', 'user_id', 'event_type'),
        Index('idx_audit_type_created', 'event_type', 'created_at'),
        Index('idx_audit_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type={self.event_type}, user_id={self.user_id})>"
