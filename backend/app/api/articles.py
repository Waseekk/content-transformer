
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
from app.models.job import Job
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
    search: Optional[str] = Query(None, description="Search in headline"),
    sources: Optional[List[str]] = Query(None, description="Filter by source names"),
    days: Optional[int] = Query(90, description="Number of days to look back (default: 90)"),
    latest_only: bool = Query(True, description="Show only articles from latest scraping run"),
    job_id: Optional[int] = Query(None, description="Filter by specific job ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's scraped articles

    Query Parameters:
    - **search**: Search in headline (optional)
    - **sources**: Filter by source names (optional, multiple allowed)
    - **days**: Number of days to look back (default: 90, max: 90)
    - **latest_only**: Show only articles from latest scraping run (default: True)
    - **job_id**: Filter by specific job ID (optional)
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)

    Returns paginated list of scraped articles

    Requires: Bearer token in Authorization header
    """
    # Limit days to 90 max
    if days > 90:
        days = 90

    # Calculate date threshold
    date_threshold = datetime.utcnow() - timedelta(days=days)

    # Build base query
    query = db.query(Article).filter(
        Article.user_id == current_user.id,
        Article.scraped_at >= date_threshold
    )

    # Filter by specific job_id if provided
    if job_id:
        query = query.filter(Article.job_id == job_id)
    # Otherwise filter by latest job only if latest_only is True
    elif latest_only:
        # Find the latest completed scraping job for this user
        latest_job = db.query(Job).filter(
            Job.user_id == current_user.id,
            Job.job_type == "scrape",
            Job.status == "completed"
        ).order_by(Job.completed_at.desc()).first()

        if latest_job:
            query = query.filter(Article.job_id == latest_job.id)

    # Filter by search term in headline
    if search:
        query = query.filter(Article.headline.ilike(f"%{search}%"))

    # Filter by publishers if specified (sources param contains publisher names)
    if sources:
        query = query.filter(Article.publisher.in_(sources))

    # Get total count
    total = query.count()

    # Paginate
    articles = query.order_by(
        Article.scraped_at.desc()
    ).offset((page - 1) * limit).limit(limit).all()

    # Calculate total pages
    total_pages = ceil(total / limit)

    # Get current job info if filtering by latest
    current_job_info = None
    if latest_only and not job_id:
        latest_job = db.query(Job).filter(
            Job.user_id == current_user.id,
            Job.job_type == "scrape",
            Job.status == "completed"
        ).order_by(Job.completed_at.desc()).first()
        if latest_job:
            current_job_info = {
                "job_id": latest_job.id,
                "completed_at": latest_job.completed_at.isoformat() if latest_job.completed_at else None,
                "status_message": latest_job.status_message
            }

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
        "limit": limit,
        "total_pages": total_pages,
        "date_range_days": days,
        "latest_only": latest_only,
        "current_job": current_job_info
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
    Get list of publishers from scraped articles

    Returns unique publisher names with article counts

    Requires: Bearer token in Authorization header
    """
    from sqlalchemy import func

    # Get publishers with counts (human-readable names shown on article cards)
    # Exclude entries where publisher equals source (those are placeholder values)
    publishers = db.query(
        Article.publisher,
        func.count(Article.id).label('count')
    ).filter(
        Article.user_id == current_user.id,
        Article.publisher.isnot(None),
        Article.publisher != '',
        Article.publisher != Article.source  # Exclude placeholder values
    ).group_by(Article.publisher).order_by(
        func.count(Article.id).desc()
    ).all()

    return {
        "sources": [
            {"source": publisher, "count": count}
            for publisher, count in publishers
        ],
        "total_sources": len(publishers)
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


@router.get("/history/sessions", response_model=dict)
async def get_scraping_sessions(
    days: Optional[int] = Query(90, description="Number of days to look back"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get scraping session history with article counts

    Returns list of past scraping jobs with article counts,
    grouped by date/time. Excludes the latest session (shown in Articles page).

    Requires: Bearer token in Authorization header
    """
    from sqlalchemy import func

    # Limit days to 90 max
    if days > 90:
        days = 90

    # Calculate date threshold
    date_threshold = datetime.utcnow() - timedelta(days=days)

    # Get the latest completed job ID (to exclude from history)
    latest_job = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.job_type == "scrape",
        Job.status == "completed"
    ).order_by(Job.completed_at.desc()).first()

    latest_job_id = latest_job.id if latest_job else None

    # Query all completed scraping jobs except the latest
    jobs_query = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.job_type == "scrape",
        Job.status == "completed",
        Job.completed_at >= date_threshold
    )

    # Exclude the latest job from history
    if latest_job_id:
        jobs_query = jobs_query.filter(Job.id != latest_job_id)

    # Get total count
    total = jobs_query.count()

    # Get paginated jobs
    jobs = jobs_query.order_by(
        Job.completed_at.desc()
    ).offset((page - 1) * limit).limit(limit).all()

    # Get article counts for each job
    sessions = []
    for job in jobs:
        article_count = db.query(func.count(Article.id)).filter(
            Article.job_id == job.id
        ).scalar()

        sessions.append({
            "job_id": job.id,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "article_count": article_count or 0,
            "status_message": job.status_message,
            "result": job.result
        })

    # Calculate total pages
    total_pages = ceil(total / limit) if limit > 0 else 0

    return {
        "sessions": sessions,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "date_range_days": days,
        "latest_job_id": latest_job_id
    }
