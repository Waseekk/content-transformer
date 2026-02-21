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
from app.models.password_reset import PasswordResetToken
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
from app.services.email import email_service

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
    hard_news_count: int
    soft_news_count: int
    other_formats_count: int
    total_articles_scraped: int
    total_scraping_sessions: int
    # Translation limits (visible to user)
    translations_used_this_month: int
    translations_remaining: int
    monthly_translation_limit: int
    translation_limit_exceeded: bool
    # Enhancement limits (visible to user)
    enhancements_used_this_month: int
    enhancements_remaining: int
    monthly_enhancement_limit: int
    enhancement_limit_exceeded: bool
    # Tokens (hidden from user, but kept for backward compatibility)
    tokens_used_this_month: int
    tokens_remaining: int
    most_used_format: Optional[str]
    average_tokens_per_translation: float


class RecentScrapingJob(BaseModel):
    """Recent scraping job response"""
    id: int
    status: str
    progress: int
    articles_count: int
    created_at: str
    completed_at: Optional[str]

    class Config:
        from_attributes = True


class AdminUserStats(BaseModel):
    """Admin view of user statistics"""
    user_id: int
    email: str
    full_name: Optional[str]
    subscription_tier: str
    is_active: bool
    is_admin: bool
    total_translations: int
    total_enhancements: int
    hard_news_count: int
    soft_news_count: int
    total_articles_scraped: int
    # Token info (admin only)
    tokens_used_this_month: int
    tokens_remaining: int
    monthly_token_limit: int
    # Enhancement limits
    enhancements_used_this_month: int
    enhancements_remaining: int
    monthly_enhancement_limit: int
    enhancement_limit_exceeded: bool
    # Translation limits
    translations_used_this_month: int
    translations_remaining: int
    monthly_translation_limit: int
    translation_limit_exceeded: bool
    created_at: str
    last_login: Optional[str]


class AdminSetTokensRequest(BaseModel):
    """Admin request to set user tokens"""
    user_id: int
    new_limit: int
    reset_used: bool = False


class AdminSetEnhancementsRequest(BaseModel):
    """Admin request to set user enhancement limit"""
    user_id: int
    new_limit: int
    reset_used: bool = False


class AdminSetTierRequest(BaseModel):
    """Admin request to set user subscription tier"""
    tier: str = Field(..., pattern="^(free|premium|enterprise)$")


class AdminToggleResponse(BaseModel):
    """Response for admin toggle operations"""
    success: bool
    message: str
    user_id: int
    new_status: bool


class AdminDeleteResponse(BaseModel):
    """Response for admin delete operations"""
    success: bool
    message: str
    user_id: int


class AdminAssignResponse(BaseModel):
    """Response for admin assignment operations"""
    success: bool
    message: str
    user_id: int
    new_value: int


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class MessageResponse(BaseModel):
    """Simple message response"""
    success: bool
    message: str


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


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset email

    - **email**: User's registered email address

    Always returns success to prevent email enumeration attacks.
    If the email exists, a password reset link will be sent.
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    if user and user.is_active:
        # Invalidate any existing tokens for this user
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False
        ).update({"used": True})

        # Create new reset token
        reset_token = PasswordResetToken.create_token(user.id)
        db.add(reset_token)
        db.commit()

        # Build reset URL
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"

        # Send email (fire and forget - don't block on email failure)
        try:
            await email_service.send_password_reset_email(
                to=user.email,
                reset_url=reset_url,
                user_name=user.full_name
            )
        except Exception:
            pass  # Log but don't expose email failures

    # Always return success to prevent email enumeration
    return {
        "success": True,
        "message": "If an account with that email exists, we've sent a password reset link."
    }


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using token from email

    - **token**: Password reset token from email link
    - **new_password**: New password (min 8 characters)
    """
    # Find token
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == request.token
    ).first()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link"
        )

    if not reset_token.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reset link has expired or already been used"
        )

    # Get user
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link"
        )

    # Update password
    user.hashed_password = get_password_hash(request.new_password)

    # Mark token as used
    reset_token.mark_used()

    db.commit()

    return {
        "success": True,
        "message": "Your password has been reset successfully. You can now log in with your new password."
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
    - Total translations, enhancements (with format breakdown)
    - Hard news, soft news, and other format counts
    - Token usage statistics
    - Most used format
    - Scraping session count
    """
    from app.models.translation import Translation
    from app.models.enhancement import Enhancement
    from app.models.article import Article
    from app.models.job import Job
    from sqlalchemy import func

    # Count translations
    total_translations = db.query(Translation).filter(
        Translation.user_id == current_user.id
    ).count()

    # Count enhancements by format type
    format_counts = db.query(
        Enhancement.format_type,
        func.count(Enhancement.id).label('count')
    ).filter(
        Enhancement.user_id == current_user.id
    ).group_by(
        Enhancement.format_type
    ).all()

    # Initialize counts
    hard_news_count = 0
    soft_news_count = 0
    other_formats_count = 0
    total_enhancements = 0

    for format_type, count in format_counts:
        total_enhancements += count
        if format_type and format_type.startswith("hard_news"):
            hard_news_count += count
        elif format_type and format_type.startswith("soft_news"):
            soft_news_count += count
        else:
            other_formats_count += count

    # Count articles
    total_articles = db.query(Article).filter(
        Article.user_id == current_user.id
    ).count()

    # Count scraping sessions (jobs with type 'scrape')
    total_scraping_sessions = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.job_type == "scrape"
    ).count()

    # Get most used format
    most_used_format = None
    if format_counts:
        most_used = max(format_counts, key=lambda x: x[1])
        most_used_format = most_used[0]

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
        "hard_news_count": hard_news_count,
        "soft_news_count": soft_news_count,
        "other_formats_count": other_formats_count,
        "total_articles_scraped": total_articles,
        "total_scraping_sessions": total_scraping_sessions,
        # Translation limits (visible to user)
        "translations_used_this_month": current_user.translations_used_this_month,
        "translations_remaining": current_user.translations_remaining,
        "monthly_translation_limit": current_user.monthly_translation_limit,
        "translation_limit_exceeded": current_user.is_translation_limit_exceeded(),
        # Enhancement limits (visible to user)
        "enhancements_used_this_month": current_user.enhancements_used_this_month,
        "enhancements_remaining": current_user.enhancements_remaining,
        "monthly_enhancement_limit": current_user.monthly_enhancement_limit,
        "enhancement_limit_exceeded": current_user.is_enhancement_limit_exceeded(),
        # Tokens (kept for backward compatibility, hidden in UI)
        "tokens_used_this_month": current_user.tokens_used,
        "tokens_remaining": current_user.tokens_remaining,
        "most_used_format": most_used_format,
        "average_tokens_per_translation": round(avg_tokens, 2)
    }


