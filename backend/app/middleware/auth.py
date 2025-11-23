"""
Authentication Middleware
Dependencies for route protection and user authentication
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user

    Usage in routes:
        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user

    Args:
        credentials: Bearer token from Authorization header
        db: Database session

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    user = AuthService.get_current_user(db, token)
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user

    Args:
        current_user: User from get_current_user

    Returns:
        Active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to ensure user is admin

    Args:
        current_user: User from get_current_active_user

    Returns:
        Admin user

    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get user if authenticated, None otherwise

    Useful for routes that work differently for authenticated vs anonymous users

    Args:
        credentials: Optional bearer token
        db: Database session

    Returns:
        User if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        user = AuthService.get_current_user(db, token)
        return user
    except HTTPException:
        return None
