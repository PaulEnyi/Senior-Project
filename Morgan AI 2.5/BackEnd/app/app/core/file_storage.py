"""
File-based storage system for user data
Each user gets their own folder in data/users/ containing:
- user_info.json (username, password hash, email, timestamps)
- chat_history/ (all previous chats organized by thread ID)
- degree_works/ (uploaded DegreeWorks files and parsed data)
- profile.json (additional user profile information)
"""

import os
import json
import hashlib
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import shutil

logger = logging.getLogger(__name__)

# Base data directory
BASE_DATA_DIR = Path(__file__).parent.parent.parent / "data"
USERS_DIR = BASE_DATA_DIR / "users"

# Morgan State University timezone (EST/EDT)
EST = timezone(timedelta(hours=-5))
EDT = timezone(timedelta(hours=-4))

def get_local_timestamp() -> str:
    """Get current timestamp in Morgan State University local timezone (EST/EDT)"""
    now_utc = datetime.now(timezone.utc)
    # Check if EDT (daylight saving time) is in effect
    # EDT is typically March-November
    month = now_utc.month
    if 3 <= month <= 10:  # EDT (daylight saving time)
        local_tz = EDT
    else:  # EST (standard time)
        local_tz = EST
    local_time = now_utc.astimezone(local_tz)
    return local_time.isoformat()

