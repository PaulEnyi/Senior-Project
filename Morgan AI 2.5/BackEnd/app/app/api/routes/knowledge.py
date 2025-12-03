"""
Knowledge base management API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from app.core.security import security_service
from app.services.knowledge_updater import KnowledgeUpdateService

logger = logging.getLogger(__name__)
router = APIRouter()

# Request models
class UpdateRequest(BaseModel):
    mode: str = Field("incremental", description="Update mode: 'full' or 'incremental'")
    force: bool = Field(False, description="Force update even if one is in progress")

class ScheduleUpdateRequest(BaseModel):
    interval_hours: int = Field(24, ge=1, le=168, description="Update interval in hours (1-168)")

# Global update service instance
update_service: Optional[KnowledgeUpdateService] = None

async def get_update_service(app_request: Request) -> KnowledgeUpdateService:
    """Get or create update service instance"""
    global update_service
    
    if update_service is None:
        update_service = KnowledgeUpdateService()
        await update_service.initialize()
        
        # Store in app state for access across requests
        app_request.app.state.knowledge_updater = update_service
    
    return update_service

@router.get("/status")
async def get_knowledge_status(
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Get current knowledge base update status"""
    try:
        service = await get_update_service(app_request)
        status = service.get_status()
        
        # Get Pinecone stats
        pinecone_stats = await service.pinecone_service.get_stats()
        
        return {
            "status": "active",
            "update_service": status,
            "vector_database": {
                "total_vectors": pinecone_stats.get("total_vector_count", 0),
                "index_fullness": pinecone_stats.get("index_fullness", 0),
                "dimension": pinecone_stats.get("dimension", 1536)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting knowledge status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update")
async def trigger_update(
    request: UpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Trigger a knowledge base update
    
    Requires admin privileges
    """
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=403, 
                detail="Admin privileges required to update knowledge base"
            )
        
        service = await get_update_service(app_request)
        
        # Check if update is already in progress
        if service.update_in_progress and not request.force:
            return {
                "success": False,
                "message": "Update already in progress. Use 'force=true' to override.",
                "status": service.get_status()
            }
        
        # Run update in background
        if request.mode == "full":
            background_tasks.add_task(service.full_refresh)
            message = "Full knowledge base refresh initiated"
        else:
            background_tasks.add_task(service.incremental_update)
            message = "Incremental knowledge base update initiated"
        
        return {
            "success": True,
            "message": message,
            "mode": request.mode,
            "initiated_at": datetime.utcnow().isoformat(),
            "initiated_by": current_user.get("email", "unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule")
async def schedule_periodic_updates(
    request: ScheduleUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Schedule periodic automatic updates
    
    Requires admin privileges
    """
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=403, 
                detail="Admin privileges required to schedule updates"
            )
        
        service = await get_update_service(app_request)
        
        # Start periodic updates in background
        background_tasks.add_task(
            service.schedule_periodic_update, 
            request.interval_hours
        )
        
        return {
            "success": True,
            "message": f"Periodic updates scheduled every {request.interval_hours} hours",
            "interval_hours": request.interval_hours,
            "scheduled_at": datetime.utcnow().isoformat(),
            "scheduled_by": current_user.get("email", "unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling updates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-changes")
async def detect_file_changes(
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Detect files that have changed since last update
    
    Requires admin privileges
    """
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=403, 
                detail="Admin privileges required"
            )
        
        service = await get_update_service(app_request)
        changed_files = await service.detect_changed_files()
        
        return {
            "success": True,
            "changed_files": [str(f) for f in changed_files],
            "total_changes": len(changed_files),
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting changes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_update_history(
    limit: int = 10,
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Get recent update history
    
    Returns logs of recent knowledge base updates
    """
    try:
        service = await get_update_service(app_request)
        
        # Read log files from processed directory
        log_files = sorted(
            service.processed_dir.glob("ingestion_log_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]
        
        history = []
        for log_file in log_files:
            try:
                import json
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
                    history.append({
                        "timestamp": log_data.get("end_time"),
                        "success": log_data.get("success", False),
                        "files_processed": log_data.get("statistics", {}).get("files_processed", 0),
                        "vectors_stored": log_data.get("statistics", {}).get("vectors_stored", 0),
                        "duration_seconds": log_data.get("duration_seconds", 0)
                    })
            except Exception as e:
                logger.warning(f"Error reading log file {log_file}: {str(e)}")
                continue
        
        return {
            "success": True,
            "history": history,
            "total_entries": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting update history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-file-watcher")
async def start_file_watching(
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Start file system watcher for automatic updates on file changes
    
    Requires admin privileges
    """
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=403, 
                detail="Admin privileges required"
            )
        
        service = await get_update_service(app_request)
        
        # Start file watcher in background
        from app.services.knowledge_updater import start_file_watcher
        background_tasks.add_task(start_file_watcher, service)
        
        return {
            "success": True,
            "message": "File watcher started - knowledge base will auto-update on file changes",
            "watching_directory": str(service.knowledge_base_dir),
            "started_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting file watcher: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
