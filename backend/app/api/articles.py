
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
from app.models.user_config import UserConfig
from app.models.enhancement import Enhancement
from app.models.translation import Translation
from app.middleware.auth import get_current_active_user
from app.schemas.scraper import ArticleResponse
from app.config import format_datetime

router = APIRouter()


def get_user_enabled_sites(db: Session, user_id: int) -> Optional[List[str]]:
    """Get user's enabled sites from UserConfig

    Returns:
        List[str]: List of enabled site names to filter by
        None: No filter should be applied (show all)
    """
    user_config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
    if user_config and user_config.enabled_sites:
        return user_config.enabled_sites
    # Return None to indicate no filter should be applied (show all)
    return None


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
    days: Optional[int] = Query(7, description="Number of days to look back (default: 7)"),
    latest_only: bool = Query(False, description="Show only articles from latest scraping run"),
    job_id: Optional[int] = Query(None, description="Filter by specific job ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's scraped articles (all unique articles by default)

    Query Parameters:
    - **search**: Search in headline (optional)
    - **sources**: Filter by source names (optional, multiple allowed)
    - **days**: Number of days to look back (default: 7, max: 7)
    - **latest_only**: Show only articles from latest scraping run (default: False)
    - **job_id**: Filter by specific job ID (optional)
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)

    Returns paginated list of scraped articles

    Requires: Bearer token in Authorization header
    """
    # Limit days to 7 max
    if days > 7:
        days = 7

    # Calculate date threshold
    date_threshold = datetime.utcnow() - timedelta(days=days)

    # Get user's enabled sites for filtering
    enabled_sites = get_user_enabled_sites(db, current_user.id)

    # Build base query with enabled sites filter
    query = db.query(Article).filter(
        Article.user_id == current_user.id,
        Article.scraped_at >= date_threshold
    )

    # Filter by enabled sites (None = no filter, [] = show nothing, list = filter)
    if enabled_sites is None:
        pass  # No filter - show all articles
    elif len(enabled_sites) == 0:
        query = query.filter(False)  # Empty list = show nothing
    else:
        query = query.filter(Article.source.in_(enabled_sites))

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
                "completed_at": format_datetime(latest_job.completed_at) if latest_job.completed_at else None,
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
    Get article statistics for current user (filtered by enabled sites)

    Returns:
    - Total articles count (from enabled sites only)
    - Articles by source
    - Articles in last 7/30 days
    - Most active sources

    Requires: Bearer token in Authorization header
    """
    from sqlalchemy import func

    # Get user's enabled sites
    enabled_sites = get_user_enabled_sites(db, current_user.id)

    # Base filter for all queries (None = no filter, [] = show nothing, list = filter)
    def apply_enabled_filter(query):
        if enabled_sites is None:
            return query  # No filter - show all
        elif len(enabled_sites) == 0:
            return query.filter(False)  # Empty list = show nothing
        else:
            return query.filter(Article.source.in_(enabled_sites))

    # Total articles (from enabled sites)
    total_articles = apply_enabled_filter(
        db.query(Article).filter(Article.user_id == current_user.id)
    ).count()

    # Articles in last 24 hours
    one_day_ago = datetime.utcnow() - timedelta(hours=24)
    recent_24h = apply_enabled_filter(
        db.query(Article).filter(
            Article.user_id == current_user.id,
            Article.scraped_at >= one_day_ago
        )
    ).count()

    # Articles in last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    last_7_days = apply_enabled_filter(
        db.query(Article).filter(
            Article.user_id == current_user.id,
            Article.scraped_at >= seven_days_ago
        )
    ).count()

    # Articles in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    last_30_days = apply_enabled_filter(
        db.query(Article).filter(
            Article.user_id == current_user.id,
            Article.scraped_at >= thirty_days_ago
        )
    ).count()

    # Articles by source (top 10, from enabled sites)
    by_source = apply_enabled_filter(
        db.query(
            Article.source,
            func.count(Article.id).label('count')
        ).filter(Article.user_id == current_user.id)
    ).group_by(Article.source).order_by(
        func.count(Article.id).desc()
    ).limit(10).all()

    # Count total unique sources (from enabled sites)
    total_sources = apply_enabled_filter(
        db.query(Article.source).filter(Article.user_id == current_user.id)
    ).distinct().count()

    return {
        "total_articles": total_articles,
        "recent_24h": recent_24h,
        "last_7_days": last_7_days,
        "last_30_days": last_30_days,
        "by_source": [
            {"source": source, "count": count}
            for source, count in by_source
        ],
        "total_sources": total_sources,
        "unique_sources": total_sources,  # Keep for backward compatibility
        "enabled_sites_count": len(enabled_sites)  # Show how many sites are enabled
    }


