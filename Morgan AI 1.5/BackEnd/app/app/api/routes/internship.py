from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import aiohttp
import logging
from app.core.config import settings
from app.core.security import security_service

logger = logging.getLogger(__name__)
router = APIRouter()

class InternshipPost(BaseModel):
    title: str
    company: str
    location: str
    description: str
    requirements: Optional[List[str]] = []
    application_link: Optional[str] = None
    deadline: Optional[datetime] = None
    posted_date: datetime
    source: str = "GroupMe"
    tags: List[str] = []

class EventPost(BaseModel):
    title: str
    description: str
    date: datetime
    location: Optional[str] = None
    registration_link: Optional[str] = None
    organizer: str
    tags: List[str] = []

class GroupMeService:
    """Service for GroupMe integration"""
    
    def __init__(self):
        self.access_token = settings.GROUPME_ACCESS_TOKEN
        self.group_id = settings.GROUPME_GROUP_ID
        self.base_url = "https://api.groupme.com/v3"
    
    async def fetch_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch messages from GroupMe group"""
        if not self.access_token or not self.group_id:
            logger.warning("GroupMe credentials not configured")
            return []
        
        url = f"{self.base_url}/groups/{self.group_id}/messages"
        params = {
            "token": self.access_token,
            "limit": limit
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", {}).get("messages", [])
                    else:
                        logger.error(f"GroupMe API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching GroupMe messages: {str(e)}")
            return []
    
    def parse_internship_message(self, message: Dict[str, Any]) -> Optional[InternshipPost]:
        """Parse a GroupMe message for internship information"""
        text = message.get("text", "").lower()
        
        # Check if message contains internship keywords
        internship_keywords = ["internship", "intern", "co-op", "summer program", "hiring"]
        if not any(keyword in text for keyword in internship_keywords):
            return None
        
        # Basic parsing (in production, use more sophisticated NLP)
        lines = message.get("text", "").split("\n")
        
        internship = {
            "title": "Internship Opportunity",
            "company": "Unknown",
            "location": "Remote/On-site",
            "description": message.get("text", ""),
            "posted_date": datetime.fromtimestamp(message.get("created_at", 0)),
            "source": "GroupMe"
        }
        
        # Extract company name if mentioned
        for line in lines:
            if "company:" in line.lower():
                internship["company"] = line.split(":", 1)[1].strip()
            elif "position:" in line.lower() or "title:" in line.lower():
                internship["title"] = line.split(":", 1)[1].strip()
            elif "location:" in line.lower():
                internship["location"] = line.split(":", 1)[1].strip()
        
        return InternshipPost(**internship)
    
    def parse_event_message(self, message: Dict[str, Any]) -> Optional[EventPost]:
        """Parse a GroupMe message for event information"""
        text = message.get("text", "").lower()
        
        # Check if message contains event keywords
        event_keywords = ["event", "workshop", "meetup", "info session", "career fair", "presentation"]
        if not any(keyword in text for keyword in event_keywords):
            return None
        
        # Basic parsing
        event = {
            "title": "Upcoming Event",
            "description": message.get("text", ""),
            "date": datetime.fromtimestamp(message.get("created_at", 0)),
            "organizer": "Morgan CS Department",
            "tags": ["event"]
        }
        
        return EventPost(**event)

groupme_service = GroupMeService()

@router.get("/list")
async def get_internships(
    current_user: Dict = Depends(security_service.get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """Get list of internship opportunities"""
    try:
        # Fetch from GroupMe
        messages = await groupme_service.fetch_messages(limit=100)
        
        # Parse internships
        internships = []
        for message in messages:
            internship = groupme_service.parse_internship_message(message)
            if internship:
                internships.append(internship.dict())
        
        # Apply pagination
        paginated = internships[offset:offset + limit]
        
        return {
            "internships": paginated,
            "total": len(internships),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching internships: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def get_events(
    current_user: Dict = Depends(security_service.get_current_user),
    upcoming_only: bool = True
):
    """Get list of campus events"""
    try:
        # Fetch from GroupMe
        messages = await groupme_service.fetch_messages(limit=100)
        
        # Parse events
        events = []
        for message in messages:
            event = groupme_service.parse_event_message(message)
            if event:
                events.append(event.dict())
        
        # Filter upcoming events if requested
        if upcoming_only:
            now = datetime.utcnow()
            events = [e for e in events if datetime.fromisoformat(e["date"]) > now]
        
        return {
            "events": events,
            "total": len(events)
        }
        
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh")
async def refresh_internships(
    background_tasks: BackgroundTasks,
    current_admin: Dict = Depends(security_service.get_current_admin)
):
    """Manually refresh internship data from GroupMe"""
    try:
        # Trigger background task to refresh data
        background_tasks.add_task(fetch_and_store_internships)
        
        return {"message": "Internship refresh initiated"}
        
    except Exception as e:
        logger.error(f"Error refreshing internships: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_and_store_internships():
    """Background task to fetch and store internship data"""
    try:
        messages = await groupme_service.fetch_messages(limit=200)
        
        internships = []
        events = []
        
        for message in messages:
            # Try parsing as internship
            internship = groupme_service.parse_internship_message(message)
            if internship:
                internships.append(internship)
            
            # Try parsing as event
            event = groupme_service.parse_event_message(message)
            if event:
                events.append(event)
        
        # In production, save to database
        logger.info(f"Found {len(internships)} internships and {len(events)} events")
        
    except Exception as e:
        logger.error(f"Error in background task: {str(e)}")

@router.get("/statistics")
async def get_statistics(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get internship and event statistics"""
    try:
        messages = await groupme_service.fetch_messages(limit=200)
        
        internship_count = 0
        event_count = 0
        companies = set()
        
        for message in messages:
            internship = groupme_service.parse_internship_message(message)
            if internship:
                internship_count += 1
                companies.add(internship.company)
            
            event = groupme_service.parse_event_message(message)
            if event:
                event_count += 1
        
        return {
            "total_internships": internship_count,
            "total_events": event_count,
            "unique_companies": len(companies),
            "top_companies": list(companies)[:10],
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscribe")
async def subscribe_to_notifications(
    email: str,
    preferences: Dict[str, bool] = {"internships": True, "events": True},
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Subscribe to internship and event notifications"""
    try:
        # In production, save subscription preferences to database
        return {
            "message": "Successfully subscribed to notifications",
            "email": email,
            "preferences": preferences
        }
        
    except Exception as e:
        logger.error(f"Subscription error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/unsubscribe")
async def unsubscribe_from_notifications(
    email: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Unsubscribe from notifications"""
    try:
        # In production, remove from database
        return {"message": f"Successfully unsubscribed {email}"}
        
    except Exception as e:
        logger.error(f"Unsubscribe error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))