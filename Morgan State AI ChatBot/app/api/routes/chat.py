from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import uuid
from datetime import datetime

from ...services.langchain_service import LangChainRAGService
from ...services.thread_manager import ThreadManager
from ...core.exceptions import create_success_response, create_error_response
from ...core.security import rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message", min_length=1, max_length=2000)
    thread_id: Optional[str] = Field(None, description="Conversation thread ID")
    category_filter: Optional[str] = Field(None, description="Knowledge base category filter")
    include_related_questions: bool = Field(False, description="Include suggested related questions")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI assistant response")
    thread_id: str = Field(..., description="Conversation thread ID")
    sources_used: List[str] = Field(default=[], description="Sources used in response")
    related_questions: List[str] = Field(default=[], description="Suggested related questions")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ThreadRequest(BaseModel):
    thread_id: str = Field(..., description="Thread ID to retrieve")
    limit: Optional[int] = Field(20, description="Maximum number of messages to retrieve")

class ThreadListResponse(BaseModel):
    threads: List[Dict[str, Any]] = Field(..., description="List of conversation threads")

# Global service instances
rag_service = LangChainRAGService()
thread_manager = ThreadManager()

@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest, http_request: Request):
    """
    Send a message to Morgan AI and get a response
    
    This endpoint handles the main chat functionality, including:
    - RAG-based response generation using Morgan State knowledge base
    - Conversation thread management
    - Context-aware responses based on chat history
    - Optional related question suggestions
    """
    try:
        # Get client IP for logging
        client_ip = http_request.client.host
        logger.info(f"Chat request from {client_ip}: {request.message[:50]}...")
        
        # Create or get thread ID
        thread_id = request.thread_id or str(uuid.uuid4())
        
        # Get conversation history
        conversation_history = []
        if request.thread_id:
            history = await thread_manager.get_thread_messages(request.thread_id, limit=10)
            conversation_history = [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in history
            ]
        
        # Generate RAG response
        response_text, context_used = await rag_service.generate_rag_response(
            query=request.message,
            conversation_history=conversation_history,
            category_filter=request.category_filter
        )
        
        # Extract sources from context
        sources_used = []
        if context_used and "[Source:" in context_used:
            import re
            source_matches = re.findall(r'\[Source: ([^\]]+)\]', context_used)
            sources_used = list(set(source_matches))  # Remove duplicates
        
        # Save messages to thread
        user_message = ChatMessage(role="user", content=request.message)
        assistant_message = ChatMessage(role="assistant", content=response_text)
        
        await thread_manager.add_message_to_thread(thread_id, user_message.dict())
        await thread_manager.add_message_to_thread(thread_id, assistant_message.dict())
        
        # Get related questions if requested
        related_questions = []
        if request.include_related_questions:
            try:
                related_questions = await rag_service.suggest_related_questions(request.message)
            except Exception as e:
                logger.warning(f"Failed to generate related questions: {str(e)}")
        
        # Update thread metadata
        await thread_manager.update_thread_metadata(
            thread_id,
            last_message=request.message[:100],
            message_count_increment=2  # User + assistant messages
        )
        
        logger.info(f"Successfully processed chat message for thread: {thread_id}")
        
        return ChatResponse(
            response=response_text,
            thread_id=thread_id,
            sources_used=sources_used,
            related_questions=related_questions
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to process your message. Please try again.",
                error_code="CHAT_PROCESSING_ERROR",
                details=str(e) if logger.level <= logging.DEBUG else None
            )
        )

@router.get("/threads")
async def list_threads(
    limit: int = 20,
    offset: int = 0
):
    """
    List conversation threads
    
    Returns a paginated list of conversation threads with metadata
    """
    try:
        threads = await thread_manager.list_threads(limit=limit, offset=offset)
        
        return create_success_response(
            data={"threads": threads},
            message=f"Retrieved {len(threads)} threads"
        )
        
    except Exception as e:
        logger.error(f"Error listing threads: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to retrieve conversation threads",
                error_code="THREAD_LIST_ERROR"
            )
        )

@router.get("/threads/{thread_id}")
async def get_thread_messages(
    thread_id: str,
    limit: int = 50,
    offset: int = 0
):
    """
    Get messages from a specific conversation thread
    
    Returns the conversation history for a given thread ID
    """
    try:
        messages = await thread_manager.get_thread_messages(
            thread_id=thread_id,
            limit=limit,
            offset=offset
        )
        
        if not messages:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    message="Thread not found",
                    error_code="THREAD_NOT_FOUND"
                )
            )
        
        return create_success_response(
            data={
                "thread_id": thread_id,
                "messages": messages,
                "message_count": len(messages)
            },
            message=f"Retrieved {len(messages)} messages from thread"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thread messages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to retrieve thread messages",
                error_code="THREAD_MESSAGES_ERROR"
            )
        )

