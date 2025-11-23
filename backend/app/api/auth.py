"""
Authentication API Routes
Endpoints for user registration, login, and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import UserRegister, UserLogin, UserWithTokens, Token, TokenRefresh, UserResponse, TokenBalance
from app.services.auth_service import AuthService
from app.services.token_service import TokenService
from app.middleware.auth import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserWithTokens, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user

    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters, must contain uppercase, lowercase, and digit
    - **full_name**: Optional full name
    - **subscription_tier**: Default is 'free', can be 'premium'

    Returns user object with access and refresh tokens
    """
    return AuthService.register_user(db, user_data)


@router.post("/login", response_model=UserWithTokens)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password

    - **email**: User's email address
    - **password**: User's password

    Returns user object with access and refresh tokens
    """
    return AuthService.login_user(db, login_data)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token

    - **refresh_token**: Valid refresh token

    Returns new access and refresh tokens
    """
    access_token, refresh_token = AuthService.refresh_access_token(db, token_data.refresh_token)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information

    Requires: Bearer token in Authorization header

    Returns user profile information
    """
    return current_user


@router.get("/token-balance", response_model=TokenBalance)
async def get_token_balance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's token balance

    Requires: Bearer token in Authorization header

    Returns:
    - **tokens_remaining**: Available tokens
    - **tokens_total**: Total monthly allocation
    - **subscription_tier**: User's subscription level
    - **next_reset**: Next token reset date
    - **can_use_tokens**: Whether user can make API calls
    """
    balance = TokenService.get_token_balance(current_user)

    return TokenBalance(
        tokens_remaining=balance["tokens_remaining"],
        tokens_total=balance["tokens_total"],
        subscription_tier=balance["subscription_tier"],
        next_reset=balance["next_reset"],
        can_use_tokens=balance["can_use_tokens"]
    )


@router.get("/usage-stats")
async def get_usage_statistics(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get token usage statistics

    Requires: Bearer token in Authorization header

    Query Parameters:
    - **days**: Number of days to look back (default: 30)

    Returns detailed usage statistics by operation
    """
    return TokenService.get_usage_stats(db, current_user, days)
