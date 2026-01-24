"""
UserConfig Model
Database model for user-specific configuration and preferences
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, JSON, Boolean
from sqlalchemy.orm import relationship
from typing import List

from app.database import Base


class UserConfig(Base):
    """
    User configuration model for storing user preferences and settings
    """
    __tablename__ = "user_configs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key (one-to-one with User)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Scraper settings
    enabled_sites = Column(JSON, default=list, nullable=False)  # List of currently enabled site names
    default_sites = Column(JSON, default=list, nullable=False)  # User's custom default sites (applied on login)
    use_custom_default = Column(Boolean, default=False, nullable=False)  # If True, use default_sites on login
    allowed_sites = Column(JSON, default=list, nullable=False)  # Admin-controlled: sites user can access (empty = all)
    scraper_schedule_enabled = Column(Boolean, default=False, nullable=False)
    scraper_schedule_interval = Column(Integer, default=6, nullable=False)  # hours

    # Format access control
    allowed_formats = Column(JSON, default=list, nullable=False)  # List of allowed format types

    # Preferences
    default_language = Column(String(10), default="bn", nullable=False)  # Bengali
    default_provider = Column(String(50), default="openai", nullable=False)
    default_model = Column(String(100), nullable=True)

    # Additional settings (JSON for flexibility)
    settings = Column(JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="config")

    def __repr__(self):
        return f"<UserConfig(user_id={self.user_id}, sites={len(self.enabled_sites)}, formats={len(self.allowed_formats)})>"

    @staticmethod
    def get_default_formats(subscription_tier: str = "free") -> List[str]:
        """
        Get default allowed formats based on subscription tier

        Args:
            subscription_tier: User subscription tier (free, premium, enterprise)

        Returns:
            List[str]: List of allowed format types
        """
        format_mapping = {
            "free": ["hard_news", "soft_news"],  # All formats available
            "premium": ["hard_news", "soft_news"],  # All formats available
            "enterprise": ["hard_news", "soft_news"],  # All formats available
        }

        return format_mapping.get(subscription_tier, format_mapping["free"])

    @staticmethod
    def get_default_sites() -> List[str]:
        """
        Get default enabled sites for new users

        Returns:
            List[str]: List of default site names
        """
        # Start with a few popular sites that don't require Selenium
        # These names must match exactly with 'name' field in sites_config.json
        return [
            "tourism_review",
            "independent_travel",
            "newsuk_travel",
            "skift",
            "unwto",
            "phocuswire"
        ]

    def add_site(self, site_name: str):
        """Add a site to enabled sites"""
        if site_name not in self.enabled_sites:
            sites = self.enabled_sites.copy() if isinstance(self.enabled_sites, list) else []
            sites.append(site_name)
            self.enabled_sites = sites

    def remove_site(self, site_name: str):
        """Remove a site from enabled sites"""
        if isinstance(self.enabled_sites, list) and site_name in self.enabled_sites:
            sites = self.enabled_sites.copy()
            sites.remove(site_name)
            self.enabled_sites = sites

    def add_format(self, format_type: str):
        """Add a format to allowed formats"""
        if format_type not in self.allowed_formats:
            formats = self.allowed_formats.copy() if isinstance(self.allowed_formats, list) else []
            formats.append(format_type)
            self.allowed_formats = formats

    def remove_format(self, format_type: str):
        """Remove a format from allowed formats"""
        if isinstance(self.allowed_formats, list) and format_type in self.allowed_formats:
            formats = self.allowed_formats.copy()
            formats.remove(format_type)
            self.allowed_formats = formats

    def has_format_access(self, format_type: str) -> bool:
        """Check if user has access to a specific format"""
        return format_type in (self.allowed_formats or [])

    def set_enabled_sites(self, sites: List[str]):
        """Set the list of enabled sites"""
        self.enabled_sites = sites.copy() if sites else []

    def set_as_default(self):
        """Set current enabled_sites as user's default"""
        self.default_sites = self.enabled_sites.copy() if self.enabled_sites else []
        self.use_custom_default = True

    def clear_custom_default(self):
        """Clear custom default and use system default"""
        self.default_sites = []
        self.use_custom_default = False

    def apply_default_sites(self):
        """Apply default sites (called on login)"""
        if self.use_custom_default and self.default_sites:
            self.enabled_sites = self.default_sites.copy()
        else:
            self.enabled_sites = self.get_default_sites()

    def set_allowed_sites(self, sites: List[str]):
        """Set the list of allowed sites (admin only)"""
        self.allowed_sites = sites.copy() if sites else []

    def get_filtered_available_sites(self, all_available_sites: List[str]) -> List[str]:
        """
        Get sites filtered by allowed_sites restriction.

        Args:
            all_available_sites: All system-available site names

        Returns:
            Filtered list: if allowed_sites is empty, returns all;
            otherwise returns intersection
        """
        allowed = self.allowed_sites or []
        if not allowed:
            # Empty allowed_sites = user can access ALL sites
            return all_available_sites
        # Return only sites that are both available and allowed
        return [s for s in all_available_sites if s in allowed]

    def can_access_site(self, site_name: str) -> bool:
        """Check if user can access a specific site"""
        allowed = self.allowed_sites or []
        if not allowed:
            # Empty = access to all
            return True
        return site_name in allowed

    def to_dict(self):
        """Convert user config to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "enabled_sites": self.enabled_sites or [],
            "default_sites": self.default_sites or [],
            "use_custom_default": self.use_custom_default,
            "allowed_sites": self.allowed_sites or [],
            "scraper_schedule_enabled": self.scraper_schedule_enabled,
            "scraper_schedule_interval": self.scraper_schedule_interval,
            "allowed_formats": self.allowed_formats or [],
            "default_language": self.default_language,
            "default_provider": self.default_provider,
            "default_model": self.default_model,
            "settings": self.settings or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def create_default_config(cls, user_id: int, subscription_tier: str = "free"):
        """
        Create default configuration for a new user

        Args:
            user_id: User ID
            subscription_tier: User subscription tier

        Returns:
            UserConfig: New user configuration instance
        """
        default_sites = cls.get_default_sites()
        return cls(
            user_id=user_id,
            enabled_sites=default_sites,  # All available sites enabled by default
            default_sites=[],  # No custom default initially
            use_custom_default=False,  # Use system default
            allowed_sites=[],  # Empty = access to all sites (admin can restrict later)
            allowed_formats=cls.get_default_formats(subscription_tier),
            scraper_schedule_enabled=False,
            scraper_schedule_interval=6,
            default_language="bn",
            default_provider="openai",
            settings={}
        )
