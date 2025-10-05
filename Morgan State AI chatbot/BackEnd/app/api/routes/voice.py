from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional
import logging
from io import BytesIO

from ...services.openai_service import OpenAIService
from ...core.exceptions import create_success_response, create_error_response, VoiceProcessingException

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech", max_length=4000)
    voice: Optional[str] = Field("alloy", description="Voice to use for TTS")

class STTResponse(BaseModel):
    text: str = Field(..., description="Transcribed text from audio")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")

# Global service instance
openai_service = OpenAIService()

@router.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using OpenAI TTS
    
    Supports multiple voices:
    - alloy (default)
    - echo
    - fable
    - onyx
    - nova
    - shimmer
    """
    try:
        if not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    message="Text cannot be empty",
                    error_code="EMPTY_TEXT"
                )
            )
        
        # Validate voice option
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if request.voice not in valid_voices:
            request.voice = "alloy"  # Default to alloy
        
        logger.info(f"Generating TTS for text length: {len(request.text)} with voice: {request.voice}")
        
        # Generate speech
        audio_content = await openai_service.text_to_speech(
            text=request.text,
            voice=request.voice
        )
        
        # Return audio as response
        return Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Content-Length": str(len(audio_content)),
                "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
            }
        )
        
    except VoiceProcessingException as e:
        logger.error(f"TTS processing error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=create_error_response(
                message="Failed to generate speech",
                error_code="TTS_PROCESSING_ERROR",
                details=str(e)
            )
        )
    except Exception as e:
        logger.error(f"Unexpected TTS error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="An unexpected error occurred during text-to-speech conversion",
                error_code="TTS_UNEXPECTED_ERROR"
            )
        )

@router.post("/speech-to-text", response_model=STTResponse)
async def speech_to_text(
    audio_file: UploadFile = File(..., description="Audio file to transcribe"),
    language: Optional[str] = Form(None, description="Language code (optional)")
):
    """
    Convert speech to text using OpenAI Whisper
    
    Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
    Max file size: 25MB
    """
    try:
        # Validate file
        if not audio_file.filename:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    message="No audio file provided",
                    error_code="NO_AUDIO_FILE"
                )
            )
        
        # Check file size (25MB limit for Whisper API)
        max_size = 25 * 1024 * 1024  # 25MB
        audio_content = await audio_file.read()
        
        if len(audio_content) > max_size:
            raise HTTPException(
                status_code=413,
                detail=create_error_response(
                    message="Audio file too large. Maximum size is 25MB.",
                    error_code="FILE_TOO_LARGE"
                )
            )
        
        if len(audio_content) == 0:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    message="Audio file is empty",
                    error_code="EMPTY_AUDIO_FILE"
                )
            )
        
        # Validate file format
        supported_formats = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
        file_extension = None
        
        for ext in supported_formats:
            if audio_file.filename.lower().endswith(ext):
                file_extension = ext[1:]  # Remove the dot
                break
        
        if not file_extension:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    message=f"Unsupported audio format. Supported formats: {', '.join(supported_formats)}",
                    error_code="UNSUPPORTED_FORMAT"
                )
            )
        
        logger.info(f"Processing STT for file: {audio_file.filename} ({len(audio_content)} bytes)")
        
        # Transcribe audio
        transcribed_text = await openai_service.speech_to_text(
            audio_data=audio_content,
            format=file_extension
        )
        
        if not transcribed_text.strip():
            logger.warning("STT returned empty transcription")
            return STTResponse(
                text="[No speech detected in audio]"
            )
        
        logger.info(f"STT successful: {len(transcribed_text)} characters transcribed")
        
        return STTResponse(
            text=transcribed_text.strip()
        )
        
    except VoiceProcessingException as e:
        logger.error(f"STT processing error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=create_error_response(
                message="Failed to transcribe audio",
                error_code="STT_PROCESSING_ERROR",
                details=str(e)
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected STT error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="An unexpected error occurred during speech-to-text conversion",
                error_code="STT_UNEXPECTED_ERROR"
            )
        )

@router.get("/voices")
async def get_available_voices():
    """
    Get list of available TTS voices
    
    Returns information about each voice including recommended use cases
    """
    voices = [
        {
            "id": "alloy",
            "name": "Alloy",
            "description": "Neutral and versatile voice, good for general use",
            "gender": "neutral",
            "recommended_for": ["general", "educational", "professional"]
        },
        {
            "id": "echo",
            "name": "Echo", 
            "description": "Male voice with warm tone",
            "gender": "male",
            "recommended_for": ["storytelling", "casual"]
        },
        {
            "id": "fable",
            "name": "Fable",
            "description": "British accent, great for storytelling",
            "gender": "male", 
            "recommended_for": ["storytelling", "educational"]
        },
        {
            "id": "onyx",
            "name": "Onyx",
            "description": "Deep male voice, authoritative tone",
            "gender": "male",
            "recommended_for": ["professional", "announcements"]
        },
        {
            "id": "nova",
            "name": "Nova",
            "description": "Female voice with energetic tone",
            "gender": "female",
            "recommended_for": ["educational", "friendly"]
        },
        {
            "id": "shimmer",
            "name": "Shimmer",
            "description": "Soft female voice, gentle tone",
            "gender": "female",
            "recommended_for": ["calming", "educational", "gentle"]
        }
    ]
    
    return create_success_response(
        data={"voices": voices},
        message=f"Retrieved {len(voices)} available voices"
    )

@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported audio formats for STT
    """
    formats = [
        {
            "extension": ".mp3",
            "mime_type": "audio/mpeg",
            "description": "MP3 audio format"
        },
        {
            "extension": ".mp4", 
            "mime_type": "video/mp4",
            "description": "MP4 audio/video format"
        },
        {
            "extension": ".mpeg",
            "mime_type": "audio/mpeg", 
            "description": "MPEG audio format"
        },
        {
            "extension": ".mpga",
            "mime_type": "audio/mpeg",
            "description": "MPGA audio format"
        },
        {
            "extension": ".m4a",
            "mime_type": "audio/m4a",
            "description": "M4A audio format"
        },
        {
            "extension": ".wav",
            "mime_type": "audio/wav",
            "description": "WAV audio format"
        },
        {
            "extension": ".webm",
            "mime_type": "audio/webm",
            "description": "WebM audio format"
        }
    ]
    
    return create_success_response(
        data={
            "formats": formats,
            "max_file_size": "25MB",
            "notes": [
                "Maximum file size is 25MB",
                "Audio quality affects transcription accuracy",
                "Clear speech with minimal background noise works best"
            ]
        },
        message=f"Retrieved {len(formats)} supported audio formats"
    )

