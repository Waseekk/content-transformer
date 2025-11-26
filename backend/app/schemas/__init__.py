"""
Pydantic Schemas
"""

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    TokenRefresh,
    UserResponse,
    UserWithTokens,
    TokenBalance
)

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserConfigResponse
)

from app.schemas.translation import (
    TranslationRequest,
    TranslationResponse,
    TranslationListItem,
    TranslationListResponse,
    TranslationDeleteResponse
)

from app.schemas.enhancement import (
    EnhancementRequest,
    EnhancementJobResponse,
    EnhancementStatus,
    EnhancementResult,
    EnhancementListItem,
    EnhancementListResponse,
    EnhancementDetailResponse,
    FormatAccessResponse,
    FormatContent
)

from app.schemas.scraper import (
    ScraperRequest,
    ScraperStatus,
    ScraperResult,
    UserSitesResponse,
    SiteConfig,
    ArticleResponse
)

__all__ = [
    # Auth schemas
    "UserRegister",
    "UserLogin",
    "Token",
    "TokenRefresh",
    "UserResponse",
    "UserWithTokens",
    "TokenBalance",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserConfigResponse",
    # Translation schemas
    "TranslationRequest",
    "TranslationResponse",
    "TranslationListItem",
    "TranslationListResponse",
    "TranslationDeleteResponse",
    # Enhancement schemas
    "EnhancementRequest",
    "EnhancementJobResponse",
    "EnhancementStatus",
    "EnhancementResult",
    "EnhancementListItem",
    "EnhancementListResponse",
    "EnhancementDetailResponse",
    "FormatAccessResponse",
    "FormatContent",
    # Scraper schemas
    "ScraperRequest",
    "ScraperStatus",
    "ScraperResult",
    "UserSitesResponse",
    "SiteConfig",
    "ArticleResponse",
]
