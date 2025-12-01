# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import os

from app.database import connect_to_mongo, close_mongo_connection, ensure_connection, is_database_connected
from app.routes import auth, disease, advisory, dashboard
from app.controllers.advisory_controller import AdvisoryController
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Crop Disease Detection API",
    description="AI-powered API for crop disease detection and farmer advisory system using Kindwise and Gemini AI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Updated for better frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:3000", 
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
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
        logger.info("Starting application...")
        
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
        # Don't fail startup if DB is not available

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
    logger.error(f"Global exception on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/")
async def root():
    """Root endpoint with system status"""
    gemini_configured = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here")
    kindwise_configured = bool(settings.KINDWISE_API_KEY and settings.KINDWISE_API_KEY != "your-kindwise-api-key-here")
    
    return {
        "message": "Crop Disease Detection API",
        "version": "2.0.0",
        "docs": "/docs",
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
        
        return {
            "status": overall_status,
            "services": {
                "database": "connected" if db_connected else "disconnected",
                "kindwise_api": kindwise_status,
                "gemini_ai": gemini_status,
                "weather_api": "configured" if settings.WEATHER_API_KEY else "not_configured"
            },
            "message": "All systems operational" if overall_status == "healthy" else "Some services unavailable"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/api-info")
async def api_info():
    """Get information about API configuration"""
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