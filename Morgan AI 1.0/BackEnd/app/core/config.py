from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Morgan AI Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Pinecone Configuration
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX_NAME: str = "morgan-ai-knowledge"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_USERNAME: str = "admin"
    
    # CHANGED: Accept either password or hash
    ADMIN_PASSWORD: Optional[str] = None
    ADMIN_PASSWORD_HASH: Optional[str] = None
    
    # Database Settings
    DATABASE_URL: Optional[str] = None
    
    # Chat Settings
    MAX_THREAD_HISTORY: int = 50
    MAX_RESPONSE_TOKENS: int = 500
    CHAT_TEMPERATURE: float = 0.7
    
    # Voice Settings
    ENABLE_VOICE_FEATURES: bool = True
    TTS_VOICE: str = "alloy"
    
    # Knowledge Base
    KNOWLEDGE_BASE_PATH: str = "data/knowledge_base"
    TRAINING_DATA_FILE: str = "training_data.txt"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # ADDED: Auto-hash password if provided
        if self.ADMIN_PASSWORD and not self.ADMIN_PASSWORD_HASH:
            self.ADMIN_PASSWORD_HASH = pwd_context.hash(self.ADMIN_PASSWORD)
        
        # ADDED: Support CORS_ORIGINS from env
        cors_origins = os.getenv("CORS_ORIGINS", "")
        if cors_origins:
            self.ALLOWED_ORIGINS.extend([
                origin.strip() for origin in cors_origins.split(",") if origin.strip()
            ])
        
        # Add extra origins
        extra_origins = os.getenv("EXTRA_ALLOWED_ORIGINS", "")
        if extra_origins:
            self.ALLOWED_ORIGINS.extend([
                origin.strip() for origin in extra_origins.split(",") if origin.strip()
            ])
    
    def validate_settings(self) -> bool:
        """Validate that all required settings are present"""
        required_fields = [
            "OPENAI_API_KEY",
            "PINECONE_API_KEY",
            "PINECONE_ENVIRONMENT",
            "SECRET_KEY"
        ]
        
        # CHANGED: Require either password or hash
        if not self.ADMIN_PASSWORD_HASH:
            required_fields.append("ADMIN_PASSWORD_HASH or ADMIN_PASSWORD")
        
        missing_fields = []
        for field in required_fields:
            if not getattr(self, field, None):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
        
        return True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # ADDED: Allow extra fields
        extra = "ignore"

# Global settings instance
settings = Settings()

# Validate on import
try:
    settings.validate_settings()
except ValueError as e:
    import logging
    logging.error(f"Configuration error: {str(e)}")
    raise