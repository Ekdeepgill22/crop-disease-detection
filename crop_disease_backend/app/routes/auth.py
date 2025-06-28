# auth.py
from fastapi import APIRouter, HTTPException, Depends
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.controllers.auth_controller import AuthController
from app.utils.auth_utils import get_current_active_user
from app.models.user import UserInDB

router = APIRouter(prefix="/auth", tags=["authentication"])
auth_controller = AuthController()

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    """Register a new farmer"""
    try:
        user = await auth_controller.register_user(user_data)
        
        # Auto-login after registration
        login_data = UserLogin(email=user_data.email, password=user_data.password)
        token = await auth_controller.login_user(login_data)
        
        return {
            "user": user,
            "access_token": token.access_token,
            "token_type": token.token_type
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=dict)
async def login(login_data: UserLogin):
    """Login farmer and get access token"""
    try:
        token = await auth_controller.login_user(login_data)
        
        # Get user data
        from app.database import get_database
        db = get_database()
        user = await db.users.find_one({"email": login_data.email})
        
        if user:
            user_response = UserResponse(
                id=str(user["_id"]),
                name=user["name"],
                email=user["email"],
                phone_number=user["phone_number"],
                region=user["region"],
                is_active=user["is_active"],
                created_at=user["created_at"]
            )
            
            return {
                "user": user_response,
                "access_token": token.access_token,
                "token_type": token.token_type
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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