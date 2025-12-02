"""
Internship Auto-Update Service
Continuously fetches and updates internship data from multiple sources
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import aiohttp
from app.core.config import settings

logger = logging.getLogger(__name__)

class InternshipUpdateService:
    """
    Service for automatic and continuous internship data updates
    Updates on:
    - User login
    - Dashboard refresh
    - Scheduled intervals (every 30 minutes)
    - Manual trigger
    """
    
    def __init__(self):
        self.internships_cache: List[Dict[str, Any]] = []
        self.last_update: Optional[datetime] = None
        self.update_interval_minutes = 30
        self.is_updating = False
        self.update_lock = asyncio.Lock()
        
        # Data sources configuration
        self.data_sources = self._initialize_data_sources()
        
        # Storage path for persistent cache
        self.cache_file = Path("data/internships_cache.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load cached data on initialization
        self._load_cache()
        
        logger.info("InternshipUpdateService initialized")
    
    def _initialize_data_sources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize data sources from environment variables"""
        sources = {}
        
        # GroupMe source
        if settings.GROUPME_ACCESS_TOKEN and settings.GROUPME_GROUP_ID:
            sources['groupme'] = {
                'enabled': True,
                'api_key': settings.GROUPME_ACCESS_TOKEN,
                'group_id': settings.GROUPME_GROUP_ID,
                'base_url': 'https://api.groupme.com/v3',
                'priority': 1
            }
            logger.info("GroupMe data source configured")
        
        # Add other API sources from environment variables
        # Example: Handshake, LinkedIn, Indeed, etc.
        if hasattr(settings, 'HANDSHAKE_API_KEY') and getattr(settings, 'HANDSHAKE_API_KEY'):
            sources['handshake'] = {
                'enabled': True,
                'api_key': getattr(settings, 'HANDSHAKE_API_KEY'),
                'base_url': 'https://api.joinhandshake.com',
                'priority': 2
            }
            logger.info("Handshake data source configured")
        
        if hasattr(settings, 'LINKEDIN_API_KEY') and getattr(settings, 'LINKEDIN_API_KEY'):
            sources['linkedin'] = {
                'enabled': True,
                'api_key': getattr(settings, 'LINKEDIN_API_KEY'),
                'base_url': 'https://api.linkedin.com/v2',
                'priority': 3
            }
            logger.info("LinkedIn data source configured")
        
        # Internal database source (always enabled)
        sources['database'] = {
            'enabled': True,
            'priority': 0
        }
        
        return sources
    
    def _load_cache(self):
        """Load internships from cache file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    self.internships_cache = cached_data.get('internships', [])
                    last_update_str = cached_data.get('last_update')
                    if last_update_str:
                        self.last_update = datetime.fromisoformat(last_update_str)
                    logger.info(f"Loaded {len(self.internships_cache)} internships from cache")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self.internships_cache = []
    
    def _save_cache(self):
        """Save internships to cache file"""
        try:
            cache_data = {
                'internships': self.internships_cache,
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'total_count': len(self.internships_cache)
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, default=str)
            logger.info(f"Saved {len(self.internships_cache)} internships to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    async def update_internships(self, force: bool = False) -> Dict[str, Any]:
        """
        Update internships from all configured sources
        
        Args:
            force: Force update even if recently updated
            
        Returns:
            Update statistics
        """
        async with self.update_lock:
            # Check if update is needed
            if not force and self.last_update:
                time_since_update = datetime.utcnow() - self.last_update
                if time_since_update < timedelta(minutes=self.update_interval_minutes):
                    logger.info(f"Skipping update - last update was {time_since_update.seconds // 60} minutes ago")
                    return {
                        'status': 'skipped',
                        'reason': 'recently_updated',
                        'last_update': self.last_update.isoformat(),
                        'total_internships': len(self.internships_cache)
                    }
            
            self.is_updating = True
            logger.info("Starting internship data update from all sources")
            
            try:
                all_internships = []
                source_stats = {}
                
                # Fetch from all enabled sources in parallel
                tasks = []
                for source_name, source_config in self.data_sources.items():
                    if source_config.get('enabled'):
                        tasks.append(self._fetch_from_source(source_name, source_config))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for source_name, result in zip(self.data_sources.keys(), results):
                    if isinstance(result, Exception):
                        logger.error(f"Error fetching from {source_name}: {result}")
                        source_stats[source_name] = {'error': str(result), 'count': 0}
                    elif result:
                        all_internships.extend(result)
                        source_stats[source_name] = {'count': len(result), 'status': 'success'}
                        logger.info(f"Fetched {len(result)} internships from {source_name}")
                
                # Remove duplicates based on title and company
                unique_internships = self._deduplicate_internships(all_internships)
                
                # Sort by posted date (newest first)
                unique_internships.sort(
                    key=lambda x: x.get('posted_date', datetime.min),
                    reverse=True
                )
                
                # Update cache
                self.internships_cache = unique_internships
                self.last_update = datetime.utcnow()
                self._save_cache()
                
                logger.info(f"Update complete: {len(unique_internships)} unique internships from {len(source_stats)} sources")
                
                return {
                    'status': 'success',
                    'last_update': self.last_update.isoformat(),
                    'total_internships': len(unique_internships),
                    'sources': source_stats,
                    'update_duration_seconds': (datetime.utcnow() - self.last_update).total_seconds()
                }
                
            except Exception as e:
                logger.error(f"Error updating internships: {e}")
                return {
                    'status': 'error',
                    'error': str(e),
                    'total_internships': len(self.internships_cache)
                }
            finally:
                self.is_updating = False
    
    async def _fetch_from_source(self, source_name: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch internships from a specific source"""
        if source_name == 'groupme':
            return await self._fetch_from_groupme(config)
        elif source_name == 'handshake':
            return await self._fetch_from_handshake(config)
        elif source_name == 'linkedin':
            return await self._fetch_from_linkedin(config)
        elif source_name == 'database':
            return await self._fetch_from_database(config)
        else:
            logger.warning(f"Unknown source: {source_name}")
            return []
    
    async def _fetch_from_groupme(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch internships from GroupMe"""
        try:
            url = f"{config['base_url']}/groups/{config['group_id']}/messages"
            params = {
                'token': config['api_key'],
                'limit': 100
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        messages = data.get('response', {}).get('messages', [])
                        
                        # Parse messages for internships
                        internships = []
                        for message in messages:
                            parsed = self._parse_groupme_message(message)
                            if parsed:
                                internships.append(parsed)
                        
                        return internships
                    else:
                        logger.error(f"GroupMe API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching from GroupMe: {e}")
            return []
    
    def _parse_groupme_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse GroupMe message for internship information"""
        text = message.get('text', '').lower()
        
        # Check for internship keywords
        keywords = ['internship', 'intern', 'co-op', 'summer program', 'hiring', 'job opening', 'position']
        if not any(keyword in text for keyword in keywords):
            return None
        
        # Extract information
        lines = message.get('text', '').split('\n')
        
        internship_data = {
            'id': f"groupme_{message.get('id', '')}",
            'title': 'Internship Opportunity',
            'company': 'Unknown Company',
            'location': 'Remote',
            'type': 'Software Development',
            'duration': '10-12 weeks',
            'salary': 'Competitive',
            'deadline': (datetime.utcnow() + timedelta(days=30)).isoformat(),
            'posted_date': datetime.fromtimestamp(message.get('created_at', 0)).isoformat(),
            'description': message.get('text', ''),
            'requirements': [],
            'benefits': [],
            'apply_url': '',
            'source': 'GroupMe',
            'featured': False,
            'raw_message': message.get('text', '')
        }
        
        # Parse structured information from message
        for line in lines:
            line_lower = line.lower()
            if 'company:' in line_lower or 'organization:' in line_lower:
                internship_data['company'] = line.split(':', 1)[1].strip()
            elif 'position:' in line_lower or 'title:' in line_lower or 'role:' in line_lower:
                internship_data['title'] = line.split(':', 1)[1].strip()
            elif 'location:' in line_lower:
                internship_data['location'] = line.split(':', 1)[1].strip()
            elif 'type:' in line_lower or 'category:' in line_lower:
                internship_data['type'] = line.split(':', 1)[1].strip()
            elif 'salary:' in line_lower or 'pay:' in line_lower or 'compensation:' in line_lower:
                internship_data['salary'] = line.split(':', 1)[1].strip()
            elif 'duration:' in line_lower or 'length:' in line_lower:
                internship_data['duration'] = line.split(':', 1)[1].strip()
            elif 'deadline:' in line_lower or 'apply by:' in line_lower:
                try:
                    deadline_str = line.split(':', 1)[1].strip()
                    # Attempt to parse deadline (basic parsing)
                    internship_data['deadline'] = deadline_str
                except:
                    pass
            elif 'apply:' in line_lower or 'link:' in line_lower or 'url:' in line_lower:
                internship_data['apply_url'] = line.split(':', 1)[1].strip()
        
        return internship_data
    
    async def _fetch_from_handshake(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch internships from Handshake API"""
        try:
            # Handshake API implementation
            url = f"{config['base_url']}/jobs"
            headers = {
                'Authorization': f"Bearer {config['api_key']}",
                'Content-Type': 'application/json'
            }
            params = {
                'job_types': 'internship',
                'limit': 50,
                'school_id': 'morgan-state-university'  # Configure as needed
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        jobs = data.get('jobs', [])
                        
                        internships = []
                        for job in jobs:
                            internships.append({
                                'id': f"handshake_{job.get('id')}",
                                'title': job.get('title', 'Internship'),
                                'company': job.get('employer_name', 'Unknown'),
                                'location': job.get('location', {}).get('city', 'Remote'),
                                'type': job.get('job_type', 'Internship'),
                                'duration': job.get('duration', '10-12 weeks'),
                                'salary': job.get('salary', 'Competitive'),
                                'deadline': job.get('expiration_date', ''),
                                'posted_date': job.get('posted_date', datetime.utcnow().isoformat()),
                                'description': job.get('description', ''),
                                'requirements': job.get('requirements', []),
                                'benefits': job.get('benefits', []),
                                'apply_url': job.get('apply_url', ''),
                                'source': 'Handshake',
                                'featured': job.get('is_featured', False)
                            })
                        
                        return internships
                    else:
                        logger.warning(f"Handshake API returned {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching from Handshake: {e}")
            return []
    
    async def _fetch_from_linkedin(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch internships from LinkedIn API"""
        try:
            # LinkedIn API implementation
            url = f"{config['base_url']}/jobSearch"
            headers = {
                'Authorization': f"Bearer {config['api_key']}",
                'X-Restli-Protocol-Version': '2.0.0'
            }
            params = {
                'keywords': 'Computer Science Internship',
                'location': 'United States',
                'count': 50
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        jobs = data.get('elements', [])
                        
                        internships = []
                        for job in jobs:
                            internships.append({
                                'id': f"linkedin_{job.get('id')}",
                                'title': job.get('title', 'Internship'),
                                'company': job.get('companyName', 'Unknown'),
                                'location': job.get('location', 'Remote'),
                                'type': 'Internship',
                                'duration': '10-12 weeks',
                                'salary': 'Competitive',
                                'deadline': '',
                                'posted_date': datetime.utcnow().isoformat(),
                                'description': job.get('description', ''),
                                'requirements': [],
                                'benefits': [],
                                'apply_url': job.get('applyUrl', ''),
                                'source': 'LinkedIn',
                                'featured': False
                            })
                        
                        return internships
                    else:
                        logger.warning(f"LinkedIn API returned {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching from LinkedIn: {e}")
            return []
    
    async def _fetch_from_database(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch internships from internal database"""
        try:
            # Database fetch implementation
            # This would query PostgreSQL for stored internships
            # For now, return empty list as database schema needs to be set up
            return []
        except Exception as e:
            logger.error(f"Error fetching from database: {e}")
            return []
    
    def _deduplicate_internships(self, internships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate internships based on title and company"""
        seen = set()
        unique = []
        
        for internship in internships:
            # Create unique key from title and company
            key = f"{internship.get('title', '').lower()}_{internship.get('company', '').lower()}"
            
            if key not in seen:
                seen.add(key)
                unique.append(internship)
        
        return unique
    
    def get_internships(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get cached internships with optional filtering
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            filters: Optional filters (type, location, company, etc.)
            
        Returns:
            Paginated and filtered internships
        """
        filtered = self.internships_cache.copy()
        
        # Apply filters
        if filters:
            if filters.get('type'):
                filtered = [i for i in filtered if i.get('type') == filters['type']]
            if filters.get('location'):
                filtered = [i for i in filtered if filters['location'].lower() in i.get('location', '').lower()]
            if filters.get('company'):
                filtered = [i for i in filtered if filters['company'].lower() in i.get('company', '').lower()]
            if filters.get('search'):
                search_term = filters['search'].lower()
                filtered = [
                    i for i in filtered
                    if search_term in i.get('title', '').lower()
                    or search_term in i.get('company', '').lower()
                    or search_term in i.get('description', '').lower()
                ]
        
        # Pagination
        total = len(filtered)
        paginated = filtered[offset:offset + limit]
        
        return {
            'internships': paginated,
            'total': total,
            'limit': limit,
            'offset': offset,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'is_updating': self.is_updating
        }
    
    async def start_periodic_updates(self):
        """Start background task for periodic updates"""
        logger.info(f"Starting periodic internship updates (every {self.update_interval_minutes} minutes)")
        
        while True:
            try:
                await asyncio.sleep(self.update_interval_minutes * 60)
                await self.update_internships(force=False)
            except Exception as e:
                logger.error(f"Error in periodic update: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

# Global instance
internship_update_service = InternshipUpdateService()