@router.get("/scraping-history", response_model=list[RecentScrapingJob])
async def get_scraping_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Get recent scraping sessions for current user

    Returns:
    - List of recent scraping jobs with article counts
    - Ordered by most recent first
    """
    from app.models.job import Job
    from app.models.article import Article
    from sqlalchemy import func

    # Get recent scraping jobs
    jobs = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.job_type == "scrape"
    ).order_by(Job.created_at.desc()).limit(limit).all()

    result = []
    for job in jobs:
        # Count articles for this job
        articles_count = db.query(Article).filter(
            Article.job_id == job.id
        ).count()

        result.append({
            "id": job.id,
            "status": job.status,
            "progress": job.progress,
            "articles_count": articles_count,
            "created_at": job.created_at.isoformat() if job.created_at else "",
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        })

    return result


# ============================================================================
# ADMIN ENDPOINTS
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


@router.get("/admin/users-stats", response_model=list[AdminUserStats])
async def get_all_users_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Get detailed usage statistics for all users

    Returns:
    - List of users with their usage stats
    - Translations, enhancements (hard/soft news), articles
    - Token usage information
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    from app.models.translation import Translation
    from app.models.enhancement import Enhancement
    from app.models.article import Article
    from sqlalchemy import func

    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []

    for user in users:
        # Count translations
        total_translations = db.query(Translation).filter(
            Translation.user_id == user.id
        ).count()

        # Count enhancements by format
        format_counts = db.query(
            Enhancement.format_type,
            func.count(Enhancement.id).label('count')
        ).filter(
            Enhancement.user_id == user.id
        ).group_by(
            Enhancement.format_type
        ).all()

        hard_news_count = 0
        soft_news_count = 0
        total_enhancements = 0

        for format_type, count in format_counts:
            total_enhancements += count
            if format_type and format_type.startswith("hard_news"):
                hard_news_count += count
            elif format_type and format_type.startswith("soft_news"):
                soft_news_count += count

        # Count articles
        total_articles = db.query(Article).filter(
            Article.user_id == user.id
        ).count()

        result.append({
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "subscription_tier": user.subscription_tier,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "total_translations": total_translations,
            "total_enhancements": total_enhancements,
            "hard_news_count": hard_news_count,
            "soft_news_count": soft_news_count,
            "total_articles_scraped": total_articles,
            "tokens_used_this_month": user.tokens_used,
            "tokens_remaining": user.tokens_remaining,
            "monthly_token_limit": user.monthly_token_limit,
            "enhancements_used_this_month": user.enhancements_used_this_month,
            "enhancements_remaining": user.enhancements_remaining,
            "monthly_enhancement_limit": user.monthly_enhancement_limit,
            "enhancement_limit_exceeded": user.is_enhancement_limit_exceeded(),
            "translations_used_this_month": user.translations_used_this_month,
            "translations_remaining": user.translations_remaining,
            "monthly_translation_limit": user.monthly_translation_limit,
            "translation_limit_exceeded": user.is_translation_limit_exceeded(),
            "created_at": user.created_at.isoformat() if user.created_at else "",
            "last_login": user.last_login.isoformat() if user.last_login else None
        })

    return result


@router.post("/admin/set-tokens", response_model=AdminAssignResponse)
async def admin_set_user_tokens(
    request: AdminSetTokensRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Set user's token limit

    - **user_id**: Target user ID
    - **new_limit**: New monthly token limit
    - **reset_used**: If True, reset tokens_used to 0
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    target_user = db.query(User).filter(User.id == request.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    target_user.admin_set_tokens(request.new_limit, request.reset_used)
    db.commit()

    return {
        "success": True,
        "message": f"Token limit updated to {request.new_limit}",
        "user_id": target_user.id,
        "new_value": target_user.tokens_remaining
    }


@router.post("/admin/set-enhancements", response_model=AdminAssignResponse)
async def admin_set_user_enhancements(
    request: AdminSetEnhancementsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Set user's enhancement limit

    - **user_id**: Target user ID
    - **new_limit**: New monthly enhancement limit
    - **reset_used**: If True, reset enhancements_used to 0
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    target_user = db.query(User).filter(User.id == request.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    target_user.admin_set_enhancement_limit(request.new_limit, request.reset_used)
    db.commit()

    return {
        "success": True,
        "message": f"Enhancement limit updated to {request.new_limit}",
        "user_id": target_user.id,
        "new_value": target_user.enhancements_remaining
    }


@router.post("/admin/auto-assign-tokens/{user_id}", response_model=AdminAssignResponse)
async def admin_trigger_auto_assign(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Trigger auto-assign tokens for a user (if below threshold)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    assigned = target_user.check_and_auto_assign_tokens()
    db.commit()

    if assigned > 0:
        return {
            "success": True,
            "message": f"Auto-assigned {assigned} tokens",
            "user_id": target_user.id,
            "new_value": target_user.tokens_remaining
        }
    else:
        return {
            "success": False,
            "message": "User has sufficient tokens, no auto-assign needed",
            "user_id": target_user.id,
            "new_value": target_user.tokens_remaining
        }


@router.post("/admin/users/{user_id}/toggle-active", response_model=AdminToggleResponse)
async def admin_toggle_user_active(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Toggle user's active status (activate/deactivate)

    - **user_id**: Target user ID

    Returns the new active status
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from deactivating themselves
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    # Toggle active status
    target_user.is_active = not target_user.is_active
    db.commit()

    action = "activated" if target_user.is_active else "deactivated"
    return {
        "success": True,
        "message": f"User {action} successfully",
        "user_id": target_user.id,
        "new_status": target_user.is_active
    }


@router.delete("/admin/users/{user_id}", response_model=AdminDeleteResponse)
async def admin_delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Delete a user and all their associated data

    - **user_id**: Target user ID

    This will cascade delete all user's:
    - Articles
    - Jobs
    - Translations
    - Enhancements
    - Token usage records
    - User config
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from deleting themselves
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user_email = target_user.email

    # Delete user (cascade will handle related records due to model relationships)
    db.delete(target_user)
    db.commit()

    return {
        "success": True,
        "message": f"User {user_email} and all associated data deleted successfully",
        "user_id": user_id
    }


@router.post("/admin/users/{user_id}/toggle-admin", response_model=AdminToggleResponse)
async def admin_toggle_admin_status(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Toggle user's admin privileges

    - **user_id**: Target user ID

    Returns the new admin status
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from removing their own admin status
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin status"
        )

    # Toggle admin status
    target_user.is_admin = not target_user.is_admin
    db.commit()

    action = "granted" if target_user.is_admin else "revoked"
    return {
        "success": True,
        "message": f"Admin privileges {action} successfully",
        "user_id": target_user.id,
        "new_status": target_user.is_admin
    }


@router.post("/admin/users/{user_id}/reset-monthly", response_model=AdminAssignResponse)
async def admin_reset_user_monthly(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Reset user's monthly usage counts (translations and enhancements)

    - **user_id**: Target user ID

    Resets translations_used and enhancements_used to 0, keeping limits unchanged.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Reset translation and enhancement counts only (NOT tokens)
    target_user.reset_monthly_translations()
    target_user.reset_monthly_enhancements()
    db.commit()

    return {
        "success": True,
        "message": "Monthly usage counts reset successfully",
        "user_id": target_user.id,
        "new_value": 0
    }


@router.post("/admin/users/{user_id}/set-tier", response_model=AdminAssignResponse)
async def admin_set_user_tier(
    user_id: int,
    request: AdminSetTierRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Set user's subscription tier

    - **user_id**: Target user ID
    - **tier**: New subscription tier (free, premium, enterprise)

    This will also update the user's token limits based on the tier
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    old_tier = target_user.subscription_tier
    target_user.upgrade_tier(request.tier)
    db.commit()

    return {
        "success": True,
        "message": f"Subscription tier changed from {old_tier} to {request.tier}",
        "user_id": target_user.id,
        "new_value": target_user.monthly_token_limit
    }
