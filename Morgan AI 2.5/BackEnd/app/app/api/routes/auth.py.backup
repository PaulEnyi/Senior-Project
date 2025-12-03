from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
import uuid
import logging

from app.core.security import SecurityService
from app.core.config import settings
from app.models.user import UserRole, UserStatus

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory user store (replace with database in production)
users_db = {}

class SignupRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: str = Field(..., min_length=6)
    role: str = Field(default="user")

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
async def signup(request: SignupRequest):
    """
    Create a new user account with JWT token
    """
    try:
        # Check if user already exists
        if request.email in users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash the password
        hashed_password = SecurityService.get_password_hash(request.password)
        
        # Create user ID
        user_id = str(uuid.uuid4())
        
        # Store user
        # Map student/faculty roles to "user", keep admin as "admin"
        user_role = "admin" if request.role == "admin" else "user"
        
        users_db[request.email] = {
            "user_id": user_id,
            "email": request.email,
            "username": request.username,
            "full_name": request.full_name,
            "hashed_password": hashed_password,
            "role": user_role,
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Generate JWT token
        token_data = {
            "sub": request.username,
            "user_id": user_id,
            "email": request.email,
            "role": users_db[request.email]["role"]
        }
        
        access_token = SecurityService.create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"New user registered: {request.email}")
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "user_id": user_id,
                "username": request.username,
                "email": request.email,
                "full_name": request.full_name,
                "role": users_db[request.email]["role"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token
    """
    try:
        # Find user
        user = users_db.get(request.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not SecurityService.verify_password(request.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check role matches if specified (map student/faculty to user for comparison)
        requested_role = "admin" if request.role == "admin" else "user"
        if requested_role and user["role"] != requested_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {request.role} role required"
            )
        
        # Generate JWT token
        token_data = {
            "sub": user["username"],
            "user_id": user["user_id"],
            "email": user["email"],
            "role": user["role"]
        }
        
        access_token = SecurityService.create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"User logged in: {request.email}")
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user.get("full_name"),
                "role": user["role"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

# OAuth Provider Start Endpoints
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
    # For now, return a message indicating OAuth is not yet configured
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
async def get_current_user_info(current_user: dict = Depends(SecurityService.get_current_user)):
    """
    Get current authenticated user information
    """
    return {
        "user_id": current_user.get("user_id"),
        "username": current_user.get("username"),
        "email": current_user.get("email"),
        "role": current_user.get("role", "user")
    }
