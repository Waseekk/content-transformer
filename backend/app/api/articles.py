
"""
Articles API Routes
Endpoints for viewing scraped articles
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from math import ceil

from app.database import get_db
from app.models.user import User
from app.models.article import Article
from app.middleware.auth import get_current_active_user
from app.schemas.scraper import ArticleResponse

router = APIRouter()


class ArticleListResponse:
    """Paginated article list response"""
    def __init__(self, articles, total, page, per_page):
        self.articles = articles
        self.total = total
        self.page = page
        self.per_page = per_page
        self.total_pages = ceil(total / per_page) if per_page > 0 else 0


@router.get("/", response_model=dict)
async def get_articles(
    source: Optional[str] = Query(None, description="Filter by source name"),
    days: Optional[int] = Query(7, description="Number of days to look back (default: 7)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's scraped articles

    Query Parameters:
    - **source**: Filter by source name (optional)
    - **days**: Number of days to look back (default: 7, max: 90)
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 20, max: 100)

    Returns paginated list of scraped articles

    Requires: Bearer token in Authorization header
    """
    # Limit days to 90 max
    if days > 90:
        days = 90

    # Calculate date threshold
    date_threshold = datetime.utcnow() - timedelta(days=days)

    # Build query
    query = db.query(Article).filter(
        Article.user_id == current_user.id,
        Article.scraped_at >= date_threshold
    )

    # Filter by source if specified
    if source:
        query = query.filter(Article.source == source)

    # Get total count
    total = query.count()

    # Paginate
    articles = query.order_by(
        Article.scraped_at.desc()
    ).offset((page - 1) * per_page).limit(per_page).all()

    # Calculate total pages
    total_pages = ceil(total / per_page)

    return {
        "articles": [
            ArticleResponse(
                id=a.id,
                source=a.source,
                publisher=a.publisher,
                headline=a.headline,
                article_url=a.article_url,
                published_time=a.published_time,
                country=a.country,
                view=a.view,
                extra_data=a.extra_data,
                scraped_at=a.scraped_at
            )
            for a in articles
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "date_range_days": days
    }


@router.get("/stats", response_model=dict)
async def get_article_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get article statistics for current user

    Returns:
    - Total articles count
    - Articles by source
    - Articles in last 7/30 days
    - Most active sources

    Requires: Bearer token in Authorization header
    """
    from sqlalchemy import func

    # Total articles
    total_articles = db.query(Article).filter(
        Article.user_id == current_user.id
    ).count()

    # Articles in last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    last_7_days = db.query(Article).filter(
        Article.user_id == current_user.id,
        Article.scraped_at >= seven_days_ago
    ).count()

    # Articles in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    last_30_days = db.query(Article).filter(
        Article.user_id == current_user.id,
        Article.scraped_at >= thirty_days_ago
    ).count()

    # Articles by source (top 10)
    by_source = db.query(
        Article.source,
        func.count(Article.id).label('count')
    ).filter(
        Article.user_id == current_user.id
    ).group_by(Article.source).order_by(
        func.count(Article.id).desc()
    ).limit(10).all()

    return {
        "total_articles": total_articles,
        "last_7_days": last_7_days,
        "last_30_days": last_30_days,
        "by_source": [
            {"source": source, "count": count}
            for source, count in by_source
        ],
        "unique_sources": len(by_source)
    }


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article_detail(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed article by ID

    Path Parameters:
    - **article_id**: Article ID

    Returns full article details

    Requires: Bearer token in Authorization header
    """
    article = db.query(Article).filter(
        Article.id == article_id,
        Article.user_id == current_user.id
    ).first()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )

    return ArticleResponse(
        id=article.id,
        source=article.source,
        publisher=article.publisher,
        headline=article.headline,
        article_url=article.article_url,
        published_time=article.published_time,
        country=article.country,
        view=article.view,
        extra_data=article.extra_data,
        scraped_at=article.scraped_at
    )


@router.get("/sources/list", response_model=dict)
async def get_article_sources(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get list of sources from scraped articles

    Returns unique source names with article counts

    Requires: Bearer token in Authorization header
    """
    from sqlalchemy import func

    # Get sources with counts
    sources = db.query(
        Article.source,
        func.count(Article.id).label('count')
    ).filter(
        Article.user_id == current_user.id
    ).group_by(Article.source).all()

    return {
        "sources": [
            {"name": source, "count": count}
            for source, count in sources
        ],
        "total_sources": len(sources)
    }


@router.delete("/{article_id}", response_model=dict)
async def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete article by ID

    Path Parameters:
    - **article_id**: Article ID

    Requires: Bearer token in Authorization header
    """
    article = db.query(Article).filter(
        Article.id == article_id,
        Article.user_id == current_user.id
    ).first()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )

    db.delete(article)
    db.commit()

    return {
        "success": True,
        "message": "Article deleted successfully",
        "deleted_id": article_id
    }
