"""Authentication router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserResponse
from services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.
    
    - **username**: Unique username (3-50 characters)
    - **password**: Password (6-100 characters)
    """
    # Check if username already exists
    existing_user = await AuthService.get_user_by_username(db, request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "USERNAME_EXISTS",
                "message": "Username already registered",
            }
        )
    
    # Create user
    user = await AuthService.create_user(db, request.username, request.password)
    await db.commit()
    
    return user


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Login and get JWT access token.
    
    - **username**: Your username
    - **password**: Your password
    """
    # Find user
    user = await AuthService.get_user_by_username(db, request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_CREDENTIALS",
                "message": "Incorrect username or password",
            }
        )
    
    # Verify password
    if not AuthService.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_CREDENTIALS",
                "message": "Incorrect username or password",
            }
        )
    
    # Create token
    access_token = AuthService.create_access_token(user.id, user.username)
    
    return AuthResponse(access_token=access_token)
