from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import io
import logging
from app.core.security import security_service
from app.core.exceptions import VoiceProcessingException
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)
router = APIRouter()

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    voice: Optional[str] = Field(default="alloy", description="Voice model to use")
    speed: Optional[float] = Field(default=1.0, ge=0.25, le=4.0, description="Speech speed")
    format: Optional[str] = Field(default="mp3", description="Audio format")

class STTResponse(BaseModel):
    text: str = Field(..., description="Transcribed text")
    confidence: Optional[float] = Field(None, description="Transcription confidence")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")

@router.post("/text-to-speech")
async def text_to_speech(
    request: TTSRequest,
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Convert text to speech using OpenAI TTS"""
    try:
        openai_service = app_request.app.state.openai
        
        # Generate audio
        audio_data = await openai_service.text_to_speech(
            text=request.text,
            voice=request.voice,
            speed=request.speed,
            response_format=request.format
        )
        
        # Return audio stream
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type=f"audio/{request.format}",
            headers={
                "Content-Disposition": f"inline; filename=speech.{request.format}"
            }
        )
        
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {str(e)}")

@router.post("/speech-to-text", response_model=STTResponse)
async def speech_to_text(
    audio: UploadFile = File(...),
    language: Optional[str] = "en",
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Convert speech to text using OpenAI Whisper"""
    try:
        # Validate audio file
        if not audio.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="Invalid audio file")
        
        # Read audio data
        audio_data = await audio.read()
        
        openai_service = app_request.app.state.openai
        
        # Transcribe audio
        result = await openai_service.speech_to_text(
            audio_data=audio_data,
            filename=audio.filename,
            language=language
        )
        
        return STTResponse(
            text=result["text"],
            confidence=result.get("confidence"),
            duration=result.get("duration")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STT error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {str(e)}")

@router.post("/realtime/connect")
async def connect_realtime(
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Initialize OpenAI Realtime API connection for voice chat"""
    try:
        openai_service = app_request.app.state.openai
        
        # Create realtime session
        session = await openai_service.create_realtime_session(
            user_id=current_user["user_id"]
        )
        
        return {
            "session_id": session["session_id"],
            "ephemeral_key": session["ephemeral_key"],
            "expires_at": session["expires_at"],
            "websocket_url": session["websocket_url"]
        }
        
    except Exception as e:
        logger.error(f"Realtime connection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to realtime API: {str(e)}")

@router.post("/realtime/disconnect")
async def disconnect_realtime(
    session_id: str,
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Disconnect from OpenAI Realtime API"""
    try:
        openai_service = app_request.app.state.openai
        
        await openai_service.close_realtime_session(session_id)
        
        return {"message": "Disconnected successfully"}
        
    except Exception as e:
        logger.error(f"Realtime disconnect error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to disconnect: {str(e)}")

@router.get("/voices")
async def get_available_voices(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get list of available TTS voices"""
    return {
        "voices": [
            {"id": "alloy", "name": "Alloy", "gender": "neutral", "accent": "American"},
            {"id": "echo", "name": "Echo", "gender": "male", "accent": "American"},
            {"id": "fable", "name": "Fable", "gender": "neutral", "accent": "British"},
            {"id": "onyx", "name": "Onyx", "gender": "male", "accent": "American"},
            {"id": "nova", "name": "Nova", "gender": "female", "accent": "American"},
            {"id": "shimmer", "name": "Shimmer", "gender": "female", "accent": "American"}
        ]
    }

@router.get("/status")
async def get_voice_status(
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Get voice service status"""
    try:
        openai_service = app_request.app.state.openai
        
        return {
            "tts_enabled": True,
            "stt_enabled": True,
            "realtime_enabled": openai_service.realtime_available,
            "default_voice": "alloy",
            "supported_formats": ["mp3", "opus", "aac", "flac", "wav", "pcm"]
        }
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return {
            "tts_enabled": False,
            "stt_enabled": False,
            "realtime_enabled": False,
            "error": str(e)
        }

@router.post("/greeting")
async def generate_greeting(
    username: str,
    voice: Optional[str] = "alloy",
    current_user: Dict = Depends(security_service.get_current_user),
    app_request: Request = None
):
    """Generate personalized greeting audio for user login"""
    try:
        openai_service = app_request.app.state.openai
        
        # Create greeting text
        greeting_text = f"Hello {username}, welcome back to Morgan AI Assistant."
        
        # Generate audio
        audio_data = await openai_service.text_to_speech(
            text=greeting_text,
            voice=voice,
            speed=1.0,
            response_format="mp3"
        )
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mp3",
            headers={
                "Content-Disposition": "inline; filename=greeting.mp3"
            }
        )
        
    except Exception as e:
        logger.error(f"Greeting generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate greeting: {str(e)}")