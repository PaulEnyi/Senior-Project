"""
Authentication Routes with PostgreSQL Database Integration
Handles user signup, login, logout with secure password hashing and session management
All user data is stored in the database - NO plain text passwords
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
import uuid
import logging

from app.core.security import SecurityService
from app.core.config import settings
from app.core.database import get_db
from app.core.db_operations import (
    create_user, get_user_by_email, get_user_by_username,
    update_user_last_login, create_user_session, 
    revoke_all_user_sessions, get_session_by_token,
    revoke_user_session, create_audit_log,
    create_chat_thread, deactivate_user_threads
)
from app.models.database import UserRole, UserStatus

logger = logging.getLogger(__name__)

router = APIRouter()


class SignupRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: str = Field(..., min_length=6)
    role: str = Field(default="user")
    student_id: Optional[str] = None  # Optional student ID field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = Field(default="user")


class LogoutRequest(BaseModel):
    session_id: Optional[str] = None  # Optional session ID to logout specific session


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, http_request: Request, db: AsyncSession = Depends(get_db)):
    """
    Create a new user account with secure password hashing
    Stores all data in PostgreSQL database with proper encryption
    """
    try:
        # Check if user already exists by email
        existing_user = await get_user_by_email(db, request.email)
        if existing_user:
            await create_audit_log(
                db, "signup", "User registration attempt", "failure",
                event_data={"email": request.email, "reason": "email_exists"},
                ip_address=http_request.client.host if http_request.client else None
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_username = await get_user_by_username(db, request.username)
        if existing_username:
            await create_audit_log(
                db, "signup", "User registration attempt", "failure",
                event_data={"username": request.username, "reason": "username_exists"},
                ip_address=http_request.client.host if http_request.client else None
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Hash the password (NEVER store plain text)
        hashed_password = SecurityService.get_password_hash(request.password)
        
        # Map student/faculty roles to "user", keep admin as "admin"
        user_role = UserRole.ADMIN if request.role == "admin" else UserRole.STUDENT
        
        # Create user in database
        user = await create_user(
            db=db,
            email=request.email,
            username=request.username,
            password_hash=hashed_password,
            full_name=request.full_name,
            role=user_role,
            student_id=request.student_id
        )
        
        # Generate JWT token
        token_data = {
            "sub": user.username,
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.value
        }
        
        access_token = SecurityService.create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Create session record
        await create_user_session(
            db=db,
            user_id=user.user_id,
            access_token=access_token,
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            ip_address=http_request.client.host if http_request.client else None,
            user_agent=http_request.headers.get("user-agent")
        )
        
        # Create initial chat thread for the user
        await create_chat_thread(
            db=db,
            user_id=user.user_id,
            title="Welcome to Morgan AI",
            is_active=True
        )
        
        # Create audit log
        await create_audit_log(
            db, "signup", "User registered successfully", "success",
            user_id=user.user_id,
            event_data={"email": user.email, "username": user.username, "role": user.role.value},
            ip_address=http_request.client.host if http_request.client else None,
            user_agent=http_request.headers.get("user-agent")
        )
        
        await db.commit()
        
        logger.info(f"✓ New user registered: {request.email} (ID: {user.user_id})")
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "student_id": user.student_id,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, http_request: Request, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT token
    Loads user data from database and creates new clean chat session
    """
    try:
        # Find user by email
        user = await get_user_by_email(db, request.email)
        
        if not user:
            await create_audit_log(
                db, "login", "Login attempt", "failure",
                event_data={"email": request.email, "reason": "user_not_found"},
                ip_address=http_request.client.host if http_request.client else None
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if account is active
        if user.status != UserStatus.ACTIVE:
            await create_audit_log(
                db, "login", "Login attempt", "failure",
                user_id=user.user_id,
                event_data={"email": request.email, "reason": f"account_{user.status.value}"},
                ip_address=http_request.client.host if http_request.client else None
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is {user.status.value}"
            )
        
        # Verify password (compares hashed passwords securely)
        if not SecurityService.verify_password(request.password, user.password_hash):
            await create_audit_log(
                db, "login", "Login attempt", "failure",
                user_id=user.user_id,
                event_data={"email": request.email, "reason": "invalid_password"},
                ip_address=http_request.client.host if http_request.client else None
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check role matches if specified (map student/faculty to user for comparison)
        requested_role = UserRole.ADMIN if request.role == "admin" else UserRole.STUDENT
        if requested_role and user.role != requested_role:
            await create_audit_log(
                db, "login", "Login attempt", "failure",
                user_id=user.user_id,
                event_data={"email": request.email, "reason": "role_mismatch"},
                ip_address=http_request.client.host if http_request.client else None
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {request.role} role required"
            )
        
        # Generate JWT token
        token_data = {
            "sub": user.username,
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.value
        }
        
        access_token = SecurityService.create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Create session record
        session = await create_user_session(
            db=db,
            user_id=user.user_id,
            access_token=access_token,
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            ip_address=http_request.client.host if http_request.client else None,
            user_agent=http_request.headers.get("user-agent")
        )
        
        # Update last login timestamp
        await update_user_last_login(db, user.user_id)
        
        # Deactivate any existing active threads (clean slate on login)
        await deactivate_user_threads(db, user.user_id)
        
        # Create new clean chat thread for this session
        new_thread = await create_chat_thread(
            db=db,
            user_id=user.user_id,
            title="New Chat",
            is_active=True
        )
        
        # Create audit log
        await create_audit_log(
            db, "login", "User logged in successfully", "success",
            user_id=user.user_id,
            event_data={
                "email": user.email, 
                "session_id": session.session_id,
                "new_thread_id": new_thread.thread_id
            },
            ip_address=http_request.client.host if http_request.client else None,
            user_agent=http_request.headers.get("user-agent")
        )
        
        await db.commit()
        
        logger.info(f"✓ User logged in: {request.email} (Session: {session.session_id})")
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "student_id": user.student_id,
                "major": user.major,
                "classification": user.classification,
                "expected_graduation": user.expected_graduation,
                "session_id": session.session_id,
                "active_thread_id": new_thread.thread_id,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout")
async def logout(
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(SecurityService.get_current_user)
):
    """
    Logout user - saves current chat, revokes session, deactivates threads
    Called by frontend before clearing localStorage
    """
    try:
        user_id = current_user["user_id"]
        
        # Get the access token from Authorization header
        auth_header = http_request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header"
            )
        
        access_token = auth_header.split(" ")[1]
        
        # Get session from token
        session = await get_session_by_token(db, access_token)
        
        if session:
            # Revoke the session
            await revoke_user_session(db, session.session_id)
            logger.info(f"Session {session.session_id} revoked for user {user_id}")
        
        # Deactivate all active chat threads (save state)
        await deactivate_user_threads(db, user_id)
        
        # Create audit log
        await create_audit_log(
            db, "logout", "User logged out", "success",
            user_id=user_id,
            event_data={
                "session_id": session.session_id if session else None,
                "username": current_user["username"]
            },
            ip_address=http_request.client.host if http_request.client else None,
            user_agent=http_request.headers.get("user-agent")
        )
        
        await db.commit()
        
        logger.info(f"✓ User logged out: {current_user['username']} (ID: {user_id})")
        
        return {
            "success": True,
            "message": "Logged out successfully",
            "user_id": user_id,
            "chat_saved": True,  # All threads automatically deactivated and saved
            "logged_out_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


# OAuth Provider Start Endpoints (Stub for future implementation)
@router.get("/oauth/{provider}/start")
async def oauth_start(provider: str, redirect: str = "/"):
    """
    Initiate OAuth flow with provider (Google, Apple, Microsoft)
    Currently returns a stub response; implement real OAuth when provider credentials are configured
    """
    supported_providers = ["google", "apple", "microsoft", "phone"]
    
    if provider not in supported_providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )
    
    # In production, redirect to provider's OAuth URL with client_id, redirect_uri, etc.
    logger.info(f"OAuth start requested for provider: {provider}")
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"{provider.capitalize()} OAuth is not configured. Please use email/password login or contact admin to enable social login."
    )


