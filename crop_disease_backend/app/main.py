# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import os

from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, disease, advisory, dashboard
from app.controllers.advisory_controller import AdvisoryController
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
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
if not os.path.exists("uploads"):
    os.makedirs("uploads")
    os.makedirs("uploads/images")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(disease.router)
app.include_router(advisory.router)
app.include_router(dashboard.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection and default data"""
    await connect_to_mongo()
    
    # Initialize default advisories
    advisory_controller = AdvisoryController()
    await advisory_controller.initialize_default_advisories()
    
    logger.info("Application startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connection"""
    await close_mongo_connection()
    logger.info("Application shutdown completed")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
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
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}