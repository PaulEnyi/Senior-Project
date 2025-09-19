from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from ...core.config import settings

logger = logging.getLogger(__name__)

def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application
    
    Sets up Cross-Origin Resource Sharing to allow frontend access
    from specified origins with appropriate security measures
    """
    
    # CORS Origins - allow frontend development and production URLs
    origins = settings.ALLOWED_ORIGINS.copy()
    
    # Add localhost variations for development
    if settings.DEBUG:
        additional_origins = [
            "http://localhost:3000",      # React dev server
            "http://localhost:5173",      # Vite dev server
            "http://127.0.0.1:3000",      # Alternative localhost
            "http://127.0.0.1:5173",      # Alternative localhost
            "http://localhost:8080",      # Alternative port
            "http://localhost:4173",      # Vite preview
        ]
        
        for origin in additional_origins:
            if origin not in origins:
                origins.append(origin)
    
    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=[
            "GET",
            "POST", 
            "PUT",
            "DELETE",
            "OPTIONS",
            "HEAD",
            "PATCH"
        ],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRFToken",
            "X-Request-ID",
            "User-Agent",
            "Referer",
            "Origin"
        ],
        expose_headers=[
            "Content-Length",
            "Content-Type",
            "X-Request-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset"
        ],
        max_age=86400  # 24 hours - how long browsers can cache preflight responses
    )
    
    logger.info(f"CORS configured with origins: {origins}")

def setup_trusted_hosts(app: FastAPI) -> None:
    """
    Configure trusted host middleware for security
    
    Validates the Host header to prevent Host header injection attacks
    """
    
    if settings.DEBUG:
        # In development, allow all hosts for easier testing
        allowed_hosts = ["*"]
    else:
        # In production, restrict to specific hosts
        allowed_hosts = [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "morgan-ai.morgan.edu",
            "api.morgan.edu",
        ]
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts
    )
    
    logger.info(f"Trusted hosts configured: {allowed_hosts}")

def setup_security_headers(app: FastAPI) -> None:
    """
    Add security headers middleware
    
    Adds various security headers to protect against common attacks
    """
    
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (CSP)
        if settings.DEBUG:
            # More permissive CSP for development
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' http://localhost:* ws://localhost:*;"
            )
        else:
            # Strict CSP for production
            csp = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self';"
            )
        
        response.headers["Content-Security-Policy"] = csp
        
        # HSTS (HTTP Strict Transport Security) for production
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # Cache control for API responses
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response

def setup_request_id_middleware(app: FastAPI) -> None:
    """
    Add request ID middleware for request tracing
    
    Adds a unique ID to each request for logging and debugging
    """
    
    @app.middleware("http")
    async def add_request_id(request, call_next):
        
        import uuid
        
        request_id = str(uuid.uuid4())# Generate unique request ID
        request.state.request_id = request_id   # Add to request state for access in route handlers
        response = await call_next(request)  # Process request
        response.headers["X-Request-ID"] = request_id  # Add request ID to response headers
        
        return response

def setup_rate_limiting_headers(app: FastAPI) -> None:
    """
    Add rate limiting headers
    
    Provides information about rate limits to clients
    """
    
    @app.middleware("http") 
    async def add_rate_limit_headers(request, call_next):
        response = await call_next(request)
        
        # Add rate limiting headers (values would come from actual rate limiter)
        response.headers["X-RateLimit-Limit"] = "100"  # requests per hour
        response.headers["X-RateLimit-Remaining"] = "99"  # remaining requests
        response.headers["X-RateLimit-Reset"] = "3600"  # seconds until reset
        
        return response

def configure_middleware(app: FastAPI) -> None:
    """
    Configure all middleware for the application
    
    Sets up CORS, security headers, trusted hosts, and other middleware
    in the correct order
    """
    
    logger.info("Configuring application middleware...")
    
    # Order matters for middleware - they execute in reverse order of registration

    setup_rate_limiting_headers(app)  # 1. Rate limiting headers (last to execute, first to add headers)
    setup_request_id_middleware(app) # 2. Request ID tracking
    setup_security_headers(app) # 3. Security headers
    setup_trusted_hosts(app) # 4. Trusted hosts (validates Host header)
    setup_cors(app) # 5. CORS (handles preflight and cross-origin requests)
    
    logger.info("All middleware configured successfully")

# Exception handling for CORS errors
def handle_cors_errors():
    """
    Helper function to handle common CORS-related errors
    
    Returns helpful error messages for CORS issues
    """
    
    cors_troubleshooting = {
        "common_issues": [
            "Frontend URL not in ALLOWED_ORIGINS",
            "Missing credentials in frontend requests",
            "Incorrect HTTP method",
            "Custom headers not allowed"
        ],
        "solutions": [
            "Check ALLOWED_ORIGINS in backend config",
            "Ensure withCredentials: true in frontend",
            "Verify HTTP method is in allow_methods",
            "Add custom headers to allow_headers"
        ]
    }
    
    return cors_troubleshooting

# Development helper
def get_cors_config():
    """
    Get current CORS configuration for debugging
    
    Returns the current CORS settings
    """
    
    return {
        "allowed_origins": settings.ALLOWED_ORIGINS,
        "debug_mode": settings.DEBUG,
        "app_name": settings.APP_NAME,
        "environment": "development" if settings.DEBUG else "production"
    }