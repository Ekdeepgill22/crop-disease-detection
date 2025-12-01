# advisory.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from app.models.advisory import WeatherAdvice
from app.models.user import UserInDB
from app.controllers.advisory_controller import AdvisoryController
from app.utils.auth_utils import get_current_active_user
from app.utils.gemini_utils import GeminiAPI
import logging

router = APIRouter(prefix="/advisory", tags=["advisory"])
advisory_controller = AdvisoryController()
gemini_api = GeminiAPI()
logger = logging.getLogger(__name__)

@router.get("/weather", response_model=Optional[WeatherAdvice])
async def get_weather_advice(
    region: Optional[str] = Query(None, description="Region name (uses user's region if not provided)"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get weather-based agricultural advice"""
    target_region = region or current_user.region
    return await advisory_controller.get_weather_advice(target_region)

@router.get("/disease/{disease_name}")
async def get_disease_advisory(
    disease_name: str,
    crop_type: str = Query("General", description="Crop type"),
    regenerate: bool = Query(False, description="Force regenerate advisory using AI"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get detailed advisory for a specific disease
    - Checks database first for existing advisory
    - If regenerate=true or no advisory exists, generates new one using Gemini AI
    """
    try:
        # Check for existing advisory first
        if not regenerate:
            advisory = await advisory_controller.get_advisory_by_disease(disease_name, crop_type)
            if advisory:
                logger.info(f"Returning existing advisory for {disease_name} on {crop_type}")
                return {
                    "source": "database",
                    "advisory": advisory
                }
        
        # Generate new advisory using Gemini
        logger.info(f"Generating new advisory for {disease_name} on {crop_type}")
        advisory = gemini_api.generate_advisory(
            disease_name=disease_name,
            crop_type=crop_type,
            confidence_score=1.0,  # Default confidence when manually requested
            kindwise_response=None
        )
        
        # Save to database
        advisory_id = await advisory_controller.create_advisory(advisory)
        
        return {
            "source": "ai_generated",
            "advisory": advisory,
            "saved": advisory_id is not None
        }
        
    except Exception as e:
        logger.error(f"Error getting disease advisory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get advisory: {str(e)}")

@router.get("/list")
async def list_advisories(
    limit: int = Query(50, ge=1, le=100, description="Number of advisories to return"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get list of all available advisories"""
    try:
        advisories = await advisory_controller.get_all_advisories(limit=limit)
        return {
            "count": len(advisories),
            "advisories": advisories
        }
    except Exception as e:
        logger.error(f"Error listing advisories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list advisories: {str(e)}")

@router.post("/regenerate")
async def regenerate_advisory(
    disease_name: str = Query(..., description="Disease name"),
    crop_type: str = Query(..., description="Crop type"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Regenerate advisory for a disease using Gemini AI
    This will create a new advisory or update existing one
    """
    try:
        logger.info(f"Regenerating advisory for {disease_name} on {crop_type}")
        
        # Generate new advisory
        advisory = gemini_api.generate_advisory(
            disease_name=disease_name,
            crop_type=crop_type,
            confidence_score=1.0,
            kindwise_response=None
        )
        
        # Check if advisory exists and update, otherwise create
        existing = await advisory_controller.get_advisory_by_disease(disease_name, crop_type)
        
        if existing:
            # Update existing
            from datetime import datetime
            advisory['updated_at'] = datetime.utcnow()
            success = await advisory_controller.update_advisory(disease_name, crop_type, advisory)
            action = "updated" if success else "failed_to_update"
        else:
            # Create new
            from datetime import datetime
            advisory['created_at'] = datetime.utcnow()
            advisory_id = await advisory_controller.create_advisory(advisory)
            action = "created" if advisory_id else "failed_to_create"
        
        return {
            "action": action,
            "disease_name": disease_name,
            "crop_type": crop_type,
            "advisory": advisory
        }
        
    except Exception as e:
        logger.error(f"Error regenerating advisory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate advisory: {str(e)}")