# run.py
import uvicorn
from app.config import settings

if __name__ == "__main__":
    # Production-ready configuration
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.is_production, 
        log_level="info",
        access_log=True,
        workers=1 if not settings.is_production else 4,  
    )