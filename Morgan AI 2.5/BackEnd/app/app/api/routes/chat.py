from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from app.core.security import security_service
from app.core.database import get_db
from app.core import db_operations
from app.services.openai_service import OpenAIService
from app.utils.timing import async_timed
from app.services.langchain_service import PineconeService
from app.services.thread_manager import ThreadManager
from app.models.chat import ChatMessage, ChatThread, ChatResponse
from app.models.database import ChatThread as DBChatThread, ChatMessage as DBChatMessage

logger = logging.getLogger(__name__)
router = APIRouter()


def _iso_utc(dt: Optional[datetime]) -> Optional[str]:
    """Return ISO-8601 UTC with milliseconds and Z from a datetime.
    If naive, assume UTC. Returns None if dt is None.
    """
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

# Quick Questions by Category
quick_questions_by_category = {
    "Department Information": [
        "Where is the Computer Science department located?",
        "Who are the faculty members in Computer Science?",
        "What are the department's office hours?",
        "How do I contact the CS department?"
    ],
    "Academic Support": [
        "What tutoring services are available for CS students?",
        "How do I get help with programming assignments?",
        "What study spaces are available for CS students?",
        "How do I form or join a study group for my CS classes?"
    ],
    "Career Resources": [
        "What internship programs are recommended?",
        "How do I prepare for technical interviews?",
        "What career resources are available through the department?",
        "How do I access NeetCode, LeetCode, and other prep resources?"
    ],
    "Student Organizations & Community": [
        "How do I join student organizations like WiCS or GDSC?",
        "What CS-related clubs and organizations can I join?",
        "Are there any upcoming hackathons I can participate in?",
        "How do I get involved with the CS student community?",
        "What networking events are available for CS majors?",
        "Are there coding competitions or programming contests?",
        "How can I connect with other CS majors for collaboration?"
    ],
    "Social & Events": [
        "What tech talks or guest speaker events happen in the CS department?",
        "Are there any CS study sessions or workshops?",
        "How do I find project partners for team assignments?",
        "What social events does the CS department host?",
        "How can I participate in code review sessions or peer programming?"
    ],
    "Advising & Registration": [
        "Who is my academic advisor and how do I contact them?",
        "How do I get an enrollment PIN for registration?",
        "What are the prerequisites for advanced CS courses?",
        "How do I submit an override request for a full class?"
    ]
}

# Request/Response models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    thread_id: Optional[str] = Field(None, description="Thread ID for conversation continuity")
    user_id: Optional[str] = Field(None, description="User ID")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

class StreamChatRequest(ChatRequest):
    stream: bool = Field(default=True, description="Enable streaming response")

