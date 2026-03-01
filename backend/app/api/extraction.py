"""
URL Content Extraction API Endpoints
Extract article content from URLs using Playwright → Trafilatura → Newspaper3k cascade
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime
import asyncio

from app.database import get_db
from app.models.user import User
from app.models.translation import Translation
from app.middleware.auth import get_current_active_user
from app.services.content_extraction import ContentExtractor, ExtractionError
from app.core.translator import OpenAITranslator
from app.utils.language_detection import detect_language

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class URLExtractionRequest(BaseModel):
    """Request to extract content from URL"""
    url: HttpUrl = Field(..., description="The URL to extract content from")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.bbc.com/travel/article/example"
            }
        }


class URLExtractionResponse(BaseModel):
    """Response from URL extraction"""
    success: bool
    content: Optional[str] = None
    title: Optional[str] = None
    extraction_method: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "content": "The full article text extracted from the webpage...",
                "title": "Article Title",
                "extraction_method": "playwright",
                "error_message": None
            }
        }


class URLExtractAndTranslateResponse(BaseModel):
    """Response from combined URL extraction + translation"""
    success: bool
    english_content: Optional[str] = None
    bengali_content: Optional[str] = None
    title: Optional[str] = None
    extraction_method: Optional[str] = None
    tokens_used: int = 0
    tokens_remaining: int = 0
    error_message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "english_content": "The full article text in English...",
                "bengali_content": "সম্পূর্ণ প্রবন্ধ বাংলায়...",
                "title": "Article Title",
                "extraction_method": "playwright",
                "tokens_used": 1500,
                "tokens_remaining": 8500,
                "error_message": None
            }
        }


# ============================================================================
# EXTRACTION ENDPOINTS
# ============================================================================

@router.post("/url", response_model=URLExtractionResponse)
async def extract_from_url(
    request: URLExtractionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Extract article content from a URL.

    **Extraction Cascade:**
    1. **Playwright** (primary) - Handles JavaScript-rendered sites
    2. **Trafilatura** (fallback) - Fast, accurate for static content
    3. **Newspaper3k** (final fallback) - News-optimized extraction

    **Use this when:**
    - User wants to extract content from a URL before translation
    - The website has JavaScript-rendered content
    - Direct paste doesn't capture the full article

    **Requirements:**
    - Valid JWT access token
    - Accessible URL (not behind paywall or login)

    **Returns:**
    - success: Whether extraction succeeded
    - content: Extracted article text (if successful)
    - title: Article title (if found)
    - extraction_method: Which method succeeded
    - error_message: Error details (if failed)
    """
    try:
        extractor = ContentExtractor()
        result = await extractor.extract(
            url=str(request.url),
            method='auto'  # Use cascade: Playwright → Trafilatura → Newspaper3k
        )

        return URLExtractionResponse(
            success=True,
            content=result.get('text', ''),
            title=result.get('title', ''),
            extraction_method=result.get('method', 'unknown'),
            error_message=None
        )

    except ExtractionError as e:
        # Extraction failed with all methods
        return URLExtractionResponse(
            success=False,
            content=None,
            title=None,
            extraction_method=None,
            error_message="Failed to extract content, please contact admin if the problem persists.\n\nNB: Some websites may need manual extraction."
        )

    except Exception as e:
        # Unexpected error
        return URLExtractionResponse(
            success=False,
            content=None,
            title=None,
            extraction_method=None,
            error_message="Failed to extract content, please contact admin if the problem persists.\n\nNB: Some websites may need manual extraction."
        )


