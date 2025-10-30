import os
from typing import List, Optional
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "Morgan AI Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./morgan_chatbot.db",
        env="DATABASE_URL"
    )
    
    # Security
    SECRET_KEY: str = Field(default="change_this_secret_key_in_production", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OpenAI
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", env="OPENAI_EMBEDDING_MODEL")
    OPENAI_MAX_TOKENS: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    OPENAI_TEMPERATURE: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # OpenAI Realtime API
    OPENAI_REALTIME_ENABLED: bool = Field(default=True, env="OPENAI_REALTIME_ENABLED")
    OPENAI_TTS_MODEL: str = Field(default="tts-1", env="OPENAI_TTS_MODEL")
    OPENAI_TTS_VOICE: str = Field(default="alloy", env="OPENAI_TTS_VOICE")
    OPENAI_STT_MODEL: str = Field(default="whisper-1", env="OPENAI_STT_MODEL")
    TTS_VOICE: str = Field(default="alloy", env="TTS_VOICE")
    TTS_SPEED: float = Field(default=1.0, env="TTS_SPEED")
    
    # Pinecone (Updated for v5.0+ - PINECONE_ENVIRONMENT is now optional)
    PINECONE_API_KEY: str = Field(default="", env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")  # Not needed in v5.0+
    PINECONE_INDEX_NAME: str = Field(default="morgan-chatbot", env="PINECONE_INDEX_NAME")
    PINECONE_DIMENSION: int = Field(default=1536, env="PINECONE_DIMENSION")
    PINECONE_METRIC: str = Field(default="cosine", env="PINECONE_METRIC")
    
    # GroupMe Integration
    GROUPME_BOT_ID: Optional[str] = Field(default=None, env="GROUPME_BOT_ID")
    GROUPME_ACCESS_TOKEN: Optional[str] = Field(default=None, env="GROUPME_ACCESS_TOKEN")
    GROUPME_GROUP_ID: Optional[str] = Field(default=None, env="GROUPME_GROUP_ID")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "https://morgan-chatbot.vercel.app"
        ],
        env="CORS_ORIGINS"
    )
    
    # File paths
    KNOWLEDGE_BASE_PATH: str = Field(
        default="data/knowledge_base",
        env="KNOWLEDGE_BASE_PATH"
    )
    UPLOAD_PATH: str = Field(
        default="uploads",
        env="UPLOAD_PATH"
    )
    
    # Directory paths as Path objects (for ingestion script compatibility)
    @property
    def KNOWLEDGE_BASE_DIR(self) -> Path:
        """Get knowledge base directory as Path object"""
        return Path(self.KNOWLEDGE_BASE_PATH)
    
    @property
    def PROCESSED_DIR(self) -> Path:
        """Get processed data directory as Path object"""
        return Path("data/processed")
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=30, env="RATE_LIMIT_PER_MINUTE")
    
    # Admin
    ADMIN_USERNAME: str = Field(default="admin", env="ADMIN_USERNAME")
    ADMIN_PASSWORD: str = Field(default="change_this_password", env="ADMIN_PASSWORD")
    ADMIN_EMAIL: str = Field(default="admin@morgan.edu", env="ADMIN_EMAIL")
    
    # Morgan State specific
    UNIVERSITY_NAME: str = "Morgan State University"
    DEPARTMENT: str = "Computer Science Department"
    CONTACT_EMAIL: str = "cs@morgan.edu"
    WEBSITE_URL: str = "https://www.morgan.edu/computer-science"
    
    # Feature flags
    ENABLE_VOICE: bool = Field(default=True, env="ENABLE_VOICE")
    ENABLE_INTERNSHIPS: bool = Field(default=True, env="ENABLE_INTERNSHIPS")
    ENABLE_ADMIN: bool = Field(default=True, env="ENABLE_ADMIN")
    ENABLE_ANALYTICS: bool = Field(default=False, env="ENABLE_ANALYTICS")
    
    # Cache
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
    # RAG Configuration
    CHUNK_SIZE: int = Field(default=1000, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=200, env="CHUNK_OVERLAP")
    TOP_K_RESULTS: int = Field(default=5, env="TOP_K_RESULTS")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = Field(default="morgan_chatbot.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def get_knowledge_base_files(self) -> List[str]:
        """Get list of knowledge base JSON files"""
        return [
            "department_info.json",
            "academics.json",
            "career_resources.json",
            "registration.json",
            "deadlines.json"
        ]
    
    def get_openai_config(self) -> dict:
        """Get OpenAI configuration"""
        return {
            "api_key": self.OPENAI_API_KEY,
            "model": self.OPENAI_MODEL,
            "embedding_model": self.OPENAI_EMBEDDING_MODEL,
            "max_tokens": self.OPENAI_MAX_TOKENS,
            "temperature": self.OPENAI_TEMPERATURE,
            "tts_model": self.OPENAI_TTS_MODEL,
            "tts_voice": self.OPENAI_TTS_VOICE,
            "stt_model": self.OPENAI_STT_MODEL
        }
    
    def get_pinecone_config(self) -> dict:
        """Get Pinecone configuration"""
        config = {
            "api_key": self.PINECONE_API_KEY,
            "index_name": self.PINECONE_INDEX_NAME,
            "dimension": self.PINECONE_DIMENSION,
            "metric": self.PINECONE_METRIC
        }
        # Only include environment if it's set (for backward compatibility)
        if self.PINECONE_ENVIRONMENT:
            config["environment"] = self.PINECONE_ENVIRONMENT
        return config


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Uses lru_cache to ensure settings are only loaded once
    """
    return Settings()

settings = get_settings()