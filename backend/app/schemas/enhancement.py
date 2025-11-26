"""
Enhancement Schemas
Pydantic models for content enhancement operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class EnhancementRequest(BaseModel):
    """Request to generate enhanced content"""
    translation_id: int = Field(..., description="ID of the translation to enhance")
    formats: Optional[List[str]] = Field(
        default=['newspaper', 'blog', 'facebook', 'instagram', 'hard_news', 'soft_news'],
        description="List of format types to generate"
    )
    provider: Optional[str] = Field(default='openai', description="AI provider (openai)")
    model: Optional[str] = Field(default=None, description="Specific model name (optional)")
    save_to_files: Optional[bool] = Field(default=True, description="Save generated content to files")


class FormatContent(BaseModel):
    """Single format content"""
    format_type: str
    content: str
    tokens_used: int
    generated_at: datetime
    success: bool = True
    error: Optional[str] = None


class EnhancementJobResponse(BaseModel):
    """Enhancement job creation response"""
    job_id: int
    status: str
    message: str
    formats_requested: List[str]


class EnhancementStatus(BaseModel):
    """Enhancement job status"""
    job_id: int
    status: str  # pending, running, completed, failed
    progress: int  # 0-100
    status_message: Optional[str] = None
    current_format: Optional[str] = None
    formats_completed: int = 0
    total_formats: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class EnhancementResult(BaseModel):
    """Enhancement job result"""
    job_id: int
    translation_id: int
    status: str
    formats: Dict[str, FormatContent]
    total_tokens: int
    total_cost_usd: float
    completed_at: Optional[datetime] = None


class EnhancementListItem(BaseModel):
    """Enhancement list item"""
    id: int
    translation_id: int
    format_type: str
    tokens_used: int
    generated_at: datetime

    class Config:
        from_attributes = True


class EnhancementListResponse(BaseModel):
    """Paginated enhancement list"""
    enhancements: List[EnhancementListItem]
    total: int
    page: int
    per_page: int
    total_pages: int


class EnhancementDetailResponse(BaseModel):
    """Single enhancement detail"""
    id: int
    translation_id: int
    format_type: str
    content: str
    tokens_used: int
    provider: str
    model: Optional[str] = None
    generated_at: datetime

    class Config:
        from_attributes = True


class FormatAccessResponse(BaseModel):
    """User's available formats"""
    available_formats: List[str]
    tier: str
    description: str