@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """
    Delete a conversation thread
    
    Permanently deletes a thread and all its messages
    """
    try:
        success = await thread_manager.delete_thread(thread_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    message="Thread not found",
                    error_code="THREAD_NOT_FOUND"
                )
            )
        
        return create_success_response(
            message="Thread deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting thread: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to delete thread",
                error_code="THREAD_DELETE_ERROR"
            )
        )

@router.post("/threads/{thread_id}/clear")
async def clear_thread(thread_id: str):
    """
    Clear all messages from a thread but keep the thread
    
    Removes all messages from a thread while preserving the thread metadata
    """
    try:
        success = await thread_manager.clear_thread_messages(thread_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    message="Thread not found",
                    error_code="THREAD_NOT_FOUND"
                )
            )
        
        return create_success_response(
            message="Thread messages cleared successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing thread: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to clear thread messages",
                error_code="THREAD_CLEAR_ERROR"
            )
        )

@router.get("/categories")
async def get_knowledge_categories():
    """
    Get available knowledge base categories for filtering
    
    Returns a list of available categories that can be used to filter responses
    """
    try:
        from ...services.pinecone_service import PineconeService
        
        pinecone_service = PineconeService()
        categories = pinecone_service.get_categories()
        
        return create_success_response(
            data={"categories": categories},
            message=f"Retrieved {len(categories)} knowledge base categories"
        )
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to retrieve knowledge categories",
                error_code="CATEGORIES_ERROR"
            )
        )

@router.get("/quick-questions")
async def get_quick_questions():
    """
    Get predefined quick questions for the Morgan State CS department
    
    Returns a list of common questions students ask about the department
    """
    quick_questions = [
        "Where is the Computer Science department located?",
        "Who are the faculty members in Computer Science?",
        "What courses do I need for a CS degree?",
        "How do I join student organizations like WiCS or GDSC?",
        "What tutoring services are available for CS students?",
        "How do I get help with programming assignments?",
        "What internship programs are recommended?",
        "How do I prepare for technical interviews?",
        "Who is my academic advisor and how do I contact them?",
        "How do I get an enrollment PIN for registration?",
        "What are the prerequisites for advanced CS courses?",
        "When are the add/drop deadlines for this semester?",
        "How do I submit an override request for a full class?",
        "What career resources are available through the department?",
        "How do I access NeetCode, LeetCode, and other prep resources?",
        "What research opportunities are available for undergraduates?",
        "How do I apply for the Google STEP or Microsoft Explore programs?"
    ]
    
    categories = {
        "Department Information": [
            "Where is the Computer Science department located?",
            "Who are the faculty members in Computer Science?",
            "What are the department's office hours?",
            "How do I contact the CS department?"
        ],
        "Academic Support": [
            "What tutoring services are available for CS students?",
            "How do I get help with programming assignments?",
            "How do I join student organizations like WiCS or GDSC?",
            "What study spaces are available for CS students?"
        ],
        "Career Resources": [
            "What internship programs are recommended?",
            "How do I prepare for technical interviews?",
            "What career resources are available through the department?",
            "How do I access NeetCode, LeetCode, and other prep resources?"
        ],
        "Advising & Registration": [
            "Who is my academic advisor and how do I contact them?",
            "How do I get an enrollment PIN for registration?",
            "What are the prerequisites for advanced CS courses?",
            "How do I submit an override request for a full class?"
        ]
    }
    
    return create_success_response(
        data={
            "quick_questions": quick_questions,
            "categories": categories
        },
        message="Retrieved quick questions and categories"
    )

@router.get("/health")
async def chat_health_check():
    """
    Health check endpoint for chat service
    
    Returns the status of chat-related services
    """
    try:
        # Test basic functionality
        health_status = {
            "chat_service": "healthy",
            "rag_service": "unknown",
            "thread_manager": "unknown",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Test RAG service
        try:
            test_context = await rag_service.get_relevant_context("test query", max_results=1)
            health_status["rag_service"] = "healthy" if test_context else "degraded"
        except Exception as e:
            health_status["rag_service"] = "unhealthy"
            logger.warning(f"RAG service health check failed: {str(e)}")
        
        # Test thread manager
        try:
            test_threads = await thread_manager.list_threads(limit=1)
            health_status["thread_manager"] = "healthy"
        except Exception as e:
            health_status["thread_manager"] = "unhealthy"
            logger.warning(f"Thread manager health check failed: {str(e)}")
        
        overall_healthy = all(
            status in ["healthy", "degraded"] 
            for status in health_status.values() 
            if status not in ["unknown", health_status["timestamp"]]
        )
        
        return create_success_response(
            data=health_status,
            message="Chat service health check completed"
        )
        
    except Exception as e:
        logger.error(f"Chat health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=create_error_response(
                message="Chat service health check failed",
                error_code="HEALTH_CHECK_ERROR"
            )
        )