# advisory.py
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.models.advisory import WeatherAdvice
from app.models.user import UserInDB
from app.controllers.advisory_controller import AdvisoryController
from app.utils.auth_utils import get_current_active_user

router = APIRouter(prefix="/advisory", tags=["advisory"])
advisory_controller = AdvisoryController()

@router.get("/weather", response_model=Optional[WeatherAdvice])
async def get_weather_advice(
    region: Optional[str] = Query(None, description="Region name (uses user's region if not provided)"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get weather-based agricultural advice"""
    target_region = region or current_user.region
    return await advisory_controller.get_weather_advice(target_region)

@router.get("/disease/{disease_name}")
async def get_disease_info(
    disease_name: str,
    crop_type: str = Query("General", description="Crop type"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get detailed information about a specific disease"""
    advisory = await advisory_controller.get_advisory_by_disease(disease_name, crop_type)
    if not advisory:
        return {"message": "Advisory not found for this disease and crop combination"}
    return advisory