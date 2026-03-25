from pydantic import BaseModel, Field
from typing import Literal, Optional
import uuid


class AdminCreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    role: Literal["operator", "supervisor"]
    status: Literal["active", "inactive", "suspended"] = "active"


class AdminCreatedUserResponse(BaseModel):
    id: uuid.UUID
    username: str
    role: str
    status: str
    profile_id: uuid.UUID
    created_by: uuid.UUID


class AdminManagedUserResponse(BaseModel):
    id: uuid.UUID
    username: str
    role: str
    status: str
    profile_id: Optional[uuid.UUID] = None


class AdminUpdateUserRequest(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=100)
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)
    role: Optional[Literal["operator", "supervisor"]] = None
    status: Optional[Literal["active", "inactive", "suspended"]] = None
