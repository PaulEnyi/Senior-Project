from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

class UserStatus(str, Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(BaseModel):
    """Base user model"""
    id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username", min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(default=None, description="User email address")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="User status")
    
    # Profile information
    display_name: Optional[str] = Field(default=None, description="Display name")
    avatar_url: Optional[str] = Field(default=None, description="Avatar image URL")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation date")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last profile update")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    last_activity: Optional[datetime] = Field(default=None, description="Last activity timestamp")
    
    # Preferences
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="User preferences")
    
    # Statistics
    total_messages: int = Field(default=0, description="Total messages sent")
    total_threads: int = Field(default=0, description="Total conversation threads")

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AdminUser(User):
    """Extended admin user model"""
    role: UserRole = Field(default=UserRole.ADMIN, description="Admin role")
    
    # Admin-specific fields
    permissions: List[str] = Field(default=[], description="Admin permissions")
    department: Optional[str] = Field(default=None, description="Department/organization")
    access_level: int = Field(default=1, description="Access level (1-5)", ge=1, le=5)
    
    # Admin activity tracking
    admin_actions_count: int = Field(default=0, description="Number of admin actions performed")
    last_admin_action: Optional[datetime] = Field(default=None, description="Last admin action timestamp")
    
    # Security
    two_factor_enabled: bool = Field(default=False, description="Two-factor authentication enabled")
    login_attempts: int = Field(default=0, description="Failed login attempts")
    account_locked_until: Optional[datetime] = Field(default=None, description="Account lock expiration")

class UserSession(BaseModel):
    """User session model"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    expires_at: datetime = Field(..., description="Session expiration time")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    
    # Session metadata
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    device_info: Optional[Dict[str, Any]] = Field(default=None, description="Device information")
    
    # Status
    is_active: bool = Field(default=True, description="Whether session is active")
    is_admin_session: bool = Field(default=False, description="Whether this is an admin session")

class UserPreferences(BaseModel):
    """User preferences model"""
    user_id: str = Field(..., description="User ID")
    
    # Chat preferences
    voice_enabled: bool = Field(default=True, description="Enable voice features")
    tts_voice: str = Field(default="alloy", description="Preferred TTS voice")
    auto_play_tts: bool = Field(default=False, description="Auto-play TTS responses")
    
    # Display preferences
    theme: str = Field(default="light", description="UI theme (light/dark)")
    language: str = Field(default="en", description="Preferred language")
    timezone: str = Field(default="UTC", description="User timezone")
    
    # Content preferences
    show_sources: bool = Field(default=True, description="Show source citations")
    show_related_questions: bool = Field(default=True, description="Show related questions")
    max_response_length: int = Field(default=500, description="Max response length", gt=0, le=2000)
    
    # Notification preferences
    email_notifications: bool = Field(default=False, description="Enable email notifications")
    browser_notifications: bool = Field(default=False, description="Enable browser notifications")
    
    # Privacy preferences
    save_chat_history: bool = Field(default=True, description="Save conversation history")
    analytics_opt_in: bool = Field(default=True, description="Allow usage analytics")
    
    # Updated timestamp
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

class UserActivity(BaseModel):
    """User activity tracking model"""
    id: str = Field(..., description="Activity ID")
    user_id: str = Field(..., description="User ID")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    
    # Activity details
    activity_type: str = Field(..., description="Type of activity")
    description: str = Field(..., description="Activity description")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Activity timestamp")
    
    # Context
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    endpoint: Optional[str] = Field(default=None, description="API endpoint accessed")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional activity metadata")
    
    # Status
    success: bool = Field(default=True, description="Whether activity was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")

class AdminAction(BaseModel):
    """Admin action tracking model"""
    id: str = Field(..., description="Action ID")
    admin_user_id: str = Field(..., description="Admin user ID")
    admin_username: str = Field(..., description="Admin username")
    
    # Action details
    action_type: str = Field(..., description="Type of admin action")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(default=None, description="ID of affected resource")
    
    # Action description and impact
    description: str = Field(..., description="Action description")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Detailed action information")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Action timestamp")
    
    # Context
    ip_address: Optional[str] = Field(default=None, description="Admin IP address")
    user_agent: Optional[str] = Field(default=None, description="Admin user agent")
    
    # Status and results
    success: bool = Field(default=True, description="Whether action was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    
    # Impact tracking
    affected_users: int = Field(default=0, description="Number of users affected")
    system_impact: Optional[str] = Field(default=None, description="System impact level")

class LoginAttempt(BaseModel):
    """Login attempt tracking model"""
    id: str = Field(..., description="Attempt ID")
    username: str = Field(..., description="Username attempted")
    ip_address: str = Field(..., description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    
    # Attempt details
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Attempt timestamp")
    success: bool = Field(..., description="Whether login was successful")
    failure_reason: Optional[str] = Field(default=None, description="Reason for failure")
    
    # Security context
    geolocation: Optional[Dict[str, Any]] = Field(default=None, description="Geographic location data")
    device_fingerprint: Optional[str] = Field(default=None, description="Device fingerprint")
    
    # Rate limiting
    attempts_in_window: int = Field(default=1, description="Attempts from this IP in time window")

class UserRegistration(BaseModel):
    """User registration request model"""
    username: str = Field(..., description="Desired username", min_length=3, max_length=50)
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password", min_length=8)
    display_name: Optional[str] = Field(default=None, description="Display name")
    
    # Terms and privacy
    accept_terms: bool = Field(..., description="Accept terms of service")
    accept_privacy: bool = Field(..., description="Accept privacy policy")
    
    # Optional fields
    department: Optional[str] = Field(default=None, description="Department/organization")
    referral_source: Optional[str] = Field(default=None, description="How they found the service")

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()
    
    @validator('accept_terms', 'accept_privacy')
    def must_accept_terms(cls, v):
        if not v:
            raise ValueError('Must accept terms and privacy policy')
        return v

class UserProfile(BaseModel):
    """Public user profile model"""
    username: str = Field(..., description="Username")
    display_name: Optional[str] = Field(default=None, description="Display name")
    avatar_url: Optional[str] = Field(default=None, description="Avatar URL")
    created_at: datetime = Field(..., description="Account creation date")
    
    # Public statistics (privacy-safe)
    public_message_count: Optional[int] = Field(default=None, description="Public message count")
    contribution_score: Optional[int] = Field(default=None, description="Contribution score")
    
    # Status
    status: UserStatus = Field(..., description="User status")
    last_seen: Optional[datetime] = Field(default=None, description="Last seen timestamp")

class PasswordReset(BaseModel):
    """Password reset request model"""
    token: str = Field(..., description="Reset token")
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Token creation time")
    expires_at: datetime = Field(..., description="Token expiration time")
    used: bool = Field(default=False, description="Whether token has been used")
    used_at: Optional[datetime] = Field(default=None, description="When token was used")