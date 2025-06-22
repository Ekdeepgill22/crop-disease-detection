# auth.py
from fastapi import APIRouter, HTTPException, Depends
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.controllers.auth_controller import AuthController
from app.utils.auth_utils import get_current_active_user
from app.models.user import UserInDB

router = APIRouter(prefix="/auth", tags=["authentication"])
auth_controller = AuthController()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new farmer"""
    return await auth_controller.register_user(user_data)

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login farmer and get access token"""
    return await auth_controller.login_user(login_data)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        region=current_user.region,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )