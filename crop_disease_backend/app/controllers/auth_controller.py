# auth_controller.py
from datetime import timedelta
from fastapi import HTTPException, status
from app.database import get_database
from app.models.user import UserCreate, UserLogin, UserInDB, UserResponse, Token
from app.utils.auth_utils import get_password_hash, verify_password, create_access_token
from app.config import settings
from pymongo.errors import DuplicateKeyError

# ...existing code...
class AuthController:
    def __init__(self):
        pass  # Remove self.db = get_database()

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        try:
            db = get_database()  # Get DB here
            hashed_password = get_password_hash(user_data.password)
            user_dict = user_data.dict(exclude={"password"})
            user_dict["hashed_password"] = hashed_password
            user_in_db = UserInDB(**user_dict)
            result = await db.users.insert_one(user_in_db.dict(by_alias=True))
            created_user = await db.users.find_one({"_id": result.inserted_id})
            return UserResponse(**created_user, id=str(created_user["_id"]))
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or phone number already registered"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )

    async def login_user(self, login_data: UserLogin) -> Token:
        """Authenticate user and return token"""
        db = get_database()  # Get DB here
        user = await db.users.find_one({"email": login_data.email})
        if not user or not verify_password(login_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
# ...existing code...