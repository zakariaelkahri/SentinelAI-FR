from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class LoginRequest(BaseModel):
    """
    Login request schema
    """
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """
    Token response schema
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """
    User response schema
    """
    id: uuid.UUID
    username: str
    status: str
    role_name: Optional[str] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """
    Login response schema with token and user info
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