@router.get("/oauth/{provider}/callback")
async def oauth_callback(provider: str, code: Optional[str] = None, state: Optional[str] = None):
    """
    Handle OAuth provider callback
    Exchange authorization code for access token and create/login user
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code missing"
        )
    
    # In production:
    # 1. Exchange code for access token with provider
    # 2. Fetch user info from provider
    # 3. Create or update user in database
    # 4. Generate JWT token
    # 5. Redirect to frontend callback with token
    
    logger.info(f"OAuth callback from {provider} with code (truncated): {code[:10]}...")
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"{provider.capitalize()} OAuth callback is not implemented"
    )


@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(SecurityService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user information from database
    Returns complete user profile including Degree Works status
    """
    try:
        user_id = current_user["user_id"]
        
        # Import here to avoid circular dependency
        from app.core.db_operations import get_user_by_id, get_latest_degree_works
        
        # Get full user record from database
        user = await get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get latest Degree Works if available
        degree_works = await get_latest_degree_works(db, user_id)
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "status": user.status.value,
            "student_id": user.student_id,
            "major": user.major,
            "classification": user.classification,
            "expected_graduation": user.expected_graduation,
            "degree_works_uploaded": degree_works is not None,
            "degree_works_processed": degree_works.is_processed if degree_works else False,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )
