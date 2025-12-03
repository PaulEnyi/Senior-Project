"""
Degree Works API endpoints
Handle PDF upload, parsing, storage, and retrieval with file-based persistence
All data saved to data/users/{user_id}/degree_works/ for permanent storage
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Request
from typing import Dict, Any
from pydantic import BaseModel
import logging
from datetime import datetime
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import security_service
from app.core.file_storage import get_file_storage, get_local_timestamp
from app.core.database import get_db
from app.core import db_operations
from app.models.database import DegreeWorksFile
from app.services.degree_works_parser import DegreeWorksParser

logger = logging.getLogger(__name__)
router = APIRouter()

# Legacy in-memory storage - kept for backward compatibility
# All new operations use file_storage for persistent data
degree_works_storage = {}

class DegreeWorksAnalysis(BaseModel):
    user_id: str
    parsed_data: Dict[str, Any]
    uploaded_at: str
    file_name: str

@router.post("/upload")
async def upload_degree_works(
    file: UploadFile = File(...),
    current_user: Dict = Depends(security_service.get_current_user),
    file_storage = Depends(get_file_storage),
    db: AsyncSession = Depends(get_db),
    app_request: Request = None
):
    """
    Upload and analyze Degree Works PDF - saves to file storage permanently
    
    Returns complete analysis including:
    - Student information
    - Academic summary (GPA, credits, classification)
    - Course breakdowns (completed, in-progress, remaining)
    - Requirement analysis
    """
    try:
        user_id = current_user.get('user_id')
        logger.info(f"Uploading Degree Works for user {user_id}: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are accepted. Please upload your Degree Works PDF."
            )
        
        # Read file bytes
        file_bytes = await file.read()
        
        if len(file_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        logger.info(f"Read {len(file_bytes)} bytes from uploaded file")
        
        # Parse the PDF
        parser = DegreeWorksParser()
        parsed_data = await parser.parse_pdf(file_bytes)
        
        if not parsed_data.get('success'):
            raise HTTPException(
                status_code=422,
                detail=f"Failed to parse Degree Works PDF: {parsed_data.get('error', 'Unknown error')}"
            )
        
        # Save PDF file to file storage
        saved_meta = file_storage.save_degree_works_file(
            user_id=user_id,
            file_name=file.filename,
            file_data=file_bytes,
            parsed_data=parsed_data
        )
        if not saved_meta:
            raise HTTPException(status_code=500, detail="Failed to save Degree Works file")
        
        # Bridge auto-create: ensure DB user exists
        user_record = await db_operations.get_user_by_id(db=db, user_id=user_id)
        if not user_record:
            email_claim = current_user.get("email")
            username_claim = current_user.get("sub") or current_user.get("username")
            if email_claim and username_claim:
                try:
                    password_hash = security_service.get_password_hash("bridge-placeholder-password")
                    user_record = await db_operations.create_user_with_id(
                        db=db,
                        user_id=user_id,
                        email=email_claim,
                        username=username_claim,
                        password_hash=password_hash,
                        full_name=current_user.get("full_name") or username_claim
                    )
                    logger.info(f"Degree Works bridge user created: {user_id}")
                except Exception as bridge_err:
                    logger.error(f"Degree Works bridge user creation failed: {bridge_err}")
                    raise HTTPException(status_code=401, detail="User record missing and bridge creation failed. Please re-auth.")
            else:
                logger.warning(f"Degree Works bridge skipped - missing claims for user: {user_id}")
                raise HTTPException(status_code=401, detail="User record missing. Please log in again.")
        
        # Also save to database for chat context retrieval
        academic_summary = parsed_data.get('academic_summary', {})
        student_info = parsed_data.get('student_info', {})
        
        db_file = DegreeWorksFile(
            user_id=user_id,
            filename=file.filename,
            file_path=saved_meta.get('file_path'),
            file_size=len(file_bytes),
            parsed_data=parsed_data,
            student_name=student_info.get('name'),
            student_id=student_info.get('student_id'),
            major=student_info.get('major'),
            classification=academic_summary.get('classification'),
            gpa=str(academic_summary.get('gpa', '')),
            credits_earned=int(academic_summary.get('completed_credits', 0)),
            credits_needed=int(academic_summary.get('total_credits_required', 120)),
            is_processed=True,
            processed_at=datetime.now()
        )
        
        db.add(db_file)
        await db.commit()
        await db.refresh(db_file)
        
        logger.info(f"✅ Saved Degree Works to database: file_id={db_file.id}")
        
        # Update user profile with degree works data
        profile_data = file_storage.load_user_profile(user_id) or {}
        profile_data.update({
            'has_degree_works': True,
            'classification': parsed_data.get('academic_summary', {}).get('classification'),
            'gpa': parsed_data.get('academic_summary', {}).get('gpa'),
            'major': parsed_data.get('student_info', {}).get('major'),
            'degree_works_updated_at': get_local_timestamp()
        })
        file_storage.save_user_profile(user_id, profile_data)
        
        logger.info(f"✅ Successfully parsed and stored Degree Works for user {user_id}")
        
        # Return analysis results
        return {
            'success': True,
            'message': 'Degree Works uploaded and analyzed successfully',
            'analysis': parsed_data,
            'uploaded_at': saved_meta.get('uploaded_at'),
            'version_id': saved_meta.get('id'),
            'previous_version_id': saved_meta.get('previous_version_id'),
            'diff_from_previous': saved_meta.get('diff_from_previous')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error uploading Degree Works: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while processing Degree Works: {str(e)}"
        )

@router.get("/analysis")
async def get_degree_works_analysis(
    current_user: Dict = Depends(security_service.get_current_user),
    file_storage = Depends(get_file_storage)
):
    """
    Get stored Degree Works analysis for current user from file storage
    
    Returns:
        Parsed Degree Works data if available, or 404 if not found
    """
    try:
        user_id = current_user.get('user_id')
        
        # Get Degree Works files from file storage
        degree_works_files = file_storage.get_user_degree_works_files(user_id)
        
        if not degree_works_files:
            raise HTTPException(
                status_code=404,
                detail="No Degree Works data found. Please upload your Degree Works PDF."
            )
        
        # Get the most recent file
        latest_file = degree_works_files[0]
        
        return {
            'success': True,
            'analysis': latest_file.get('parsed_data', {}),
            'uploaded_at': latest_file.get('uploaded_at'),
            'file_name': latest_file.get('file_name'),
            'version_id': latest_file.get('id'),
            'previous_version_id': latest_file.get('previous_version_id'),
            'diff_from_previous': latest_file.get('diff_from_previous')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving Degree Works: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/analysis")
async def delete_degree_works(
    current_user: Dict = Depends(security_service.get_current_user),
    file_storage = Depends(get_file_storage),
    db: AsyncSession = Depends(get_db)
):
    """Delete stored Degree Works data for current user from file storage and database"""
    try:
        user_id = current_user.get('user_id')
        
        # Delete from database (soft delete)
        from sqlalchemy import update
        await db.execute(
            update(DegreeWorksFile)
            .where(DegreeWorksFile.user_id == user_id)
            .values(deleted_at=datetime.utcnow())
        )
        await db.commit()
        
        # Get all Degree Works files
        degree_works_files = file_storage.get_user_degree_works_files(user_id)
        
        if not degree_works_files:
            # Even if no files in storage, deletion from DB was successful
            return {
                'success': True,
                'message': 'Degree Works data deleted successfully'
            }
        
        # Delete all Degree Works files for this user from file storage
        import shutil
        from pathlib import Path
        
        degree_works_folder = file_storage.BASE_DATA_DIR / "users" / user_id / "degree_works"
        if degree_works_folder.exists():
            shutil.rmtree(degree_works_folder)
            degree_works_folder.mkdir(exist_ok=True)
        
        # Update user profile
        profile_data = file_storage.load_user_profile(user_id) or {}
        profile_data.update({
            'has_degree_works': False,
            'classification': None,
            'degree_works_deleted_at': datetime.utcnow().isoformat()
        })
        file_storage.save_user_profile(user_id, profile_data)
        
        return {
            'success': True,
            'message': 'Degree Works data deleted successfully'
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting Degree Works: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context")
async def get_degree_works_context(
    current_user: Dict = Depends(security_service.get_current_user),
    file_storage = Depends(get_file_storage)
):
    """
    Get Degree Works data formatted for chatbot context from file storage
    
    Returns formatted text that can be injected into chat context
    """
    try:
        user_id = current_user.get('user_id')
        
        # Get Degree Works files from file storage
        degree_works_files = file_storage.get_user_degree_works_files(user_id)
        
        if not degree_works_files:
            return {
                'success': False,
                'has_data': False,
                'context': ''
            }
        
        # Get the most recent file
        latest_file = degree_works_files[0]
        parser = DegreeWorksParser()
        
        context = parser.format_for_chatbot(latest_file.get('parsed_data', {}))
        
        return {
            'success': True,
            'has_data': True,
            'context': context,
            'uploaded_at': latest_file.get('uploaded_at')
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting Degree Works context: {str(e)}")
        return {
            'success': False,
            'has_data': False,
            'context': '',
            'error': str(e)
        }

@router.get("/summary")
async def get_academic_summary(
    current_user: Dict = Depends(security_service.get_current_user),
    file_storage = Depends(get_file_storage)
):
    """
    Get just the academic summary (GPA, credits, classification) from file storage
    Lightweight endpoint for quick status checks
    """
    try:
        user_id = current_user.get('user_id')
        
        # Get Degree Works files from file storage
        degree_works_files = file_storage.get_user_degree_works_files(user_id)
        
        if not degree_works_files:
            raise HTTPException(
                status_code=404,
                detail="No Degree Works data found"
            )
        
        # Get the most recent file
        latest_file = degree_works_files[0]
        parsed_data = latest_file.get('parsed_data', {})
        
        return {
            'success': True,
            'student_info': parsed_data.get('student_info', {}),
            'academic_summary': parsed_data.get('academic_summary', {}),
            'uploaded_at': latest_file.get('uploaded_at'),
            'version_id': latest_file.get('id')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting academic summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/courses/{status}")
async def get_courses_by_status(
    status: str,
    current_user: Dict = Depends(security_service.get_current_user),
    file_storage = Depends(get_file_storage)
):
    """
    Get courses filtered by status: completed, in_progress, or remaining from file storage
    
    Args:
        status: One of 'completed', 'in_progress', or 'remaining'
    """
    try:
        if status not in ['completed', 'in_progress', 'remaining']:
            raise HTTPException(
                status_code=400,
                detail="Status must be 'completed', 'in_progress', or 'remaining'"
            )
        
        user_id = current_user.get('user_id')
        
        # Get Degree Works files from file storage
        degree_works_files = file_storage.get_user_degree_works_files(user_id)
        
        if not degree_works_files:
            raise HTTPException(
                status_code=404,
                detail="No Degree Works data found"
            )
        
        # Get the most recent file
        latest_file = degree_works_files[0]
        courses = latest_file.get('parsed_data', {}).get('courses', {})
        
        # Convert underscores for API consistency
        status_key = status
        
        return {
            'success': True,
            'status': status,
            'courses': courses.get(status_key, []),
            'count': len(courses.get(status_key, []))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting courses by status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/requirements")
async def get_requirements_analysis(
    current_user: Dict = Depends(security_service.get_current_user),
    file_storage = Depends(get_file_storage)
):
    """
    Get detailed requirements analysis grouped by category from file storage
    (Major Core, Gen Ed, Electives, etc.)
    """
    try:
        user_id = current_user.get('user_id')
        
        # Get Degree Works files from file storage
        degree_works_files = file_storage.get_user_degree_works_files(user_id)
        
        if not degree_works_files:
            raise HTTPException(
                status_code=404,
                detail="No Degree Works data found"
            )
        
        # Get the most recent file
        latest_file = degree_works_files[0]
        requirements = latest_file.get('parsed_data', {}).get('requirements', {})
        
        return {
            'success': True,
            'requirements': requirements
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting requirements analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/versions")
async def list_degree_works_versions(
    current_user: Dict = Depends(security_service.get_current_user),
    file_storage = Depends(get_file_storage)
):
    user_id = current_user.get('user_id')
    versions = file_storage.get_user_degree_works_files(user_id)
    return {
        'success': True,
        'count': len(versions),
        'versions': [
            {
                'id': v.get('id'),
                'file_name': v.get('file_name'),
                'uploaded_at': v.get('uploaded_at'),
                'file_size': v.get('file_size'),
                'classification': v.get('parsed_data', {}).get('academic_summary', {}).get('classification'),
                'completed_credits': v.get('parsed_data', {}).get('academic_summary', {}).get('completed_credits'),
                'gpa': v.get('parsed_data', {}).get('academic_summary', {}).get('gpa'),
                'previous_version_id': v.get('previous_version_id'),
                'diff_from_previous': v.get('diff_from_previous')
            }
            for v in versions
        ]
    }

@router.get("/versions/{version_id}")
async def get_degree_works_version(
    version_id: str,
    current_user: Dict = Depends(security_service.get_current_user),
    file_storage = Depends(get_file_storage)
):
    user_id = current_user.get('user_id')
    versions = file_storage.get_user_degree_works_files(user_id)
    for v in versions:
        if v.get('id') == version_id:
            return {
                'success': True,
                'version_id': v.get('id'),
                'uploaded_at': v.get('uploaded_at'),
                'file_name': v.get('file_name'),
                'analysis': v.get('parsed_data'),
                'previous_version_id': v.get('previous_version_id'),
                'diff_from_previous': v.get('diff_from_previous')
            }
    raise HTTPException(status_code=404, detail="Version not found")

@router.get("/versions/{version_id}/diff/{other_version_id}")
async def diff_degree_works_versions(
    version_id: str,
    other_version_id: str,
    current_user: Dict = Depends(security_service.get_current_user),
    file_storage = Depends(get_file_storage)
):
    user_id = current_user.get('user_id')
    versions = file_storage.get_user_degree_works_files(user_id)
    by_id = {v.get('id'): v for v in versions}
    if version_id not in by_id or other_version_id not in by_id:
        raise HTTPException(status_code=404, detail="One or both version IDs not found")
    diff = file_storage._diff_degree_works(by_id[other_version_id].get('parsed_data', {}), by_id[version_id].get('parsed_data', {}))
    return {
        'success': True,
        'base_version_id': other_version_id,
        'target_version_id': version_id,
        'diff': diff
    }

@router.delete("/versions/{version_id}")
async def delete_degree_works_version(
    version_id: str,
    current_user: Dict = Depends(security_service.get_current_user),
    file_storage = Depends(get_file_storage)
):
    user_id = current_user.get('user_id')
    success = file_storage.delete_degree_works_version(user_id, version_id)
    if not success:
        raise HTTPException(status_code=404, detail="Version not found or could not be deleted")
    return {'success': True, 'message': 'Version deleted', 'version_id': version_id}

@router.get("/timeline")
async def get_course_timeline(
    current_user: Dict = Depends(security_service.get_current_user),
    file_storage = Depends(get_file_storage)
):
    user_id = current_user.get('user_id')
    versions = file_storage.get_user_degree_works_files(user_id)
    if not versions:
        raise HTTPException(status_code=404, detail="No Degree Works data found")
    latest = versions[0]
    timeline = latest.get('parsed_data', {}).get('course_timeline', {})
    return {'success': True, 'timeline_terms': len(timeline), 'timeline': timeline}

