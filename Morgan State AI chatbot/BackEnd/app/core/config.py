from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Morgan AI Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
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
    ADMIN_PASSWORD_HASH: str  # bcrypt hash of admin password
    
    # Database Settings
    DATABASE_URL: Optional[str] = None
    
    # Chat Settings
    MAX_THREAD_HISTORY: int = 50
    MAX_RESPONSE_TOKENS: int = 500
    CHAT_TEMPERATURE: float = 0.7
    
    # Voice Settings
    ENABLE_VOICE_FEATURES: bool = True
    TTS_VOICE: str = "alloy"  # OpenAI TTS voice
    
    # Knowledge Base
    KNOWLEDGE_BASE_PATH: str = "data/knowledge_base"
    TRAINING_DATA_FILE: str = "training_data.txt"
    
    # CORS Settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()