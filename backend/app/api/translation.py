"""
Translation API Endpoints
URL content extraction and Bengali translation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.translation import Translation
from app.middleware.auth import get_current_active_user
from app.services.content_extraction import ContentExtractor, ExtractionError
from app.core.translator import OpenAITranslator

router = APIRouter()

# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class ExtractAndTranslateRequest(BaseModel):
    """Request to extract content from URL and translate"""
    url: HttpUrl
    extraction_method: str = Field(default='auto', description="auto, trafilatura, or newspaper")
    save_to_history: bool = Field(default=True, description="Save translation to history")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.bbc.com/travel/article/20231201-travel-destination",
                "extraction_method": "auto",
                "save_to_history": True
            }
        }


class TranslateTextRequest(BaseModel):
    """Request to translate raw text"""
    text: str = Field(..., min_length=10, max_length=50000)
    title: Optional[str] = None
    save_to_history: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is a travel article about an amazing destination...",
                "title": "Amazing Travel Destination",
                "save_to_history": True
            }
        }


class TranslationResponse(BaseModel):
    """Translation result"""
    id: Optional[int] = None
    original_url: Optional[str] = None
    original_title: str
    original_text: str
    original_author: Optional[str] = None
    original_date: Optional[str] = None
    translated_text: str
    extraction_method: Optional[str] = None
    tokens_used: int
    tokens_remaining: int
    created_at: str

    class Config:
        from_attributes = True


class TranslationListResponse(BaseModel):
    """Paginated list of translations"""
    total: int
    page: int
    page_size: int
    translations: List[TranslationResponse]


# ============================================================================
# TRANSLATION ENDPOINTS
# ============================================================================

@router.post("/extract-and-translate", response_model=TranslationResponse, status_code=status.HTTP_201_CREATED)
async def extract_and_translate_from_url(
    request: ExtractAndTranslateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Extract content from URL and translate to Bengali

    **Workflow:**
    1. Extract article content from URL (using Trafilatura or Newspaper3k)
    2. Translate extracted content to Bengali using OpenAI
    3. Deduct tokens from user balance
    4. Save translation to database (if save_to_history=True)

    **Token Cost:** ~1000-3000 tokens depending on article length

    **Requirements:**
    - Valid JWT access token
    - Sufficient token balance (minimum 500 tokens)
    - Accessible URL with extractable content

    **Returns:**
    - Original content (title, text, author, date)
    - Bengali translation
    - Tokens used and remaining
    - Extraction method used
    """
    # Check token balance (minimum 500 tokens for extraction + translation)
    if not current_user.has_tokens(500):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient tokens. You have {current_user.tokens_remaining} tokens remaining. Minimum 500 tokens required."
        )

    # Extract content from URL
    try:
        extractor = ContentExtractor()
        extracted_content = await extractor.extract(
            url=str(request.url),
            method=request.extraction_method
        )
    except ExtractionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content extraction failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction error: {str(e)}"
        )

    # Check if content is substantial enough
    if len(extracted_content['text']) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extracted content is too short (minimum 100 characters)"
        )

    # Translate to Bengali using OpenAI
    try:
        translator = OpenAITranslator()
        translation_result = translator.simple_translate(extracted_content['text'])

        # Extract translation data
        if isinstance(translation_result, dict):
            translated_text = translation_result.get('translation', translation_result.get('content', ''))
            tokens_used = translation_result.get('tokens_used', 0)
        else:
            # Handle tuple response (legacy)
            translated_text, tokens_used = translation_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation error: {str(e)}"
        )

    # Deduct tokens from user
    if not current_user.deduct_tokens(tokens_used):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Failed to deduct tokens. Account may have been paused."
        )

    # Save to database
    translation_record = None
    if request.save_to_history:
        translation_record = Translation(
            user_id=current_user.id,
            original_url=str(request.url),
            title=extracted_content.get('title', ''),
            original_text=extracted_content['text'],
            author=extracted_content.get('author'),
            publish_date=extracted_content.get('date'),
            translated_text=translated_text,
            extraction_method=extracted_content['method'],
            tokens_used=tokens_used
        )
        db.add(translation_record)

    # Commit changes
    db.commit()
    if translation_record:
        db.refresh(translation_record)

    return TranslationResponse(
        id=translation_record.id if translation_record else None,
        original_url=str(request.url),
        original_title=extracted_content.get('title', ''),
        original_text=extracted_content['text'],
        original_author=extracted_content.get('author'),
        original_date=extracted_content.get('date'),
        translated_text=translated_text,
        extraction_method=extracted_content['method'],
        tokens_used=tokens_used,
        tokens_remaining=current_user.tokens_remaining,
        created_at=translation_record.created_at.isoformat() if translation_record else datetime.utcnow().isoformat()
    )


