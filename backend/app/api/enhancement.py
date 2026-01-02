"""
Content Enhancement API Endpoints
Multi-format content generation from Bengali translations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.enhancement import Enhancement
from app.models.translation import Translation
from app.models.user_config import UserConfig
from app.middleware.auth import get_current_active_user
from shared.core.enhancer import ContentEnhancer, EnhancementResult

router = APIRouter()

# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class EnhanceRequest(BaseModel):
    """Request to enhance translated content"""
    translation_id: Optional[int] = Field(None, description="ID of saved translation to enhance")
    text: Optional[str] = Field(None, min_length=100, max_length=50000, description="Direct Bengali text to enhance")
    headline: Optional[str] = Field(None, description="Article headline/title")
    formats: List[str] = Field(default=["hard_news"], description="Formats to generate")

    class Config:
        json_schema_extra = {
            "example": {
                "translation_id": 1,
                "formats": ["hard_news", "soft_news"]
            }
        }


class FormatOutput(BaseModel):
    """Single format output"""
    format_type: str
    content: str
    headline: Optional[str] = None
    tokens_used: int


class EnhancementResponse(BaseModel):
    """Enhancement result"""
    id: Optional[int] = None
    translation_id: Optional[int] = None
    formats: List[FormatOutput]
    total_tokens_used: int
    tokens_remaining: int
    created_at: str

    class Config:
        from_attributes = True


class EnhancementListResponse(BaseModel):
    """Paginated list of enhancements"""
    total: int
    page: int
    page_size: int
    enhancements: List[dict]


class AvailableFormatsResponse(BaseModel):
    """List of available formats for user"""
    available_formats: List[dict]
    user_tier: str


# ============================================================================
# ENHANCEMENT ENDPOINTS
# ============================================================================

@router.get("/formats", response_model=AvailableFormatsResponse)
async def get_available_formats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get available content formats for current user

    Format access is based on subscription tier:
    - Free: hard_news only
    - Premium: hard_news, soft_news
    - Enterprise: All formats (hard_news, soft_news, newspaper, blog, facebook, instagram)
    """
    # Get user config or use defaults
    user_config = db.query(UserConfig).filter(
        UserConfig.user_id == current_user.id
    ).first()

    if user_config and user_config.allowed_formats:
        allowed_formats = user_config.allowed_formats
    else:
        # Use tier-based defaults
        allowed_formats = UserConfig.get_default_formats(current_user.subscription_tier)

    # Format definitions
    all_formats = {
        "hard_news": {
            "name": "Hard News",
            "description": "Professional factual news reporting (BC News style)",
            "icon": "📰",
            "tier_required": "free"
        },
        "soft_news": {
            "name": "Soft News",
            "description": "Literary travel feature article (BC News style)",
            "icon": "✈️",
            "tier_required": "premium"
        },
        "newspaper": {
            "name": "Newspaper Article",
            "description": "Formal newspaper-style article",
            "icon": "📜",
            "tier_required": "enterprise"
        },
        "blog": {
            "name": "Blog Post",
            "description": "Personal travel blog style",
            "icon": "📝",
            "tier_required": "enterprise"
        },
        "facebook": {
            "name": "Facebook Post",
            "description": "Social media post (100-150 words)",
            "icon": "📱",
            "tier_required": "enterprise"
        },
        "instagram": {
            "name": "Instagram Caption",
            "description": "Short caption with hashtags (50-100 words)",
            "icon": "📸",
            "tier_required": "enterprise"
        }
    }

    # Filter to allowed formats
    available = [
        {
            "format_type": fmt,
            **all_formats[fmt]
        }
        for fmt in allowed_formats
        if fmt in all_formats
    ]

    return {
        "available_formats": available,
        "user_tier": current_user.subscription_tier
    }


