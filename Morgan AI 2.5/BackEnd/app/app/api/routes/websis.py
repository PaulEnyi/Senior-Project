"""
WebSIS Integration API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from app.core.security import security_service
from app.services.websis_service import websis_service

logger = logging.getLogger(__name__)
router = APIRouter()

class WebSISLoginRequest(BaseModel):
    username: str = Field(..., description="WebSIS username/student ID")
    password: str = Field(..., description="WebSIS password")

class CourseSearchRequest(BaseModel):
    term_code: str = Field(..., description="Term code (e.g., 202501)")
    subject: Optional[str] = Field("COSC", description="Subject code")
    course_number: Optional[str] = Field(None, description="Course number")

@router.post("/login")
async def websis_login(
    request: WebSISLoginRequest,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Authenticate with WebSIS using student credentials
    """
    try:
        logger.info(f"WebSIS login attempt for user: {request.username}")
        
        result = await websis_service.authenticate(
            username=request.username,
            password=request.password
        )
        
        if result['success']:
            logger.info(f"WebSIS authentication successful for: {request.username}")
            return {
                'success': True,
                'message': 'Successfully connected to WebSIS',
                'session_id': result.get('session_id')
            }
        else:
            logger.warning(f"WebSIS authentication failed for: {request.username}")
            raise HTTPException(status_code=401, detail=result.get('message', 'Authentication failed'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WebSIS login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"WebSIS login error: {str(e)}")

@router.get("/schedule/{session_id}")
async def get_schedule(
    session_id: str,
    term_code: Optional[str] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Fetch student's class schedule from WebSIS
    """
    try:
        logger.info(f"Fetching schedule for session: {session_id[:8]}...")
        
        schedule = await websis_service.fetch_student_schedule(
            session_id=session_id,
            term_code=term_code
        )
        
        if schedule.get('success', False):
            return schedule
        else:
            raise HTTPException(status_code=404, detail=schedule.get('message', 'Failed to fetch schedule'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching schedule: {str(e)}")

@router.get("/grades/{session_id}")
async def get_grades(
    session_id: str,
    term_code: Optional[str] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Fetch student's grades from WebSIS
    """
    try:
        logger.info(f"Fetching grades for session: {session_id[:8]}...")
        
        grades = await websis_service.fetch_grades(
            session_id=session_id,
            term_code=term_code
        )
        
        if grades.get('success', False):
            return grades
        else:
            raise HTTPException(status_code=404, detail=grades.get('message', 'Failed to fetch grades'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching grades: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching grades: {str(e)}")

@router.get("/registration-status/{session_id}")
async def get_registration_status(
    session_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Check registration status and holds
    """
    try:
        logger.info(f"Checking registration status for session: {session_id[:8]}...")
        
        status = await websis_service.fetch_registration_status(session_id=session_id)
        
        if status.get('success', False):
            return status
        else:
            raise HTTPException(status_code=404, detail=status.get('message', 'Failed to check registration status'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking registration status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking registration status: {str(e)}")

@router.post("/search-courses")
async def search_courses(
    request: CourseSearchRequest,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Search for available courses
    """
    try:
        logger.info(f"Searching courses: {request.subject} {request.course_number or 'all'}")
        
        courses = await websis_service.search_courses(
            term_code=request.term_code,
            subject=request.subject,
            course_number=request.course_number
        )
        
        if courses.get('success', False):
            return courses
        else:
            raise HTTPException(status_code=404, detail=courses.get('message', 'No courses found'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching courses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching courses: {str(e)}")
