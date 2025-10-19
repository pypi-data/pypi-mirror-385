"""
Authentication Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    """Login request schema"""
    username: Optional[str] = None
    email: Optional[str] = None
    password: str

class RegisterRequest(BaseModel):
    """Registration request schema"""
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    """User response schema"""
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    """Authentication response schema"""
    user: UserResponse
    token: str