class FileStorageService:
    """Manages file-based storage for all user data"""
    
    def __init__(self):
        """Initialize file storage and create base directories"""
        self.users_dir = USERS_DIR
        self.ensure_base_directories()
    
    def ensure_base_directories(self):
        """Create base directory structure if it doesn't exist"""
        try:
            self.users_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ User storage directory initialized at: {self.users_dir}")
        except Exception as e:
            logger.error(f"Failed to create users directory: {e}")
            raise
    
    def get_user_folder(self, user_id: str) -> Path:
        """Get the folder path for a specific user"""
        return self.users_dir / user_id
    
    def create_user_folder_structure(self, user_id: str) -> Dict[str, Path]:
        """
        Create complete folder structure for a new user
        
        Returns:
            Dict with paths to all user folders
        """
        try:
            user_folder = self.get_user_folder(user_id)
            
            # Create main user folder
            user_folder.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            folders = {
                'user_folder': user_folder,
                'chat_history': user_folder / 'chat_history',
                'degree_works': user_folder / 'degree_works',
                'files': user_folder / 'files',
                'temp': user_folder / 'temp'
            }
            
            for folder_name, folder_path in folders.items():
                if folder_name != 'user_folder':  # user_folder already created
                    folder_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"✓ Created folder structure for user: {user_id}")
            return folders
            
        except Exception as e:
            logger.error(f"Error creating user folder structure: {e}")
            raise
    
    def save_user_info(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """
        Save user information to user_info.json
        
        Args:
            user_id: Unique user identifier
            user_data: Dict containing username, password_hash, email, etc.
        
        Returns:
            True if successful
        """
        try:
            user_folder = self.get_user_folder(user_id)
            user_info_path = user_folder / 'user_info.json'
            
            # Add timestamps if not present
            if 'created_at' not in user_data:
                user_data['created_at'] = datetime.utcnow().isoformat()
            
            user_data['updated_at'] = datetime.utcnow().isoformat()
            user_data['user_id'] = user_id
            
            # Write user info
            with open(user_info_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Saved user info for: {user_data.get('username', user_id)}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user info: {e}")
            return False
    
    def load_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load user information from user_info.json
        
        Args:
            user_id: Unique user identifier
        
        Returns:
            User data dict or None if not found
        """
        try:
            user_folder = self.get_user_folder(user_id)
            user_info_path = user_folder / 'user_info.json'
            
            if not user_info_path.exists():
                return None
            
            with open(user_info_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            return user_data
            
        except Exception as e:
            logger.error(f"Error loading user info: {e}")
            return None
    
    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by email address
        
        Args:
            email: Email to search for
        
        Returns:
            User data dict or None if not found
        """
        try:
            # Search through all user folders
            for user_folder in self.users_dir.iterdir():
                if user_folder.is_dir():
                    user_info_path = user_folder / 'user_info.json'
                    if user_info_path.exists():
                        with open(user_info_path, 'r', encoding='utf-8') as f:
                            user_data = json.load(f)
                        
                        if user_data.get('email', '').lower() == email.lower():
                            return user_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding user by email: {e}")
            return None
    
    def find_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by username
        
        Args:
            username: Username to search for
        
        Returns:
            User data dict or None if not found
        """
        try:
            # Search through all user folders
            for user_folder in self.users_dir.iterdir():
                if user_folder.is_dir():
                    user_info_path = user_folder / 'user_info.json'
                    if user_info_path.exists():
                        with open(user_info_path, 'r', encoding='utf-8') as f:
                            user_data = json.load(f)
                        
                        if user_data.get('username', '').lower() == username.lower():
                            return user_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding user by username: {e}")
            return None
    
    def save_chat_thread(self, user_id: str, thread_id: str, thread_data: Dict[str, Any]) -> bool:
        """
        Save a chat thread to user's chat_history folder
        
        Args:
            user_id: Unique user identifier
            thread_id: Unique thread identifier
            thread_data: Dict containing thread title, messages, timestamps, etc.
        
        Returns:
            True if successful
        """
        try:
            chat_history_folder = self.get_user_folder(user_id) / 'chat_history'
            chat_history_folder.mkdir(parents=True, exist_ok=True)
            
            thread_file_path = chat_history_folder / f"{thread_id}.json"
            
            # Add timestamps
            if 'created_at' not in thread_data:
                thread_data['created_at'] = datetime.utcnow().isoformat()
            
            thread_data['updated_at'] = datetime.utcnow().isoformat()
            thread_data['thread_id'] = thread_id
            thread_data['user_id'] = user_id
            
            # Write thread data
            with open(thread_file_path, 'w', encoding='utf-8') as f:
                json.dump(thread_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Saved chat thread {thread_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving chat thread: {e}")
            return False
    
    def load_chat_thread(self, user_id: str, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific chat thread
        
        Args:
            user_id: Unique user identifier
            thread_id: Unique thread identifier
        
        Returns:
            Thread data dict or None if not found
        """
        try:
            thread_file_path = self.get_user_folder(user_id) / 'chat_history' / f"{thread_id}.json"
            
            if not thread_file_path.exists():
                return None
            
            with open(thread_file_path, 'r', encoding='utf-8') as f:
                thread_data = json.load(f)
            
            return thread_data
            
        except Exception as e:
            logger.error(f"Error loading chat thread: {e}")
            return None
    
    def get_user_chat_threads(self, user_id: str, limit: int = 20, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        Get all chat threads for a user
        
        Args:
            user_id: Unique user identifier
            limit: Maximum number of threads to return
            include_deleted: Include soft-deleted threads
        
        Returns:
            List of thread data dicts, sorted by updated_at descending
        """
        try:
            chat_history_folder = self.get_user_folder(user_id) / 'chat_history'
            
            if not chat_history_folder.exists():
                return []
            
            threads = []
            
            # Load all thread files
            for thread_file in chat_history_folder.glob('*.json'):
                try:
                    with open(thread_file, 'r', encoding='utf-8') as f:
                        thread_data = json.load(f)
                    
                    # Filter deleted threads if requested
                    if not include_deleted and thread_data.get('is_deleted', False):
                        continue
                    
                    threads.append(thread_data)
                    
                except Exception as e:
                    logger.warning(f"Error loading thread file {thread_file}: {e}")
                    continue
            
            # Sort by updated_at descending (most recent first)
            threads.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            # Apply limit
            return threads[:limit]
            
        except Exception as e:
            logger.error(f"Error getting user chat threads: {e}")
            return []
    
    def delete_chat_thread(self, user_id: str, thread_id: str, soft_delete: bool = True) -> bool:
        """
        Delete a chat thread (soft or hard delete)
        
        Args:
            user_id: Unique user identifier
            thread_id: Unique thread identifier
            soft_delete: If True, mark as deleted. If False, permanently delete file.
        
        Returns:
            True if successful
        """
        try:
            thread_file_path = self.get_user_folder(user_id) / 'chat_history' / f"{thread_id}.json"
            
            if not thread_file_path.exists():
                logger.warning(f"Thread file not found: {thread_id}")
                return False
            
            if soft_delete:
                # Soft delete: mark as deleted in the JSON
                with open(thread_file_path, 'r', encoding='utf-8') as f:
                    thread_data = json.load(f)
                
                thread_data['is_deleted'] = True
                thread_data['deleted_at'] = datetime.utcnow().isoformat()
                
                with open(thread_file_path, 'w', encoding='utf-8') as f:
                    json.dump(thread_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✓ Soft deleted thread {thread_id}")
            else:
                # Hard delete: remove file
                thread_file_path.unlink()
                logger.info(f"✓ Permanently deleted thread {thread_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting chat thread: {e}")
            return False
    
    def search_chat_threads(self, user_id: str, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search chat threads by title or message content
        
        Args:
            user_id: Unique user identifier
            query: Search query string
            limit: Maximum number of results
        
        Returns:
            List of matching threads with highlighted matches
        """
        try:
            threads = self.get_user_chat_threads(user_id, limit=1000, include_deleted=False)
            
            query_lower = query.lower()
            matching_threads = []
            
            for thread in threads:
                matches = []
                
                # Search in thread title
                title = thread.get('title', '')
                if query_lower in title.lower():
                    matches.append({
                        'type': 'title',
                        'content': title
                    })
                
                # Search in messages
                messages = thread.get('messages', [])
                for message in messages:
                    content = message.get('content', '')
                    if query_lower in content.lower():
                        matches.append({
                            'type': 'message',
                            'role': message.get('role', ''),
                            'content': content,
                            'timestamp': message.get('timestamp', '')
                        })
                
                # If matches found, add to results
                if matches:
                    result = {
                        'thread_id': thread.get('thread_id', ''),
                        'thread_title': thread.get('title', 'Untitled Chat'),
                        'created_at': thread.get('created_at', ''),
                        'updated_at': thread.get('updated_at', ''),
                        'message_count': len(messages),
                        'matches': matches[:3]  # Limit to 3 matches per thread
                    }
                    matching_threads.append(result)
            
            # Sort by relevance (number of matches) then by updated_at
            matching_threads.sort(key=lambda x: (len(x['matches']), x['updated_at']), reverse=True)
            
            return matching_threads[:limit]
            
        except Exception as e:
            logger.error(f"Error searching chat threads: {e}")
            return []
    
    def save_degree_works_file(self, user_id: str, file_name: str, file_data: bytes, parsed_data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Save a DegreeWorks file to user's degree_works folder
        
        Args:
            user_id: Unique user identifier
            file_name: Original filename
            file_data: Binary file data
            parsed_data: Optional parsed/extracted data from the file
        
        Returns:
            True if successful
        """
        try:
            degree_works_folder = self.get_user_folder(user_id) / 'degree_works'
            degree_works_folder.mkdir(parents=True, exist_ok=True)
            
            # Save the file
            file_path = degree_works_folder / file_name
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            previous_versions = self.get_user_degree_works_files(user_id)
            version_id = str(uuid.uuid4())
            uploaded_at = get_local_timestamp()
            metadata = {
                'id': version_id,
                'file_name': file_name,
                'file_path': str(file_path),
                'uploaded_at': uploaded_at,
                'file_size': len(file_data),
                'parsed_data': parsed_data or {},
                'previous_version_id': previous_versions[0]['id'] if previous_versions else None,
                'diff_from_previous': None
            }
            if previous_versions:
                try:
                    last = previous_versions[0].get('parsed_data', {})
                    curr = parsed_data or {}
                    metadata['diff_from_previous'] = self._diff_degree_works(last, curr)
                except Exception as e:
                    metadata['diff_from_previous'] = {'error': str(e)}
            
            metadata_path = degree_works_folder / f"{file_name}.meta.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Saved DegreeWorks file for user {user_id}: {file_name} (version {version_id})")
            return metadata
            
        except Exception as e:
            logger.error(f"Error saving DegreeWorks file: {e}")
            return None

    def _diff_degree_works(self, previous: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prev_summary = previous.get('academic_summary', {})
            curr_summary = current.get('academic_summary', {})

            def as_set(data: Dict, key: str) -> set:
                courses_block = data.get('courses', {})
                return {c.get('course_code') for c in courses_block.get(key, []) if c.get('course_code')}

            prev_completed = as_set(previous, 'completed')
            curr_completed = as_set(current, 'completed')
            prev_in_progress = as_set(previous, 'in_progress')
            curr_in_progress = as_set(current, 'in_progress')
            prev_remaining = as_set(previous, 'remaining')
            curr_remaining = as_set(current, 'remaining')

            def grade_map(data: Dict, status: str) -> Dict[str, Any]:
                mapping = {}
                for c in data.get('courses', {}).get(status, []):
                    code = c.get('course_code')
                    if code:
                        mapping[code] = c.get('grade')
                return mapping
            prev_grades = grade_map(previous, 'completed')
            curr_grades = grade_map(current, 'completed')
            grade_changes = []
            for code, old_grade in prev_grades.items():
                if code in curr_grades:
                    new_grade = curr_grades[code]
                    if old_grade and new_grade and old_grade != new_grade:
                        grade_changes.append({'course_code': code, 'previous_grade': old_grade, 'current_grade': new_grade})

            prev_timeline = previous.get('course_timeline', {})
            curr_timeline = current.get('course_timeline', {})
            prev_terms = set(prev_timeline.keys())
            curr_terms = set(curr_timeline.keys())

            diff = {
                'completed_credits_delta': round(curr_summary.get('completed_credits', 0) - prev_summary.get('completed_credits', 0), 2),
                'in_progress_credits_delta': round(curr_summary.get('in_progress_credits', 0) - prev_summary.get('in_progress_credits', 0), 2),
                'gpa_delta': round((curr_summary.get('gpa') or 0) - (prev_summary.get('gpa') or 0), 3),
                'classification_changed': prev_summary.get('classification') != curr_summary.get('classification'),
                'previous_classification': prev_summary.get('classification'),
                'current_classification': curr_summary.get('classification'),
                'newly_completed_courses': sorted(list(curr_completed - prev_completed)),
                'new_in_progress_courses': sorted(list(curr_in_progress - prev_in_progress)),
                'courses_no_longer_in_progress': sorted(list(prev_in_progress - curr_in_progress)),
                'newly_remaining_courses': sorted(list(curr_remaining - prev_remaining)),
                'remaining_courses_resolved': sorted(list(prev_remaining - curr_remaining)),
                'grade_changes': grade_changes,
                'terms_added': sorted(list(curr_terms - prev_terms)),
                'terms_removed': sorted(list(prev_terms - curr_terms))
            }
            return diff
        except Exception as e:
            return {'error': str(e)}

    def delete_degree_works_version(self, user_id: str, version_id: str) -> bool:
        try:
            degree_works_folder = self.get_user_folder(user_id) / 'degree_works'
            if not degree_works_folder.exists():
                return False
            deleted = False
            for meta_file in degree_works_folder.glob('*.meta.json'):
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    if metadata.get('id') == version_id:
                        meta_file.unlink(missing_ok=True)
                        pdf_path = metadata.get('file_path')
                        if pdf_path and os.path.exists(pdf_path):
                            referenced_elsewhere = False
                            for other_meta in degree_works_folder.glob('*.meta.json'):
                                with open(other_meta, 'r', encoding='utf-8') as g:
                                    other_data = json.load(g)
                                if other_data.get('file_path') == pdf_path:
                                    referenced_elsewhere = True
                                    break
                            if not referenced_elsewhere:
                                try:
                                    os.remove(pdf_path)
                                except OSError:
                                    pass
                        deleted = True
                        break
                except Exception:
                    continue
            return deleted
        except Exception as e:
            logger.error(f"Error deleting Degree Works version: {e}")
            return False
    
    def get_user_degree_works_files(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all DegreeWorks files for a user
        
        Args:
            user_id: Unique user identifier
        
        Returns:
            List of file metadata dicts
        """
        try:
            degree_works_folder = self.get_user_folder(user_id) / 'degree_works'
            
            if not degree_works_folder.exists():
                return []
            
            files_metadata = []
            
            # Load all metadata files
            for meta_file in degree_works_folder.glob('*.meta.json'):
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    files_metadata.append(metadata)
                    
                except Exception as e:
                    logger.warning(f"Error loading metadata file {meta_file}: {e}")
                    continue
            
            # Sort by uploaded_at descending
            files_metadata.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
            
            return files_metadata
            
        except Exception as e:
            logger.error(f"Error getting DegreeWorks files: {e}")
            return []
    
    def save_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        Save user profile data to profile.json
        
        Args:
            user_id: Unique user identifier
            profile_data: Dict containing profile information
        
        Returns:
            True if successful
        """
        try:
            user_folder = self.get_user_folder(user_id)
            profile_path = user_folder / 'profile.json'
            
            profile_data['updated_at'] = datetime.utcnow().isoformat()
            
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Saved profile for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
            return False
    
    def load_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load user profile data from profile.json
        
        Args:
            user_id: Unique user identifier
        
        Returns:
            Profile data dict or None if not found
        """
        try:
            profile_path = self.get_user_folder(user_id) / 'profile.json'
            
            if not profile_path.exists():
                return None
            
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error loading user profile: {e}")
            return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get information about all users
        
        Returns:
            List of user info dicts
        """
        try:
            users = []
            
            for user_folder in self.users_dir.iterdir():
                if user_folder.is_dir():
                    user_info_path = user_folder / 'user_info.json'
                    if user_info_path.exists():
                        with open(user_info_path, 'r', encoding='utf-8') as f:
                            user_data = json.load(f)
                        
                        users.append(user_data)
            
            # Sort by created_at descending
            users.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return users
            
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def delete_user(self, user_id: str, permanent: bool = False) -> bool:
        """
        Delete a user and all their data
        
        Args:
            user_id: Unique user identifier
            permanent: If True, permanently delete folder. If False, mark as deleted.
        
        Returns:
            True if successful
        """
        try:
            user_folder = self.get_user_folder(user_id)
            
            if not user_folder.exists():
                logger.warning(f"User folder not found: {user_id}")
                return False
            
            if permanent:
                # Permanently delete entire user folder
                shutil.rmtree(user_folder)
                logger.info(f"✓ Permanently deleted user {user_id}")
            else:
                # Soft delete: mark user as deleted in user_info.json
                user_info_path = user_folder / 'user_info.json'
                if user_info_path.exists():
                    with open(user_info_path, 'r', encoding='utf-8') as f:
                        user_data = json.load(f)
                    
                    user_data['is_deleted'] = True
                    user_data['deleted_at'] = datetime.utcnow().isoformat()
                    
                    with open(user_info_path, 'w', encoding='utf-8') as f:
                        json.dump(user_data, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"✓ Soft deleted user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the file storage system
        
        Returns:
            Dict with total users, threads, files, etc.
        """
        try:
            stats = {
                'total_users': 0,
                'active_users': 0,
                'deleted_users': 0,
                'total_chat_threads': 0,
                'total_degree_works_files': 0,
                'total_storage_bytes': 0
            }
            
            for user_folder in self.users_dir.iterdir():
                if user_folder.is_dir():
                    stats['total_users'] += 1
                    
                    # Check user info
                    user_info_path = user_folder / 'user_info.json'
                    if user_info_path.exists():
                        with open(user_info_path, 'r', encoding='utf-8') as f:
                            user_data = json.load(f)
                        
                        if user_data.get('is_deleted', False):
                            stats['deleted_users'] += 1
                        else:
                            stats['active_users'] += 1
                    
                    # Count chat threads
                    chat_history_folder = user_folder / 'chat_history'
                    if chat_history_folder.exists():
                        stats['total_chat_threads'] += len(list(chat_history_folder.glob('*.json')))
                    
                    # Count degree works files
                    degree_works_folder = user_folder / 'degree_works'
                    if degree_works_folder.exists():
                        stats['total_degree_works_files'] += len(list(degree_works_folder.glob('*.meta.json')))
                    
                    # Calculate storage size
                    for file_path in user_folder.rglob('*'):
                        if file_path.is_file():
                            stats['total_storage_bytes'] += file_path.stat().st_size
            
            # Convert bytes to MB
            stats['total_storage_mb'] = round(stats['total_storage_bytes'] / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}


# Global file storage service instance
file_storage = FileStorageService()


def get_file_storage() -> FileStorageService:
    """Get the global file storage service instance"""
    return file_storage
