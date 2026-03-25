from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.auth import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse, TokenResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint to authenticate users and return JWT token

    Args:
        login_data: Login credentials (username and password)
        db: Database session

    Returns:
        JWT access token and user information

    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user from database with role relationship
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.username == login_data.username)
    )
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )

    # Prepare user response
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        status=user.status.value,
        role_name=user.role.name if user.role else None,
        last_login=user.last_login
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user=user_response
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information

    Args:
        current_user: Current authenticated user from JWT token

    Returns:
        User information
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        status=current_user.status.value,
        role_name=current_user.role.name if current_user.role else None,
        last_login=current_user.last_login
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout endpoint (client should discard the token)

    Note: Since we're using stateless JWT, the actual token invalidation
    happens on the client side by removing the token from storage.

    Args:
        current_user: Current authenticated user

    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}
