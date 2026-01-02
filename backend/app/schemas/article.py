
"""
Article Schemas
Pydantic models for article operations
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ArticleBase(BaseModel):
    """Base article schema"""
    source: str
    publisher: Optional[str] = None
    headline: str
    article_url: str
    published_time: Optional[str] = None
    country: Optional[str] = None
    view: Optional[str] = None


class ArticleCreate(ArticleBase):
    """Article creation schema"""
    user_id: int
    extra_data: Optional[Dict[str, Any]] = None


class ArticleInDB(ArticleBase):
    """Article as stored in database"""
    id: int
    user_id: int
    extra_data: Optional[Dict[str, Any]] = None
    scraped_at: datetime

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """Paginated article list response"""
    total: int
    page: int
    page_size: int
    total_pages: int
    articles: list[ArticleInDB]


class ArticleFilterParams(BaseModel):
    """Article filtering parameters"""
    source: Optional[str] = None
    publisher: Optional[str] = None
    country: Optional[str] = None
    view: Optional[str] = None
    search: Optional[str] = None  # Search in headline
    page: int = 1
    page_size: int = 20
