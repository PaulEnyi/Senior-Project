from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import time
from contextlib import asynccontextmanager

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

# Import middleware configuration 
from .api.middleware.cors import configure_middleware

# Import API routes
from .api.routes.chat import router as chat_router
from .api.routes.voice import router as voice_router
from .api.routes.admin import router as admin_router

# Import services for initialization
from .services.pinecone_service import PineconeService
from .services.openai_service import OpenAIService

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        # Initialize services
        logger.info("Initializing services...")
        
        # Test OpenAI connection
        openai_service = OpenAIService()
        await openai_service.test_connection()
        logger.info("OpenAI service initialized")
        
        # Test Pinecone connection
        pinecone_service = PineconeService()
        await pinecone_service.test_connection()
        logger.info("Pinecone service initialized")
        
        logger.info("Morgan AI Chatbot started successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise e
    
    yield
    
    # Shutdown
    logger.info("Shutting down Morgan AI Chatbot...")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    Morgan AI Chatbot - Your Computer Science Department Assistant
    
    This chatbot provides comprehensive support for Morgan State University 
    Computer Science students with information about:
    
    - Department Information (faculty, staff, locations, contact info)
    - Academic Support (tutoring, course guidance, prerequisites)  
    - Career Resources (internships, interview prep, job search tools)
    - Advising & Registration (enrollment, forms, deadlines)
    - Voice Features (text-to-speech, speech-to-text)
    - Admin Tools (knowledge base management)
    """,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Configure comprehensive middleware (CORS, security headers, request ID, rate limiting, etc.)
configure_middleware(app)

# Custom middleware for application-specific logging and rate limiting
@app.middleware("http")
async def logging_and_rate_limit_middleware(request: Request, call_next):
    """Log requests and apply additional rate limiting logic"""
    start_time = time.time()
    
    # Get client IP (supports proxy headers)
    client_ip = request.client.host
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    elif "x-real-ip" in request.headers:
        client_ip = request.headers["x-real-ip"]
    
    # Application-specific rate limiting (additional to middleware headers)
    
    # Skip rate limiting for admin endpoints in debug mode
    if not (settings.DEBUG and request.url.path.startswith("/api/admin")):
        if not rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": True,
                    "message": "Too many requests. Please slow down and try again later.",
                    "type": "RateLimitError"
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": "100",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + 3600)
                }
            )
    
    # Process request
    response = await call_next(request)
    
    # Log request with additional details
    process_time = time.time() - start_time
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "time": f"{process_time:.3f}s",
        "ip": client_ip,
        "user_agent": request.headers.get("user-agent", "unknown")[:100]
    }
    
    # Log at appropriate level based on status code
    if response.status_code >= 500:
        logger.error(f"Server Error: {log_data}")
    elif response.status_code >= 400:
        logger.warning(f"Client Error: {log_data}")
    else:
        logger.info(f"Request: {log_data['method']} {log_data['path']} - "
                   f"Status: {log_data['status']} - Time: {log_data['time']} - IP: {log_data['ip']}")
    
    return response

# Exception handlers (in order of specificity)
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
    """
    Health check endpoint
    
    Returns the current status of the application and key metrics
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time(),
        "environment": "development" if settings.DEBUG else "production",
        "services": {
            "api": "running",
            "middleware": "configured",
            "routes": "loaded"
        }
    }

# Detailed health check for monitoring
@app.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check for monitoring systems
    
    Provides comprehensive status information
    """
    try:
        # Test basic functionality
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "app_info": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": "development" if settings.DEBUG else "production"
            },
            "system": {
                "middleware_configured": True,
                "routes_loaded": len(app.routes),
                "exception_handlers": len(app.exception_handlers)
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information
    
    Provides basic information about the Morgan AI Chatbot API
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "description": "AI Chatbot for Morgan State University Computer Science Department",
        "features": [
            "Natural language chat with AI",
            "Voice-to-text and text-to-speech",
            "Morgan State CS department knowledge",
            "Thread-based conversations",
            "Admin management tools"
        ],
        "endpoints": {
            "chat": "/api/chat",
            "voice": "/api/voice", 
            "admin": "/api/admin",
            "health": "/health",
            "detailed_health": "/health/detailed",
            "docs": "/docs" if settings.DEBUG else "Disabled in production",
            "redoc": "/redoc" if settings.DEBUG else "Disabled in production"
        },
        "support": {
            "university": "Morgan State University",
            "department": "Computer Science",
            "contact": "For support, contact the CS department"
        }
    }

# Development-only endpoint for debugging
if settings.DEBUG:
    @app.get("/debug/middleware")
    async def debug_middleware():
        """Debug endpoint to check middleware configuration"""
        from .api.middleware.cors import get_cors_config
        
        return {
            "middleware_stack": [str(middleware) for middleware in app.user_middleware],
            "cors_config": get_cors_config(),
            "debug_mode": settings.DEBUG,
            "rate_limiter_active": True
        }

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Morgan AI Chatbot server...")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        access_log=True,
        reload_excludes=["*.pyc", "*.pyo", "__pycache__"]
    )
