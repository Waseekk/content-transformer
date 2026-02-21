"""
Pydantic Schemas for FormatConfig
Request/Response models for format configuration API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class FormatRules(BaseModel):
    """Rules for content formatting"""
    max_sentences_per_paragraph: Optional[int] = Field(None, description="Max sentences per paragraph (null = no limit)")
    quotation_on_last_line: bool = Field(False, description="Quotes must appear at end of paragraphs")
    quotation_must_end_paragraph: bool = Field(False, description="Quotes must end paragraphs")
    allow_subheads: bool = Field(True, description="Whether subheads are allowed")
    min_words: Optional[int] = Field(None, description="Minimum word count")
    max_words: Optional[int] = Field(None, description="Maximum word count")
    save_original_content: bool = Field(True, description="Whether to save original source content")


class FormatConfigBase(BaseModel):
    """Base schema for FormatConfig"""
    slug: str = Field(..., min_length=1, max_length=50, description="Unique identifier (e.g., 'hard_news')")
    display_name: str = Field(..., min_length=1, max_length=100, description="Display name (e.g., 'Hard News')")
    description: Optional[str] = Field(None, description="Description of the format")
    icon: str = Field("newspaper", description="Icon identifier")
    system_prompt: str = Field(..., min_length=10, description="AI system prompt for this format")
    temperature: float = Field(0.5, ge=0.0, le=2.0, description="AI temperature (0-2)")
    max_tokens: int = Field(4096, ge=100, le=16000, description="Max tokens for AI response")
    rules: Dict[str, Any] = Field(default_factory=dict, description="Format-specific rules")
    is_active: bool = Field(True, description="Whether format is active")


class FormatConfigCreate(FormatConfigBase):
    """Schema for creating a new format config"""
    pass


class FormatConfigUpdate(BaseModel):
    """Schema for updating a format config (all fields optional)"""
    slug: Optional[str] = Field(None, min_length=1, max_length=50)
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    system_prompt: Optional[str] = Field(None, min_length=10)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=16000)
    rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class FormatConfigResponse(FormatConfigBase):
    """Schema for format config response"""
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FormatConfigListResponse(BaseModel):
    """Schema for list of format configs"""
    formats: List[FormatConfigResponse]
    total: int


class FormatConfigForEnhancer(BaseModel):
    """Minimal format config for enhancer (used in user config endpoint)"""
    id: int
    slug: str
    display_name: str
    description: Optional[str] = None
    icon: str

    class Config:
        from_attributes = True
