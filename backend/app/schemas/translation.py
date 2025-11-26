"""
Translation Schemas
Pydantic models for translation-related operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TranslationRequest(BaseModel):
    """Request to translate content"""
    pasted_content: str = Field(..., description="Pasted webpage content to extract and translate", min_length=10)
    target_lang: str = Field(default='bn', description="Target language code (default: Bengali)")
    provider: Optional[str] = Field(default='openai', description="AI provider (openai)")
    model: Optional[str] = Field(default=None, description="Specific model name (optional)")


class TranslationResponse(BaseModel):
    """Translation result"""
    id: Optional[int] = None
    headline: str
    content: str
    author: Optional[str] = None
    date: Optional[str] = None
    original_headline: str
    translated_text: str
    tokens_used: int
    provider: str
    model: Optional[str] = None
    created_at: Optional[datetime] = None
    success: bool = True
    error: Optional[str] = None

    class Config:
        from_attributes = True


class TranslationListItem(BaseModel):
    """Translation list item"""
    id: int
    headline: str
    original_headline: str
    tokens_used: int
    provider: str
    created_at: datetime

    class Config:
        from_attributes = True


class TranslationListResponse(BaseModel):
    """Paginated translation list"""
    translations: List[TranslationListItem]
    total: int
    page: int
    per_page: int
    total_pages: int


class TranslationDeleteResponse(BaseModel):
    """Translation deletion result"""
    success: bool
    message: str
    deleted_id: int
