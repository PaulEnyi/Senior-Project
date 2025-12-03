"""
Database Service Layer for Morgan AI Chatbot
Provides async SQLAlchemy session management, connection pooling, and CRUD operations
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.models.database import Base

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Manages database connections and provides session management
    Implements connection pooling and async operations for optimal performance
    """
    
    def __init__(self):
        """Initialize database service with connection pooling"""
        self.engine = None
        self.async_session_maker = None
        self._is_initialized = False
        
    async def initialize(self):
        """
        Initialize database connection and create tables if they don't exist
        Called on application startup
        """
        if self._is_initialized:
            logger.warning("Database service already initialized")
            return
            
        try:
            # Convert DATABASE_URL to async format
            database_url = self._get_async_database_url()
            
            # Create async engine with connection pooling
            self.engine = create_async_engine(
                database_url,
                echo=settings.DEBUG,  # Log SQL queries in debug mode
                pool_size=20,  # Maximum number of connections in pool
                max_overflow=10,  # Additional connections that can be created
                pool_timeout=30,  # Timeout for getting connection from pool
                pool_recycle=3600,  # Recycle connections after 1 hour
                pool_pre_ping=True,  # Verify connections before using
            )
            
            # Create async session factory
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,  # Don't expire objects after commit
                autocommit=False,
                autoflush=False,
            )
            
            # Create all tables if they don't exist
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                
            self._is_initialized = True
            logger.info("✓ Database service initialized successfully")
            logger.info(f"Database URL: {self._mask_password(database_url)}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database service: {str(e)}")
            raise
    
    async def close(self):
        """
        Close database connections
        Called on application shutdown
        """
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")
            self._is_initialized = False
    
    def _get_async_database_url(self) -> str:
        """
        Convert DATABASE_URL to async format
        PostgreSQL: postgresql:// -> postgresql+asyncpg://
        SQLite: sqlite:/// -> sqlite+aiosqlite:///
        """
        database_url = settings.DATABASE_URL
        
        if database_url.startswith("postgresql://"):
            # Convert to asyncpg driver
            return database_url.replace("postgresql://", "postgresql+asyncpg://")
        elif database_url.startswith("sqlite://"):
            # Convert to aiosqlite driver
            return database_url.replace("sqlite://", "sqlite+aiosqlite://")
        else:
            # Already async or unsupported
            return database_url
    
    def _mask_password(self, url: str) -> str:
        """Mask password in database URL for logging"""
        try:
            if "@" in url:
                parts = url.split("@")
                credentials = parts[0].split("://")[1]
                if ":" in credentials:
                    user = credentials.split(":")[0]
                    return url.replace(credentials, f"{user}:****")
            return url
        except Exception:
            return url
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get async database session with automatic cleanup
        
        Usage:
            async with db_service.get_session() as session:
                result = await session.execute(query)
                await session.commit()
        """
        if not self._is_initialized:
            raise RuntimeError("Database service not initialized. Call initialize() first.")
        
        session = self.async_session_maker()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()
    
    async def health_check(self) -> bool:
        """
        Check database connectivity
        Returns True if database is reachable, False otherwise
        """
        try:
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
    
    async def get_table_counts(self) -> dict:
        """
        Get row counts for all tables
        Useful for monitoring and debugging
        """
        try:
            async with self.get_session() as session:
                counts = {}
                
                # Query each table
                tables = ['users', 'degree_works_files', 'chat_threads', 'chat_messages', 
                         'user_sessions', 'audit_logs']
                
                for table in tables:
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    counts[table] = count
                
                return counts
        except Exception as e:
            logger.error(f"Error getting table counts: {str(e)}")
            return {}


# Global database service instance
db_service = DatabaseService()


# Dependency for FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting database session
    
    Usage in routes:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with db_service.get_session() as session:
        yield session
