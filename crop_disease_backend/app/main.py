# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import os

from app.database import connect_to_mongo, close_mongo_connection, ensure_connection, is_database_connected
from app.routes import auth, disease, advisory, dashboard
from app.controllers.advisory_controller import AdvisoryController
from app.config import settings

# Configure logging
log_level = logging.DEBUG if not settings.is_production else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Crop Disease Detection API",
    description="AI-powered API for crop disease detection and farmer advisory system using Kindwise and Gemini AI",
    version="2.0.0",
    docs_url="/docs" if not settings.is_production else None,  # Disable docs in production
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None
)

# Security: Add trusted host middleware in production
if settings.is_production:
    # Add your production domain(s) here
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# CORS middleware - Use environment variable for origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Mount static files
uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
os.makedirs(os.path.join(uploads_dir, "images"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(disease.router)
app.include_router(advisory.router)
app.include_router(dashboard.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection and default data"""
    try:
        logger.info(f"Starting application in {settings.ENVIRONMENT} mode...")
        
        # Validate critical environment variables
        if not settings.SECRET_KEY:
            logger.error("SECRET_KEY not set!")
            raise ValueError("SECRET_KEY environment variable is required")
        
        # Try to connect to MongoDB
        db_connected = await connect_to_mongo()
        
        if db_connected:
            # Initialize minimal default advisories (optional since we use Gemini)
            try:
                advisory_controller = AdvisoryController()
                await advisory_controller.initialize_default_advisories()
                logger.info("Default advisories initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize default advisories: {e}")
        else:
            logger.warning("MongoDB not available - running in fallback mode")
        
        # Check API configurations
        if settings.KINDWISE_API_KEY and settings.KINDWISE_API_KEY != "your-kindwise-api-key-here":
            logger.info("✓ Kindwise API configured")
        else:
            logger.warning("⚠ Kindwise API key not configured - using mock predictions")
        
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
            logger.info("✓ Gemini AI configured for advisory generation")
        else:
            logger.warning("⚠ Gemini API key not configured - using fallback advisories")
        
        logger.info("Application startup completed")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        if settings.is_production:
            raise  # Fail fast in production

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connection"""
    try:
        await close_mongo_connection()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception on {request.url}: {str(exc)}", exc_info=not settings.is_production)
    
    # Don't expose internal errors in production
    error_detail = "Internal server error" if settings.is_production else str(exc)
    
    return JSONResponse(
        status_code=500,
        content={"detail": error_detail}
    )

@app.get("/")
async def root():
    """Root endpoint with system status"""
    gemini_configured = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here")
    kindwise_configured = bool(settings.KINDWISE_API_KEY and settings.KINDWISE_API_KEY != "your-kindwise-api-key-here")
    
    return {
        "message": "Crop Disease Detection API",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if not settings.is_production else "disabled",
        "features": {
            "disease_detection": "Kindwise API" if kindwise_configured else "Mock Mode",
            "advisory_generation": "Gemini AI" if gemini_configured else "Fallback Mode",
            "database": "connected" if is_database_connected() else "disconnected"
        },
        "endpoints": {
            "disease_detection": "/disease/predict",
            "diagnosis_history": "/disease/history",
            "advisory": "/advisory/disease/{disease_name}",
            "weather_advice": "/advisory/weather"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status"""
    try:
        db_connected = is_database_connected()
        if db_connected:
            await ensure_connection()
        
        gemini_status = "configured" if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here" else "not_configured"
        kindwise_status = "configured" if settings.KINDWISE_API_KEY and settings.KINDWISE_API_KEY != "your-kindwise-api-key-here" else "not_configured"
        
        overall_status = "healthy" if db_connected and gemini_status == "configured" else "degraded"
        
        response = {
            "status": overall_status,
            "environment": settings.ENVIRONMENT
        }
        
        # Only expose detailed service info in non-production
        if not settings.is_production:
            response["services"] = {
                "database": "connected" if db_connected else "disconnected",
                "kindwise_api": kindwise_status,
                "gemini_ai": gemini_status,
                "weather_api": "configured" if settings.WEATHER_API_KEY else "not_configured"
            }
        
        response["message"] = "All systems operational" if overall_status == "healthy" else "Some services unavailable"
        
        return response
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "environment": settings.ENVIRONMENT,
            "error": str(e) if not settings.is_production else "Service unavailable"
        }

@app.get("/api-info")
async def api_info():
    """Get information about API configuration"""
    # Don't expose detailed config in production
    if settings.is_production:
        return {
            "message": "API information endpoint disabled in production",
            "version": "2.0.0"
        }
    
    return {
        "kindwise_api": {
            "configured": bool(settings.KINDWISE_API_KEY and settings.KINDWISE_API_KEY != "your-kindwise-api-key-here"),
            "purpose": "Disease detection from crop images",
            "fallback": "Mock predictions available when not configured"
        },
        "gemini_ai": {
            "configured": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here"),
            "model": settings.GEMINI_MODEL,
            "purpose": "Generate comprehensive disease advisories",
            "fallback": "Basic advisories available when not configured"
        },
        "weather_api": {
            "configured": bool(settings.WEATHER_API_KEY),
            "purpose": "Weather-based agricultural advice",
            "fallback": "Dummy weather data available when not configured"
        }
    }