"""
Pydantic Schemas for ClientConfig
Request/Response models for client configuration API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.schemas.format_config import FormatConfigForEnhancer


class UISettings(BaseModel):
    """UI settings for client"""
    show_content_preview: bool = Field(True, description="Show content preview section")
    workflow_type: str = Field("full", description="Workflow type: 'full' or 'simple'")
    show_format_selection: bool = Field(True, description="Show format selection dropdown")
    app_title: str = Field("Swiftor", description="Custom app title")
    # NEW: Client UI customization settings
    hide_format_labels: bool = Field(False, description="Hide format type labels (হার্ড নিউজ/সফট নিউজ) everywhere")
    hide_main_content_export: bool = Field(False, description="Hide English source in Word export")
    download_prefix: str = Field("", description="Custom prefix for download filenames (empty = use client name)")


class ClientConfigBase(BaseModel):
    """Base schema for ClientConfig"""
    name: str = Field(..., min_length=1, max_length=100, description="Client name")
    slug: str = Field(..., min_length=1, max_length=50, description="Unique identifier")
    allowed_format_ids: List[int] = Field(default_factory=list, description="List of allowed format IDs")
    default_format_id: Optional[int] = Field(None, description="Default format ID")
    ui_settings: Dict[str, Any] = Field(default_factory=dict, description="UI configuration")
    display_overrides: Dict[str, str] = Field(default_factory=dict, description="Format display name overrides")
    is_active: bool = Field(True, description="Whether client config is active")


class ClientConfigCreate(ClientConfigBase):
    """Schema for creating a new client config"""
    pass


class ClientConfigUpdate(BaseModel):
    """Schema for updating a client config (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=50)
    allowed_format_ids: Optional[List[int]] = None
    default_format_id: Optional[int] = None
    ui_settings: Optional[Dict[str, Any]] = None
    display_overrides: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None


class ClientConfigResponse(ClientConfigBase):
    """Schema for client config response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientConfigListResponse(BaseModel):
    """Schema for list of client configs"""
    clients: List[ClientConfigResponse]
    total: int


class UserAssignClientRequest(BaseModel):
    """Schema for assigning a user to a client"""
    client_config_id: Optional[int] = Field(None, description="Client config ID (null to unassign)")


class UserClientConfigResponse(BaseModel):
    """Response for user's client configuration (used by frontend)"""
    client: Optional[ClientConfigResponse] = None
    formats: List[FormatConfigForEnhancer] = Field(default_factory=list)
    default_format: Optional[FormatConfigForEnhancer] = None
    ui_settings: Dict[str, Any] = Field(default_factory=dict)
    display_overrides: Dict[str, str] = Field(default_factory=dict)
