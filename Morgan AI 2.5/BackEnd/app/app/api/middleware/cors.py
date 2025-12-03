from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def setup_cors(
    app: FastAPI,
    allowed_origins: Optional[List[str]] = None,
    allowed_methods: Optional[List[str]] = None,
    allowed_headers: Optional[List[str]] = None,
    allow_credentials: bool = True,
    max_age: int = 3600
):
    """
    Configure CORS middleware for the FastAPI application
    
    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed origins
        allowed_methods: List of allowed HTTP methods
        allowed_headers: List of allowed headers
        allow_credentials: Whether to allow credentials
        max_age: Max age for preflight cache
    """
    
    # Default allowed origins
    if allowed_origins is None:
        allowed_origins = [
            "http://localhost:3000",      # React development
            "http://localhost:5173",      # Vite development
            "http://localhost:8000",      # API documentation
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8000",
        ]
    
    # Default allowed methods
    if allowed_methods is None:
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    
    # Default allowed headers
    if allowed_headers is None:
        allowed_headers = [
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "X-Requested-With",
            "X-CSRF-Token",
            "X-Auth-Token"
        ]
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        max_age=max_age
    )
    
    logger.info(f"CORS configured with origins: {allowed_origins}")
    logger.info(f"CORS methods allowed: {allowed_methods}")
    logger.info(f"CORS credentials allowed: {allow_credentials}")

def get_cors_config(production: bool = False) -> dict:
    """
    Get CORS configuration based on environment
    
    Args:
        production: Whether running in production mode
    
    Returns:
        Dictionary with CORS configuration
    """
    
    if production:
        # Production configuration
        return {
            "allowed_origins": [
                "https://morgan-chatbot.edu",
                "https://www.morgan-chatbot.edu",
                "https://api.morgan-chatbot.edu"
            ],
            "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
            "allowed_headers": ["Content-Type", "Authorization"],
            "allow_credentials": True,
            "max_age": 86400  # 24 hours
        }
    else:
        # Development configuration
        return {
            "allowed_origins": ["*"],  # Allow all origins in development
            "allowed_methods": ["*"],  # Allow all methods
            "allowed_headers": ["*"],  # Allow all headers
            "allow_credentials": True,
            "max_age": 3600  # 1 hour
        }

class CORSConfig:
    """CORS configuration class"""
    
    def __init__(self, app: FastAPI, production: bool = False):
        self.app = app
        self.production = production
        self.config = get_cors_config(production)
        
    def apply(self):
        """Apply CORS configuration to the app"""
        setup_cors(
            self.app,
            allowed_origins=self.config["allowed_origins"],
            allowed_methods=self.config["allowed_methods"],
            allowed_headers=self.config["allowed_headers"],
            allow_credentials=self.config["allow_credentials"],
            max_age=self.config["max_age"]
        )
        
    def update_origins(self, origins: List[str]):
        """Update allowed origins dynamically"""
        self.config["allowed_origins"] = origins
        logger.info(f"Updated CORS origins: {origins}")
        
    def add_origin(self, origin: str):
        """Add a new allowed origin"""
        if origin not in self.config["allowed_origins"]:
            self.config["allowed_origins"].append(origin)
            logger.info(f"Added CORS origin: {origin}")
            
    def remove_origin(self, origin: str):
        """Remove an allowed origin"""
        if origin in self.config["allowed_origins"]:
            self.config["allowed_origins"].remove(origin)
            logger.info(f"Removed CORS origin: {origin}")

# Custom CORS headers for specific routes
def add_cors_headers(response):
    """Add CORS headers to response"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response
