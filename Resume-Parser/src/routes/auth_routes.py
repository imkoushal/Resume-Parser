"""
auth_routes.py - Authentication endpoints.

POST /auth/register  — create a new user account
POST /auth/login     — authenticate and receive a JWT token
GET  /auth/me        — get the current authenticated user's info
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.auth import create_access_token, get_current_user
from src.models.response_models import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from src.services import user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest):
    """Register a new user and return a JWT token."""
    try:
        user = await user_service.create_user(
            email=body.email,
            password=body.password,
            full_name=body.full_name,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    token = create_access_token(data={"sub": user["email"]})
    return TokenResponse(access_token=token)


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    """Authenticate a user and return a JWT token."""
    user = await user_service.authenticate_user(
        email=body.email,
        password=body.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={"sub": user["email"]})
    return TokenResponse(access_token=token)


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Return the current authenticated user's information."""
    user = await user_service.get_user_by_email(current_user["sub"])

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        email=user["email"],
        full_name=user["full_name"],
    )
