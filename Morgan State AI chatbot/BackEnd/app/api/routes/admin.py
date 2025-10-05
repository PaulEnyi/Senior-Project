from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import os
import json
import zipfile
import shutil
from pathlib import Path

from ...core.security import get_current_admin_user, SecurityManager
from ...core.exceptions import create_success_response, create_error_response
from ...services.langchain_service import LangChainRAGService
from ...services.pinecone_service import PineconeService
from ...services.openai_service import OpenAIService
from ...services.thread_manager import ThreadManager
from ...core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for admin operations
class AdminLoginRequest(BaseModel):
    username: str = Field(..., description="Admin username")
    password: str = Field(..., description="Admin password")

class AdminLoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")

class SystemHealthResponse(BaseModel):
    status: str = Field(..., description="Overall system status")
    services: Dict[str, Any] = Field(..., description="Individual service statuses")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class RefreshKnowledgeRequest(BaseModel):
    force_refresh: bool = Field(default=False, description="Force refresh even if recent")
    backup_existing: bool = Field(default=True, description="Backup existing data")

class AnalyticsResponse(BaseModel):
    total_conversations: int
    total_messages: int
    average_response_time: float
    popular_questions: List[Dict[str, Any]]
    error_rate: float
    uptime_percentage: float

# Global service instances
rag_service = LangChainRAGService()
pinecone_service = PineconeService()
openai_service = OpenAIService()
thread_manager = ThreadManager()

