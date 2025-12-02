from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
from app.core.config import settings
from app.core.security import security_service
from app.services.pinecone_service import PineconeService
from app.services.langchain_service import PineconeService

logger = logging.getLogger(__name__)
router = APIRouter()

class AdminSettings(BaseModel):
    enable_voice: bool = Field(default=True)
    tts_voice: str = Field(default="alloy")
    tts_speed: float = Field(default=1.0, ge=0.25, le=4.0)
    max_tokens: int = Field(default=2000, ge=100, le=4000)
    temperature: float = Field(default=0.7, ge=0, le=2)
    top_k_results: int = Field(default=5, ge=1, le=20)

class UserManagement(BaseModel):
    username: str
    email: Optional[str] = None
    role: str = Field(default="user")
    is_active: bool = Field(default=True)

class KnowledgeBaseUpdate(BaseModel):
    operation: str = Field(..., description="Operation type: add, update, delete, refresh")
    content: Optional[str] = Field(None, description="Content to add/update")
    document_id: Optional[str] = Field(None, description="Document ID for update/delete")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

@router.post("/login")
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Admin login endpoint"""
    try:
        # Verify admin credentials
        if not security_service.verify_admin_credentials(
            form_data.username,
            form_data.password
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid admin credentials"
            )
        
        # Create access token
        access_token = security_service.create_access_token(
            data={
                "sub": form_data.username,
                "role": "admin",
                "user_id": "admin"
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": "admin"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.get("/dashboard")
async def get_dashboard_stats(
    current_admin: Dict = Depends(security_service.get_current_admin),
    app_request: Request = None
):
    """Get admin dashboard statistics"""
    try:
        pinecone_service = app_request.app.state.pinecone
        
        stats = {
            "total_users": 0,  # Would fetch from database
            "active_sessions": 0,  # Would track active sessions
            "total_messages": 0,  # Would count from database
            "knowledge_base": {
                "total_documents": await pinecone_service.get_stats(),
                "last_updated": datetime.utcnow().isoformat()
            },
            "system_status": {
                "openai": "connected",
                "pinecone": "connected",
                "voice_enabled": settings.ENABLE_VOICE
            }
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings")
async def get_settings(
    current_admin: Dict = Depends(security_service.get_current_admin)
):
    """Get current admin settings"""
    return AdminSettings(
        enable_voice=settings.ENABLE_VOICE,
        tts_voice=settings.TTS_VOICE,
        tts_speed=settings.TTS_SPEED,
        max_tokens=settings.OPENAI_MAX_TOKENS,
        temperature=settings.OPENAI_TEMPERATURE,
        top_k_results=settings.TOP_K_RESULTS
    )

@router.put("/settings")
async def update_settings(
    settings_update: AdminSettings,
    current_admin: Dict = Depends(security_service.get_current_admin)
):
    """Update admin settings"""
    try:
        # Update settings (in production, persist to database)
        settings.ENABLE_VOICE = settings_update.enable_voice
        settings.TTS_VOICE = settings_update.tts_voice
        settings.TTS_SPEED = settings_update.tts_speed
        settings.OPENAI_MAX_TOKENS = settings_update.max_tokens
        settings.OPENAI_TEMPERATURE = settings_update.temperature
        settings.TOP_K_RESULTS = settings_update.top_k_results
        
        return {"message": "Settings updated successfully"}
        
    except Exception as e:
        logger.error(f"Settings update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def get_users(
    current_admin: Dict = Depends(security_service.get_current_admin),
    limit: int = 50,
    offset: int = 0
):
    """Get list of users"""
    try:
        # In production, fetch from database
        users = [
            {
                "user_id": "user_001",
                "username": "student1",
                "email": "student1@morgan.edu",
                "role": "user",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat()
            }
        ]
        
        return {
            "users": users,
            "total": len(users),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users")
async def create_user(
    user_data: UserManagement,
    current_admin: Dict = Depends(security_service.get_current_admin)
):
    """Create new user"""
    try:
        # In production, save to database
        new_user = {
            "user_id": f"user_{datetime.utcnow().timestamp()}",
            "username": user_data.username,
            "email": user_data.email,
            "role": user_data.role,
            "is_active": user_data.is_active,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {"message": "User created successfully", "user": new_user}
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserManagement,
    current_admin: Dict = Depends(security_service.get_current_admin)
):
    """Update user information"""
    try:
        # In production, update in database
        return {"message": f"User {user_id} updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_admin: Dict = Depends(security_service.get_current_admin)
):
    """Delete a user"""
    try:
        # In production, delete from database
        return {"message": f"User {user_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge-base/update")
async def update_knowledge_base(
    update: KnowledgeBaseUpdate,
    background_tasks: BackgroundTasks,
    current_admin: Dict = Depends(security_service.get_current_admin),
    app_request: Request = None
):
    """Update knowledge base"""
    try:
        langchain_service = PineconeService()
        
        if update.operation == "refresh":
            # Trigger background task to reingest all data
            background_tasks.add_task(
                langchain_service.refresh_knowledge_base
            )
            return {"message": "Knowledge base refresh initiated"}
            
        elif update.operation == "add":
            # Add new content
            await langchain_service.add_document(
                content=update.content,
                metadata=update.metadata
            )
            return {"message": "Document added successfully"}
            
        elif update.operation == "update":
            # Update existing document
            await langchain_service.update_document(
                document_id=update.document_id,
                content=update.content,
                metadata=update.metadata
            )
            return {"message": "Document updated successfully"}
            
        elif update.operation == "delete":
            # Delete document
            await langchain_service.delete_document(update.document_id)
            return {"message": "Document deleted successfully"}
            
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Knowledge base update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-base/status")
async def get_knowledge_base_status(
    current_admin: Dict = Depends(security_service.get_current_admin),
    app_request: Request = None
):
    """Get knowledge base status"""
    try:
        pinecone_service = app_request.app.state.pinecone
        
        stats = await pinecone_service.get_stats()
        
        return {
            "status": "operational",
            "total_vectors": stats.get("total_vector_count", 0),
            "dimension": stats.get("dimension", 0),
            "index_fullness": stats.get("index_fullness", 0),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Knowledge base status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/terminate")
async def terminate_user_session(
    user_id: str,
    current_admin: Dict = Depends(security_service.get_current_admin)
):
    """Terminate a user's session"""
    try:
        # In production, invalidate user's tokens
        return {"message": f"Session terminated for user {user_id}"}
        
    except Exception as e:
        logger.error(f"Session termination error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_system_logs(
    current_admin: Dict = Depends(security_service.get_current_admin),
    level: str = "INFO",
    limit: int = 100
):
    """Get system logs"""
    try:
        # In production, fetch from log storage
        logs = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level,
                "message": "System operational",
                "module": "app.main"
            }
        ]
        
        return {"logs": logs, "total": len(logs)}
        
    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))