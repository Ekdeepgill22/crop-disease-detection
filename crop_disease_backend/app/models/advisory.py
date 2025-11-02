# advisory.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class Treatment(BaseModel):
    step: int
    description: str
    materials_needed: Optional[List[str]] = []

class Advisory(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    disease_name: str
    crop_type: str
    severity: str = Field(..., pattern="^(mild|moderate|severe)$")
    description: str
    symptoms: List[str]
    treatment_steps: List[Treatment]
    recommended_pesticide: Optional[str] = None
    recommended_fertilizer: Optional[str] = None
    prevention_tips: List[str]
    estimated_recovery_time: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class WeatherAdvice(BaseModel):
    temperature: float
    humidity: float
    weather_condition: str
    planting_advice: str
    irrigation_advice: str
    pest_risk: str
    humidity_advice: str = ""