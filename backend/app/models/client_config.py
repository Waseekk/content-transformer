"""
ClientConfig Model
Database model for per-client configuration (formats, UI settings, branding)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ClientConfig(Base):
    """
    ClientConfig model for storing per-client settings.
    Each client can have different allowed formats, UI settings, and branding.
    """
    __tablename__ = "client_configs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Identification
    name = Column(String(100), nullable=False)  # "Banglar Columbus", "Client B"
    slug = Column(String(50), unique=True, nullable=False, index=True)  # "banglar_columbus", "client_b"

    # Format Access
    allowed_format_ids = Column(JSON, default=list)  # [1, 2] - format IDs user can access
    default_format_id = Column(Integer, ForeignKey("format_configs.id"), nullable=True)

    # UI Settings (JSON)
    # Example: {
    #   "show_content_preview": true,
    #   "workflow_type": "full",  # "full" | "simple"
    #   "show_format_selection": true,
    #   "app_title": "Swiftor"
    # }
    ui_settings = Column(JSON, default=dict)

    # Custom Display Names (override format display_name per client)
    # Example: { "hard_news": "AI Content", "soft_news": "Feature Article" }
    display_overrides = Column(JSON, default=dict)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    default_format = relationship("FormatConfig", foreign_keys=[default_format_id])
    users = relationship("User", back_populates="client_config")

    def __repr__(self):
        return f"<ClientConfig(id={self.id}, slug={self.slug}, name={self.name})>"

    def to_dict(self, include_formats=False):
        """Convert to dictionary for API responses"""
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "allowed_format_ids": self.allowed_format_ids or [],
            "default_format_id": self.default_format_id,
            "ui_settings": self.ui_settings or {},
            "display_overrides": self.display_overrides or {},
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_formats and self.default_format:
            data["default_format"] = self.default_format.to_dict()

        return data

    def get_ui_setting(self, key: str, default=None):
        """Get a specific UI setting with fallback"""
        if not self.ui_settings:
            return default
        return self.ui_settings.get(key, default)

    def get_display_name_for_format(self, format_slug: str, original_name: str) -> str:
        """Get display name for a format (with override support)"""
        if self.display_overrides and format_slug in self.display_overrides:
            return self.display_overrides[format_slug]
        return original_name
