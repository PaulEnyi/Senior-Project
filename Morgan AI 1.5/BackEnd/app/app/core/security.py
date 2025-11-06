from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
import logging
import hashlib

logger = logging.getLogger(__name__)

# Password hashing with bcrypt (limits passwords to 72 bytes via SHA256 pre-hash)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

class SecurityService:
    """Handle authentication and authorization"""
    
    @staticmethod
    def _normalize_password(password: str) -> str:
        """
        Normalize password to avoid bcrypt 72-byte limit.
        Uses SHA256 to create a fixed-length hash that's safe for bcrypt.
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        normalized = SecurityService._normalize_password(plain_password)
        return pwd_context.verify(normalized, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        normalized = SecurityService._normalize_password(password)
        return pwd_context.hash(normalized)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError as e:
            logger.error(f"JWT decode error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
        """Get current user from JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = SecurityService.decode_token(token)
            username: str = payload.get("sub")
            
            if username is None:
                raise credentials_exception
                
            return {
                "username": username,
                "user_id": payload.get("user_id"),
                "role": payload.get("role", "user")
            }
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise credentials_exception
    
    @staticmethod
    async def get_current_admin(current_user: Dict = Depends(get_current_user)) -> Dict[str, Any]:
        """Verify current user is an admin"""
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    
    @staticmethod
    def verify_admin_credentials(username: str, password: str) -> bool:
        """Verify admin credentials"""
        # In production, this should check against a database
        return (
            username == settings.ADMIN_USERNAME and 
            password == settings.ADMIN_PASSWORD
        )

# Create security service instance
security_service = SecurityService()