# ============================================================================
# ENHANCEMENT HISTORY (must be before /{article_id} to avoid route conflict)
# ============================================================================

@router.get("/enhancement-sessions", response_model=dict)
async def get_enhancement_sessions(
    days: Optional[int] = Query(7, description="Number of days to look back"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get enhancement sessions grouped by date/translation

    Returns enhancement sessions from the last N days, grouped by date and translation.
    Each session contains both hard_news and soft_news if available.

    Requires: Bearer token in Authorization header
    """
    from sqlalchemy import func, cast, Date

    # Bangladesh timezone offset (UTC+6)
    BD_OFFSET_HOURS = 6

    # Limit days to 7 max
    if days > 7:
        days = 7

    # Calculate date threshold
    date_threshold = datetime.utcnow() - timedelta(days=days)

    # Get all enhancements for this user within the date range
    enhancements = db.query(Enhancement).filter(
        Enhancement.user_id == current_user.id,
        Enhancement.created_at >= date_threshold
    ).order_by(Enhancement.created_at.desc()).all()

    # Group enhancements by date and translation_id
    sessions_by_date = {}

    for enhancement in enhancements:
        # Convert UTC time to Bangladesh time (UTC+6) for date grouping
        bd_time = enhancement.created_at + timedelta(hours=BD_OFFSET_HOURS)
        # Get the date string in Bangladesh timezone (YYYY-MM-DD)
        date_str = bd_time.strftime("%Y-%m-%d")

        # Get translation info if available
        translation = None
        english_content = None
        headline = None

        if enhancement.translation_id:
            translation = db.query(Translation).filter(
                Translation.id == enhancement.translation_id
            ).first()

            if translation:
                english_content = translation.original_text
                headline = translation.title or "Untitled"
        else:
            headline = enhancement.headline or "Direct Enhancement"

        # Create session key:
        # - If has translation_id: group by translation_id
        # - If direct enhancement: group by timestamp (minute precision) to group Hard+Soft generated together
        if enhancement.translation_id:
            session_key = f"{date_str}_{enhancement.translation_id}"
        else:
            # Group direct enhancements by minute (so Hard+Soft generated together are in same session)
            minute_key = bd_time.strftime("%Y%m%d%H%M")
            session_key = f"{date_str}_direct_{minute_key}"

        if date_str not in sessions_by_date:
            sessions_by_date[date_str] = {}

        if session_key not in sessions_by_date[date_str]:
            sessions_by_date[date_str][session_key] = {
                "translation_id": enhancement.translation_id,
                "headline": headline,
                "english_content": english_content,
                "hard_news": None,
                "soft_news": None,
                "created_at": enhancement.created_at.isoformat()
            }

        # Add the enhancement to the appropriate format slot
        enhancement_data = {
            "id": enhancement.id,
            "content": enhancement.content,
            "word_count": enhancement.word_count or len(enhancement.content.split()) if enhancement.content else 0,
            "tokens_used": enhancement.tokens_used,
            "created_at": enhancement.created_at.isoformat()
        }

        if enhancement.format_type and enhancement.format_type.startswith("hard_news"):
            sessions_by_date[date_str][session_key]["hard_news"] = enhancement_data
        elif enhancement.format_type and enhancement.format_type.startswith("soft_news"):
            sessions_by_date[date_str][session_key]["soft_news"] = enhancement_data

    # Convert to response format: list of dates with sessions
    result = []
    for date_str in sorted(sessions_by_date.keys(), reverse=True):
        sessions = list(sessions_by_date[date_str].values())
        # Sort sessions by created_at (most recent first)
        sessions.sort(key=lambda x: x["created_at"], reverse=True)
        result.append({
            "date": date_str,
            "sessions": sessions,
            "count": len(sessions)
        })

    return {
        "enhancement_sessions": result,
        "total_sessions": sum(len(d["sessions"]) for d in result),
        "date_range_days": days
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
    Get list of publishers from scraped articles (filtered by enabled sites)

    Returns unique publisher names with article counts

    Requires: Bearer token in Authorization header
    """
    from sqlalchemy import func

    # Get user's enabled sites
    enabled_sites = get_user_enabled_sites(db, current_user.id)

    # Get publishers with counts (human-readable names shown on article cards)
    # Exclude entries where publisher equals source (those are placeholder values)
    query = db.query(
        Article.publisher,
        func.count(Article.id).label('count')
    ).filter(
        Article.user_id == current_user.id,
        Article.publisher.isnot(None),
        Article.publisher != '',
        Article.publisher != Article.source  # Exclude placeholder values
    )

    # Filter by enabled sites (None = no filter, [] = show nothing, list = filter)
    if enabled_sites is None:
        pass  # No filter - show all sources
    elif len(enabled_sites) == 0:
        query = query.filter(False)  # Empty list = show nothing
    else:
        query = query.filter(Article.source.in_(enabled_sites))

    publishers = query.group_by(Article.publisher).order_by(
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
    days: Optional[int] = Query(7, description="Number of days to look back"),
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

    # Limit days to 7 max
    if days > 7:
        days = 7

    # Calculate date threshold
    date_threshold = datetime.utcnow() - timedelta(days=days)

    # Get the latest completed job ID (to mark in response)
    latest_job = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.job_type == "scrape",
        Job.status == "completed"
    ).order_by(Job.completed_at.desc()).first()

    latest_job_id = latest_job.id if latest_job else None

    # Query ALL completed scraping jobs (including the latest)
    jobs_query = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.job_type == "scrape",
        Job.status == "completed",
        Job.completed_at >= date_threshold
    )

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
            "completed_at": format_datetime(job.completed_at) if job.completed_at else None,
            "started_at": format_datetime(job.started_at) if job.started_at else None,
            "article_count": article_count or 0,
            "status_message": job.status_message,
            "result": job.result,
            "is_latest": job.id == latest_job_id,
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


@router.delete("/history/sessions/{job_id}", response_model=dict)
async def delete_session(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a single scraping session and its articles

    Path Parameters:
    - **job_id**: Job ID to delete

    Requires: Bearer token in Authorization header
    """
    # Find the job
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id,
        Job.job_type == "scrape"
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Count articles before deletion
    articles_count = db.query(Article).filter(Article.job_id == job_id).count()

    # Delete articles from this job
    db.query(Article).filter(Article.job_id == job_id).delete()

    # Delete the job
    db.delete(job)
    db.commit()

    return {
        "success": True,
        "message": f"Deleted session and {articles_count} articles",
        "deleted_job_id": job_id,
        "deleted_articles_count": articles_count
    }


@router.delete("/history/sessions", response_model=dict)
async def delete_all_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete ALL scraping history (full reset)

    This will delete:
    - All scraping jobs
    - All scraped articles

    Requires: Bearer token in Authorization header
    """
    # Count before deletion
    jobs_count = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.job_type == "scrape"
    ).count()

    articles_count = db.query(Article).filter(
        Article.user_id == current_user.id
    ).count()

    # Delete all articles for this user
    db.query(Article).filter(Article.user_id == current_user.id).delete()

    # Delete all scraping jobs for this user
    db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.job_type == "scrape"
    ).delete()

    db.commit()

    return {
        "success": True,
        "message": f"Deleted {jobs_count} sessions and {articles_count} articles",
        "deleted_jobs_count": jobs_count,
        "deleted_articles_count": articles_count
    }
