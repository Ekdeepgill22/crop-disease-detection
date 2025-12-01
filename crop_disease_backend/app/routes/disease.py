# disease.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from app.models.diagnosis import PredictionResult
from app.models.user import UserInDB
from app.controllers.disease_controller import DiseaseController
from app.utils.auth_utils import get_current_active_user
from typing import List
import logging

router = APIRouter(prefix="/disease", tags=["disease detection"])
disease_controller = DiseaseController()
logger = logging.getLogger(__name__)

@router.post("/predict")
async def predict_disease(
    file: UploadFile = File(..., description="Crop image (JPEG/PNG)"),
    crop_type: str = Form(..., description="Type of crop (e.g., tomato, potato)"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Upload crop image and get disease prediction
    - Uses Kindwise API for disease detection
    - Generates comprehensive advisory using Gemini AI
    - Stores results in database
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        result = await disease_controller.predict_disease(file, crop_type, current_user)
        logger.info(f"Disease prediction successful for user {current_user.email}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disease prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/history", response_model=List[dict])
async def get_diagnosis_history(
    current_user: UserInDB = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=50, description="Number of diagnoses to return")
):
    """Get user's diagnosis history"""
    try:
        history = await disease_controller.get_diagnosis_history(current_user, limit)
        return history
    except Exception as e:
        logger.error(f"Failed to get diagnosis history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@router.get("/diagnosis/{diagnosis_id}", response_model=dict)
async def get_diagnosis_by_id(
    diagnosis_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get specific diagnosis by ID with full advisory details"""
    try:
        diagnosis = await disease_controller.get_diagnosis_by_id(diagnosis_id, current_user)
        return diagnosis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get diagnosis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get diagnosis: {str(e)}")

@router.delete("/diagnosis/{diagnosis_id}", response_model=dict)
async def delete_diagnosis(
    diagnosis_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Delete a diagnosis and its associated image file"""
    try:
        result = await disease_controller.delete_diagnosis(diagnosis_id, current_user)
        logger.info(f"Deleted diagnosis {diagnosis_id} for user {current_user.email}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete diagnosis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete diagnosis: {str(e)}")

@router.get("/supported-crops")
async def get_supported_crops():
    """Get list of supported crop types"""
    return {
        "crops": [
            "apple", "banana", "barley", "cassava", "citrus", "cocoa", 
            "coffee", "corn", "cotton", "cucumber", "eggplant", "garlic", 
            "grapevine", "oil palm", "onion", "potato", "rice", "soybean", 
            "sugarcane", "tea", "tobacco", "tomato", "wheat"
        ],
        "note": "System uses AI to generate advisories for all crops, including those not listed"
    }

@router.get("/statistics")
async def get_disease_statistics(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get statistics about detected diseases for the current user"""
    try:
        from app.database import get_database
        db = get_database()
        
        # Get disease frequency
        pipeline = [
            {"$match": {"user_id": str(current_user.id)}},
            {"$group": {
                "_id": "$predicted_disease",
                "count": {"$sum": 1},
                "avg_confidence": {"$avg": "$confidence_score"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        disease_stats = []
        async for stat in db.diagnoses.aggregate(pipeline):
            disease_stats.append({
                "disease": stat["_id"],
                "count": stat["count"],
                "avg_confidence": round(stat["avg_confidence"], 2)
            })
        
        # Get crop frequency
        pipeline[1]["$group"]["_id"] = "$crop_type"
        crop_stats = []
        async for stat in db.diagnoses.aggregate(pipeline):
            crop_stats.append({
                "crop": stat["_id"],
                "count": stat["count"],
                "avg_confidence": round(stat["avg_confidence"], 2)
            })
        
        return {
            "disease_frequency": disease_stats,
            "crop_frequency": crop_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")