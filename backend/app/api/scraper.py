"""
Scraper API Routes
Endpoints for news scraping operations
"""

import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, SessionLocal
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.schemas.scraper import (
    ScraperRequest,
    ScraperStatus,
    ScraperResult,
    UserSitesResponse,
    SiteConfig,
    ArticleResponse
)
from app.services.scraper_service import ScraperService
from app.config import format_datetime

router = APIRouter()


def run_scraper_background(user_id: int, job_id: int, sites: List[str] = None):
    """
    Background task wrapper that creates its own database session
    """
    db = SessionLocal()
    try:
        # Reload user and job from database
        user = db.query(User).filter(User.id == user_id).first()
        from app.models.job import Job
        job = db.query(Job).filter(Job.id == job_id).first()

        if user and job:
            ScraperService.run_scraper_sync(db, user, job, sites)
    finally:
        db.close()


@router.post("/run", response_model=ScraperStatus, status_code=status.HTTP_202_ACCEPTED)
async def trigger_scraping(
    request: ScraperRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Trigger news scraping for current user

    - **sites**: Optional list of specific sites to scrape (defaults to all user's enabled sites)
    - **save_to_db**: Whether to save scraped articles to database (default: true)

    Returns job ID and status for tracking progress
    """
    # Get user's enabled sites
    user_sites = ScraperService.get_user_sites(db, current_user)

    if not user_sites:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No sites enabled for your account. Please contact admin to configure scraping sources."
        )

    # Create job
    job = ScraperService.create_scraper_job(db, current_user, request.sites)

    # Run scraping in background (pass IDs only, not objects)
    background_tasks.add_task(
        run_scraper_background,
        user_id=current_user.id,
        job_id=job.id,
        sites=request.sites
    )

    return ScraperStatus(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        status_message=job.status_message,
        started_at=job.started_at
    )


@router.get("/status/{job_id}", response_model=ScraperStatus)
async def get_scraper_status(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get status of a scraping job

    Returns current status, progress, and any error messages
    """
    job = ScraperService.get_job_status(db, current_user, job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Parse result for additional info
    result = job.result or {}
    articles_by_site = result.get('articles_by_site', {})

    return ScraperStatus(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        status_message=job.status_message,
        articles_count=result.get('total_articles'),
        sites_completed=result.get('sites_completed', len(articles_by_site)),
        total_sites=result.get('total_sites', len(result.get('sites', []))),
        started_at=job.started_at,
        completed_at=job.completed_at,
        error=job.error
    )


@router.get("/result/{job_id}", response_model=ScraperResult)
async def get_scraper_result(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed results of a completed scraping job

    Includes list of scraped articles
    """
    job = ScraperService.get_job_status(db, current_user, job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not completed yet. Current status: {job.status}"
        )

    result = job.result or {}

    # Get articles from database for this job (articles scraped after job creation)
    from app.models.article import Article
    articles = db.query(Article).filter(
        Article.user_id == current_user.id,
        Article.scraped_at >= job.created_at
    ).limit(result.get('total_articles', 100)).all()

    return ScraperResult(
        job_id=job.id,
        status=job.status,
        total_articles=result.get('total_articles', 0),
        articles_by_site=result.get('articles_by_site', {}),
        articles=[ArticleResponse.model_validate(article) for article in articles],
        completed_at=job.completed_at
    )


@router.get("/sites", response_model=UserSitesResponse)
async def get_user_sites(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get list of scraper sites available to current user

    Returns:
    - **enabled_sites**: Sites currently enabled for the user
    - **available_sites**: All available sites in the system
    """
    # Get user's enabled sites
    enabled_sites = ScraperService.get_user_sites(db, current_user)

    # Get all available sites from configuration
    all_sites_config = ScraperService.get_all_available_sites()

    available_sites = [
        SiteConfig(
            name=site.get('name', 'Unknown'),
            url=site.get('url', ''),
            enabled=site.get('name') in enabled_sites,
            description=f"Source: {site.get('name')}"
        )
        for site in all_sites_config
    ]

    return UserSitesResponse(
        enabled_sites=enabled_sites,
        available_sites=available_sites
    )


@router.get("/jobs", response_model=List[ScraperStatus])
async def get_scraper_jobs(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get list of user's recent scraping jobs

    Query Parameters:
    - **limit**: Maximum number of jobs to return (default: 10)
    """
    jobs = ScraperService.get_user_jobs(db, current_user, job_type="scrape", limit=limit)

    return [
        ScraperStatus(
            job_id=job.id,
            status=job.status,
            progress=job.progress,
            status_message=job.status_message,
            articles_count=(job.result or {}).get('total_articles'),
            started_at=job.started_at,
            completed_at=job.completed_at,
            error=job.error
        )
        for job in jobs
    ]


@router.get("/status/{job_id}/stream")
async def stream_scraper_status(
    job_id: int,
    request: Request,
    token: str = None,
):
    """
    Server-Sent Events (SSE) endpoint for real-time scraper status updates.

    Streams status updates until the job completes or fails.
    Client should connect using EventSource API.

    Note: Token must be passed as query parameter since EventSource doesn't support headers.
    """
    from app.middleware.auth import decode_token

    # Validate token from query param (SSE doesn't support Authorization header)
    if not token:
        async def error_gen():
            yield f"data: {json.dumps({'error': 'Authentication required'})}\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream")

    try:
        payload = decode_token(token)
        user_email = payload.get("sub")
    except Exception:
        async def error_gen():
            yield f"data: {json.dumps({'error': 'Invalid token'})}\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream")

    # Get user_id from email
    db_init = SessionLocal()
    try:
        user = db_init.query(User).filter(User.email == user_email).first()
        if not user:
            async def error_gen():
                yield f"data: {json.dumps({'error': 'User not found'})}\n\n"
            return StreamingResponse(error_gen(), media_type="text/event-stream")
        user_id = user.id
    finally:
        db_init.close()

    async def event_generator():
        """Generate SSE events for job status updates"""
        last_status = None
        last_progress = -1

        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break

            # Create a new db session for each check
            db = SessionLocal()
            try:
                from app.models.job import Job
                job = db.query(Job).filter(
                    Job.id == job_id,
                    Job.user_id == user_id
                ).first()

                if not job:
                    # Job not found - send error and close
                    yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                    break

                # Parse result for additional info
                result = job.result or {}

                # Get real-time stats (updated during scraping)
                sites_completed = result.get('sites_completed', 0)
                site_stats = result.get('site_stats', {})
                current_site = result.get('current_site', '')
                articles_count = result.get('articles_count', 0)

                # After completion, use final stats
                if job.status == 'completed':
                    articles_by_site = result.get('articles_by_site', site_stats)
                    sites_completed = len(articles_by_site)
                    articles_count = result.get('total_articles', articles_count)

                # Build status data
                status_data = {
                    "job_id": job.id,
                    "status": job.status,
                    "progress": job.progress,
                    "status_message": job.status_message,
                    "current_site": current_site,
                    "articles_count": articles_count,
                    "articles_saved": result.get('articles_saved'),
                    "sites_completed": sites_completed,
                    "total_sites": result.get('total_sites', len(result.get('sites', []))),
                    "site_stats": site_stats,
                    "started_at": format_datetime(job.started_at) if job.started_at else None,
                    "completed_at": format_datetime(job.completed_at) if job.completed_at else None,
                    "error": job.error
                }

                # Only send update if status or progress changed
                if job.status != last_status or job.progress != last_progress:
                    yield f"data: {json.dumps(status_data)}\n\n"
                    last_status = job.status
                    last_progress = job.progress

                # If job is done (completed or failed), send final update and close
                if job.status in ["completed", "failed"]:
                    break

            finally:
                db.close()

            # Wait before next check (500ms for responsive updates)
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