@router.post("/url-and-translate", response_model=URLExtractAndTranslateResponse)
async def extract_and_translate_from_url(
    request: URLExtractionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Extract article content from URL AND translate to Bengali in one step.

    **Flow:**
    1. Playwright/Trafilatura/Newspaper3k extracts clean content
    2. OpenAI translates to Bengali (no re-extraction needed)

    **Benefits:**
    - Single API call for URL → Bengali translation
    - Saves tokens (no double extraction)
    - Faster than extract + process separately

    **Requirements:**
    - Valid JWT access token
    - Sufficient token balance
    - Accessible URL (not behind paywall)

    **Returns:**
    - english_content: Clean extracted English text
    - bengali_content: Bengali translation
    - tokens_used/remaining: Token usage info
    """
    # Step 1: Extract content from URL
    try:
        extractor = ContentExtractor()
        extracted = await extractor.extract(
            url=str(request.url),
            method='auto'
        )
    except ExtractionError as e:
        return URLExtractAndTranslateResponse(
            success=False,
            error_message="Failed to extract content, please contact admin if the problem persists.\n\nNB: Some websites may need manual extraction."
        )
    except Exception as e:
        return URLExtractAndTranslateResponse(
            success=False,
            error_message="Failed to extract content, please contact admin if the problem persists.\n\nNB: Some websites may need manual extraction."
        )

    extracted_content = extracted.get('text', '')
    title = extracted.get('title', '')
    extraction_method = extracted.get('method', 'unknown')

    # Check content length
    if len(extracted_content) < 100:
        return URLExtractAndTranslateResponse(
            success=False,
            english_content=extracted_content,
            title=title,
            extraction_method=extraction_method,
            error_message="Extracted content is too short (minimum 100 characters)"
        )

    # Step 2: Detect language of extracted content
    detected_language = detect_language(extracted_content)

    # Step 3: Handle Bengali content - skip translation
    if detected_language == 'bn':
        # Bengali content: no translation needed, return as-is
        # Track translation usage (even though no tokens used)
        current_user.use_translation()

        # Save to history with bengali_passthrough marker
        translation_record = Translation(
            user_id=current_user.id,
            original_url=str(request.url),
            title=title,
            original_text=extracted_content,  # Bengali content
            translated_text=extracted_content,  # Same as original
            extraction_method=f"{extraction_method}_bengali_passthrough",
            tokens_used=0
        )
        db.add(translation_record)
        db.commit()

        return URLExtractAndTranslateResponse(
            success=True,
            english_content=extracted_content,  # Actually Bengali, but field name is fixed
            bengali_content=extracted_content,  # Same content
            title=title,
            extraction_method=f"{extraction_method}_bengali_passthrough",
            tokens_used=0,
            tokens_remaining=current_user.tokens_remaining,
            error_message=None
        )

    # Step 4: English content - proceed with translation
    # Check token balance
    estimated_tokens = max(500, int(len(extracted_content) / 4 * 1.5))

    # Auto-assign tokens if low
    auto_assigned = current_user.check_and_auto_assign_tokens()
    if auto_assigned > 0:
        db.commit()

    if not current_user.has_tokens(estimated_tokens):
        return URLExtractAndTranslateResponse(
            success=False,
            english_content=extracted_content,
            title=title,
            extraction_method=extraction_method,
            tokens_remaining=current_user.tokens_remaining,
            error_message=f"Insufficient tokens. Estimated: ~{estimated_tokens:,}, Available: {current_user.tokens_remaining:,}"
        )

    # Step 5: Translate English to Bengali (non-blocking with 60s cap)
    try:
        translator = OpenAITranslator()
        translation_result = await asyncio.wait_for(
            asyncio.to_thread(translator.translate_only, extracted_content),
            timeout=60.0
        )

        bengali_content = translation_result.get('translation', '')
        tokens_used = translation_result.get('tokens_used', 0)

    except asyncio.TimeoutError:
        return URLExtractAndTranslateResponse(
            success=False,
            english_content=extracted_content,
            title=title,
            extraction_method=extraction_method,
            error_message="Translation timed out. Please try again or paste the content directly."
        )
    except Exception as e:
        return URLExtractAndTranslateResponse(
            success=False,
            english_content=extracted_content,
            title=title,
            extraction_method=extraction_method,
            error_message=f"Translation failed: {str(e)}"
        )

    # Step 6: Deduct tokens
    if not current_user.deduct_tokens(tokens_used):
        return URLExtractAndTranslateResponse(
            success=False,
            english_content=extracted_content,
            title=title,
            extraction_method=extraction_method,
            error_message="Insufficient tokens for translation"
        )

    # Step 7: Track translation usage
    current_user.use_translation()

    # Step 8: Save to history
    translation_record = Translation(
        user_id=current_user.id,
        original_url=str(request.url),
        title=title,
        original_text=extracted_content,
        translated_text=bengali_content,
        extraction_method=extraction_method,
        tokens_used=tokens_used
    )
    db.add(translation_record)
    db.commit()

    return URLExtractAndTranslateResponse(
        success=True,
        english_content=extracted_content,
        bengali_content=bengali_content,
        title=title,
        extraction_method=extraction_method,
        tokens_used=tokens_used,
        tokens_remaining=current_user.tokens_remaining,
        error_message=None
    )
