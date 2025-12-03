from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os
import json
import base64
import time
from dotenv import load_dotenv

# Import routers
from app.api.routes import chat, voice, admin, internship, auth, knowledge, degree_works, websis, scraper, recommendations, auth_database_backup
from app.api.routes import debug as debug_routes
from app.services.pinecone_service import PineconeService
from app.services.openai_service import OpenAIService
from app.services.internship_update_service import internship_update_service
from app.services.websis_service import websis_service
from app.services.morgan_cs_scraper import morgan_cs_scraper
from app.core.config import settings
from app.core.security import SecurityService
from app.core.database import db_service
from app.api.middleware.cors import setup_cors, get_cors_config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
# websocket_manager = WebSocketManager()  # Commented out if not used

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup, cleanup on shutdown"""
    logger.info("Starting Morgan AI Chatbot Backend...")
    
    # Initialize Database FIRST
    try:
        await db_service.initialize()
        app.state.db = db_service
        logger.info("✓ Database service initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
        raise
    
    # Initialize Pinecone
    try:
        pinecone_service = PineconeService()
        app.state.pinecone = pinecone_service
        logger.info("✓ Pinecone service initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize Pinecone: {e}")
    
    # Initialize OpenAI
    try:
        openai_service = OpenAIService()
        app.state.openai = openai_service
        logger.info("✓ OpenAI service initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize OpenAI: {e}")
    
    # Initialize and start internship auto-update service
    try:
        # Perform initial update
        logger.info("Performing initial internship data update...")
        await internship_update_service.update_internships(force=True)
        
        # Start periodic updates in background
        import asyncio
        asyncio.create_task(internship_update_service.start_periodic_updates())
        logger.info("✓ Internship auto-update service started")
    except Exception as e:
        logger.error(f"✗ Failed to initialize internship update service: {e}")
    
    logger.info("=" * 60)
    logger.info("🚀 Morgan AI Backend Successfully Started!")
    logger.info(f"📊 Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'SQLite'}")
    logger.info(f"🔐 All user data securely stored and encrypted")
    logger.info("=" * 60)
    
    yield
    
    # Cleanup
    logger.info("Shutting down Morgan AI Chatbot Backend...")
    
    # Close database connections
    try:
        await db_service.close()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"✗ Error closing database: {e}")

# Create FastAPI app
app = FastAPI(
    title="Morgan AI Chatbot API",
    description="AI-powered assistant for Morgan State University Computer Science Department",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
# Apply CORS (dev allows all; set production=True when deploying under domain)
cors_cfg = get_cors_config(production=False)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_cfg["allowed_origins"],
    allow_methods=cors_cfg["allowed_methods"],
    allow_headers=cors_cfg["allowed_headers"],
    allow_credentials=cors_cfg["allow_credentials"],
    max_age=cors_cfg["max_age"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication (File)"])
app.include_router(auth_database_backup.router, prefix="/api/auth-db", tags=["Authentication (DB)"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(internship.router, prefix="/api/internships", tags=["Internships"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Knowledge Base"])
app.include_router(degree_works.router, prefix="/api/degree-works", tags=["Degree Works"])
app.include_router(websis.router, prefix="/api/websis", tags=["WebSIS Integration"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["Web Scraper"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Course Recommendations"])
app.include_router(debug_routes.router, prefix="/api/debug", tags=["Debug"])

# Serve static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Morgan AI Chatbot API",
        "status": "operational",
        "version": "1.0.0",
        "university": "Morgan State University",
        "department": "Computer Science"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "services": {
            "api": "operational",
            "database": "unknown",
            "openai": "unknown",
            "pinecone": "unknown"
        }
    }
    
    # Check Database
    try:
        if hasattr(app.state, 'db'):
            is_healthy = await db_service.health_check()
            health_status["services"]["database"] = "operational" if is_healthy else "error"
            
            # Get table counts for monitoring
            if is_healthy:
                counts = await db_service.get_table_counts()
                health_status["database_stats"] = counts
    except Exception as e:
        health_status["services"]["database"] = "error"
        logger.error(f"Database health check failed: {e}")
    
    # Check OpenAI
    try:
        if hasattr(app.state, 'openai'):
            health_status["services"]["openai"] = "operational"
    except:
        health_status["services"]["openai"] = "error"
    
    # Check Pinecone
    try:
        if hasattr(app.state, 'pinecone'):
            health_status["services"]["pinecone"] = "operational"
    except:
        health_status["services"]["pinecone"] = "error"
    
    return health_status

@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    # Simple echo chat until a manager is implemented
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"echo:{session_id}:{data}")
            
    except WebSocketDisconnect:
        logger.info(f"Client {session_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

@app.websocket("/ws/voice/{session_id}")
async def websocket_voice(websocket: WebSocket, session_id: str):
    """Voice streaming WebSocket: client sends audio bytes, receives transcripts + responses.
    Protocol:
      - Binary frames: raw audio chunks (mp3/wav/webm)
      - Text frames:
            'commit' -> finalize, generate response + TTS
            'reset'  -> clear buffer
            JSON {'type':'ping'} -> latency echo
    Server messages (text JSON):
        {'type':'transcript','text':...,'bytes':int}
        {'type':'response','text':...,'audio_b64':...,'metrics':{...}}
        {'type':'error','error':...}
    """
    # Auth: require Bearer token in query (?token=) or header
    token = websocket.query_params.get('token') or websocket.headers.get('authorization')
    try:
        if token and isinstance(token, str) and token.lower().startswith('bearer '):
            token = token.split(' ', 1)[1]
        payload = SecurityService.decode_token(token) if token else None
        user_id = payload.get('user_id') if payload else None
        if payload is None:
            await websocket.close(code=4401)  # Unauthorized
            return
    except Exception:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    buffer = bytearray()
    last_partial_size = 0
    MIN_PARTIAL_BYTES = 30000
    MAX_SESSION_BYTES = 2_000_000
    openai_service = getattr(websocket.app.state, 'openai', None)
    start_time = time.perf_counter()
    try:
        while True:
            msg = await websocket.receive()
            if 'bytes' in msg and msg['bytes'] is not None:
                chunk = msg['bytes']
                buffer.extend(chunk)
                if len(buffer) > MAX_SESSION_BYTES:
                    await websocket.send_text(json.dumps({'type':'error','error':'audio too large'}))
                    await websocket.close(code=1009)
                    return
                if openai_service and (len(buffer) - last_partial_size) >= MIN_PARTIAL_BYTES:
                    t0 = time.perf_counter()
                    transcript = await openai_service.speech_to_text(bytes(buffer))
                    t1 = time.perf_counter()
                    last_partial_size = len(buffer)
                    await websocket.send_text(json.dumps({'type':'transcript','text':transcript,'bytes':len(buffer),'stt_ms':int((t1-t0)*1000)}))
            elif 'text' in msg and msg['text'] is not None:
                text_msg = msg['text']
                if text_msg == 'commit':
                    if not openai_service:
                        await websocket.send_text(json.dumps({'type':'error','error':'service unavailable'}))
                        continue
                    # Final transcript (re-run for quality)
                    stt_start = time.perf_counter()
                    transcript = await openai_service.speech_to_text(bytes(buffer)) if buffer else ''
                    stt_end = time.perf_counter()
                    # Generate chat response
                    gen_start = time.perf_counter()
                    chat = await openai_service.generate_chat_response(transcript or 'Hello', session_id=session_id, use_rag=True)
                    gen_end = time.perf_counter()
                    # TTS response
                    tts_start = time.perf_counter()
                    audio_bytes = await openai_service.text_to_speech(chat.get('response',''))
                    tts_end = time.perf_counter()
                    metrics = {
                        'stt_ms': int((stt_end-stt_start)*1000),
                        'chat_ms': int((gen_end-gen_start)*1000),
                        'tts_ms': int((tts_end-tts_start)*1000),
                        'total_ms': int((time.perf_counter()-start_time)*1000),
                        'bytes_received': len(buffer)
                    }
                    # Persist metrics to JSONL
                    try:
                        os.makedirs('app/data/metrics', exist_ok=True)
                        with open('app/data/metrics/voice_ws.jsonl', 'a', encoding='utf-8') as f:
                            out = {
                                'ts': time.time(),
                                'session_id': session_id,
                                'user_id': user_id,
                                **metrics
                            }
                            f.write(json.dumps(out) + "\n")
                    except Exception as e:
                        logger.error(f"Failed to persist voice metrics: {e}")

                    # Send response text + metrics first
                    await websocket.send_text(json.dumps({
                        'type':'response',
                        'text': chat.get('response',''),
                        'transcript': transcript,
                        'metrics': metrics
                    }))
                    # Stream audio in chunks
                    await websocket.send_text(json.dumps({'type':'audio_start','format':'mp3'}))
                    CHUNK = 32768
                    for i in range(0, len(audio_bytes), CHUNK):
                        chunk = audio_bytes[i:i+CHUNK]
                        await websocket.send_text(json.dumps({'type':'audio_chunk','b64': base64.b64encode(chunk).decode()}))
                    await websocket.send_text(json.dumps({'type':'audio_end'}))
                elif text_msg == 'reset':
                    buffer.clear(); last_partial_size = 0
                    await websocket.send_text(json.dumps({'type':'reset'}))
                else:
                    # Try parse JSON ping
                    try:
                        obj = json.loads(text_msg)
                        if obj.get('type') == 'ping':
                            await websocket.send_text(json.dumps({'type':'pong','ts':time.time()}))
                        else:
                            await websocket.send_text(json.dumps({'type':'ack'}))
                    except json.JSONDecodeError:
                        await websocket.send_text(json.dumps({'type':'ack'}))
    except WebSocketDisconnect:
        logger.info(f"Voice client {session_id} disconnected")
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")
        try:
            await websocket.send_text(json.dumps({'type':'error','error':str(e)}))
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )