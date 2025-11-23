"""
User Configuration Model
Stores user-specific settings (sites, formats, schedules)
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class UserConfig(Base):
    """User configuration model"""

    __tablename__ = "user_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # Scraper configuration
    enabled_sites = Column(JSON, default=list)  # List of site names user has access to
    scraper_schedule_enabled = Column(Boolean, default=False)
    scraper_schedule_interval = Column(Integer, default=24)  # Hours

    # Format permissions (which formats user can generate)
    allowed_formats = Column(JSON, default=list)  # List of format types

    # AI preferences
    preferred_provider = Column(String(50), default="openai")
    preferred_model = Column(String(100), default="gpt-4o-mini")

    # Additional settings
    settings = Column(JSON, default=dict)  # Flexible settings storage

    # Relationships
    user = relationship("User", back_populates="config")

    def __repr__(self):
        return f"<UserConfig for User {self.user_id}>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "user_id": self.user_id,
            "enabled_sites": self.enabled_sites,
            "scraper_schedule_enabled": self.scraper_schedule_enabled,
            "scraper_schedule_interval": self.scraper_schedule_interval,
            "allowed_formats": self.allowed_formats,
            "preferred_provider": self.preferred_provider,
            "preferred_model": self.preferred_model,
            "settings": self.settings,
        }

    def has_format_access(self, format_type: str) -> bool:
        """Check if user has access to a specific format"""
        return format_type in self.allowed_formats

    def has_site_access(self, site_name: str) -> bool:
        """Check if user has access to a specific site"""
        return site_name in self.enabled_sites

    @staticmethod
    def get_default_formats(subscription_tier: str) -> list:
        """Get default formats for a subscription tier"""
        from app.config import get_settings
        settings = get_settings()

        tier_config = settings.SUBSCRIPTION_TIERS.get(subscription_tier, {})
        return tier_config.get("formats", ["hard_news", "soft_news"])
