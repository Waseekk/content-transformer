"""
Search Schemas
Pydantic models for Google News search operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GoogleNewsSearchRequest(BaseModel):
    """Request to search Google News"""
    keyword: str = Field(..., description="Search keyword (e.g., 'sylhet', 'bangladesh tourism')")
    time_filter: str = Field(
        default="24h",
        description="Time filter: '24h' (past day), '7d' (past week), '30d' (past month)"
    )
    max_results: int = Field(default=50, ge=1, le=100, description="Maximum results to fetch")

    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "sylhet",
                "time_filter": "24h",
                "max_results": 50
            }
        }


class GoogleNewsResult(BaseModel):
    """Single Google News search result"""
    title: str
    url: str
    source: Optional[str] = None
    published_time: Optional[str] = None
    snippet: Optional[str] = None

    class Config:
        from_attributes = True


class GoogleNewsSearchResponse(BaseModel):
    """Response from Google News search"""
    success: bool
    keyword: str
    total_results: int
    results: List[GoogleNewsResult]
    search_time_ms: int
    cached: bool = False
    error_message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "keyword": "sylhet",
                "total_results": 15,
                "results": [
                    {
                        "title": "Tourism in Sylhet sees growth",
                        "url": "https://example.com/article",
                        "source": "The Daily Star",
                        "published_time": "2 hours ago",
                        "snippet": "Sylhet tourism industry shows promising growth..."
                    }
                ],
                "search_time_ms": 1250,
                "cached": False,
                "error_message": None
            }
        }


class PaginatedSearchRequest(BaseModel):
    """Request for paginated search results"""
    keyword: str
    time_filter: str = "24h"
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=50)


class PaginatedSearchResponse(BaseModel):
    """Paginated search results response"""
    success: bool
    results: List[GoogleNewsResult]
    total: int
    page: int
    limit: int
    total_pages: int
    keyword: str
    time_filter: str
    cached: bool = False
    error_message: Optional[str] = None
