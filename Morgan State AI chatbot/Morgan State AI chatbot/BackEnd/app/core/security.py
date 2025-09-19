from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token bearer
security = HTTPBearer()

class SecurityManager:
    """Handles authentication and authorization for the Morgan AI Chatbot"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token for admin authentication"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access_token"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def authenticate_admin(username: str, password: str) -> bool:
        """Authenticate admin user"""
        if username != settings.ADMIN_USERNAME:
            return False
        return SecurityManager.verify_password(password, settings.ADMIN_PASSWORD_HASH)

# Dependency for admin authentication
async def get_current_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to verify admin access"""
    token = credentials.credentials
    payload = SecurityManager.verify_token(token)
    
    username: str = payload.get("sub")
    if username is None or username != settings.ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate admin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"username": username, "role": "admin"}

# Rate limiting helper
class RateLimiter:
    """Simple in-memory rate limiter for API endpoints"""
    
    def __init__(self):
        self.requests = {}  # {ip: [(timestamp, count), ...]}
        self.max_requests_per_minute = 60
        self.max_requests_per_hour = 1000
    
    def is_allowed(self, ip: str) -> bool:
        """Check if request is allowed based on rate limits"""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        if ip not in self.requests:
            self.requests[ip] = []
        
        # Clean old requests
        self.requests[ip] = [
            (timestamp, count) for timestamp, count in self.requests[ip]
            if timestamp > hour_ago
        ]
        
        # Count recent requests
        minute_requests = sum(
            count for timestamp, count in self.requests[ip]
            if timestamp > minute_ago
        )
        hour_requests = sum(count for timestamp, count in self.requests[ip])
        
        # Check limits
        if minute_requests >= self.max_requests_per_minute:
            return False
        if hour_requests >= self.max_requests_per_hour:
            return False
        
        # Add current request
        self.requests[ip].append((now, 1))
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()