# Initialize services
langchain_service = PineconeService()

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: Dict = Depends(security_service.get_current_user),
    db: AsyncSession = Depends(get_db),
    app_request: Request = None
):
    """Send a message to the chatbot and get a response, save to database"""
    try:
        user_id = current_user["user_id"]
        request_id = f"req-{datetime.utcnow().timestamp()}-{user_id[:8]}"
        start_time = datetime.now(timezone.utc)
        logger.info(f"[CHAT] {request_id} START user={user_id} thread_req={request.thread_id}")

        # Bridge auto-create: ensure DB user exists (strict fallback 401)
        user_record = await db_operations.get_user_by_id(db=db, user_id=user_id)
        if not user_record:
            email_claim = current_user.get("email")
            username_claim = current_user.get("sub") or current_user.get("username")
            if email_claim and username_claim:
                try:
                    password_hash = security_service.get_password_hash("bridge-placeholder-password")
                    user_record = await db_operations.create_user_with_id(
                        db=db,
                        user_id=user_id,
                        email=email_claim,
                        username=username_claim,
                        password_hash=password_hash,
                        full_name=current_user.get("full_name") or username_claim
                    )
                    logger.info(f"[CHAT] {request_id} BRIDGE_USER_CREATED user={user_id}")
                except Exception as bridge_err:
                    logger.error(f"[CHAT] {request_id} BRIDGE_USER_FAIL user={user_id} err={bridge_err}")
                    raise HTTPException(status_code=401, detail="User record missing and bridge creation failed. Please re-auth.")
            else:
                logger.warning(f"[CHAT] {request_id} BRIDGE_USER_SKIPPED missing_claims user={user_id}")
                raise HTTPException(status_code=401, detail="User record missing. Please log in again.")
        
        # Get or create thread in database
        if request.thread_id:
            thread = await db_operations.get_chat_thread(db=db, thread_id=request.thread_id)
            if not thread:
                # Create new thread in database
                thread = await db_operations.create_chat_thread(
                    db=db,
                    user_id=user_id,
                    title="New Chat"
                )
                thread_id = str(thread.thread_id)
            else:
                thread_id = request.thread_id
                # Verify ownership
                if str(thread.user_id) != user_id:
                    raise HTTPException(status_code=403, detail="Access denied to this thread")
        else:
            # Create new thread in database
            thread = await db_operations.create_chat_thread(
                db=db,
                user_id=user_id,
                title="New Chat"
            )
            thread_id = str(thread.thread_id)
        
        # Also maintain in-memory ThreadManager for OpenAI service compatibility
        openai_service = app_request.app.state.openai
        thread_manager: ThreadManager = openai_service.thread_manager
        
        # Sync with ThreadManager
        memory_thread = await thread_manager.get_thread(thread_id)
        if not memory_thread:
            memory_thread = await thread_manager.create_thread(
                user_id=user_id,
                thread_id=thread_id
            )
        
        # Save user message to database first
        user_message = await db_operations.create_chat_message(
            db=db,
            thread_id=thread_id,
            content=request.message,
            role="user",
            metadata=request.context or {}
        )
        logger.info(f"[CHAT] {request_id} USER_MSG_SAVED msg_id={user_message.message_id} thread={thread_id}")
        
        # Generate response using OpenAI service (timed)
        @async_timed("openai_generate_chat_response")
        async def timed_generate():
            return await openai_service.generate_chat_response(
                message=request.message,
                session_id=thread_id,
                user_id=user_id,
                use_rag=True
            )

        response = await timed_generate()
        
        # Check if response was successful
        if not response.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=response.get("error", "Failed to generate response")
            )
        
        # Get assistant's response
        assistant_content = response.get("response", "")
        
        # Save assistant message to database
        assistant_message = await db_operations.create_chat_message(
            db=db,
            thread_id=thread_id,
            content=assistant_content,
            role="assistant",
            metadata={
                "model": response.get("model", ""),
                "context_used": response.get("context_used", False),
                "sources": response.get("sources", [])
            }
        )
        logger.info(f"[CHAT] {request_id} ASSISTANT_MSG_SAVED msg_id={assistant_message.message_id} thread={thread_id}")
        
        # Update thread title if it's still "New Chat" and this is the first message
        if thread.title == "New Chat" and thread.message_count <= 2:
            # Generate title from first user message (first 50 chars)
            auto_title = request.message[:50] + ("..." if len(request.message) > 50 else "")
            await db_operations.update_chat_thread(
                db=db,
                thread_id=thread_id,
                title=auto_title
            )
        
        total_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000.0
        logger.info(f"[CHAT] {request_id} COMPLETE thread={thread_id} duration_ms={total_ms:.2f}")
        return ChatResponse(
            thread_id=thread_id,
            message=assistant_content,
            sources=response.get("sources", []),
            timestamp=datetime.now(timezone.utc),
            metadata={
                "model": response.get("model", ""),
                "context_used": response.get("context_used", False),
                "message_id": str(assistant_message.message_id)
            }
        )
        
    except HTTPException as http_exc:
        logger.info(f"[CHAT] ERROR http status={http_exc.status_code} detail={http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"[CHAT] UNEXPECTED_ERROR err={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_message(
    request: StreamChatRequest,
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Stream a chat response using Server-Sent Events"""
    try:
        # Use the ThreadManager inside OpenAIService
        openai_service = app_request.app.state.openai
        thread_manager: ThreadManager = openai_service.thread_manager
        
        # Get or create thread
        if request.thread_id:
            thread = await thread_manager.get_thread(request.thread_id)
            if not thread:
                thread = await thread_manager.create_thread(
                    user_id=current_user["user_id"],
                    thread_id=request.thread_id
                )
        else:
            thread = await thread_manager.create_thread(user_id=current_user["user_id"])
        
        # Get context and history
        context = await langchain_service.get_relevant_context(request.message)
        history = await thread_manager.get_messages(thread.thread_id, limit=10)
        
        # Stream response
        async for chunk in openai_service.stream_chat_response(
            message=request.message,
            context=context,
            history=history,
            session_id=thread.thread_id,
            user_id=current_user["user_id"]
        ):
            yield f"data: {chunk}\n\n"
            
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
        yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

@router.get("/threads")
async def get_user_threads(
    current_user: Dict = Depends(security_service.get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
    include_deleted: bool = False,
    only_active: bool = False
):
    """Get user's chat threads from database"""
    try:
        user_id = current_user["user_id"]
        
        # Fetch threads from database
        threads = await db_operations.get_user_chat_threads(
            db=db,
            user_id=user_id,
            include_archived=include_deleted,
            limit=limit
        )
        
        # Convert to response format
        thread_list = []
        for thread in threads:
            thread_list.append({
                "thread_id": str(thread.thread_id),
                "title": thread.title or "Untitled Chat",
                "message_count": thread.message_count,
                "created_at": _iso_utc(thread.created_at),
                "updated_at": _iso_utc(thread.updated_at),
                "last_message_at": _iso_utc(thread.last_message_at),
                "is_active": thread.is_active,
                "metadata": thread.thread_metadata or {}
            })
        
        return {
            "threads": thread_list,
            "total": len(thread_list),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error fetching threads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threads/{thread_id}")
async def get_thread_messages(
    thread_id: str,
    current_user: Dict = Depends(security_service.get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    include_deleted: bool = False
):
    """Get messages from a specific thread from database"""
    try:
        user_id = current_user["user_id"]
        
        # Verify thread exists and belongs to user
        thread = await db_operations.get_chat_thread(db=db, thread_id=thread_id)
        
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        if str(thread.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this thread")
        
        # Get messages from database
        messages = await db_operations.get_thread_messages(
            db=db,
            thread_id=thread_id,
            include_deleted=include_deleted
        )
        
        # Convert to response format
        message_list = []
        for msg in messages:
            message_list.append({
                "id": str(msg.message_id),  # Frontend expects 'id'
                "message_id": str(msg.message_id),
                "content": msg.content,
                "role": msg.role,
                "timestamp": _iso_utc(msg.created_at),
                "feedback_rating": msg.feedback_rating,
                "feedback_comment": msg.feedback_comment,
                "metadata": msg.message_metadata or {}
            })
        
        return {
            "thread_id": thread_id,
            "title": thread.title,
            "messages": message_list,
            "total": len(message_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    current_user: Dict = Depends(security_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a chat thread (soft delete in database)"""
    try:
        user_id = current_user["user_id"]
        
        # Verify thread exists and belongs to user
        thread = await db_operations.get_chat_thread(db=db, thread_id=thread_id)
        
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        if str(thread.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this thread")
        
        # Soft delete the thread
        await db_operations.delete_chat_thread(db=db, thread_id=thread_id)
        
        logger.info(f"Thread {thread_id} deleted by user {user_id}")
        
        return {
            "success": True,
            "message": "Thread deleted successfully",
            "thread_id": thread_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting thread: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/threads/{thread_id}/title")
async def update_thread_title(
    thread_id: str,
    request: Dict[str, str],
    current_user: Dict = Depends(security_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a thread's title in database"""
    try:
        user_id = current_user["user_id"]
        
        # Verify thread exists and belongs to user
        thread = await db_operations.get_chat_thread(db=db, thread_id=thread_id)
        
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        if str(thread.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this thread")
        
        # Update thread title in database
        title = request.get("title", "").strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        
        await db_operations.update_chat_thread(
            db=db,
            thread_id=thread_id,
            title=title
        )
        
        logger.info(f"Thread {thread_id} title updated to '{title}' by user {user_id}")
        
        return {
            "success": True,
            "message": "Thread title updated successfully",
            "title": title,
            "thread_id": thread_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating thread title: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/threads/new")
async def create_new_thread(
    current_user: Dict = Depends(security_service.get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Optional[Dict[str, Any]] = None
):
    """Create a new chat thread and deactivate all old threads"""
    try:
        user_id = current_user["user_id"]
        
        # Deactivate all existing threads for this user
        await db_operations.deactivate_user_threads(db=db, user_id=user_id)
        
        # Create new thread
        title = request.get("title", "New Chat") if request else "New Chat"
        thread_data = request.get("metadata", {}) if request else {}
        
        new_thread = await db_operations.create_chat_thread(
            db=db,
            user_id=user_id,
            title=title
        )
        
        logger.info(f"Created new thread {new_thread.thread_id} for user {user_id}")
        
        return {
            "success": True,
            "message": "New chat thread created",
            "thread": {
                "thread_id": str(new_thread.thread_id),
                "title": new_thread.title,
                "created_at": new_thread.created_at.isoformat(),
                "is_active": new_thread.is_active,
                "message_count": new_thread.message_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating new thread: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def submit_feedback(
    thread_id: str = Query(...),
    message_id: str = Query(...),
    rating: int = Query(..., ge=1, le=5),
    feedback: Optional[str] = Query(None),
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Submit feedback for a chat response"""
    try:
        openai_service = app_request.app.state.openai
        thread_manager: ThreadManager = openai_service.thread_manager
        await thread_manager.add_feedback(
            thread_id=thread_id,
            message_id=message_id,
            rating=rating,
            feedback=feedback,
            user_id=current_user["user_id"]
        )
        return {"message": "Feedback submitted successfully"}
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_chat_history(
    query: str,
    current_user: Dict = Depends(security_service.get_current_user),
    db: AsyncSession = Depends(get_db),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 20
):
    """Search user's chat history by title, content, and date range"""
    try:
        user_id = current_user["user_id"]
        
        if not query or not query.strip():
            return {"results": [], "total": 0, "query": query}
        
        # Build search pattern
        search_pattern = f"%{query.strip()}%"
        
        # Search in thread titles
        thread_stmt = select(DBChatThread).where(
            and_(
                DBChatThread.user_id == user_id,
                DBChatThread.deleted_at.is_(None),
                DBChatThread.title.ilike(search_pattern)
            )
        )
        
        # Add date filters if provided
        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                thread_stmt = thread_stmt.where(DBChatThread.created_at >= date_from_dt)
            except ValueError:
                logger.warning(f"Invalid date_from format: {date_from}")
        
        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                thread_stmt = thread_stmt.where(DBChatThread.created_at <= date_to_dt)
            except ValueError:
                logger.warning(f"Invalid date_to format: {date_to}")
        
        # Execute thread search
        thread_result = await db.execute(thread_stmt)
        matching_threads = thread_result.scalars().all()
        
        # Search in message content
        message_stmt = select(DBChatMessage).join(
            DBChatThread,
            DBChatMessage.thread_id == DBChatThread.thread_id
        ).where(
            and_(
                DBChatThread.user_id == user_id,
                DBChatThread.deleted_at.is_(None),
                DBChatMessage.content.ilike(search_pattern)
            )
        ).order_by(DBChatMessage.created_at.desc())
        
        message_result = await db.execute(message_stmt)
        matching_messages = message_result.scalars().all()
        
        # Combine results
        thread_results = {}
        
        # Add threads that matched by title
        for thread in matching_threads:
            thread_id = str(thread.thread_id)
            thread_results[thread_id] = {
                "thread_id": thread_id,
                "thread_title": thread.title or "Untitled Chat",
                "created_at": _iso_utc(thread.created_at),
                "updated_at": _iso_utc(thread.updated_at),
                "message_count": thread.message_count,
                "matches": [],
                "matched_in": "title"
            }
        
        # Add messages that matched by content
        for message in matching_messages:
            # Get the thread for this message
            thread_stmt = select(DBChatThread).where(
                DBChatThread.thread_id == message.thread_id
            )
            thread_result = await db.execute(thread_stmt)
            thread = thread_result.scalar_one_or_none()
            
            if thread:
                thread_id = str(thread.thread_id)
                
                if thread_id not in thread_results:
                    thread_results[thread_id] = {
                        "thread_id": thread_id,
                        "thread_title": thread.title or "Untitled Chat",
                        "created_at": _iso_utc(thread.created_at),
                        "updated_at": _iso_utc(thread.updated_at),
                        "message_count": thread.message_count,
                        "matches": [],
                        "matched_in": "content"
                    }
                else:
                    thread_results[thread_id]["matched_in"] = "both"
                
                # Add message snippet with context
                content_lower = message.content.lower()
                query_lower = query.strip().lower()
                match_index = content_lower.find(query_lower)
                
                # Extract snippet around match (50 chars before and after)
                start = max(0, match_index - 50)
                end = min(len(message.content), match_index + len(query) + 50)
                snippet = message.content[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(message.content):
                    snippet = snippet + "..."
                
                thread_results[thread_id]["matches"].append({
                    "message_id": str(message.message_id),
                    "content": message.content,
                    "snippet": snippet,
                    "role": message.role,
                    "timestamp": _iso_utc(message.created_at)
                })
        
        # Convert to list, sort by updated_at, and limit results
        results_list = sorted(
            thread_results.values(),
            key=lambda x: x.get('updated_at', ''),
            reverse=True
        )[:limit]
        
        logger.info(f"Search query '{query}' returned {len(results_list)} results for user {user_id}")
        
        return {
            "results": results_list,
            "total": len(results_list),
            "query": query,
            "filters": {
                "date_from": date_from,
                "date_to": date_to
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching chats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/quick-questions")
async def get_quick_questions():
    """Get categorized quick questions for the chat interface"""
    try:
        return {
            "categories": quick_questions_by_category,
            "total_categories": len(quick_questions_by_category),
            "total_questions": sum(len(questions) for questions in quick_questions_by_category.values())
        }
    except Exception as e:
        logger.error(f"Error fetching quick questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quick-save")
async def quick_save_chat(
    thread_id: str,
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """
    Quick save current chat session (simplified endpoint for logout/login)
    """
    try:
        openai_service = app_request.app.state.openai
        thread_manager: ThreadManager = openai_service.thread_manager
        
        thread = await thread_manager.get_thread(thread_id)
        
        if not thread or thread.user_id != current_user["user_id"]:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Update thread metadata to mark as saved
        thread.metadata = thread.metadata or {}
        thread.metadata['last_saved'] = datetime.utcnow().isoformat()
        thread.metadata['saved_on_logout'] = True
        
        logger.info(f"Quick saved chat for user {current_user['user_id']}: {thread_id}")
        
        return {
            'success': True,
            'message': 'Chat saved successfully',
            'thread_id': thread_id,
            'saved_at': thread.metadata['last_saved']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error quick saving chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quick-load/{thread_id}")
async def quick_load_chat(
    thread_id: str,
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """
    Quick load saved chat session (simplified endpoint for login recovery)
    """
    try:
        openai_service = app_request.app.state.openai
        thread_manager: ThreadManager = openai_service.thread_manager
        
        thread = await thread_manager.get_thread(thread_id)
        
        if not thread or thread.user_id != current_user["user_id"]:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        messages = await thread_manager.get_thread_messages(thread_id)
        
        logger.info(f"Quick loaded chat for user {current_user['user_id']}: {thread_id}")
        
        return {
            'success': True,
            'thread': {
                'thread_id': thread.thread_id,
                'title': thread.title,
                'created_at': thread.created_at.isoformat(),
                'updated_at': thread.updated_at.isoformat(),
                'message_count': thread.message_count
            },
            'messages': [
                {
                    'message_id': msg.message_id,
                    'content': msg.content,
                    'role': msg.role,
                    'timestamp': _iso_utc(msg.timestamp)
                } for msg in messages
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error quick loading chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