@router.post("/translate-text", response_model=TranslationResponse, status_code=status.HTTP_201_CREATED)
async def translate_raw_text(
    request: TranslateTextRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Translate raw text to Bengali (without URL extraction)

    **Use this when:**
    - You already have the content
    - Content is from a source that doesn't have a URL
    - You want to translate custom text

    **Token Cost:** ~500-2000 tokens depending on text length

    **Requirements:**
    - Valid JWT access token
    - Sufficient token balance
    - Text between 10-50,000 characters
    """
    # Check token balance
    if not current_user.has_tokens(100):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient tokens. You have {current_user.tokens_remaining} tokens remaining."
        )

    # Translate to Bengali
    try:
        translator = OpenAITranslator()
        translation_result = translator.simple_translate(request.text)

        if isinstance(translation_result, dict):
            translated_text = translation_result.get('translation', translation_result.get('content', ''))
            tokens_used = translation_result.get('tokens_used', 0)
        else:
            translated_text, tokens_used = translation_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation error: {str(e)}"
        )

    # Deduct tokens
    if not current_user.deduct_tokens(tokens_used):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Failed to deduct tokens"
        )

    # Save to database
    translation_record = None
    if request.save_to_history:
        translation_record = Translation(
            user_id=current_user.id,
            original_url=None,
            title=request.title or "Direct Text Translation",
            original_text=request.text,
            translated_text=translated_text,
            tokens_used=tokens_used
        )
        db.add(translation_record)

    db.commit()
    if translation_record:
        db.refresh(translation_record)

    return TranslationResponse(
        id=translation_record.id if translation_record else None,
        original_url=None,
        original_title=request.title or "Direct Text Translation",
        original_text=request.text,
        translated_text=translated_text,
        tokens_used=tokens_used,
        tokens_remaining=current_user.tokens_remaining,
        created_at=translation_record.created_at.isoformat() if translation_record else datetime.utcnow().isoformat()
    )


@router.get("/", response_model=TranslationListResponse)
async def list_translations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get translation history for current user

    Returns paginated list of all translations made by the user.
    Most recent translations first.
    """
    # Get total count
    total = db.query(Translation).filter(
        Translation.user_id == current_user.id
    ).count()

    # Get paginated translations
    translations = db.query(Translation).filter(
        Translation.user_id == current_user.id
    ).order_by(
        Translation.created_at.desc()
    ).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    # Map Translation models to TranslationResponse schema
    translation_responses = []
    for t in translations:
        translation_responses.append(TranslationResponse(
            id=t.id,
            original_url=t.original_url,
            original_title=t.title or "",
            original_text=t.original_text,
            original_author=t.author,
            original_date=t.publish_date,
            translated_text=t.translated_text,
            extraction_method=t.extraction_method,
            tokens_used=t.tokens_used,
            tokens_remaining=current_user.tokens_remaining,
            created_at=t.created_at.isoformat()
        ))

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "translations": translation_responses
    }


@router.get("/{translation_id}", response_model=TranslationResponse)
async def get_translation(
    translation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific translation by ID

    Only returns translations belonging to the current user.
    """
    translation = db.query(Translation).filter(
        Translation.id == translation_id,
        Translation.user_id == current_user.id
    ).first()

    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )

    # Map Translation model to TranslationResponse schema
    return TranslationResponse(
        id=translation.id,
        original_url=translation.original_url,
        original_title=translation.title or "",
        original_text=translation.original_text,
        original_author=translation.author,
        original_date=translation.publish_date,
        translated_text=translation.translated_text,
        extraction_method=translation.extraction_method,
        tokens_used=translation.tokens_used,
        tokens_remaining=current_user.tokens_remaining,
        created_at=translation.created_at.isoformat()
    )


@router.delete("/{translation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_translation(
    translation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a translation

    Only allows deletion of translations belonging to the current user.
    """
    translation = db.query(Translation).filter(
        Translation.id == translation_id,
        Translation.user_id == current_user.id
    ).first()

    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )

    db.delete(translation)
    db.commit()

    return None