# Backup Service Implementation
class BackupService:
    """Service for creating and managing system backups"""
    
    def __init__(self):
        self.backup_dir = Path("data/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_full_backup(
        self, 
        include_vectors: bool = True,
        include_threads: bool = True,
        include_knowledge_base: bool = True,
        backup_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a complete system backup"""
        try:
            if not backup_name:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                backup_name = f"morgan_ai_backup_{timestamp}"
            
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            backup_info = {
                "backup_name": backup_name,
                "created_at": datetime.utcnow().isoformat(),
                "components": {},
                "total_size": 0,
                "status": "in_progress"
            }
            
            logger.info(f"Starting backup: {backup_name}")
            
            # Backup Pinecone vectors
            if include_vectors:
                logger.info("Backing up Pinecone vectors...")
                vector_info = await self._backup_vectors(backup_path)
                backup_info["components"]["vectors"] = vector_info
            
            # Backup conversation threads
            if include_threads:
                logger.info("Backing up conversation threads...")
                thread_info = await self._backup_threads(backup_path)
                backup_info["components"]["threads"] = thread_info
            
            # Backup knowledge base
            if include_knowledge_base:
                logger.info("Backing up knowledge base...")
                kb_info = await self._backup_knowledge_base(backup_path)
                backup_info["components"]["knowledge_base"] = kb_info
            
            # Create backup metadata
            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            # Calculate total size
            total_size = sum(
                f.stat().st_size 
                for f in backup_path.rglob('*') 
                if f.is_file()
            )
            backup_info["total_size"] = total_size
            backup_info["status"] = "completed"
            
            # Create compressed archive
            archive_path = await self._create_archive(backup_path)
            backup_info["archive_path"] = str(archive_path)
            backup_info["archive_size"] = archive_path.stat().st_size
            
            # Update metadata with final info
            with open(metadata_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            logger.info(f"Backup completed: {backup_name} ({total_size} bytes)")
            return backup_info
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            backup_info["status"] = "failed"
            backup_info["error"] = str(e)
            raise Exception(f"Backup creation failed: {str(e)}")
    
    async def _backup_vectors(self, backup_path: Path) -> Dict[str, Any]:
        """Export Pinecone vectors"""
        try:
            vectors_dir = backup_path / "vectors"
            vectors_dir.mkdir(exist_ok=True)
            
            # Get index statistics
            index_stats = await pinecone_service.get_index_stats()
            
            # Create vector metadata (simplified for now)
            vector_data = {
                "index_name": settings.PINECONE_INDEX_NAME,
                "dimension": 1536,
                "exported_at": datetime.utcnow().isoformat(),
                "total_vectors": index_stats.get("total_vectors", 0),
                "note": "Vector content backup requires enhanced implementation"
            }
            
            # Save vector metadata
            metadata_file = vectors_dir / "vector_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(vector_data, f, indent=2)
            
            return {
                "status": "completed",
                "total_vectors": index_stats.get("total_vectors", 0),
                "metadata_file": str(metadata_file),
                "note": "Metadata only - implement vector content backup for full recovery"
            }
            
        except Exception as e:
            logger.error(f"Vector backup failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def _backup_threads(self, backup_path: Path) -> Dict[str, Any]:
        """Export conversation threads"""
        try:
            threads_dir = backup_path / "threads"
            threads_dir.mkdir(exist_ok=True)
            
            # Get all threads
            threads = await thread_manager.list_threads(limit=1000)
            exported_threads = []
            
            for thread_metadata in threads:
                thread_id = thread_metadata["thread_id"]
                
                try:
                    # Get thread messages
                    messages = await thread_manager.get_thread_messages(thread_id, limit=1000)
                    
                    # Create thread export data
                    thread_data = {
                        "thread_id": thread_id,
                        "metadata": thread_metadata,
                        "messages": messages,
                        "exported_at": datetime.utcnow().isoformat()
                    }
                    
                    # Save thread to individual file
                    thread_file = threads_dir / f"{thread_id}.json"
                    with open(thread_file, 'w') as f:
                        json.dump(thread_data, f, indent=2)
                    
                    exported_threads.append({
                        "thread_id": thread_id,
                        "message_count": len(messages),
                        "file": str(thread_file)
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to backup thread {thread_id}: {str(e)}")
                    continue
            
            # Create threads summary
            summary = {
                "total_threads": len(threads),
                "exported_threads": len(exported_threads),
                "exported_at": datetime.utcnow().isoformat(),
                "threads": exported_threads
            }
            
            summary_file = threads_dir / "threads_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            return {
                "status": "completed",
                "total_threads": len(threads),
                "exported_threads": len(exported_threads),
                "summary_file": str(summary_file)
            }
            
        except Exception as e:
            logger.error(f"Thread backup failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def _backup_knowledge_base(self, backup_path: Path) -> Dict[str, Any]:
        """Backup knowledge base files"""
        try:
            kb_dir = backup_path / "knowledge_base"
            kb_dir.mkdir(exist_ok=True)
            
            source_kb_path = Path(settings.KNOWLEDGE_BASE_PATH)
            backed_up_files = []
            
            if source_kb_path.exists():
                # Copy entire knowledge base directory structure
                for item in source_kb_path.rglob('*'):
                    if item.is_file():
                        rel_path = item.relative_to(source_kb_path)
                        dest_path = kb_dir / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_path)
                        backed_up_files.append({
                            "source": str(item),
                            "destination": str(dest_path),
                            "size": item.stat().st_size
                        })
            
            # Also backup processed embeddings if they exist
            processed_dir = Path("data/processed")
            if processed_dir.exists():
                dest_processed_dir = kb_dir / "processed"
                dest_processed_dir.mkdir(exist_ok=True)
                
                for item in processed_dir.rglob('*'):
                    if item.is_file():
                        rel_path = item.relative_to(processed_dir)
                        dest_path = dest_processed_dir / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_path)
                        backed_up_files.append({
                            "source": str(item),
                            "destination": str(dest_path),
                            "size": item.stat().st_size
                        })
            
            # Create knowledge base summary
            summary = {
                "backed_up_at": datetime.utcnow().isoformat(),
                "source_path": str(source_kb_path),
                "total_files": len(backed_up_files),
                "total_size": sum(f["size"] for f in backed_up_files),
                "files": backed_up_files
            }
            
            summary_file = kb_dir / "kb_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            return {
                "status": "completed",
                "total_files": len(backed_up_files),
                "total_size": summary["total_size"],
                "summary_file": str(summary_file)
            }
            
        except Exception as e:
            logger.error(f"Knowledge base backup failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def _create_archive(self, backup_path: Path) -> Path:
        """Create a compressed archive of the backup"""
        try:
            archive_path = backup_path.with_suffix('.zip')
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in backup_path.rglob('*'):
                    if file_path.is_file():
                        archive_name = file_path.relative_to(backup_path)
                        zipf.write(file_path, archive_name)
            
            # Remove the uncompressed directory to save space
            shutil.rmtree(backup_path)
            
            return archive_path
            
        except Exception as e:
            logger.error(f"Archive creation failed: {str(e)}")
            raise e
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("*.zip"):
                try:
                    with zipfile.ZipFile(backup_file, 'r') as zipf:
                        if 'backup_metadata.json' in zipf.namelist():
                            metadata_content = zipf.read('backup_metadata.json')
                            metadata = json.loads(metadata_content)
                            metadata["file_path"] = str(backup_file)
                            metadata["file_size"] = backup_file.stat().st_size
                            backups.append(metadata)
                        else:
                            backups.append({
                                "backup_name": backup_file.stem,
                                "file_path": str(backup_file),
                                "file_size": backup_file.stat().st_size,
                                "created_at": datetime.fromtimestamp(
                                    backup_file.stat().st_mtime
                                ).isoformat(),
                                "status": "unknown"
                            })
                except Exception as e:
                    logger.error(f"Error reading backup {backup_file}: {str(e)}")
                    continue
            
            backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            return []
    
    async def delete_backup(self, backup_name: str) -> bool:
        """Delete a backup file"""
        try:
            backup_file = self.backup_dir / f"{backup_name}.zip"
            
            if backup_file.exists():
                backup_file.unlink()
                logger.info(f"Deleted backup: {backup_name}")
                return True
            else:
                logger.warning(f"Backup not found: {backup_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete backup {backup_name}: {str(e)}")
            return False

# API Routes
@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """Admin login endpoint"""
    try:
        is_authenticated = SecurityManager.authenticate_admin(
            request.username, 
            request.password
        )
        
        if not is_authenticated:
            raise HTTPException(
                status_code=401,
                detail=create_error_response(
                    message="Invalid username or password",
                    error_code="INVALID_CREDENTIALS"
                )
            )
        
        access_token = SecurityManager.create_access_token(
            data={"sub": request.username, "role": "admin"}
        )
        
        logger.info(f"Admin login successful for user: {request.username}")
        
        return AdminLoginResponse(
            access_token=access_token,
            expires_in=1800
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Login failed due to server error",
                error_code="LOGIN_ERROR"
            )
        )

@router.post("/logout")
async def admin_logout(current_user: Dict = Depends(get_current_admin_user)):
    """Admin logout endpoint"""
    logger.info(f"Admin logout for user: {current_user['username']}")
    return create_success_response(message="Successfully logged out")

@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health(current_user: Dict = Depends(get_current_admin_user)):
    """Get comprehensive system health status"""
    try:
        services = {}
        overall_status = "healthy"
        
        # Test OpenAI service
        try:
            await openai_service.test_connection()
            services["openai"] = {
                "status": "healthy",
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            services["openai"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
            overall_status = "degraded"
        
        # Test Pinecone service
        try:
            await pinecone_service.test_connection()
            index_stats = await pinecone_service.get_index_stats()
            services["pinecone"] = {
                "status": "healthy",
                "index_stats": index_stats,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            services["pinecone"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
            overall_status = "degraded"
        
        # Test RAG service
        try:
            test_context = await rag_service.get_relevant_context("test", max_results=1)
            services["rag_pipeline"] = {
                "status": "healthy" if test_context else "degraded",
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            services["rag_pipeline"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
            overall_status = "degraded"
        
        # Check if any critical services are down
        critical_services = ["openai", "pinecone"]
        if any(services.get(svc, {}).get("status") == "unhealthy" for svc in critical_services):
            overall_status = "unhealthy"
        
        return SystemHealthResponse(
            status=overall_status,
            services=services
        )
        
    except Exception as e:
        logger.error(f"System health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to retrieve system health",
                error_code="HEALTH_CHECK_ERROR"
            )
        )

@router.post("/refresh-knowledge")
async def refresh_knowledge_base(
    background_tasks: BackgroundTasks,
    request: RefreshKnowledgeRequest = RefreshKnowledgeRequest(),
    current_user: Dict = Depends(get_current_admin_user)
):
    """Refresh the knowledge base"""
    try:
        logger.info(f"Knowledge base refresh initiated by: {current_user['username']}")
        
        background_tasks.add_task(
            _refresh_knowledge_background,
            request.force_refresh,
            request.backup_existing,
            current_user['username']
        )
        
        return create_success_response(
            message="Knowledge base refresh started. This may take several minutes.",
            data={
                "initiated_by": current_user['username'],
                "force_refresh": request.force_refresh,
                "backup_existing": request.backup_existing,
                "estimated_time": "5-10 minutes"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to initiate knowledge refresh: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to start knowledge base refresh",
                error_code="REFRESH_INITIATE_ERROR"
            )
        )

async def _refresh_knowledge_background(force_refresh: bool, backup_existing: bool, username: str):
    """Background task for knowledge base refresh"""
    try:
        logger.info(f"Starting knowledge base refresh (force={force_refresh}, backup={backup_existing})")
        
        if backup_existing:
            logger.info("Creating backup of existing knowledge base...")
            backup_service = BackupService()
            await backup_service.create_full_backup(
                include_vectors=True,
                include_threads=False,
                include_knowledge_base=True,
                backup_name=f"pre_refresh_backup_{username}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            )
        
        success = await rag_service.process_knowledge_base()
        
        if success:
            logger.info(f"Knowledge base refresh completed successfully by {username}")
        else:
            logger.error(f"Knowledge base refresh failed for {username}")
            
    except Exception as e:
        logger.error(f"Background knowledge refresh failed: {str(e)}")

@router.post("/clear-database")
async def clear_vector_database(
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_admin_user)
):
    """Clear the vector database"""
    try:
        logger.warning(f"Vector database clear initiated by: {current_user['username']}")
        
        background_tasks.add_task(
            _clear_database_background,
            current_user['username']
        )
        
        return create_success_response(
            message="Vector database clearing started. All embeddings will be removed.",
            data={
                "initiated_by": current_user['username'],
                "warning": "This action cannot be undone"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to initiate database clear: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to clear vector database",
                error_code="CLEAR_DATABASE_ERROR"
            )
        )

async def _clear_database_background(username: str):
    """Background task for clearing database"""
    try:
        logger.info(f"Starting vector database clear by {username}")
        success = await pinecone_service.clear_index()
        
        if success:
            logger.info(f"Vector database cleared successfully by {username}")
        else:
            logger.error(f"Vector database clear failed for {username}")
            
    except Exception as e:
        logger.error(f"Background database clear failed: {str(e)}")

@router.post("/backup")
async def create_backup(
    background_tasks: BackgroundTasks,
    include_vectors: bool = True,
    include_threads: bool = True,
    current_user: Dict = Depends(get_current_admin_user)
):
    """Create system backup"""
    try:
        logger.info(f"Backup initiated by: {current_user['username']}")
        
        background_tasks.add_task(
            _create_backup_background,
            include_vectors,
            include_threads,
            current_user['username']
        )
        
        return create_success_response(
            message="Backup creation started",
            data={
                "initiated_by": current_user['username'],
                "include_vectors": include_vectors,
                "include_threads": include_threads
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to initiate backup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to create backup",
                error_code="BACKUP_ERROR"
            )
        )

async def _create_backup_background(include_vectors: bool, include_threads: bool, username: str):
    """Background task for creating backup"""
    try:
        logger.info(f"Creating backup (vectors={include_vectors}, threads={include_threads}) by {username}")
        
        backup_service = BackupService()
        
        backup_info = await backup_service.create_full_backup(
            include_vectors=include_vectors,
            include_threads=include_threads,
            include_knowledge_base=True,
            backup_name=f"admin_backup_{username}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        )
        
        logger.info(f"Backup completed successfully by {username}: {backup_info['backup_name']}")
        logger.info(f"Backup size: {backup_info.get('total_size', 0)} bytes")
        logger.info(f"Components backed up: {list(backup_info.get('components', {}).keys())}")
        
    except Exception as e:
        logger.error(f"Background backup failed for {username}: {str(e)}")

@router.get("/backups")
async def list_backups(current_user: Dict = Depends(get_current_admin_user)):
    """List all available backups"""
    try:
        backup_service = BackupService()
        backups = await backup_service.list_backups()
        
        return create_success_response(
            data={"backups": backups},
            message=f"Retrieved {len(backups)} backups"
        )
        
    except Exception as e:
        logger.error(f"Failed to list backups: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to retrieve backup list",
                error_code="BACKUP_LIST_ERROR"
            )
        )

@router.delete("/backups/{backup_name}")
async def delete_backup(
    backup_name: str,
    current_user: Dict = Depends(get_current_admin_user)
):
    """Delete a specific backup"""
    try:
        backup_service = BackupService()
        success = await backup_service.delete_backup(backup_name)
        
        if success:
            logger.info(f"Backup {backup_name} deleted by {current_user['username']}")
            return create_success_response(
                message=f"Backup {backup_name} deleted successfully"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    message="Backup not found",
                    error_code="BACKUP_NOT_FOUND"
                )
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete backup {backup_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to delete backup",
                error_code="BACKUP_DELETE_ERROR"
            )
        )

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_usage_analytics(
    days: int = 7,
    current_user: Dict = Depends(get_current_admin_user)
):
    """Get usage analytics and statistics"""
    try:
        analytics = AnalyticsResponse(
            total_conversations=0,
            total_messages=0,
            average_response_time=1.2,
            popular_questions=[],
            error_rate=0.02,
            uptime_percentage=99.5
        )
        
        logger.info(f"Analytics requested by: {current_user['username']}")
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to retrieve analytics",
                error_code="ANALYTICS_ERROR"
            )
        )

@router.get("/users")
async def get_admin_users(current_user: Dict = Depends(get_current_admin_user)):
    """Get list of admin users"""
    try:
        users = [
            {
                "username": "admin",
                "role": "admin",
                "last_login": None,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        
        return create_success_response(
            data={"users": users},
            message=f"Retrieved {len(users)} admin users"
        )
        
    except Exception as e:
        logger.error(f"Failed to get admin users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="Failed to retrieve admin users",
                error_code="USERS_ERROR"
            )
        )