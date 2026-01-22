"""
Google News Search API Endpoints
Search Google News with Playwright and return paginated results
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.schemas.search import (
    GoogleNewsSearchRequest,
    GoogleNewsSearchResponse,
    PaginatedSearchRequest,
    PaginatedSearchResponse,
    GoogleNewsResult
)
from app.services.google_news_search import get_google_news_searcher

router = APIRouter()


@router.post("/google-news", response_model=GoogleNewsSearchResponse)
async def search_google_news(
    request: GoogleNewsSearchRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Search Google News for articles matching the keyword.

    **Features:**
    - Searches Google News by keyword
    - Filters by time period (24h, 7d, 30d)
    - Results are cached for 5 minutes to prevent rate limiting
    - Detects and reports CAPTCHA challenges

    **Time Filters:**
    - `24h`: Past 24 hours (default)
    - `7d`: Past week
    - `30d`: Past month

    **Example:**
    ```json
    {
        "keyword": "sylhet tourism",
        "time_filter": "24h",
        "max_results": 50
    }
    ```

    **Requirements:**
    - Valid JWT access token
    - Playwright browser automation (server-side)

    **Returns:**
    - List of news articles with title, URL, source, time, and snippet
    - Search time in milliseconds
    - Cache status
    """
    try:
        searcher = get_google_news_searcher()
        result = await searcher.search(
            keyword=request.keyword,
            time_filter=request.time_filter,
            max_results=request.max_results,
            user_id=current_user.id
        )

        return GoogleNewsSearchResponse(
            success=result['success'],
            keyword=result['keyword'],
            total_results=result['total_results'],
            results=[GoogleNewsResult(**r) for r in result['results']],
            search_time_ms=result['search_time_ms'],
            cached=result.get('cached', False),
            error_message=result.get('error_message')
        )

    except RuntimeError as e:
        # Playwright not installed
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        print(f"Search error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/google-news/paginated", response_model=PaginatedSearchResponse)
async def get_paginated_results(
    keyword: str = Query(..., description="Search keyword"),
    time_filter: str = Query(default="24h", description="Time filter: 24h, 7d, 30d"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=50, description="Results per page"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get paginated results from a previous search.

    **Note:** You must first call POST `/google-news` to perform the search.
    Results are cached for 5 minutes.

    **Example:**
    ```
    GET /google-news/paginated?keyword=sylhet&time_filter=24h&page=1&limit=10
    ```

    **Returns:**
    - Paginated subset of cached search results
    - Total count and page info for pagination controls
    """
    try:
        searcher = get_google_news_searcher()
        result = searcher.get_paginated_results(
            keyword=keyword,
            time_filter=time_filter,
            page=page,
            limit=limit,
            user_id=current_user.id
        )

        return PaginatedSearchResponse(
            success=result['success'],
            results=[GoogleNewsResult(**r) for r in result['results']],
            total=result['total'],
            page=result['page'],
            limit=result['limit'],
            total_pages=result['total_pages'],
            keyword=result['keyword'],
            time_filter=result['time_filter'],
            cached=result.get('cached', False),
            error_message=result.get('error_message')
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get results: {str(e)}"
        )


@router.delete("/google-news/cache")
async def clear_search_cache(
    current_user: User = Depends(get_current_active_user)
):
    """
    Clear the search results cache.

    **Use this when:**
    - You want fresh results immediately
    - The cache seems stale
    """
    try:
        searcher = get_google_news_searcher()
        searcher.clear_cache()
        return {"success": True, "message": "Search cache cleared"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )
