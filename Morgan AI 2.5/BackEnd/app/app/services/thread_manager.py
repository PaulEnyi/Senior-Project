from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import json
import logging
from collections import defaultdict
from app.models.chat import ChatMessage, ChatThread

logger = logging.getLogger(__name__)

class ThreadManager:
    """Manage chat threads and message history"""
    
    def __init__(self):
        # In-memory storage (in production, use a database)
        self.threads: Dict[str, ChatThread] = {}
        self.messages: Dict[str, List[ChatMessage]] = defaultdict(list)
        self.user_threads: Dict[str, List[str]] = defaultdict(list)
    
    async def create_thread(
        self,
        user_id: str,
        thread_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatThread:
        """Create a new chat thread"""
        try:
            if not thread_id:
                thread_id = str(uuid.uuid4())
            
            thread = ChatThread(
                thread_id=thread_id,
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            self.threads[thread_id] = thread
            self.user_threads[user_id].append(thread_id)
            
            logger.info(f"Created thread {thread_id} for user {user_id}")
            return thread
            
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            raise
    
    async def get_thread(
        self,
        thread_id: str
    ) -> Optional[ChatThread]:
        """Get a thread by ID"""
        return self.threads.get(thread_id)
    
    async def get_user_threads(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[ChatThread]:
        """Get all threads for a user"""
        try:
            thread_ids = self.user_threads.get(user_id, [])
            
            # Sort by updated time (most recent first)
            threads = []
            for thread_id in thread_ids:
                if thread_id in self.threads:
                    threads.append(self.threads[thread_id])
            
            threads.sort(key=lambda x: x.updated_at, reverse=True)
            
            # Apply pagination
            return threads[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error getting user threads: {str(e)}")
            return []
    
    async def add_message(
        self,
        thread_id: str,
        message: ChatMessage
    ) -> ChatMessage:
        """Add a message to a thread"""
        try:
            if thread_id not in self.threads:
                raise ValueError(f"Thread {thread_id} not found")
            
            # Add message ID if not present
            if not hasattr(message, 'message_id'):
                message.message_id = str(uuid.uuid4())
            
            # Add timestamp if not present
            if not hasattr(message, 'timestamp'):
                message.timestamp = datetime.utcnow()
            
            self.messages[thread_id].append(message)
            
            # Update thread's last updated time
            self.threads[thread_id].updated_at = datetime.utcnow()
            self.threads[thread_id].message_count = len(self.messages[thread_id])
            
            # Update thread title if it's the first user message
            if message.role == "user" and self.threads[thread_id].message_count == 1:
                # Extract first few words as title
                title = message.content[:50]
                if len(message.content) > 50:
                    title += "..."
                self.threads[thread_id].title = title
            
            logger.debug(f"Added message to thread {thread_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            raise
    
    async def get_messages(
        self,
        thread_id: str,
        limit: Optional[int] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None
    ) -> List[ChatMessage]:
        """Get messages from a thread"""
        try:
            if thread_id not in self.messages:
                return []
            
            messages = self.messages[thread_id]
            
            # Filter by time if specified
            if before:
                messages = [m for m in messages if m.timestamp < before]
            if after:
                messages = [m for m in messages if m.timestamp > after]
            
            # Apply limit
            if limit:
                messages = messages[-limit:]
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return []
    
    async def delete_thread(
        self,
        thread_id: str
    ):
        """Delete a thread and its messages"""
        try:
            if thread_id in self.threads:
                user_id = self.threads[thread_id].user_id
                
                # Remove from user's thread list
                if user_id in self.user_threads:
                    self.user_threads[user_id] = [
                        tid for tid in self.user_threads[user_id] 
                        if tid != thread_id
                    ]
                
                # Delete thread and messages
                del self.threads[thread_id]
                if thread_id in self.messages:
                    del self.messages[thread_id]
                
                logger.info(f"Deleted thread {thread_id}")
                
        except Exception as e:
            logger.error(f"Error deleting thread: {str(e)}")
            raise
    
    async def search_user_chats(
        self,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search through a user's chat history"""
        try:
            results = []
            query_lower = query.lower()
            
            # Get user's threads
            thread_ids = self.user_threads.get(user_id, [])
            
            for thread_id in thread_ids:
                if thread_id not in self.messages:
                    continue
                
                # Search messages in thread
                for message in self.messages[thread_id]:
                    if query_lower in message.content.lower():
                        results.append({
                            "thread_id": thread_id,
                            "message_id": getattr(message, 'message_id', ''),
                            "content": message.content,
                            "role": message.role,
                            "timestamp": message.timestamp.isoformat() if message.timestamp else None,
                            "thread_title": self.threads[thread_id].title if thread_id in self.threads else ""
                        })
                        
                        if len(results) >= limit:
                            break
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching chats: {str(e)}")
            return []
    
    async def add_feedback(
        self,
        thread_id: str,
        message_id: str,
        rating: int,
        feedback: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Add feedback for a message"""
        try:
            if thread_id not in self.messages:
                raise ValueError(f"Thread {thread_id} not found")
            
            # Find the message
            for message in self.messages[thread_id]:
                if getattr(message, 'message_id', '') == message_id:
                    # Add feedback to message metadata
                    if not hasattr(message, 'metadata'):
                        message.metadata = {}
                    
                    message.metadata['feedback'] = {
                        'rating': rating,
                        'comment': feedback,
                        'user_id': user_id,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    logger.info(f"Added feedback to message {message_id}")
                    break
                    
        except Exception as e:
            logger.error(f"Error adding feedback: {str(e)}")
            raise
    
    async def get_thread_summary(
        self,
        thread_id: str
    ) -> Dict[str, Any]:
        """Get a summary of a thread"""
        try:
            if thread_id not in self.threads:
                return {}
            
            thread = self.threads[thread_id]
            messages = self.messages.get(thread_id, [])
            
            # Calculate statistics
            user_messages = [m for m in messages if m.role == "user"]
            assistant_messages = [m for m in messages if m.role == "assistant"]
            
            return {
                "thread_id": thread_id,
                "title": thread.title,
                "created_at": thread.created_at.isoformat() if thread.created_at else None,
                "updated_at": thread.updated_at.isoformat() if thread.updated_at else None,
                "message_count": len(messages),
                "user_message_count": len(user_messages),
                "assistant_message_count": len(assistant_messages),
                "last_message": messages[-1].content[:100] if messages else None
            }
            
        except Exception as e:
            logger.error(f"Error getting thread summary: {str(e)}")
            return {}
    
    async def cleanup_old_threads(
        self,
        days_old: int = 30
    ):
        """Clean up threads older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            threads_to_delete = []
            
            for thread_id, thread in self.threads.items():
                if thread.updated_at < cutoff_date:
                    threads_to_delete.append(thread_id)
            
            for thread_id in threads_to_delete:
                await self.delete_thread(thread_id)
            
            logger.info(f"Cleaned up {len(threads_to_delete)} old threads")
            return len(threads_to_delete)
            
        except Exception as e:
            logger.error(f"Error cleaning up threads: {str(e)}")
            return 0