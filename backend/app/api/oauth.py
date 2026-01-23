"""
Google OAuth API Endpoints
Sign in with Google functionality
"""

from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import logging

from app.database import get_db
from app.models.user import User
from app.middleware.auth import create_access_token, create_refresh_token
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

# Initialize OAuth
oauth = OAuth()

# Register Google OAuth only if credentials are configured
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


@router.get("/google")
async def google_login(request: Request):
    """
    Initiate Google OAuth login
    Redirects user to Google's login page
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
        )

    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback
    Creates or updates user account and returns JWT tokens via HTTP-only cookies
    """
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )

        email = user_info.get('email')
        full_name = user_info.get('name', '')
        google_id = user_info.get('sub')
        picture = user_info.get('picture', '')

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()

        if user:
            # Update existing user with Google info
            user.google_id = google_id
            user.avatar_url = picture
            if not user.full_name and full_name:
                user.full_name = full_name
            user.last_login = datetime.utcnow()
            db.commit()
        else:
            # Create new user
            # Use special marker for OAuth users - prevents password login
            user = User(
                email=email,
                full_name=full_name,
                google_id=google_id,
                avatar_url=picture,
                hashed_password="!OAUTH_USER_NO_PASSWORD!",
                subscription_tier="free",
                subscription_status="active",
                tokens_remaining=settings.FREE_TIER_TOKENS,
                monthly_token_limit=settings.FREE_TIER_TOKENS,
                is_active=True,
                is_verified=True,  # Google accounts are pre-verified
                last_login=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Create JWT tokens
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(
            data={"sub": user.email}
        )

        # Redirect to frontend with tokens in HTTP-only cookies
        frontend_url = settings.FRONTEND_URL or "http://localhost:5173"
        response = RedirectResponse(url=f"{frontend_url}/auth/callback?oauth=success")

        # Set secure cookies for tokens
        # In production (HTTPS), use secure=True; for localhost development, secure=False
        is_production = not frontend_url.startswith("http://localhost")
        response.set_cookie(
            key="oauth_access_token",
            value=access_token,
            httponly=True,
            secure=is_production,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        response.set_cookie(
            key="oauth_refresh_token",
            value=refresh_token,
            httponly=True,
            secure=is_production,
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed. Please try again."
        )


@router.get("/exchange-tokens")
async def exchange_oauth_tokens(request: Request):
    """
    Exchange OAuth cookies for tokens.
    Frontend calls this after OAuth callback to get tokens and store in localStorage.
    Then clears the HTTP-only cookies.
    """
    access_token = request.cookies.get("oauth_access_token")
    refresh_token = request.cookies.get("oauth_refresh_token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No OAuth tokens found. Please login again."
        )

    # Return tokens and clear cookies
    from fastapi.responses import JSONResponse
    response = JSONResponse(content={
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    })

    # Clear the HTTP-only cookies after exchange
    response.delete_cookie(key="oauth_access_token")
    response.delete_cookie(key="oauth_refresh_token")

    return response


@router.get("/status")
async def oauth_status():
    """
    Check if Google OAuth is configured
    """
    google_configured = bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)

    return {
        "google": {
            "configured": google_configured,
            "login_url": "/api/oauth/google" if google_configured else None
        }
    }
