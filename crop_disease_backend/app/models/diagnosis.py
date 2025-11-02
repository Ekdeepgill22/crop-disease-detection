# diagnosis.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class DiagnosisCreate(BaseModel):
    crop_type: str
    image_path: str
    predicted_disease: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    advisory_id: Optional[str] = None

class DiagnosisInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    crop_type: str
    image_path: str
    image_url: str
    predicted_disease: str
    confidence_score: float
    advisory: Optional[Dict[str, Any]] = None
    api_response: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class DiagnosisResponse(BaseModel):
    id: str
    crop_type: str
    image_url: str
    predicted_disease: str
    confidence_score: float
    advisory: Optional[Dict[str, Any]] = None
    api_response: Optional[Dict[str, Any]] = None
    created_at: datetime

class PredictionResult(BaseModel):
    disease_name: str
    confidence_score: float
    crop_type: str
    advisory: Dict[str, Any]
    api_response: Optional[Dict[str, Any]] = None