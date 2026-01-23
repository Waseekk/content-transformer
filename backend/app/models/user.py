"""
User Model
Database model for user accounts and token management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base
from app.config import get_settings

settings = get_settings()


class User(Base):
    """
    User model for authentication and token management
    """
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # OAuth
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    avatar_url = Column(String(500), nullable=True)

    # Token management
    tokens_remaining = Column(Integer, default=settings.DEFAULT_MONTHLY_TOKENS, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    monthly_token_limit = Column(Integer, default=settings.DEFAULT_MONTHLY_TOKENS, nullable=False)
    token_reset_day = Column(Integer, default=settings.TOKEN_RESET_DAY, nullable=False)  # 1-31

    # Enhancement limits (monthly)
    monthly_enhancement_limit = Column(Integer, default=settings.DEFAULT_MONTHLY_ENHANCEMENTS, nullable=False)
    enhancements_used_this_month = Column(Integer, default=0, nullable=False)

    # Translation limits (monthly)
    monthly_translation_limit = Column(Integer, default=settings.DEFAULT_MONTHLY_TRANSLATIONS, nullable=False)
    translations_used_this_month = Column(Integer, default=0, nullable=False)

    # Subscription
    subscription_tier = Column(String(50), default="free", nullable=False)  # free, premium, enterprise
    subscription_status = Column(String(50), default="active", nullable=False)  # active, paused, cancelled

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    articles = relationship("Article", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    translations = relationship("Translation", back_populates="user", cascade="all, delete-orphan")
    enhancements = relationship("Enhancement", back_populates="user", cascade="all, delete-orphan")
    token_usage = relationship("TokenUsage", back_populates="user", cascade="all, delete-orphan")
    config = relationship("UserConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")
    support_tickets = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, tier={self.subscription_tier})>"

    @property
    def tokens_percentage(self) -> float:
        """Calculate percentage of tokens used"""
        if self.monthly_token_limit == 0:
            return 100.0
        return (self.tokens_used / self.monthly_token_limit) * 100

    def has_tokens(self, required_tokens: int = 1) -> bool:
        """
        Check if user has enough tokens

        Args:
            required_tokens: Number of tokens required

        Returns:
            bool: True if user has enough tokens
        """
        return self.tokens_remaining >= required_tokens

    def deduct_tokens(self, tokens: int) -> bool:
        """
        Deduct tokens from user's balance

        Args:
            tokens: Number of tokens to deduct

        Returns:
            bool: True if successful, False if insufficient tokens
        """
        if not self.has_tokens(tokens):
            return False

        self.tokens_used += tokens
        self.tokens_remaining = max(0, self.monthly_token_limit - self.tokens_used)

        # Auto-pause if no tokens remaining
        if self.tokens_remaining <= 0:
            self.subscription_status = "paused"

        return True

    def add_tokens(self, tokens: int):
        """
        Add tokens to user's balance (admin function)

        Args:
            tokens: Number of tokens to add
        """
        self.monthly_token_limit += tokens
        self.tokens_remaining = self.monthly_token_limit - self.tokens_used

        # Reactivate if was paused
        if self.subscription_status == "paused" and self.tokens_remaining > 0:
            self.subscription_status = "active"

    def reset_monthly_tokens(self):
        """
        Reset tokens for new month
        Called by Celery Beat on the 1st of each month
        """
        self.tokens_used = 0
        self.tokens_remaining = self.monthly_token_limit

        # Reactivate subscription if it was paused
        if self.subscription_status == "paused":
            self.subscription_status = "active"

    def upgrade_tier(self, tier: str):
        """
        Upgrade user subscription tier

        Args:
            tier: Subscription tier (free, premium, enterprise)
        """
        self.subscription_tier = tier

        # Update token limits based on tier
        if tier == "free":
            self.monthly_token_limit = settings.FREE_TIER_TOKENS
        elif tier == "premium":
            self.monthly_token_limit = settings.PREMIUM_TIER_TOKENS
        else:  # enterprise or custom
            # Keep existing limit or set custom
            pass

        # Recalculate remaining tokens
        self.tokens_remaining = max(0, self.monthly_token_limit - self.tokens_used)

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()

    # Enhancement quota methods
    @property
    def enhancements_remaining(self) -> int:
        """Get remaining enhancements for this month"""
        return max(0, self.monthly_enhancement_limit - self.enhancements_used_this_month)

    @property
    def enhancements_percentage(self) -> float:
        """Calculate percentage of enhancements used"""
        if self.monthly_enhancement_limit == 0:
            return 100.0
        return (self.enhancements_used_this_month / self.monthly_enhancement_limit) * 100

    def has_enhancement_quota(self, required: int = 1) -> bool:
        """Check if user has enough enhancement quota"""
        return self.enhancements_remaining >= required

    def use_enhancement(self, count: int = 1) -> bool:
        """
        Use enhancement quota

        Args:
            count: Number of enhancements to use

        Returns:
            bool: True if successful
        """
        if not self.has_enhancement_quota(count):
            return False
        self.enhancements_used_this_month += count
        return True

    def reset_monthly_enhancements(self):
        """Reset enhancement quota for new month"""
        self.enhancements_used_this_month = 0

    # Translation quota methods
    @property
    def translations_remaining(self) -> int:
        """Get remaining translations for this month"""
        return max(0, self.monthly_translation_limit - self.translations_used_this_month)

    @property
    def translations_percentage(self) -> float:
        """Calculate percentage of translations used"""
        if self.monthly_translation_limit == 0:
            return 100.0
        return (self.translations_used_this_month / self.monthly_translation_limit) * 100

    def is_translation_limit_exceeded(self) -> bool:
        """Check if translation limit is exceeded (for warning, not blocking)"""
        return self.translations_used_this_month >= self.monthly_translation_limit

    def use_translation(self, count: int = 1):
        """Track translation usage (doesn't block, just tracks)"""
        self.translations_used_this_month += count

    def reset_monthly_translations(self):
        """Reset translation quota for new month"""
        self.translations_used_this_month = 0

    def is_enhancement_limit_exceeded(self) -> bool:
        """Check if enhancement limit is exceeded (for warning, not blocking)"""
        return self.enhancements_used_this_month >= self.monthly_enhancement_limit

    # Auto-assign tokens
    def check_and_auto_assign_tokens(self) -> int:
        """
        Check if tokens are low and auto-assign if needed

        Returns:
            int: Number of tokens auto-assigned (0 if not needed)
        """
        if self.tokens_remaining < settings.AUTO_ASSIGN_TOKENS_THRESHOLD:
            amount = settings.AUTO_ASSIGN_TOKENS_AMOUNT
            self.monthly_token_limit += amount
            self.tokens_remaining += amount

            # Reactivate if paused
            if self.subscription_status == "paused":
                self.subscription_status = "active"

            return amount
        return 0

    def admin_set_tokens(self, new_limit: int, reset_used: bool = False):
        """
        Admin: Set user's token limit

        Args:
            new_limit: New monthly token limit
            reset_used: If True, also reset tokens_used to 0
        """
        self.monthly_token_limit = new_limit
        if reset_used:
            self.tokens_used = 0
        self.tokens_remaining = self.monthly_token_limit - self.tokens_used

        # Reactivate if paused
        if self.subscription_status == "paused" and self.tokens_remaining > 0:
            self.subscription_status = "active"

    def admin_set_enhancement_limit(self, new_limit: int, reset_used: bool = False):
        """
        Admin: Set user's enhancement limit

        Args:
            new_limit: New monthly enhancement limit
            reset_used: If True, also reset enhancements_used to 0
        """
        self.monthly_enhancement_limit = new_limit
        if reset_used:
            self.enhancements_used_this_month = 0
