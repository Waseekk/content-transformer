"""
Authentication Service
Business logic for user authentication and management
"""

from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.user_config import UserConfig
from app.schemas.auth import UserRegister, UserLogin, UserWithTokens
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from app.config import get_settings

settings = get_settings()


class AuthService:
    """Authentication service for user operations"""

    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> UserWithTokens:
        """
        Register a new user

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            User with JWT tokens

        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Get subscription tier config
        tier_config = settings.SUBSCRIPTION_TIERS.get(user_data.subscription_tier, settings.SUBSCRIPTION_TIERS["free"])

        # Create user
        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            subscription_tier=user_data.subscription_tier,
            tokens_remaining=tier_config["monthly_tokens"],
            tokens_total=tier_config["monthly_tokens"],
            last_token_reset=datetime.utcnow()
        )

        db.add(user)
        db.flush()  # Get user.id before commit

        # Create user config with default settings
        user_config = UserConfig(
            user_id=user.id,
            enabled_sites=[],  # Admin will assign sites
            allowed_formats=tier_config["formats"],
            preferred_provider="openai",
            preferred_model="gpt-4o-mini"
        )

        db.add(user_config)
        db.commit()
        db.refresh(user)

        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return UserWithTokens(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            subscription_tier=user.subscription_tier,
            tokens_remaining=user.tokens_remaining,
            tokens_total=user.tokens_total,
            created_at=user.created_at,
            last_login=user.last_login,
            access_token=access_token,
            refresh_token=refresh_token
        )

    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> UserWithTokens:
        """
        Authenticate user and generate tokens

        Args:
            db: Database session
            login_data: Login credentials

        Returns:
            User with JWT tokens

        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)

        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return UserWithTokens(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            subscription_tier=user.subscription_tier,
            tokens_remaining=user.tokens_remaining,
            tokens_total=user.tokens_total,
            created_at=user.created_at,
            last_login=user.last_login,
            access_token=access_token,
            refresh_token=refresh_token
        )

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Tuple[str, str]:
        """
        Generate new access token from refresh token

        Args:
            db: Database session
            refresh_token: Refresh token

        Returns:
            Tuple of (new_access_token, new_refresh_token)

        Raises:
            HTTPException: If refresh token is invalid
        """
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Generate new tokens
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return access_token, new_refresh_token

    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """
        Get current user from access token

        Args:
            db: Database session
            token: Access token

        Returns:
            User object

        Raises:
            HTTPException: If token is invalid or user not found
        """
        payload = verify_token(token, token_type="access")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

        return user

    @staticmethod
    def verify_admin(user: User) -> None:
        """
        Verify user has admin privileges

        Args:
            user: User object

        Raises:
            HTTPException: If user is not admin
        """
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
