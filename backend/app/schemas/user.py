"""
User Schemas
Pydantic models for user-related operations
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str
    subscription_tier: str = "free"


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    subscription_tier: Optional[str] = None


class UserInDB(UserBase):
    """User as stored in database"""
    id: int
    is_active: bool
    is_admin: bool
    subscription_tier: str
    tokens_remaining: int
    tokens_total: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserConfigResponse(BaseModel):
    """User configuration response"""
    user_id: int
    enabled_sites: List[str]
    scraper_schedule_enabled: bool
    scraper_schedule_interval: int
    allowed_formats: List[str]
    preferred_provider: str
    preferred_model: str

    class Config:
        from_attributes = True
