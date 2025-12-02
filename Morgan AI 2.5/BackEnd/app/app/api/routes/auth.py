"""
Authentication Routes with File-Based Storage
Handles user signup, login, logout with secure password hashing
All user data stored in data/users/{user_id}/user_info.json - NO database required
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import logging
import bcrypt

from app.core.security import SecurityService
from app.core.config import settings
from app.core.file_storage import get_file_storage
from app.core.database import get_db
from app.models.database import User as DBUser

logger = logging.getLogger(__name__)
router = APIRouter()


class SignupRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: str = Field(..., min_length=6)
    role: str = Field(default="user")
    student_id: Optional[str] = None
    major: Optional[str] = None
    concentration: Optional[str] = None
    classification: Optional[str] = None  # Freshman, Sophomore, Junior, Senior
    expected_graduation: Optional[str] = None  # e.g., "Spring 2025"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = Field(default="user")


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    http_request: Request,
    file_storage = Depends(get_file_storage),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new user account with file-based storage and database entry
    Saves to data/users/{user_id}/user_info.json with bcrypt hashed password
    Also creates corresponding database user record
    """
    try:
        # Check if email already exists
        existing_user = file_storage.find_user_by_email(request.email)
        if existing_user:
            logger.warning(f"❌ Signup attempt with existing email: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please login instead."
            )
        
        # Check if username already exists
        existing_username = file_storage.find_user_by_username(request.username)
        if existing_username:
            logger.warning(f"❌ Signup attempt with existing username: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken. Please choose another."
            )
        
        # Generate unique user ID
        user_id = str(uuid.uuid4())
        
        # Create user folder structure
        folders = file_storage.create_user_folder_structure(user_id)
        logger.info(f"📁 Created folder structure for user: {user_id}")
        
        # Hash password with bcrypt (NEVER store plain text)
        password_hash = SecurityService.get_password_hash(request.password)
        
        # Prepare user data
        user_data = {
            "user_id": user_id,
            "email": request.email,
            "username": request.username,
            "full_name": request.full_name or request.username,
            "password_hash": password_hash,
            "role": "admin" if request.role == "admin" else "student",
            "student_id": request.student_id,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "last_login": None
        }
        
        # Save user info to file
        success = file_storage.save_user_info(user_id, user_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )
        
        # Create database user entry
        try:
            db_user = DBUser(
                user_id=user_id,
                email=request.email,
                username=request.username,
                full_name=request.full_name or request.username,
                password_hash=password_hash,
                role="admin" if request.role == "admin" else "student",
                student_id=request.student_id,
                status="active"
            )
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            logger.info(f"✅ Database user created: {user_id}")
        except Exception as db_err:
            await db.rollback()
            logger.error(f"❌ Failed to create database user: {db_err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account in database"
            )
        
        # Create initial user profile with academic data
        profile_data = {
            "user_id": user_id,
            "student_id": request.student_id,
            "major": request.major,
            "concentration": request.concentration,
            "classification": request.classification,
            "expected_graduation": request.expected_graduation,
            "gpa": None,
            "has_degree_works": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        file_storage.save_user_profile(user_id, profile_data)
        logger.info(f"📋 Created profile for user: {user_id}")
        
        # Generate JWT token
        token_data = {
            "sub": user_data["username"],
            "user_id": user_id,
            "email": user_data["email"],
            "role": user_data["role"]
        }
        
        access_token = SecurityService.create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Create initial chat thread
        initial_thread = {
            "thread_id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Welcome to Morgan AI",
            "messages": [
                {
                    "message_id": str(uuid.uuid4()),
                    "role": "assistant",
                    "content": f"Hello {user_data['full_name']}! 👋 Welcome to Morgan AI Assistant. I'm here to help you with anything related to Morgan State University's Computer Science program. You can ask me about courses, advising, internships, campus resources, and much more!",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "message_count": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        file_storage.save_chat_thread(user_id, initial_thread["thread_id"], initial_thread)
        
        logger.info(f"✅ New user created: {request.email} (ID: {user_id})")
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "user_id": user_id,
                "username": user_data["username"],
                "email": user_data["email"],
                "full_name": user_data["full_name"],
                "role": user_data["role"],
                "student_id": request.student_id,
                "major": request.major,
                "concentration": request.concentration,
                "classification": request.classification,
                "expected_graduation": request.expected_graduation,
                "has_degree_works": False,
                "chat_history_count": 1,
                "active_thread_id": initial_thread["thread_id"],
                "created_at": user_data["created_at"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Signup error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account. Please try again."
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    file_storage = Depends(get_file_storage),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user from file storage and return JWT token
    Loads user data and creates new clean chat session
    """
    try:
        # Find user by email in file storage
        user_data = file_storage.find_user_by_email(request.email)
        
        if not user_data:
            logger.warning(f"❌ Login attempt with non-existent email: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        file_user_id = user_data.get("user_id")
        logger.info(f"🔍 Found user: {user_data.get('username')} (File ID: {file_user_id})")
        
        # Get database user_id by email
        db_user_query = select(DBUser).where(DBUser.email == request.email)
        db_result = await db.execute(db_user_query)
        db_user = db_result.scalar_one_or_none()
        
        if not db_user:
            logger.error(f"❌ User exists in file storage but not in database: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User data inconsistency. Please contact support."
            )
        
        user_id = str(db_user.user_id)
        logger.info(f"✅ Database user_id: {user_id}")
        
        # Check account status
        if user_data.get("status") != "active":
            logger.warning(f"❌ Login attempt with {user_data.get('status')} account: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is {user_data.get('status')}. Please contact support."
            )
        
        # Verify password (bcrypt comparison)
        logger.info(f"🔐 Verifying password for user: {user_data.get('username')}")
        password_valid = SecurityService.verify_password(request.password, user_data["password_hash"])
        
        if not password_valid:
            logger.warning(f"❌ Login attempt with wrong password for: {request.email}")
            logger.debug(f"Password hash stored: {user_data['password_hash'][:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        logger.info(f"✅ Password verified successfully for: {user_data.get('username')}")
        
        # Check role matches if specified
        requested_role = "admin" if request.role == "admin" else "student"
        if user_data.get("role") != requested_role:
            logger.warning(f"❌ Login attempt with wrong role: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {request.role} role required"
            )
        
        # Update last login in file storage
        user_data["last_login"] = datetime.utcnow().isoformat()
        user_data["updated_at"] = datetime.utcnow().isoformat()
        file_storage.save_user_info(file_user_id, user_data)
        
        # Generate JWT token with DATABASE user_id
        token_data = {
            "sub": user_data["username"],
            "user_id": user_id,  # Use database user_id, not file storage user_id
            "email": user_data["email"],
            "role": user_data["role"]
        }
        
        access_token = SecurityService.create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Get user's chat threads from database (not file storage)
        from app.core import db_operations
        db_threads = await db_operations.get_user_chat_threads(db=db, user_id=user_id, limit=10)
        chat_threads = [
            {
                "thread_id": str(t.thread_id),
                "title": t.title or "New Chat",
                "message_count": t.message_count,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in db_threads
        ]
        
        # Get Degree Works status
        degree_works_files = file_storage.get_user_degree_works_files(file_user_id)
        has_degree_works = len(degree_works_files) > 0
        
        # Load user profile for additional info
        profile = file_storage.load_user_profile(user_id) or {}
        
        # Create new active chat thread for this session
        new_thread_id = str(uuid.uuid4())
        new_thread = {
            "thread_id": new_thread_id,
            "user_id": user_id,
            "title": "New Chat",
            "messages": [],
            "message_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        file_storage.save_chat_thread(user_id, new_thread_id, new_thread)
        
        # Load DegreeWorks analysis data if available
        degree_works_data = None
        if has_degree_works and len(degree_works_files) > 0:
            latest_dw = degree_works_files[0]
            degree_works_data = latest_dw.get('parsed_data')
        
        logger.info(f"✅ User logged in: {request.email} (ID: {user_id})")
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "user_id": user_id,
                "username": user_data["username"],
                "email": user_data["email"],
                "full_name": user_data["full_name"],
                "role": user_data["role"],
                "student_id": user_data.get("student_id") or profile.get("student_id"),
                "major": profile.get("major"),
                "concentration": profile.get("concentration"),
                "classification": profile.get("classification"),
                "expected_graduation": profile.get("expected_graduation"),
                "gpa": profile.get("gpa"),
                "has_degree_works": has_degree_works,
                "degree_works_data": degree_works_data,
                "chat_history_count": len(chat_threads),
                "chat_threads": [
                    {
                        "thread_id": t.get("thread_id"),
                        "title": t.get("title", "Untitled Chat"),
                        "message_count": t.get("message_count", 0),
                        "updated_at": t.get("updated_at"),
                        "is_active": t.get("is_active", False)
                    } for t in chat_threads
                ],
                "active_thread_id": new_thread_id,
                "last_login": user_data.get("last_login"),
                "created_at": user_data.get("created_at")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.post("/logout")
async def logout(
    http_request: Request,
    current_user: Dict = Depends(SecurityService.get_current_user),
    file_storage = Depends(get_file_storage)
):
    """
    Logout user - deactivates current chat threads, saves state
    Frontend should clear localStorage and redirect to login
    """
    try:
        user_id = current_user["user_id"]
        
        # Deactivate all active threads (marks them as inactive)
        threads = file_storage.get_user_chat_threads(user_id, limit=100)
        for thread_info in threads:
            thread_data = file_storage.load_chat_thread(user_id, thread_info['thread_id'])
            if thread_data and thread_data.get('is_active'):
                thread_data['is_active'] = False
                thread_data['updated_at'] = datetime.utcnow().isoformat()
                file_storage.save_chat_thread(user_id, thread_info['thread_id'], thread_data)
        
        logger.info(f"✅ User logged out: {current_user['username']} (ID: {user_id})")
        
        return {
            "success": True,
            "message": "Logged out successfully",
            "user_id": user_id,
            "chat_saved": True,
            "logged_out_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(SecurityService.get_current_user),
    file_storage = Depends(get_file_storage)
):
    """
    Get current authenticated user information from file storage
    Returns complete user profile including Degree Works status
    """
    try:
        user_id = current_user["user_id"]
        
        # Load user info from file
        user_data = file_storage.load_user_info(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Load profile
        profile = file_storage.load_user_profile(user_id) or {}
        
        # Get Degree Works status and data
        degree_works_files = file_storage.get_user_degree_works_files(user_id)
        has_degree_works = len(degree_works_files) > 0
        degree_works_data = None
        if has_degree_works and len(degree_works_files) > 0:
            latest_dw = degree_works_files[0]
            degree_works_data = latest_dw.get('parsed_data')
        
        # Get chat statistics
        chat_threads = file_storage.get_user_chat_threads(user_id, limit=20)
        
        return {
            "user_id": user_id,
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "full_name": user_data.get("full_name"),
            "role": user_data.get("role"),
            "status": user_data.get("status", "active"),
            "student_id": user_data.get("student_id") or profile.get("student_id"),
            "major": profile.get("major"),
            "concentration": profile.get("concentration"),
            "classification": profile.get("classification"),
            "expected_graduation": profile.get("expected_graduation"),
            "gpa": profile.get("gpa"),
            "degree_works_uploaded": has_degree_works,
            "degree_works_data": degree_works_data,
            "total_chats": len(chat_threads),
            "chat_threads": [
                {
                    "thread_id": t.get("thread_id"),
                    "title": t.get("title", "Untitled Chat"),
                    "message_count": t.get("message_count", 0),
                    "updated_at": t.get("updated_at"),
                    "is_active": t.get("is_active", False)
                } for t in chat_threads
            ],
            "created_at": user_data.get("created_at"),
            "last_login": user_data.get("last_login")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


class UpdateProfileRequest(BaseModel):
    """Request model for updating user profile"""
    student_id: Optional[str] = None
    major: Optional[str] = None
    concentration: Optional[str] = None
    classification: Optional[str] = None
    expected_graduation: Optional[str] = None


@router.put("/profile")
async def update_user_profile(
    profile_update: UpdateProfileRequest,
    current_user: dict = Depends(SecurityService.get_current_user),
    file_storage = Depends(get_file_storage)
):
    """
    Update user profile information
    Allows users to update their academic information
    """
    try:
        user_id = current_user["user_id"]
        
        # Load existing profile or create new one
        profile = file_storage.load_user_profile(user_id) or {}
        
        # Update fields (only if provided)
        if profile_update.student_id is not None:
            profile["student_id"] = profile_update.student_id
        if profile_update.major is not None:
            profile["major"] = profile_update.major
        if profile_update.concentration is not None:
            profile["concentration"] = profile_update.concentration
        if profile_update.classification is not None:
            profile["classification"] = profile_update.classification
        if profile_update.expected_graduation is not None:
            profile["expected_graduation"] = profile_update.expected_graduation
        
        # Save updated profile
        profile["user_id"] = user_id
        profile["updated_at"] = datetime.utcnow().isoformat()
        
        success = file_storage.save_user_profile(user_id, profile)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
        
        logger.info(f"✅ Profile updated for user: {user_id}")
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "profile": profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


# OAuth endpoints (stubs for future implementation)
@router.get("/oauth/{provider}/start")
async def oauth_start(provider: str, redirect: str = "/"):
    """Initiate OAuth flow - stub for future implementation"""
    supported_providers = ["google", "apple", "microsoft", "phone"]
    
    if provider not in supported_providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )
    
    logger.info(f"OAuth start requested for provider: {provider}")
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"{provider.capitalize()} OAuth is not configured. Please use email/password login."
    )


@router.get("/oauth/{provider}/callback")
async def oauth_callback(provider: str, code: Optional[str] = None):
    """Handle OAuth provider callback - stub for future implementation"""
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code missing"
        )
    
    logger.info(f"OAuth callback from {provider}")
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"{provider.capitalize()} OAuth callback is not implemented"
    )
