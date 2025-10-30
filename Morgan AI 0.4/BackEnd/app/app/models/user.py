from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    GUEST = "guest"

class UserStatus(str, Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class User(BaseModel):
    """User model"""
    user_id: str = Field(..., description="Unique user ID")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Account status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User preferences")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        use_enum_values = True

class UserProfile(BaseModel):
    """User profile model"""
    user_id: str = Field(..., description="User ID")
    student_id: Optional[str] = Field(None, description="Student ID")
    major: Optional[str] = Field(None, description="Academic major")
    year: Optional[str] = Field(None, description="Academic year")
    courses: Optional[List[str]] = Field(default_factory=list, description="Enrolled courses")
    interests: Optional[List[str]] = Field(default_factory=list, description="Academic interests")
    graduation_year: Optional[int] = Field(None, description="Expected graduation year")
    advisor: Optional[str] = Field(None, description="Academic advisor")

class UserPreferences(BaseModel):
    """User preferences model"""
    user_id: str = Field(..., description="User ID")
    enable_voice: bool = Field(default=True, description="Enable voice features")
    tts_voice: str = Field(default="alloy", description="TTS voice preference")
    tts_speed: float = Field(default=1.0, ge=0.25, le=4.0, description="TTS speed")
    theme: str = Field(default="dark", description="UI theme")
    language: str = Field(default="en", description="Preferred language")
    notification_settings: Dict[str, bool] = Field(
        default_factory=lambda: {
            "email": True,
            "push": False,
            "sms": False,
            "internships": True,
            "events": True,
            "deadlines": True
        },
        description="Notification preferences"
    )
    chat_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "save_history": True,
            "auto_suggestions": True,
            "quick_questions": True
        },
        description="Chat preferences"
    )

class UserSession(BaseModel):
    """User session model"""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    token: str = Field(..., description="Session token")
    created_at: datetime = Field(..., description="Session start time")
    expires_at: datetime = Field(..., description="Session expiration")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    is_active: bool = Field(default=True, description="Session active status")

class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(default=False, description="Extended session")

class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: User = Field(..., description="User information")
    preferences: Optional[UserPreferences] = Field(None, description="User preferences")

class RegisterRequest(BaseModel):
    """Registration request model"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    full_name: Optional[str] = Field(None, description="Full name")
    student_id: Optional[str] = Field(None, description="Student ID")

class PasswordResetRequest(BaseModel):
    """Password reset request model"""
    email: EmailStr = Field(..., description="Email address")

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")

class UserActivity(BaseModel):
    """User activity model"""
    user_id: str = Field(..., description="User ID")
    activity_type: str = Field(..., description="Activity type")
    description: str = Field(..., description="Activity description")
    timestamp: datetime = Field(..., description="Activity timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Activity metadata")