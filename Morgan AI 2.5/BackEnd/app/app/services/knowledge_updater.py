"""
Knowledge base auto-update service
Automatically updates knowledge base when files change
"""

import asyncio
import logging
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

from app.core.config import settings
from app.scripts.ingest_data import KnowledgeBaseIngestor
from app.services.pinecone_service import PineconeService

logger = logging.getLogger(__name__)

class KnowledgeUpdateService:
    """Service to manage automatic knowledge base updates"""
    
    def __init__(self):
        self.ingestor = KnowledgeBaseIngestor()
        self.pinecone_service = PineconeService()
        self.knowledge_base_dir = settings.KNOWLEDGE_BASE_DIR
        self.processed_dir = settings.PROCESSED_DIR
        self.hash_file = self.processed_dir / "file_hashes.json"
        self.file_hashes: Dict[str, str] = {}
        self.update_in_progress = False
        self.last_update_time: Optional[datetime] = None
        self.pending_files: Set[str] = set()
        
    async def initialize(self):
        """Initialize the service and load existing hashes"""
        try:
            # Create directories if they don't exist
            self.processed_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing file hashes
            await self.load_file_hashes()
            
            # Initialize Pinecone
            await self.pinecone_service.initialize()
            
            logger.info("Knowledge update service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge update service: {str(e)}")
            raise
    
    async def load_file_hashes(self):
        """Load file hashes from disk"""
        try:
            if self.hash_file.exists():
                with open(self.hash_file, 'r') as f:
                    self.file_hashes = json.load(f)
                logger.info(f"Loaded {len(self.file_hashes)} file hashes")
            else:
                self.file_hashes = {}
                logger.info("No existing file hashes found, will create new")
        except Exception as e:
            logger.error(f"Error loading file hashes: {str(e)}")
            self.file_hashes = {}
    
    async def save_file_hashes(self):
        """Save file hashes to disk"""
        try:
            with open(self.hash_file, 'w') as f:
                json.dump(self.file_hashes, f, indent=2)
            logger.info(f"Saved {len(self.file_hashes)} file hashes")
        except Exception as e:
            logger.error(f"Error saving file hashes: {str(e)}")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {str(e)}")
            return ""
    
    async def detect_changed_files(self) -> List[Path]:
        """Detect files that have changed since last update"""
        changed_files = []
        
        try:
            # Check all JSON and TXT files in knowledge base
            for pattern in ["*.json", "*.txt"]:
                for file_path in self.knowledge_base_dir.glob(pattern):
                    file_key = str(file_path.relative_to(self.knowledge_base_dir))
                    current_hash = self.calculate_file_hash(file_path)
                    
                    if not current_hash:
                        continue
                    
                    # Check if file is new or modified
                    if file_key not in self.file_hashes or self.file_hashes[file_key] != current_hash:
                        changed_files.append(file_path)
                        logger.info(f"Detected change in: {file_key}")
                        # Update hash
                        self.file_hashes[file_key] = current_hash
            
            if changed_files:
                await self.save_file_hashes()
                
        except Exception as e:
            logger.error(f"Error detecting changed files: {str(e)}")
        
        return changed_files
    
    async def incremental_update(self, files: Optional[List[Path]] = None):
        """Perform incremental update of changed files"""
        if self.update_in_progress:
            logger.warning("Update already in progress, skipping...")
            return {"success": False, "message": "Update already in progress"}
        
        try:
            self.update_in_progress = True
            start_time = datetime.now()
            
            logger.info("Starting incremental knowledge base update...")
            
            # Detect changed files if not provided
            if files is None:
                files = await self.detect_changed_files()
            
            if not files:
                logger.info("No changed files detected")
                return {"success": True, "message": "No changes to update", "files_updated": 0}
            
            logger.info(f"Updating {len(files)} changed files...")
            
            # Process changed files
            documents = []
            for file_path in files:
                try:
                    if file_path.suffix == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Use the ingestor's processing methods
                        if "courses" in file_path.name:
                            content = self.ingestor._process_courses_json(data)
                        elif "prerequisites" in file_path.name:
                            content = self.ingestor._process_prerequisites_json(data)
                        elif "faculty" in file_path.name:
                            content = self.ingestor._process_faculty_json(data)
                        elif "deadlines" in file_path.name:
                            content = self.ingestor._process_deadlines_json(data)
                        elif "advising" in file_path.name:
                            content = self.ingestor._process_advising_json(data)
                        else:
                            content = self.ingestor._json_to_text(data)
                    else:  # .txt file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    # Create document
                    doc = {
                        "content": content,
                        "metadata": {
                            "source": file_path.name,
                            "type": file_path.stem,
                            "category": self.ingestor._categorize_file(file_path.stem),
                            "document_id": self.ingestor._generate_document_id(file_path.stem),
                            "file_size": file_path.stat().st_size,
                            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            "content_length": len(content),
                            "ingested_at": datetime.utcnow().isoformat()
                        }
                    }
                    documents.append(doc)
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
            
            if not documents:
                return {"success": False, "message": "No valid documents to update", "files_updated": 0}
            
            # Delete old vectors for these documents
            for doc in documents:
                doc_id = doc["metadata"]["document_id"]
                try:
                    await self.pinecone_service.delete_vectors(
                        filter_dict={"document_id": doc_id}
                    )
                except Exception as e:
                    logger.warning(f"Error deleting old vectors for {doc_id}: {str(e)}")
            
            # Process and store new vectors
            from app.services.langchain_service import PineconeService as LangchainService
            langchain_service = LangchainService()
            result = await langchain_service.process_documents(documents)
            
            self.last_update_time = datetime.now()
            duration = (self.last_update_time - start_time).total_seconds()
            
            update_result = {
                "success": True,
                "files_updated": len(files),
                "documents_processed": len(documents),
                "vectors_stored": result.get("vectors_stored", 0),
                "duration_seconds": duration,
                "timestamp": self.last_update_time.isoformat()
            }
            
            logger.info(f"Incremental update complete: {update_result}")
            return update_result
            
        except Exception as e:
            logger.error(f"Incremental update failed: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            self.update_in_progress = False
    
    async def full_refresh(self):
        """Perform full knowledge base refresh"""
        if self.update_in_progress:
            logger.warning("Update already in progress, skipping...")
            return {"success": False, "message": "Update already in progress"}
        
        try:
            self.update_in_progress = True
            logger.info("Starting full knowledge base refresh...")
            
            # Run full ingestion
            result = await self.ingestor.ingest_all(clear_existing=True)
            
            # Update all file hashes
            self.file_hashes = {}
            for pattern in ["*.json", "*.txt"]:
                for file_path in self.knowledge_base_dir.glob(pattern):
                    file_key = str(file_path.relative_to(self.knowledge_base_dir))
                    self.file_hashes[file_key] = self.calculate_file_hash(file_path)
            
            await self.save_file_hashes()
            self.last_update_time = datetime.now()
            
            return result
            
        except Exception as e:
            logger.error(f"Full refresh failed: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            self.update_in_progress = False
    
    async def schedule_periodic_update(self, interval_hours: int = 24):
        """Schedule periodic updates"""
        logger.info(f"Starting periodic update scheduler (every {interval_hours} hours)")
        
        while True:
            try:
                await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
                
                logger.info("Running scheduled knowledge base update...")
                result = await self.incremental_update()
                
                if result.get("success"):
                    logger.info(f"Scheduled update completed: {result}")
                else:
                    logger.error(f"Scheduled update failed: {result}")
                    
            except asyncio.CancelledError:
                logger.info("Periodic update scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"Error in periodic update: {str(e)}")
                # Continue running even if one update fails
                continue
    
    def get_status(self) -> Dict:
        """Get current update service status"""
        return {
            "update_in_progress": self.update_in_progress,
            "last_update_time": self.last_update_time.isoformat() if self.last_update_time else None,
            "tracked_files": len(self.file_hashes),
            "pending_files": len(self.pending_files)
        }


class FileChangeHandler(FileSystemEventHandler):
    """Handle file system events for knowledge base updates"""
    
    def __init__(self, update_service: KnowledgeUpdateService):
        self.update_service = update_service
        self.debounce_seconds = 5  # Wait 5 seconds before triggering update
        self.pending_updates: Dict[str, datetime] = {}
        
    def on_modified(self, event):
        if isinstance(event, (FileModifiedEvent, FileCreatedEvent)):
            if event.src_path.endswith(('.json', '.txt')):
                self._schedule_update(event.src_path)
    
    def on_created(self, event):
        if isinstance(event, FileCreatedEvent):
            if event.src_path.endswith(('.json', '.txt')):
                self._schedule_update(event.src_path)
    
    def _schedule_update(self, file_path: str):
        """Schedule an update with debouncing"""
        self.pending_updates[file_path] = datetime.now()
        logger.info(f"File change detected: {file_path}")


async def start_file_watcher(update_service: KnowledgeUpdateService):
    """Start watching knowledge base directory for changes"""
    event_handler = FileChangeHandler(update_service)
    observer = Observer()
    observer.schedule(event_handler, str(update_service.knowledge_base_dir), recursive=True)
    observer.start()
    
    logger.info(f"File watcher started for: {update_service.knowledge_base_dir}")
    
    try:
        while True:
            await asyncio.sleep(10)
            
            # Check for pending updates
            if event_handler.pending_updates:
                now = datetime.now()
                files_to_update = []
                
                for file_path, timestamp in list(event_handler.pending_updates.items()):
                    if (now - timestamp).total_seconds() >= event_handler.debounce_seconds:
                        files_to_update.append(Path(file_path))
                        del event_handler.pending_updates[file_path]
                
                if files_to_update:
                    logger.info(f"Triggering update for {len(files_to_update)} files")
                    await update_service.incremental_update(files_to_update)
                    
    except asyncio.CancelledError:
        observer.stop()
        logger.info("File watcher stopped")
    finally:
        observer.join()
