"""
Authentication Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None
    subscription_tier: str = Field(default="free", pattern="^(free|premium)$")

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User data response"""
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    subscription_tier: str
    tokens_remaining: int
    tokens_total: int
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserWithTokens(UserResponse):
    """User response with JWT tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenBalance(BaseModel):
    """Token balance response"""
    tokens_remaining: int
    tokens_total: int
    subscription_tier: str
    next_reset: Optional[datetime]
    can_use_tokens: bool