@router.get("/health")
async def voice_health_check():
    """
    Health check endpoint for voice services
    
    Tests the availability of TTS and STT services
    """
    try:
        health_status = {
            "voice_service": "healthy",
            "tts_service": "unknown", 
            "stt_service": "unknown",
            "openai_connection": "unknown",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Test OpenAI connection
        try:
            await openai_service.test_connection()
            health_status["openai_connection"] = "healthy"
        except Exception as e:
            health_status["openai_connection"] = "unhealthy"
            logger.warning(f"OpenAI connection test failed: {str(e)}")
        
        # Test TTS service with a short phrase
        try:
            test_audio = await openai_service.text_to_speech("Test", voice="alloy")
            health_status["tts_service"] = "healthy" if len(test_audio) > 0 else "degraded"
        except Exception as e:
            health_status["tts_service"] = "unhealthy"
            logger.warning(f"TTS service test failed: {str(e)}")
        
        # Note: STT testing would require an audio file, so we'll skip it in health check
        health_status["stt_service"] = "available"  # Assume available if OpenAI is working
        
        # Update timestamp
        from datetime import datetime
        health_status["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        overall_healthy = all(
            status in ["healthy", "available", "degraded"] 
            for status in health_status.values() 
            if status not in ["unknown", health_status["timestamp"]]
        )
        
        return create_success_response(
            data=health_status,
            message="Voice service health check completed"
        )
        
    except Exception as e:
        logger.error(f"Voice health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=create_error_response(
                message="Voice service health check failed",
                error_code="VOICE_HEALTH_CHECK_ERROR"
            )
        )