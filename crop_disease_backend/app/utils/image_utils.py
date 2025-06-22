# image_utils.py
import os
import uuid
from typing import Tuple
from PIL import Image
from fastapi import HTTPException, UploadFile
from app.config import settings

def validate_image(file: UploadFile) -> None:
    """Validate uploaded image file"""
    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Supported types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )

async def save_image(file: UploadFile) -> Tuple[str, str]:
    """Save uploaded image and return file path and URL"""
    validate_image(file)
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Create URL (adjust based on your server setup)
    file_url = f"/uploads/images/{unique_filename}"
    
    return file_path, file_url

def preprocess_image(image_path: str, target_size: Tuple[int, int] = (224, 224)) -> Image.Image:
    """Preprocess image for ML model"""
    try:
        image = Image.open(image_path)
        image = image.convert('RGB')
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")