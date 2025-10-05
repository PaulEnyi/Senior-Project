from typing import List, Dict, Any, Optional
import logging
import json
import os
import uuid
from datetime import datetime, timedelta
from ..core.config import settings
from ..core.exceptions import ThreadManagementException

logger = logging.getLogger(__name__)

class ThreadManager:
    """Service for managing conversation threads and message history"""
    
    def __init__(self):
        self.storage_path = os.path.join("data", "threads")
        self.max_thread_messages = settings.MAX_THREAD_HISTORY
        self._ensure_storage_directory()
        
        # In-memory cache for recent threads (in production, use Redis)
        self.thread_cache = {}
        self.cache_ttl = timedelta(hours=1)
    
    def _ensure_storage_directory(self):
        """Ensure the storage directory exists"""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            logger.debug(f"Thread storage directory: {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to create storage directory: {str(e)}")
            raise ThreadManagementException(f"Failed to create storage directory: {str(e)}")
    
    def _get_thread_file_path(self, thread_id: str) -> str:
        """Get the file path for a thread"""
        return os.path.join(self.storage_path, f"{thread_id}.json")
    
    def _get_thread_metadata_path(self, thread_id: str) -> str:
        """Get the file path for thread metadata"""
        return os.path.join(self.storage_path, f"{thread_id}_meta.json")
    
    async def create_thread(self, thread_id: str = None) -> str:
        """Create a new conversation thread"""
        try:
            thread_id = thread_id or str(uuid.uuid4())
            
            # Initialize thread data
            thread_data = {
                "thread_id": thread_id,
                "created_at": datetime.utcnow().isoformat(),
                "messages": []
            }
            
            # Initialize thread metadata
            metadata = {
                "thread_id": thread_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "message_count": 0,
                "last_message": "",
                "title": "New Conversation",
                "tags": []
            }
            
            # Save to files
            thread_file = self._get_thread_file_path(thread_id)
            meta_file = self._get_thread_metadata_path(thread_id)
            
            with open(thread_file, 'w', encoding='utf-8') as f:
                json.dump(thread_data, f, indent=2)
            
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Add to cache
            self.thread_cache[thread_id] = {
                "data": thread_data,
                "metadata": metadata,
                "cached_at": datetime.utcnow()
            }
            
            logger.info(f"Created new thread: {thread_id}")
            return thread_id
            
        except Exception as e:
            logger.error(f"Failed to create thread: {str(e)}")
            raise ThreadManagementException(f"Failed to create thread: {str(e)}")
    
    async def add_message_to_thread(self, thread_id: str, message: Dict[str, Any]) -> bool:
        """Add a message to a conversation thread"""
        try:
            # Load thread data
            thread_data = await self._load_thread_data(thread_id)
            
            if not thread_data:
                # Create thread if it doesn't exist
                await self.create_thread(thread_id)
                thread_data = await self._load_thread_data(thread_id)
            
            # Add timestamp if not present
            if "timestamp" not in message:
                message["timestamp"] = datetime.utcnow().isoformat()
            
            # Add message
            thread_data["messages"].append(message)
            
            # Limit message history
            if len(thread_data["messages"]) > self.max_thread_messages:
                # Keep the first message (often contains important context)
                # and the most recent messages
                first_message = thread_data["messages"][0]
                recent_messages = thread_data["messages"][-(self.max_thread_messages-1):]
                thread_data["messages"] = [first_message] + recent_messages
            
            # Save updated thread
            await self._save_thread_data(thread_id, thread_data)
            
            logger.debug(f"Added message to thread {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add message to thread {thread_id}: {str(e)}")
            raise ThreadManagementException(f"Failed to add message to thread: {str(e)}")
    
    async def get_thread_messages(
        self, 
        thread_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get messages from a conversation thread"""
        try:
            thread_data = await self._load_thread_data(thread_id)
            
            if not thread_data:
                return []
            
            messages = thread_data.get("messages", [])
            
            # Apply pagination
            start_idx = max(0, len(messages) - offset - limit)
            end_idx = len(messages) - offset
            
            if start_idx >= end_idx:
                return []
            
            return messages[start_idx:end_idx]
            
        except Exception as e:
            logger.error(f"Failed to get thread messages: {str(e)}")
            raise ThreadManagementException(f"Failed to get thread messages: {str(e)}")
    
    async def update_thread_metadata(
        self,
        thread_id: str,
        title: str = None,
        last_message: str = None,
        message_count_increment: int = 0,
        tags: List[str] = None
    ) -> bool:
        """Update thread metadata"""
        try:
            metadata = await self._load_thread_metadata(thread_id)
            
            if not metadata:
                return False
            
            # Update fields
            if title:
                metadata["title"] = title
            if last_message is not None:
                metadata["last_message"] = last_message
            if message_count_increment:
                metadata["message_count"] = metadata.get("message_count", 0) + message_count_increment
            if tags is not None:
                metadata["tags"] = tags
            
            metadata["updated_at"] = datetime.utcnow().isoformat()
            
            # Save metadata
            await self._save_thread_metadata(thread_id, metadata)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update thread metadata: {str(e)}")
            raise ThreadManagementException(f"Failed to update thread metadata: {str(e)}")
    
    async def list_threads(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """List conversation threads with metadata"""
        try:
            threads = []
            
            # Get all thread metadata files
            if not os.path.exists(self.storage_path):
                return []
            
            meta_files = [
                f for f in os.listdir(self.storage_path) 
                if f.endswith('_meta.json')
            ]
            
            # Load metadata for each thread
            for meta_file in meta_files:
                thread_id = meta_file.replace('_meta.json', '')
                metadata = await self._load_thread_metadata(thread_id)
                
                if metadata:
                    threads.append(metadata)
            
            # Sort by updated_at (most recent first)
            threads.sort(
                key=lambda x: x.get("updated_at", ""), 
                reverse=True
            )
            
            # Apply pagination
            return threads[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Failed to list threads: {str(e)}")
            raise ThreadManagementException(f"Failed to list threads: {str(e)}")
    
    async def delete_thread(self, thread_id: str) -> bool:
        """Delete a conversation thread"""
        try:
            thread_file = self._get_thread_file_path(thread_id)
            meta_file = self._get_thread_metadata_path(thread_id)
            
            deleted = False
            
            # Delete thread data file
            if os.path.exists(thread_file):
                os.remove(thread_file)
                deleted = True
            
            # Delete metadata file
            if os.path.exists(meta_file):
                os.remove(meta_file)
                deleted = True
            
            # Remove from cache
            if thread_id in self.thread_cache:
                del self.thread_cache[thread_id]
            
            if deleted:
                logger.info(f"Deleted thread: {thread_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete thread {thread_id}: {str(e)}")
            raise ThreadManagementException(f"Failed to delete thread: {str(e)}")
    
    async def clear_thread_messages(self, thread_id: str) -> bool:
        """Clear all messages from a thread but keep the thread"""
        try:
            thread_data = await self._load_thread_data(thread_id)
            
            if not thread_data:
                return False
            
            # Clear messages but keep thread structure
            thread_data["messages"] = []
            
            # Save updated thread
            await self._save_thread_data(thread_id, thread_data)
            
            # Update metadata
            await self.update_thread_metadata(
                thread_id,
                last_message="",
                message_count_increment=-thread_data.get("message_count", 0)
            )
            
            logger.info(f"Cleared messages from thread: {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear thread messages: {str(e)}")
            raise ThreadManagementException(f"Failed to clear thread messages: {str(e)}")
    
    async def _load_thread_data(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Load thread data from file or cache"""
        try:
            # Check cache first
            if thread_id in self.thread_cache:
                cached_data = self.thread_cache[thread_id]
                if datetime.utcnow() - cached_data["cached_at"] < self.cache_ttl:
                    return cached_data["data"]
            
            # Load from file
            thread_file = self._get_thread_file_path(thread_id)
            
            if not os.path.exists(thread_file):
                return None
            
            with open(thread_file, 'r', encoding='utf-8') as f:
                thread_data = json.load(f)
            
            # Update cache
            if thread_id not in self.thread_cache:
                self.thread_cache[thread_id] = {}
            
            self.thread_cache[thread_id]["data"] = thread_data
            self.thread_cache[thread_id]["cached_at"] = datetime.utcnow()
            
            return thread_data
            
        except Exception as e:
            logger.error(f"Failed to load thread data for {thread_id}: {str(e)}")
            return None
    
    async def _load_thread_metadata(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Load thread metadata from file or cache"""
        try:
            # Check cache first
            if thread_id in self.thread_cache:
                cached_data = self.thread_cache[thread_id]
                if datetime.utcnow() - cached_data["cached_at"] < self.cache_ttl:
                    return cached_data.get("metadata")
            
            # Load from file
            meta_file = self._get_thread_metadata_path(thread_id)
            
            if not os.path.exists(meta_file):
                return None
            
            with open(meta_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Update cache
            if thread_id not in self.thread_cache:
                self.thread_cache[thread_id] = {}
            
            self.thread_cache[thread_id]["metadata"] = metadata
            self.thread_cache[thread_id]["cached_at"] = datetime.utcnow()
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to load thread metadata for {thread_id}: {str(e)}")
            return None
    
    async def _save_thread_data(self, thread_id: str, thread_data: Dict[str, Any]) -> bool:
        """Save thread data to file and update cache"""
        try:
            thread_file = self._get_thread_file_path(thread_id)
            
            with open(thread_file, 'w', encoding='utf-8') as f:
                json.dump(thread_data, f, indent=2)
            
            # Update cache
            if thread_id not in self.thread_cache:
                self.thread_cache[thread_id] = {}
            
            self.thread_cache[thread_id]["data"] = thread_data
            self.thread_cache[thread_id]["cached_at"] = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save thread data for {thread_id}: {str(e)}")
            return False
    
    async def _save_thread_metadata(self, thread_id: str, metadata: Dict[str, Any]) -> bool:
        """Save thread metadata to file and update cache"""
        try:
            meta_file = self._get_thread_metadata_path(thread_id)
            
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Update cache
            if thread_id not in self.thread_cache:
                self.thread_cache[thread_id] = {}
            
            self.thread_cache[thread_id]["metadata"] = metadata
            self.thread_cache[thread_id]["cached_at"] = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save thread metadata for {thread_id}: {str(e)}")
            return False
    
    async def cleanup_old_threads(self, days_old: int = 30) -> int:
        """Clean up old threads to save storage space"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            deleted_count = 0
            
            threads = await self.list_threads(limit=1000)  # Get all threads
            
            for thread_metadata in threads:
                thread_id = thread_metadata["thread_id"]
                updated_at_str = thread_metadata.get("updated_at", thread_metadata.get("created_at"))
                
                try:
                    updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                    
                    if updated_at < cutoff_date:
                        if await self.delete_thread(thread_id):
                            deleted_count += 1
                            
                except ValueError:
                    # Skip threads with invalid timestamps
                    continue
            
            logger.info(f"Cleaned up {deleted_count} old threads")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old threads: {str(e)}")
            return 0