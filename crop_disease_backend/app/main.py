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
    description="API for crop disease detection and farmer advisory system",
    version="1.0.0",
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
            # Initialize default advisories only if DB is connected
            try:
                advisory_controller = AdvisoryController()
                await advisory_controller.initialize_default_advisories()
                logger.info("Default advisories initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize default advisories: {e}")
        else:
            logger.warning("MongoDB not available - running in fallback mode")
        
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
    """Root endpoint"""
    return {
        "message": "Crop Disease Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "database_status": "connected" if is_database_connected() else "disconnected"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if is_database_connected():
            await ensure_connection()
            return {
                "status": "healthy", 
                "database": "connected",
                "mongodb_url": settings.MONGODB_URL.replace("mongodb://", "mongodb://***:***@") if "://" in settings.MONGODB_URL else "***"
            }
        else:
            return {
                "status": "degraded", 
                "database": "disconnected",
                "message": "API is functional but database is not available",
                "mongodb_url": settings.MONGODB_URL.replace("mongodb://", "mongodb://***:***@") if "://" in settings.MONGODB_URL else "***"
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "database": "error", 
            "error": str(e),
            "mongodb_url": settings.MONGODB_URL.replace("mongodb://", "mongodb://***:***@") if "://" in settings.MONGODB_URL else "***"
        }