"""
Morgan CS Department Web Scraper API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from typing import Dict, Any
import logging
from app.core.security import security_service
from app.services.morgan_cs_scraper import morgan_cs_scraper

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/scrape")
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(security_service.get_current_user),
    request: Request = None
):
    """
    Trigger a web scrape of Morgan CS website (Admin only)
    Runs in background to avoid timeout
    """
    try:
        # Check if user is admin
        if not current_user.get('is_admin', False):
            raise HTTPException(
                status_code=403,
                detail="Admin privileges required to trigger web scraping"
            )
        
        logger.info(f"Web scrape triggered by admin: {current_user.get('email')}")
        
        # Run scraping in background
        background_tasks.add_task(morgan_cs_scraper.scrape_all)
        
        return {
            'success': True,
            'message': 'Web scraping initiated in background',
            'status': 'running'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering web scrape: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger web scrape: {str(e)}"
        )

@router.post("/scrape-and-update")
async def scrape_and_update_knowledge_base(
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(security_service.get_current_user),
    request: Request = None
):
    """
    Scrape Morgan CS website and update knowledge base (Admin only)
    """
    try:
        # Check if user is admin
        if not current_user.get('is_admin', False):
            raise HTTPException(
                status_code=403,
                detail="Admin privileges required"
            )
        
        logger.info(f"Scrape and update triggered by admin: {current_user.get('email')}")
        
        # Run scraping and knowledge base update in background
        background_tasks.add_task(morgan_cs_scraper.update_knowledge_base)
        
        return {
            'success': True,
            'message': 'Web scraping and knowledge base update initiated',
            'status': 'running'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in scrape and update: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape and update: {str(e)}"
        )

@router.get("/cached-data")
async def get_cached_data(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Get cached scraped data from Morgan CS website
    """
    try:
        cached_data = morgan_cs_scraper.get_cached_data()
        
        return {
            'success': True,
            'data': cached_data['data'],
            'last_scrape': cached_data['last_scrape'],
            'is_fresh': cached_data['is_fresh']
        }
        
    except Exception as e:
        logger.error(f"Error retrieving cached data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cached data: {str(e)}"
        )

@router.get("/faculty")
async def get_faculty_info(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Get cached faculty information
    """
    try:
        cached_data = morgan_cs_scraper.get_cached_data()
        
        return {
            'success': True,
            'faculty': cached_data['data'].get('faculty', []),
            'count': len(cached_data['data'].get('faculty', [])),
            'last_updated': cached_data['last_scrape']
        }
        
    except Exception as e:
        logger.error(f"Error retrieving faculty info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve faculty info: {str(e)}"
        )

@router.get("/news")
async def get_department_news(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Get cached department news
    """
    try:
        cached_data = morgan_cs_scraper.get_cached_data()
        
        return {
            'success': True,
            'news': cached_data['data'].get('news', []),
            'count': len(cached_data['data'].get('news', [])),
            'last_updated': cached_data['last_scrape']
        }
        
    except Exception as e:
        logger.error(f"Error retrieving news: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve news: {str(e)}"
        )

@router.get("/events")
async def get_department_events(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Get cached department events
    """
    try:
        cached_data = morgan_cs_scraper.get_cached_data()
        
        return {
            'success': True,
            'events': cached_data['data'].get('events', []),
            'count': len(cached_data['data'].get('events', [])),
            'last_updated': cached_data['last_scrape']
        }
        
    except Exception as e:
        logger.error(f"Error retrieving events: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve events: {str(e)}"
        )

@router.get("/courses")
async def get_course_catalog(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Get cached course catalog from website
    """
    try:
        cached_data = morgan_cs_scraper.get_cached_data()
        
        return {
            'success': True,
            'courses': cached_data['data'].get('courses', []),
            'count': len(cached_data['data'].get('courses', [])),
            'last_updated': cached_data['last_scrape']
        }
        
    except Exception as e:
        logger.error(f"Error retrieving course catalog: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve course catalog: {str(e)}"
        )
