"""
Authentication API Endpoints
User registration, login, token management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_serializer

from app.database import get_db
from app.models.user import User
from app.middleware.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    get_current_active_user
)
from app.config import settings

router = APIRouter()

# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None
    subscription_tier: str = "free"

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
                "full_name": "John Doe",
                "subscription_tier": "free"
            }
        }


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
    """Refresh token request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User information response"""
    id: int
    email: str
    full_name: Optional[str]
    subscription_tier: str
    subscription_status: str
    tokens_remaining: int
    tokens_used: int
    monthly_token_limit: int
    is_active: bool
    is_admin: bool
    created_at: str

    @field_serializer('created_at')
    def serialize_datetime(self, value, _info):
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    class Config:
        from_attributes = True


class TokenWithUser(BaseModel):
    """JWT token response with user data"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenBalance(BaseModel):
    """Token balance response"""
    tokens_remaining: int
    tokens_used: int
    monthly_token_limit: int
    subscription_tier: str
    subscription_status: str
    reset_date: str


class UsageStats(BaseModel):
    """Usage statistics response"""
    total_translations: int
    total_enhancements: int
    total_articles_scraped: int
    tokens_used_this_month: int
    tokens_remaining: int
    most_used_format: Optional[str]
    average_tokens_per_translation: float


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user

    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **full_name**: Optional full name
    - **subscription_tier**: free, premium, or enterprise (default: free)

    Returns user information with initial token allocation
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        subscription_tier=user_data.subscription_tier,
        subscription_status="active"
    )

    # Set token limits based on tier
    if user_data.subscription_tier == "free":
        new_user.monthly_token_limit = settings.FREE_TIER_TOKENS
    elif user_data.subscription_tier == "premium":
        new_user.monthly_token_limit = settings.PREMIUM_TIER_TOKENS
    else:
        new_user.monthly_token_limit = settings.DEFAULT_MONTHLY_TOKENS

    new_user.tokens_remaining = new_user.monthly_token_limit

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "subscription_tier": new_user.subscription_tier,
        "subscription_status": new_user.subscription_status,
        "tokens_remaining": new_user.tokens_remaining,
        "tokens_used": new_user.tokens_used,
        "monthly_token_limit": new_user.monthly_token_limit,
        "is_active": new_user.is_active,
        "is_admin": new_user.is_admin,
        "created_at": new_user.created_at.isoformat() if new_user.created_at else ""
    }


@router.post("/login", response_model=TokenWithUser)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login (OAuth2 compatible)

    - **username**: User's email address
    - **password**: User's password

    Returns JWT access token, refresh token, and user data

    Note: Use email as username for Swagger UI authorization
    """
    # Find user by email (username field contains email)
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Create access and refresh tokens
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = create_refresh_token(
        data={"sub": user.email}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "subscription_tier": user.subscription_tier,
            "subscription_status": user.subscription_status,
            "tokens_remaining": user.tokens_remaining,
            "tokens_used": user.tokens_used,
            "monthly_token_limit": user.monthly_token_limit,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat() if user.created_at else ""
        }
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh JWT access token using refresh token

    - **refresh_token**: Valid refresh token

    Returns new access token and refresh token
    """
    try:
        payload = decode_token(token_data.refresh_token)
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user = db.query(User).filter(User.email == email).first()
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new tokens
        new_access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        new_refresh_token = create_refresh_token(
            data={"sub": user.email}
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information

    Requires valid JWT access token

    Returns complete user profile and token balance
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "subscription_tier": current_user.subscription_tier,
        "subscription_status": current_user.subscription_status,
        "tokens_remaining": current_user.tokens_remaining,
        "tokens_used": current_user.tokens_used,
        "monthly_token_limit": current_user.monthly_token_limit,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else ""
    }


@router.get("/token-balance", response_model=TokenBalance)
async def get_token_balance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current token balance

    Returns:
    - tokens_remaining: Available tokens for this month
    - tokens_used: Tokens consumed this month
    - monthly_token_limit: Total monthly allocation
    - subscription_tier: Current subscription level
    - subscription_status: active or paused
    - reset_date: When tokens will be reset
    """
    from datetime import datetime

    # Calculate next reset date (1st of next month)
    now = datetime.utcnow()
    if now.day >= settings.TOKEN_RESET_DAY:
        if now.month == 12:
            reset_date = datetime(now.year + 1, 1, settings.TOKEN_RESET_DAY)
        else:
            reset_date = datetime(now.year, now.month + 1, settings.TOKEN_RESET_DAY)
    else:
        reset_date = datetime(now.year, now.month, settings.TOKEN_RESET_DAY)

    return {
        "tokens_remaining": current_user.tokens_remaining,
        "tokens_used": current_user.tokens_used,
        "monthly_token_limit": current_user.monthly_token_limit,
        "subscription_tier": current_user.subscription_tier,
        "subscription_status": current_user.subscription_status,
        "reset_date": reset_date.isoformat()
    }


@router.get("/usage-stats", response_model=UsageStats)
async def get_usage_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed usage statistics for current user

    Returns:
    - Total translations, enhancements, articles scraped
    - Token usage statistics
    - Most used format
    - Average tokens per operation
    """
    from app.models.translation import Translation
    from app.models.enhancement import Enhancement
    from app.models.article import Article
    from sqlalchemy import func

    # Count translations
    total_translations = db.query(Translation).filter(
        Translation.user_id == current_user.id
    ).count()

    # Count enhancements
    total_enhancements = db.query(Enhancement).filter(
        Enhancement.user_id == current_user.id
    ).count()

    # Count articles
    total_articles = db.query(Article).filter(
        Article.user_id == current_user.id
    ).count()

    # Get most used format
    most_used_format_query = db.query(
        Enhancement.format_type,
        func.count(Enhancement.id).label('count')
    ).filter(
        Enhancement.user_id == current_user.id
    ).group_by(
        Enhancement.format_type
    ).order_by(
        func.count(Enhancement.id).desc()
    ).first()

    most_used_format = most_used_format_query[0] if most_used_format_query else None

    # Calculate average tokens per translation
    avg_tokens = 0.0
    if total_translations > 0:
        total_tokens_translations = db.query(
            func.sum(Translation.tokens_used)
        ).filter(
            Translation.user_id == current_user.id
        ).scalar() or 0
        avg_tokens = total_tokens_translations / total_translations

    return {
        "total_translations": total_translations,
        "total_enhancements": total_enhancements,
        "total_articles_scraped": total_articles,
        "tokens_used_this_month": current_user.tokens_used,
        "tokens_remaining": current_user.tokens_remaining,
        "most_used_format": most_used_format,
        "average_tokens_per_translation": round(avg_tokens, 2)
    }


# ============================================================================
# ADMIN ENDPOINTS (Optional - for future use)
# ============================================================================

@router.get("/admin/users")
async def list_all_users(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: List all users

    Requires admin privileges
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    users = db.query(User).all()
    return users
