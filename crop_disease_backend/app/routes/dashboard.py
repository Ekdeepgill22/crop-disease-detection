# dashboard.py
from fastapi import APIRouter, Depends, Query
from typing import List
from app.models.diagnosis import DiagnosisResponse
from app.models.user import UserInDB
from app.controllers.dashboard_controller import DashboardController
from app.utils.auth_utils import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
dashboard_controller = DashboardController()

@router.get("/history", response_model=List[DiagnosisResponse])
async def get_diagnosis_history(
    limit: int = Query(50, description="Number of records to fetch", ge=1, le=100),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get user's diagnosis history"""
    return await dashboard_controller.get_user_diagnosis_history(current_user, limit)

@router.get("/statistics")
async def get_user_statistics(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get user's statistics and insights"""
    return await dashboard_controller.get_user_statistics(current_user)