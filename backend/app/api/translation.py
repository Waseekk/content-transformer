"""
Translation API Routes
Endpoints for content translation operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.schemas.translation import (
    TranslationRequest,
    TranslationResponse,
    TranslationListResponse,
    TranslationListItem,
    TranslationDeleteResponse
)
from app.services.translation_service import TranslationService

router = APIRouter()


@router.post("/", response_model=TranslationResponse, status_code=status.HTTP_201_CREATED)
async def translate_content(
    request: TranslationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Translate pasted webpage content to Bengali

    - **pasted_content**: Full webpage content pasted by user
    - **target_lang**: Target language code (default: 'bn' for Bengali)
    - **provider**: AI provider (default: 'openai')
    - **model**: Specific model name (optional)

    This endpoint:
    1. Extracts article content from pasted text
    2. Translates to natural Bangladeshi Bengali
    3. Deducts tokens from user balance
    4. Saves translation to database
    5. Returns translated content with metadata

    Requires: Bearer token in Authorization header
    """
    result = TranslationService.translate_content(
        db=db,
        user=current_user,
        pasted_content=request.pasted_content,
        target_lang=request.target_lang,
        provider=request.provider,
        model=request.model
    )

    if not result.get('success', False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get('error', 'Translation failed')
        )

    return TranslationResponse(
        id=result.get('translation_id'),
        headline=result.get('headline', ''),
        content=result.get('content', ''),
        author=result.get('author'),
        date=result.get('date'),
        original_headline=result.get('original_headline', ''),
        translated_text=result.get('translated_text', ''),
        tokens_used=result.get('tokens_used', 0),
        provider=result.get('provider', 'openai'),
        model=result.get('model'),
        created_at=result.get('created_at'),
        success=True
    )


@router.get("/", response_model=TranslationListResponse)
async def get_translations(
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's translation history

    Query Parameters:
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 20, max: 100)

    Returns paginated list of translations

    Requires: Bearer token in Authorization header
    """
    if per_page > 100:
        per_page = 100

    result = TranslationService.get_user_translations(
        db=db,
        user=current_user,
        page=page,
        per_page=per_page
    )

    return TranslationListResponse(
        translations=[
            TranslationListItem(
                id=t.id,
                headline=(t.extra_data or {}).get('headline', 'Untitled'),
                original_headline=(t.extra_data or {}).get('original_headline', ''),
                tokens_used=t.tokens_used,
                provider=t.provider,
                created_at=t.created_at
            )
            for t in result['translations']
        ],
        total=result['total'],
        page=result['page'],
        per_page=result['per_page'],
        total_pages=result['total_pages']
    )


@router.get("/{translation_id}", response_model=TranslationResponse)
async def get_translation_detail(
    translation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed translation by ID

    Path Parameters:
    - **translation_id**: Translation ID

    Returns full translation details including content

    Requires: Bearer token in Authorization header
    """
    translation = TranslationService.get_translation_by_id(
        db=db,
        user=current_user,
        translation_id=translation_id
    )

    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )

    extra_data = translation.extra_data or {}

    return TranslationResponse(
        id=translation.id,
        headline=extra_data.get('headline', ''),
        content=extra_data.get('content', ''),
        author=extra_data.get('author'),
        date=extra_data.get('date'),
        original_headline=extra_data.get('original_headline', ''),
        translated_text=translation.translated_text,
        tokens_used=translation.tokens_used,
        provider=translation.provider,
        model=translation.model,
        created_at=translation.created_at,
        success=True
    )


@router.delete("/{translation_id}", response_model=TranslationDeleteResponse)
async def delete_translation(
    translation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete translation and associated enhancements

    Path Parameters:
    - **translation_id**: Translation ID

    This will also delete all enhancements created from this translation

    Requires: Bearer token in Authorization header
    """
    result = TranslationService.delete_translation(
        db=db,
        user=current_user,
        translation_id=translation_id
    )

    if not result.get('success', False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get('error', 'Translation not found')
        )

    return TranslationDeleteResponse(
        success=True,
        message=result.get('message', 'Translation deleted'),
        deleted_id=result.get('deleted_id', translation_id)
    )