@router.post("/", response_model=EnhancementResponse, status_code=status.HTTP_201_CREATED)
async def enhance_content(
    request: EnhanceRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate multi-format content from Bengali translation

    **Input Options:**
    1. Provide `translation_id` to enhance a saved translation
    2. Provide direct `text` and `headline` to enhance custom content

    **Formats:**
    - hard_news: Professional news reporting
    - soft_news: Literary travel feature
    - newspaper: Formal newspaper article (Enterprise only)
    - blog: Personal blog style (Enterprise only)
    - facebook: Social media post (Enterprise only)
    - instagram: Caption with hashtags (Enterprise only)

    **Token Cost:** ~500-1500 tokens per format

    **Requirements:**
    - Valid JWT access token
    - Sufficient token balance
    - Access to requested formats (tier-based)
    """
    # Validate input
    if not request.translation_id and not request.text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either translation_id or text must be provided"
        )

    # Get content to enhance
    if request.translation_id:
        # Load from database
        translation = db.query(Translation).filter(
            Translation.id == request.translation_id,
            Translation.user_id == current_user.id
        ).first()

        if not translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation not found"
            )

        content_text = translation.translated_text
        headline_text = translation.original_title or "Travel News"
    else:
        # Use provided text
        content_text = request.text
        headline_text = request.headline or "Travel News"

    # Validate formats
    user_config = db.query(UserConfig).filter(
        UserConfig.user_id == current_user.id
    ).first()

    if user_config and user_config.allowed_formats:
        allowed_formats = user_config.allowed_formats
    else:
        allowed_formats = UserConfig.get_default_formats(current_user.subscription_tier)

    # Check if user has access to requested formats
    unauthorized_formats = [fmt for fmt in request.formats if fmt not in allowed_formats]
    if unauthorized_formats:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to formats: {', '.join(unauthorized_formats)}. Your tier ({current_user.subscription_tier}) allows: {', '.join(allowed_formats)}"
        )

    # Estimate token cost (rough estimate: 500-1500 per format)
    estimated_tokens = len(request.formats) * 1000

    if not current_user.has_tokens(estimated_tokens):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient tokens. Estimated cost: {estimated_tokens} tokens. You have: {current_user.tokens_remaining} tokens."
        )

    # Generate enhanced content
    try:
        # Use gpt-4o-mini for enhancement (same as translation)
        enhancer = ContentEnhancer(provider_name='openai', model='gpt-4o-mini')

        # Prepare article info dict
        article_info = {
            'headline': headline_text,
            'source': 'user_translation'
        }

        # Call enhancer with correct parameter names
        results_dict = enhancer.enhance_all_formats(
            translated_text=content_text,
            article_info=article_info,
            formats=request.formats
        )

        # Convert dict of results to list
        enhancement_results: List[EnhancementResult] = list(results_dict.values())

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhancement error: {str(e)}"
        )

    # Calculate total tokens used
    total_tokens = sum(result.tokens_used for result in enhancement_results)

    # Deduct tokens
    if not current_user.deduct_tokens(total_tokens):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Failed to deduct tokens"
        )

    # Save to database
    enhancement_records = []
    for result in enhancement_results:
        enhancement_record = Enhancement(
            user_id=current_user.id,
            translation_id=request.translation_id,
            format_type=result.format_type,
            content=result.content,
            headline=None,  # EnhancementResult doesn't provide headline
            tokens_used=result.tokens_used
        )
        db.add(enhancement_record)
        enhancement_records.append(enhancement_record)

    db.commit()
    for record in enhancement_records:
        db.refresh(record)

    # Build response
    format_outputs = [
        FormatOutput(
            format_type=result.format_type,
            content=result.content,
            headline=None,  # EnhancementResult doesn't provide headline
            tokens_used=result.tokens_used
        )
        for result in enhancement_results
    ]

    return EnhancementResponse(
        id=enhancement_records[0].id if enhancement_records else None,
        translation_id=request.translation_id,
        formats=format_outputs,
        total_tokens_used=total_tokens,
        tokens_remaining=current_user.tokens_remaining,
        created_at=enhancement_records[0].created_at.isoformat() if enhancement_records else datetime.utcnow().isoformat()
    )


@router.get("/", response_model=EnhancementListResponse)
async def list_enhancements(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    format_type: Optional[str] = Query(None, description="Filter by format type"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get enhancement history for current user

    Returns paginated list of all enhancements.
    Can filter by format type.
    """
    # Build query
    query = db.query(Enhancement).filter(
        Enhancement.user_id == current_user.id
    )

    if format_type:
        query = query.filter(Enhancement.format_type == format_type)

    # Get total count
    total = query.count()

    # Get paginated enhancements
    enhancements = query.order_by(
        Enhancement.created_at.desc()
    ).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    # Convert to dict for response
    enhancement_dicts = [
        {
            "id": e.id,
            "translation_id": e.translation_id,
            "format_type": e.format_type,
            "headline": e.headline,
            "content_preview": e.content[:200] + "..." if len(e.content) > 200 else e.content,
            "tokens_used": e.tokens_used,
            "created_at": e.created_at.isoformat()
        }
        for e in enhancements
    ]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "enhancements": enhancement_dicts
    }


@router.get("/{enhancement_id}")
async def get_enhancement(
    enhancement_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific enhancement by ID

    Returns full enhancement content.
    Only returns enhancements belonging to the current user.
    """
    enhancement = db.query(Enhancement).filter(
        Enhancement.id == enhancement_id,
        Enhancement.user_id == current_user.id
    ).first()

    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enhancement not found"
        )

    return {
        "id": enhancement.id,
        "translation_id": enhancement.translation_id,
        "format_type": enhancement.format_type,
        "headline": enhancement.headline,
        "content": enhancement.content,
        "tokens_used": enhancement.tokens_used,
        "created_at": enhancement.created_at.isoformat()
    }


@router.delete("/{enhancement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enhancement(
    enhancement_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an enhancement

    Only allows deletion of enhancements belonging to the current user.
    """
    enhancement = db.query(Enhancement).filter(
        Enhancement.id == enhancement_id,
        Enhancement.user_id == current_user.id
    ).first()

    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enhancement not found"
        )

    db.delete(enhancement)
    db.commit()

    return None
