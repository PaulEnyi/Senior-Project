# FastAPI application entry

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time 

# Import core modules

from .core.config import settings
from .core.exceptions import (
    MorganAIChatbotException, 
    morgan_ai_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    custom_http_exception_handler
)
from .core.security import rate_limiter

# Import API routes

from. api.routes.chat import router as chat_router
from. api.routes.voice import router as voice_router
from. api.routes.user import router as user_router
from. api.routes.admin import router as admin_router

# Import services for initialization

from .services.pinecone_service import Pineconeservice
from .serices.openai_service import OpenAIService

# Configure logging

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging = logging.getLogger(__name__)

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    "Manage applicattion liffcycle"
    # Startup tasks
    logging.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        # Initialize services
        logging.info("Initializing Pinecone service...")

        # Test OpenAI connection
        openai_service = OpenAIService()
        await openai_service.test_connection()
        logging.info("OpenAI service initialized successfully.")

        # Initialize Pinecone
        pinecone_service = PineconeService()
        await pinecone_service.test_connection()
        logging.info("Pinecone service initialized successfully.")

        logging.info("Morgan AI Chatbot started successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize services: {str(e)}")
        raise e

    yield

    # Shutdown
    loger.info("Shutting down Morgan AI Chatbot...")
    
# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    Morgan AI Chatbot - Your Computer Science Department Assistant
    For students studying computer science at Morgan State University, this chatbot offers thorough assistance with details regarding:
    
    - Department Information (faculty, staff, locations, contact info)
    - Academic Support (tutoring, course guidance, prerequisites)
    - Career Resources (internships, interview prep, job search tools)
    - Advising & Registration (enrollment, forms, deadlines)
    - Voice Features (text-to-speech, speech-to-text)
    - Admin Tools (knowledge base management)
    """,
    version=settings.APP_VERSION,
    doc_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trust proxy headers if behind reverse proxy

app.add_middleware(
    TrueedHostMiddleware, 
    allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
)

# Custom middleware for logging and rate limiting

@app.middleware("http")
async def logging_and_rate_limit_middleware(request: Request, call_next):
    """Log requests and apply rate limiting"""
    start_time = time.time()
    
    # Get client IP
    client_ip = request.client.host
    
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    
    # Rate limiting (skip for admin endpoints in debug mode)
    if not (settings.DEBUG and request.url.path.startswith("/admin")):
        if not rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": True,
                    "message": "Too many requests. Please slow down and try again later.",
                    "type": "RateLimitError"
                }
            )
    
    # Process request
    response = await call_next(request)
    
    # Log request
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s - "
        f"IP: {client_ip}"
    )
    
    return response

# Exception handlers
app.add_exception_handler(MorganAIChatbotException, morgan_ai_exception_handler)
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# API Routes
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time()
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "description": "AI Chatbot for Morgan State University Computer Science Department",
        "endpoints": {
            "chat": "/api/chat",
            "voice": "/api/voice", 
            "admin": "/api/admin",
            "health": "/health",
            "docs": "/docs" if settings.DEBUG else "Disabled in production"
        }
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )