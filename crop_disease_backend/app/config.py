# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "crop_disease_db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    UPLOAD_DIR: str = "uploads/images"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png"}
    
    # Kindwise API
    KINDWISE_API_KEY: str = os.getenv("KINDWISE_API_KEY", "")

     # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.5-flash" 
        
    # Weather API (optional)
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    WEATHER_API_URL: str = "http://api.openweathermap.org/data/2.5/weather"

settings = Settings()