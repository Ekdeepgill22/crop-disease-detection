# disease.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from app.models.diagnosis import PredictionResult
from app.models.user import UserInDB
from app.controllers.disease_controller import DiseaseController
from app.utils.auth_utils import get_current_active_user
from typing import List

router = APIRouter(prefix="/disease", tags=["disease detection"])
disease_controller = DiseaseController()

@router.post("/predict")
async def predict_disease(
    file: UploadFile = File(..., description="Crop image (JPEG/PNG)"),
    crop_type: str = Form(..., description="Type of crop (e.g., tomato, potato)"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Upload crop image and get disease prediction using Kindwise API"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    return await disease_controller.predict_disease(file, crop_type, current_user)

@router.get("/history", response_model=List[dict])
async def get_diagnosis_history(
    current_user: UserInDB = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=50, description="Number of diagnoses to return")
):
    """Get user's diagnosis history"""
    return await disease_controller.get_diagnosis_history(current_user, limit)

@router.get("/diagnosis/{diagnosis_id}", response_model=dict)
async def get_diagnosis_by_id(
    diagnosis_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get specific diagnosis by ID"""
    return await disease_controller.get_diagnosis_by_id(diagnosis_id, current_user)

@router.delete("/diagnosis/{diagnosis_id}", response_model=dict)
async def delete_diagnosis(
    diagnosis_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Delete a diagnosis and its image file"""
    return await disease_controller.delete_diagnosis(diagnosis_id, current_user)

@router.get("/supported-crops")
async def get_supported_crops():
    """Get list of supported crop types"""
    return {
        "crops": [
            "tomato", "potato", "pepper", "corn", "wheat", 
            "rice", "cotton", "soybean", "apple", "grape",
            "cucumber", "lettuce", "carrot", "onion", "garlic",
            "strawberry", "blueberry", "raspberry", "blackberry",
            "cabbage", "broccoli", "cauliflower", "spinach", "kale"
        ]
    }