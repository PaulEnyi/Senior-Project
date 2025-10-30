from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# Import routers
from app.api.routes import chat, voice, admin, internship, auth
from app.services.pinecone_service import PineconeService
from app.services.openai_service import OpenAIService
from app.core.config import settings
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
    
    # Initialize Pinecone
    try:
        pinecone_service = PineconeService()
        app.state.pinecone = pinecone_service
        logger.info("Pinecone service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone: {e}")
    
    # Initialize OpenAI
    try:
        openai_service = OpenAIService()
        app.state.openai = openai_service
        logger.info("OpenAI service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI: {e}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Morgan AI Chatbot Backend...")
    # await websocket_manager.disconnect_all()  # Commented out if not used

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
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(internship.router, prefix="/api/internships", tags=["Internships"])
# app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Knowledge Base"])

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
            "openai": "unknown",
            "pinecone": "unknown"
        }
    }
    
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
    """WebSocket endpoint for real-time voice communication"""
    await websocket.accept()
    try:
        while True:
            # Receive any bytes/text and acknowledge
            msg = await websocket.receive()
            if 'bytes' in msg:
                await websocket.send_text("voice:bytes_received")
            elif 'text' in msg:
                await websocket.send_text("voice:text_received")
            
    except WebSocketDisconnect:
        logger.info(f"Voice client {session_id} disconnected")
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )