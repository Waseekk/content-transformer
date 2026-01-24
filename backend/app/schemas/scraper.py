"""
Scraper Schemas
Pydantic models for scraper-related operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ScraperRequest(BaseModel):
    """Request to trigger scraping"""
    sites: Optional[List[str]] = Field(default=None, description="Specific sites to scrape (if None, scrapes all user's enabled sites)")
    save_to_db: bool = Field(default=True, description="Save scraped articles to database")


class ArticleResponse(BaseModel):
    """Single article response"""
    id: Optional[int] = None
    source: str
    publisher: Optional[str] = None
    headline: str
    article_url: str
    published_time: Optional[str] = None
    country: Optional[str] = None
    view: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    scraped_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScraperStatus(BaseModel):
    """Scraper job status"""
    job_id: int
    status: str  # pending, running, completed, failed
    progress: int  # 0-100
    status_message: Optional[str] = None
    articles_count: Optional[int] = None
    current_site: Optional[str] = None
    sites_completed: Optional[int] = None
    total_sites: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class ScraperResult(BaseModel):
    """Scraper job result"""
    job_id: int
    status: str
    total_articles: int
    articles_by_site: Dict[str, int]
    articles: List[ArticleResponse]
    completed_at: Optional[datetime] = None


class SiteConfig(BaseModel):
    """Site configuration response"""
    name: str
    url: str
    enabled: bool
    description: Optional[str] = None


class UserSitesResponse(BaseModel):
    """User's available scraper sites"""
    enabled_sites: List[str]
    available_sites: List[SiteConfig]
    default_sites: List[str] = []
    use_custom_default: bool = False
    allowed_sites: List[str] = []  # Admin-restricted sites (empty = all)


class UpdateSitesRequest(BaseModel):
    """Request to update user's enabled sites"""
    enabled_sites: List[str] = Field(..., description="List of site names to enable")


class SetDefaultSitesRequest(BaseModel):
    """Request to set current sites as default"""
    set_as_default: bool = Field(default=True, description="Set current enabled sites as default")


class SitesUpdateResponse(BaseModel):
    """Response after updating sites"""
    success: bool
    enabled_sites: List[str]
    default_sites: List[str]
    use_custom_default: bool
    message: str


# Admin schemas for site assignment
class AdminAssignSitesRequest(BaseModel):
    """Admin request to assign allowed sites to a user"""
    allowed_sites: List[str] = Field(
        default=[],
        description="List of site names user can access. Empty list = access to ALL sites."
    )


class AdminUserSitesResponse(BaseModel):
    """Admin response for user's site configuration"""
    user_id: int
    username: str
    email: str
    allowed_sites: List[str]
    enabled_sites: List[str]
    all_available_sites: List[str]
    message: str = ""
