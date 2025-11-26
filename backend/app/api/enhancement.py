"""
Enhancement API Routes
Endpoints for multi-format content generation
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, SessionLocal
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.schemas.enhancement import (
    EnhancementRequest,
    EnhancementJobResponse,
    EnhancementStatus,
    EnhancementResult,
    EnhancementListResponse,
    EnhancementListItem,
    EnhancementDetailResponse,
    FormatAccessResponse,
    FormatContent
)
from app.services.enhancement_service import EnhancementService

router = APIRouter()


def run_enhancement_background(
    user_id: int,
    job_id: int,
    translation_id: int,
    formats: List[str],
    provider: str,
    model: str = None,
    save_to_files: bool = True
):
    """
    Background task wrapper for enhancement
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        from app.models.job import Job
        job = db.query(Job).filter(Job.id == job_id).first()

        if user and job:
            EnhancementService.run_enhancement_sync(
                db=db,
                user=user,
                job=job,
                translation_id=translation_id,
                formats=formats,
                provider=provider,
                model=model,
                save_to_files=save_to_files
            )
    finally:
        db.close()


@router.post("/", response_model=EnhancementJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_enhancement(
    request: EnhancementRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate multi-format enhanced content from translation

    - **translation_id**: ID of the translation to enhance
    - **formats**: List of format types to generate (optional, defaults to all 6)
    - **provider**: AI provider (default: 'openai')
    - **model**: Specific model name (optional)
    - **save_to_files**: Save generated content to files (default: true)

    Available formats:
    - newspaper: Formal newspaper article
    - blog: Personal blog style
    - facebook: Social media post (100-150 words)
    - instagram: Caption with hashtags (50-100 words)
    - hard_news: Professional factual reporting (BC News style)
    - soft_news: Literary travel feature (BC News style)

    Returns job ID for tracking progress

    Requires: Bearer token in Authorization header
    """
    # Validate formats
    validation = EnhancementService.validate_formats(
        db=db,
        user=current_user,
        requested_formats=request.formats
    )

    if not validation['valid']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=validation['error']
        )

    # Check if translation exists and belongs to user
    from app.services.translation_service import TranslationService
    translation = TranslationService.get_translation_by_id(
        db=db,
        user=current_user,
        translation_id=request.translation_id
    )

    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )

    # Create job
    job = EnhancementService.create_enhancement_job(
        db=db,
        user=current_user,
        translation_id=request.translation_id,
        formats=request.formats
    )

    # Run enhancement in background
    background_tasks.add_task(
        run_enhancement_background,
        user_id=current_user.id,
        job_id=job.id,
        translation_id=request.translation_id,
        formats=request.formats,
        provider=request.provider,
        model=request.model,
        save_to_files=request.save_to_files
    )

    return EnhancementJobResponse(
        job_id=job.id,
        status=job.status,
        message="Enhancement job created. Processing in background...",
        formats_requested=request.formats
    )


@router.get("/status/{job_id}", response_model=EnhancementStatus)
async def get_enhancement_status(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get status of an enhancement job

    Path Parameters:
    - **job_id**: Enhancement job ID

    Returns current status, progress, and any error messages

    Requires: Bearer token in Authorization header
    """
    job = EnhancementService.get_job_status(db, current_user, job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    result = job.result or {}
    formats_completed = result.get('formats_completed', [])
    total_formats = len(result.get('formats', []))

    return EnhancementStatus(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        status_message=job.status_message,
        formats_completed=len(formats_completed),
        total_formats=total_formats,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error=job.error
    )


@router.get("/result/{job_id}", response_model=EnhancementResult)
async def get_enhancement_result(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed results of a completed enhancement job

    Path Parameters:
    - **job_id**: Enhancement job ID

    Returns all generated formats with content

    Requires: Bearer token in Authorization header
    """
    job = EnhancementService.get_job_status(db, current_user, job_id)

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
    translation_id = result.get('translation_id')

    # Get enhancements from database
    from app.models.enhancement import Enhancement
    enhancements = db.query(Enhancement).filter(
        Enhancement.user_id == current_user.id,
        Enhancement.translation_id == translation_id
    ).all()

    formats_dict = {}
    for enh in enhancements:
        formats_dict[enh.format_type] = FormatContent(
            format_type=enh.format_type,
            content=enh.content,
            tokens_used=enh.tokens_used,
            generated_at=enh.generated_at,
            success=True
        )

    return EnhancementResult(
        job_id=job.id,
        translation_id=translation_id,
        status=job.status,
        formats=formats_dict,
        total_tokens=result.get('total_tokens', 0),
        total_cost_usd=result.get('total_cost_usd', 0.0),
        completed_at=job.completed_at
    )


@router.get("/", response_model=EnhancementListResponse)
async def get_enhancements(
    translation_id: int = None,
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's enhancement history

    Query Parameters:
    - **translation_id**: Filter by translation ID (optional)
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 20, max: 100)

    Returns paginated list of enhancements

    Requires: Bearer token in Authorization header
    """
    if per_page > 100:
        per_page = 100

    result = EnhancementService.get_user_enhancements(
        db=db,
        user=current_user,
        translation_id=translation_id,
        page=page,
        per_page=per_page
    )

    return EnhancementListResponse(
        enhancements=[
            EnhancementListItem(
                id=e.id,
                translation_id=e.translation_id,
                format_type=e.format_type,
                tokens_used=e.tokens_used,
                generated_at=e.generated_at
            )
            for e in result['enhancements']
        ],
        total=result['total'],
        page=result['page'],
        per_page=result['per_page'],
        total_pages=result['total_pages']
    )


@router.get("/{enhancement_id}", response_model=EnhancementDetailResponse)
async def get_enhancement_detail(
    enhancement_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed enhancement by ID

    Path Parameters:
    - **enhancement_id**: Enhancement ID

    Returns full enhancement details including content

    Requires: Bearer token in Authorization header
    """
    enhancement = EnhancementService.get_enhancement_by_id(
        db=db,
        user=current_user,
        enhancement_id=enhancement_id
    )

    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enhancement not found"
        )

    return EnhancementDetailResponse(
        id=enhancement.id,
        translation_id=enhancement.translation_id,
        format_type=enhancement.format_type,
        content=enhancement.content,
        tokens_used=enhancement.tokens_used,
        provider=enhancement.provider,
        model=enhancement.model,
        generated_at=enhancement.generated_at
    )


@router.get("/formats/available", response_model=FormatAccessResponse)
async def get_available_formats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get formats available to current user based on subscription tier

    Returns list of format types user can access

    Requires: Bearer token in Authorization header
    """
    allowed_formats = EnhancementService.get_user_allowed_formats(db, current_user)

    tier_descriptions = {
        'free': 'Free tier: Basic formats (newspaper, blog, facebook, instagram)',
        'premium': 'Premium tier: All formats including BC News styles (hard_news, soft_news)'
    }

    return FormatAccessResponse(
        available_formats=allowed_formats,
        tier=current_user.subscription_tier,
        description=tier_descriptions.get(
            current_user.subscription_tier,
            f'{current_user.subscription_tier} tier'
        )
    )
