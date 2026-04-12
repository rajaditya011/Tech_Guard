"""
HomeGuardian AI — Authentication Routes
"""

from fastapi import APIRouter, HTTPException, status, Depends

from models import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from auth import (
    register_user, authenticate_user,
    create_access_token, create_refresh_token,
    decode_token, get_current_user
)
from config import settings

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(request: RegisterRequest):
    """Register a new user (old_device or new_device)."""
    try:
        user = register_user(
            device_name=request.device_name,
            password=request.password,
            role=request.role.value,
            fcm_token=request.fcm_token
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Registration failed")

    access_token = create_access_token(user["id"], user["role"])
    refresh_token = create_refresh_token(user["id"], user["role"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user["role"],
        expires_in=settings.JWT_ACCESS_EXPIRY_MINUTES * 60
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate a user and return JWT tokens."""
    user = authenticate_user(request.device_name, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device name or password")

    access_token = create_access_token(user["id"], user["role"])
    refresh_token = create_refresh_token(user["id"], user["role"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user["role"],
        expires_in=settings.JWT_ACCESS_EXPIRY_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Refresh an access token using a refresh token."""
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    role = payload.get("role")

    new_access_token = create_access_token(user_id, role)
    new_refresh_token = create_refresh_token(user_id, role)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        role=role,
        expires_in=settings.JWT_ACCESS_EXPIRY_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """Get the current authenticated user's info."""
    return UserResponse(id=user["id"], role=user["role"], device_name=user["device_name"], created_at="")
