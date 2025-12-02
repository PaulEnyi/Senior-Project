"""
Course Recommendation API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from app.core.security import security_service
from app.services.course_recommendation_engine import course_recommendation_engine
from app.api.routes.degree_works import degree_works_storage

logger = logging.getLogger(__name__)
router = APIRouter()

class CoursePlanRequest(BaseModel):
    semesters_ahead: int = Field(4, description="Number of semesters to plan ahead")

@router.get("/analyze-progress")
async def analyze_academic_progress(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Analyze student's academic progress and provide recommendations
    Requires uploaded Degree Works data
    """
    try:
        user_id = current_user.get('user_id')
        storage_key = f"{user_id}_degree_works"
        
        # Get Degree Works data
        degree_works_data = degree_works_storage.get(storage_key)
        
        if not degree_works_data:
            raise HTTPException(
                status_code=404,
                detail="No Degree Works data found. Please upload your Degree Works PDF first."
            )
        
        logger.info(f"Analyzing academic progress for user: {user_id}")
        
        # Analyze progress
        analysis = course_recommendation_engine.analyze_student_progress(degree_works_data)
        
        if analysis.get('success', False):
            return analysis
        else:
            raise HTTPException(
                status_code=500,
                detail=analysis.get('error', 'Failed to analyze progress')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing progress: {str(e)}"
        )

@router.post("/generate-plan")
async def generate_course_plan(
    request: CoursePlanRequest,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Generate comprehensive course plan for upcoming semesters
    Requires uploaded Degree Works data
    """
    try:
        user_id = current_user.get('user_id')
        storage_key = f"{user_id}_degree_works"
        
        # Get Degree Works data
        degree_works_data = degree_works_storage.get(storage_key)
        
        if not degree_works_data:
            raise HTTPException(
                status_code=404,
                detail="No Degree Works data found. Please upload your Degree Works PDF first."
            )
        
        logger.info(f"Generating course plan for user: {user_id} ({request.semesters_ahead} semesters)")
        
        # Generate plan
        plan = course_recommendation_engine.generate_course_plan(
            degree_works_data=degree_works_data,
            semesters_ahead=request.semesters_ahead
        )
        
        if plan.get('success', False):
            return plan
        else:
            raise HTTPException(
                status_code=500,
                detail=plan.get('error', 'Failed to generate course plan')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating course plan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating course plan: {str(e)}"
        )

@router.get("/next-courses")
async def get_next_recommended_courses(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Get immediate next course recommendations
    """
    try:
        user_id = current_user.get('user_id')
        storage_key = f"{user_id}_degree_works"
        
        # Get Degree Works data
        degree_works_data = degree_works_storage.get(storage_key)
        
        if not degree_works_data:
            raise HTTPException(
                status_code=404,
                detail="No Degree Works data found. Please upload your Degree Works PDF first."
            )
        
        logger.info(f"Getting next course recommendations for user: {user_id}")
        
        # Analyze progress to get recommendations
        analysis = course_recommendation_engine.analyze_student_progress(degree_works_data)
        
        if analysis.get('success', False):
            return {
                'success': True,
                'recommendations': analysis.get('next_recommended_courses', []),
                'classification': analysis.get('classification', 'Unknown'),
                'completion_percentage': analysis.get('completion_percentage', 0)
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=analysis.get('error', 'Failed to get recommendations')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )

@router.get("/graduation-estimate")
async def get_graduation_estimate(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """
    Get estimated graduation date based on current progress
    """
    try:
        user_id = current_user.get('user_id')
        storage_key = f"{user_id}_degree_works"
        
        # Get Degree Works data
        degree_works_data = degree_works_storage.get(storage_key)
        
        if not degree_works_data:
            raise HTTPException(
                status_code=404,
                detail="No Degree Works data found. Please upload your Degree Works PDF first."
            )
        
        logger.info(f"Getting graduation estimate for user: {user_id}")
        
        # Analyze progress
        analysis = course_recommendation_engine.analyze_student_progress(degree_works_data)
        
        if analysis.get('success', False):
            return {
                'success': True,
                'estimated_graduation': analysis.get('estimated_graduation', 'Unknown'),
                'credits_needed': analysis.get('credits_needed', 0),
                'completion_percentage': analysis.get('completion_percentage', 0),
                'classification': analysis.get('classification', 'Unknown')
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=analysis.get('error', 'Failed to estimate graduation')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error estimating graduation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error estimating graduation: {str(e)}"
        )
