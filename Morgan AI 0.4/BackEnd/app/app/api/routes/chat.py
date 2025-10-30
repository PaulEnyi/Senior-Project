from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging
from app.core.security import security_service
from app.services.openai_service import OpenAIService
from app.services.langchain_service import PineconeService
from app.services.thread_manager import ThreadManager
from app.models.chat import ChatMessage, ChatThread, ChatResponse

logger = logging.getLogger(__name__)
router = APIRouter()

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
    app_request: Request = None
):
    """Send a message to the chatbot and get a response"""
    try:
        # Use the ThreadManager inside OpenAIService to ensure a single shared source of truth
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
        
        # Generate response using OpenAI service
        # The OpenAI service will handle RAG context retrieval and thread management internally
        response = await openai_service.generate_chat_response(
              message=request.message,
              session_id=thread.thread_id,
              user_id=current_user["user_id"],
              use_rag=True
        )
        
        # Check if response was successful
        if not response.get("success", False):
            raise HTTPException(
                status_code=500, 
                detail=response.get("error", "Failed to generate response")
            )
        
        # Get the latest messages from thread (including the ones just added by OpenAI service)
        messages = await thread_manager.get_messages(thread.thread_id, limit=2)
        
        # Find the assistant's response
        assistant_content = response.get("response", "")
        
        return ChatResponse(
            thread_id=thread.thread_id,
            message=assistant_content,
            sources=[],  # RAG sources would be included here if available
            timestamp=datetime.utcnow(),
            metadata={
                "model": response.get("model", ""),
                "context_used": response.get("context_used", False)
            }
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
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
            history=history
        ):
            yield f"data: {chunk}\n\n"
            
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
        yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

@router.get("/threads")
async def get_user_threads(
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None,
    limit: int = 20,
    offset: int = 0
):
    """Get user's chat threads"""
    try:
        openai_service = app_request.app.state.openai
        thread_manager: ThreadManager = openai_service.thread_manager
        threads = await thread_manager.get_user_threads(
            user_id=current_user["user_id"],
            limit=limit,
            offset=offset
        )
        return {"threads": threads, "total": len(threads)}
    except Exception as e:
        logger.error(f"Error fetching threads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threads/{thread_id}")
async def get_thread_messages(
    thread_id: str,
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None,
    limit: int = 50
):
    """Get messages from a specific thread"""
    try:
        openai_service = app_request.app.state.openai
        thread_manager: ThreadManager = openai_service.thread_manager
        # Verify thread belongs to user
        thread = await thread_manager.get_thread(thread_id)
        if not thread or thread.user_id != current_user["user_id"]:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        messages = await thread_manager.get_messages(thread_id, limit=limit)
        return {
            "thread_id": thread_id,
            "messages": messages,
            "total": len(messages)
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
    app_request: Request = None
):
    """Delete a chat thread"""
    try:
        openai_service = app_request.app.state.openai
        thread_manager: ThreadManager = openai_service.thread_manager
        # Verify thread belongs to user
        thread = await thread_manager.get_thread(thread_id)
        if not thread or thread.user_id != current_user["user_id"]:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        await thread_manager.delete_thread(thread_id)
        return {"message": "Thread deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting thread: {str(e)}")
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
    app_request: Request = None,
    limit: int = 20
):
    """Search user's chat history"""
    try:
        openai_service = app_request.app.state.openai
        thread_manager: ThreadManager = openai_service.thread_manager
        results = await thread_manager.search_user_chats(
            user_id=current_user["user_id"],
            query=query,
            limit=limit
        )
        return {"results": results, "total": len(results)}
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
