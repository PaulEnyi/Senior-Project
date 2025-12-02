"""
Database CRUD Operations for Morgan AI Chatbot
Provides reusable database operations for all models
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import logging
from app.utils.timing import async_timed

from app.models.database import (
    User, UserRole, UserStatus,
    DegreeWorksFile,
    ChatThread, ChatMessage,
    UserSession, AuditLog
)

logger = logging.getLogger(__name__)


# ==================== USER CRUD OPERATIONS ====================

@async_timed("create_user")
async def create_user(
    db: AsyncSession,
    email: str,
    username: str,
    password_hash: str,
    full_name: Optional[str] = None,
    role: UserRole = UserRole.STUDENT,
    student_id: Optional[str] = None
) -> User:
    """Create a new user account"""
    user = User(
        user_id=str(uuid.uuid4()),
        email=email.lower(),
        username=username,
        password_hash=password_hash,
        full_name=full_name,
        role=role,
        status=UserStatus.ACTIVE,
        student_id=student_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(user)
    await db.flush()
    await db.refresh(user)
    
    logger.info(f"Created user: {user.email} (ID: {user.user_id})")
    return user

@async_timed("create_user_with_id")
async def create_user_with_id(
    db: AsyncSession,
    user_id: str,
    email: str,
    username: str,
    password_hash: str,
    full_name: Optional[str] = None,
    role: UserRole = UserRole.STUDENT,
    student_id: Optional[str] = None
) -> User:
    """Create a user specifying a predetermined user_id (bridge migration)."""
    user = User(
        user_id=user_id,
        email=email.lower(),
        username=username,
        password_hash=password_hash,
        full_name=full_name,
        role=role,
        status=UserStatus.ACTIVE,
        student_id=student_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    logger.info(f"[BRIDGE-AUTO] Created user with provided ID: {user.user_id}")
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email address"""
    result = await db.execute(
        select(User).where(
            and_(
                User.email == email.lower(),
                User.deleted_at.is_(None)
            )
        )
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(
        select(User).where(
            and_(
                User.user_id == user_id,
                User.deleted_at.is_(None)
            )
        )
    )
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username"""
    result = await db.execute(
        select(User).where(
            and_(
                User.username == username,
                User.deleted_at.is_(None)
            )
        )
    )
    return result.scalar_one_or_none()


async def update_user_last_login(db: AsyncSession, user_id: str) -> None:
    """Update user's last login timestamp"""
    await db.execute(
        update(User)
        .where(User.user_id == user_id)
        .values(
            last_login=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    )


async def update_user_profile(
    db: AsyncSession,
    user_id: str,
    **fields
) -> Optional[User]:
    """Update user profile fields"""
    fields['updated_at'] = datetime.utcnow()
    
    await db.execute(
        update(User)
        .where(User.user_id == user_id)
        .values(**fields)
    )
    
    return await get_user_by_id(db, user_id)


# ==================== DEGREE WORKS CRUD OPERATIONS ====================

@async_timed("create_degree_works_file")
async def create_degree_works_file(
    db: AsyncSession,
    user_id: str,
    filename: str,
    file_path: Optional[str] = None,
    file_blob: Optional[bytes] = None,
    file_size: Optional[int] = None,
    file_hash: Optional[str] = None
) -> DegreeWorksFile:
    """Create a new Degree Works file record"""
    degree_works = DegreeWorksFile(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_blob=file_blob,
        file_size=file_size,
        file_hash=file_hash,
        is_processed=False,
        uploaded_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(degree_works)
    await db.flush()
    await db.refresh(degree_works)
    
    logger.info(f"Created Degree Works file for user {user_id}: {filename}")
    return degree_works


async def update_degree_works_parsed_data(
    db: AsyncSession,
    file_id: int,
    parsed_data: Dict[str, Any],
    student_name: Optional[str] = None,
    student_id: Optional[str] = None,
    major: Optional[str] = None,
    classification: Optional[str] = None,
    gpa: Optional[str] = None,
    credits_earned: Optional[int] = None,
    credits_needed: Optional[int] = None
) -> DegreeWorksFile:
    """Update Degree Works file with parsed data"""
    await db.execute(
        update(DegreeWorksFile)
        .where(DegreeWorksFile.id == file_id)
        .values(
            parsed_data=parsed_data,
            student_name=student_name,
            student_id=student_id,
            major=major,
            classification=classification,
            gpa=gpa,
            credits_earned=credits_earned,
            credits_needed=credits_needed,
            is_processed=True,
            processed_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    )
    
    result = await db.execute(
        select(DegreeWorksFile).where(DegreeWorksFile.id == file_id)
    )
    return result.scalar_one()


async def get_latest_degree_works(db: AsyncSession, user_id: str) -> Optional[DegreeWorksFile]:
    """Get the most recent Degree Works file for a user"""
    result = await db.execute(
        select(DegreeWorksFile)
        .where(
            and_(
                DegreeWorksFile.user_id == user_id,
                DegreeWorksFile.deleted_at.is_(None)
            )
        )
        .order_by(desc(DegreeWorksFile.uploaded_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_all_degree_works_for_user(db: AsyncSession, user_id: str) -> List[DegreeWorksFile]:
    """Get all Degree Works files for a user"""
    result = await db.execute(
        select(DegreeWorksFile)
        .where(
            and_(
                DegreeWorksFile.user_id == user_id,
                DegreeWorksFile.deleted_at.is_(None)
            )
        )
        .order_by(desc(DegreeWorksFile.uploaded_at))
    )
    return result.scalars().all()


# ==================== CHAT THREAD CRUD OPERATIONS ====================

@async_timed("create_chat_thread")
async def create_chat_thread(
    db: AsyncSession,
    user_id: str,
    title: Optional[str] = None,
    is_active: bool = True
) -> ChatThread:
    """Create a new chat thread"""
    thread = ChatThread(
        thread_id=str(uuid.uuid4()),
        user_id=user_id,
        title=title or "New Chat",
        is_active=is_active,
        is_archived=False,
        message_count=0,
        thread_metadata={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(thread)
    await db.flush()
    await db.refresh(thread)
    
    logger.info(f"Created chat thread {thread.thread_id} for user {user_id}")
    return thread


async def get_chat_thread(
    db: AsyncSession,
    thread_id: str,
    user_id: Optional[str] = None
) -> Optional[ChatThread]:
    """Get chat thread by ID with optional user validation"""
    conditions = [
        ChatThread.thread_id == thread_id,
        ChatThread.deleted_at.is_(None)
    ]
    
    if user_id:
        conditions.append(ChatThread.user_id == user_id)
    
    result = await db.execute(
        select(ChatThread).where(and_(*conditions))
    )
    return result.scalar_one_or_none()


async def get_user_chat_threads(
    db: AsyncSession,
    user_id: str,
    include_archived: bool = False,
    limit: int = 50
) -> List[ChatThread]:
    """Get all chat threads for a user"""
    conditions = [
        ChatThread.user_id == user_id,
        ChatThread.deleted_at.is_(None)
    ]
    
    if not include_archived:
        conditions.append(ChatThread.is_archived == False)
    
    result = await db.execute(
        select(ChatThread)
        .where(and_(*conditions))
        .order_by(desc(ChatThread.updated_at))
        .limit(limit)
    )
    return result.scalars().all()


async def update_chat_thread(
    db: AsyncSession,
    thread_id: str,
    **fields
) -> Optional[ChatThread]:
    """Update chat thread fields"""
    fields['updated_at'] = datetime.utcnow()
    
    await db.execute(
        update(ChatThread)
        .where(ChatThread.thread_id == thread_id)
        .values(**fields)
    )
    
    return await get_chat_thread(db, thread_id)


async def deactivate_user_threads(db: AsyncSession, user_id: str) -> None:
    """Deactivate all active threads for a user (for logout)"""
    await db.execute(
        update(ChatThread)
        .where(
            and_(
                ChatThread.user_id == user_id,
                ChatThread.is_active == True
            )
        )
        .values(
            is_active=False,
            updated_at=datetime.utcnow()
        )
    )


async def delete_chat_thread(db: AsyncSession, thread_id: str) -> None:
    """Soft delete a chat thread"""
    await db.execute(
        update(ChatThread)
        .where(ChatThread.thread_id == thread_id)
        .values(
            deleted_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    )


# ==================== CHAT MESSAGE CRUD OPERATIONS ====================

@async_timed("create_chat_message")
async def create_chat_message(
    db: AsyncSession,
    thread_id: str,
    role: str,
    content: str,
    token_count: Optional[int] = None,
    model: Optional[str] = None,
    context_used: Optional[Dict] = None,
    sources: Optional[Dict] = None,
    metadata: Optional[Dict] = None
) -> ChatMessage:
    """Create a new chat message"""
    message = ChatMessage(
        message_id=str(uuid.uuid4()),
        thread_id=thread_id,
        role=role,
        content=content,
        token_count=token_count,
        model=model,
        context_used=context_used,
        sources=sources,
        message_metadata=metadata or {},
        created_at=datetime.utcnow()
    )
    
    db.add(message)
    
    # Update thread message count and last_message_at
    await db.execute(
        update(ChatThread)
        .where(ChatThread.thread_id == thread_id)
        .values(
            message_count=ChatThread.message_count + 1,
            last_message_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    )
    
    await db.flush()
    await db.refresh(message)
    
    return message


async def get_thread_messages(
    db: AsyncSession,
    thread_id: str,
    limit: Optional[int] = None,
    include_deleted: bool = False
) -> List[ChatMessage]:
    """Get all messages for a chat thread"""
    query = select(ChatMessage).where(ChatMessage.thread_id == thread_id)
    
    if not include_deleted:
        query = query.where(ChatMessage.deleted_at.is_(None))
    
    query = query.order_by(ChatMessage.created_at)
    
    if limit:
        query = query.limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def update_message_feedback(
    db: AsyncSession,
    message_id: str,
    rating: int,
    comment: Optional[str] = None
) -> Optional[ChatMessage]:
    """Update message feedback"""
    await db.execute(
        update(ChatMessage)
        .where(ChatMessage.message_id == message_id)
        .values(
            feedback_rating=rating,
            feedback_comment=comment,
            feedback_submitted_at=datetime.utcnow()
        )
    )
    
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.message_id == message_id)
    )
    return result.scalar_one_or_none()


# ==================== SESSION CRUD OPERATIONS ====================

@async_timed("create_user_session")
async def create_user_session(
    db: AsyncSession,
    user_id: str,
    access_token: str,
    expires_in_minutes: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> UserSession:
    """Create a new user session"""
    session = UserSession(
        session_id=str(uuid.uuid4()),
        user_id=user_id,
        access_token=access_token,
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True,
        is_revoked=False,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes),
        last_activity=datetime.utcnow()
    )
    
    db.add(session)
    await db.flush()
    await db.refresh(session)
    
    return session


async def get_session_by_token(db: AsyncSession, access_token: str) -> Optional[UserSession]:
    """Get session by access token"""
    result = await db.execute(
        select(UserSession).where(
            and_(
                UserSession.access_token == access_token,
                UserSession.is_active == True,
                UserSession.is_revoked == False,
                UserSession.expires_at > datetime.utcnow()
            )
        )
    )
    return result.scalar_one_or_none()


async def revoke_user_session(db: AsyncSession, session_id: str) -> None:
    """Revoke a user session (for logout)"""
    await db.execute(
        update(UserSession)
        .where(UserSession.session_id == session_id)
        .values(
            is_active=False,
            is_revoked=True,
            revoked_at=datetime.utcnow()
        )
    )


async def revoke_all_user_sessions(db: AsyncSession, user_id: str) -> None:
    """Revoke all sessions for a user"""
    await db.execute(
        update(UserSession)
        .where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        )
        .values(
            is_active=False,
            is_revoked=True,
            revoked_at=datetime.utcnow()
        )
    )


# ==================== AUDIT LOG OPERATIONS ====================

@async_timed("create_audit_log")
async def create_audit_log(
    db: AsyncSession,
    event_type: str,
    event_action: str,
    event_result: str,
    user_id: Optional[str] = None,
    event_data: Optional[Dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_path: Optional[str] = None,
    request_method: Optional[str] = None,
    error_message: Optional[str] = None
) -> AuditLog:
    """Create an audit log entry"""
    audit_log = AuditLog(
        user_id=user_id,
        event_type=event_type,
        event_action=event_action,
        event_result=event_result,
        event_data=event_data,
        ip_address=ip_address,
        user_agent=user_agent,
        request_path=request_path,
        request_method=request_method,
        error_message=error_message,
        created_at=datetime.utcnow()
    )
    
    db.add(audit_log)
    await db.flush()
    
    return audit_log


async def get_user_audit_logs(
    db: AsyncSession,
    user_id: str,
    event_type: Optional[str] = None,
    limit: int = 100
) -> List[AuditLog]:
    """Get audit logs for a user"""
    conditions = [AuditLog.user_id == user_id]
    
    if event_type:
        conditions.append(AuditLog.event_type == event_type)
    
    result = await db.execute(
        select(AuditLog)
        .where(and_(*conditions))
        .order_by(desc(AuditLog.created_at))
        .limit(limit)
    )
    return result.scalars().all()
