"""
User Model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    """User account model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # User info
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Subscription
    subscription_tier = Column(String(50), default="free")  # free, premium
    tokens_remaining = Column(Integer, default=10000)  # Free tier default
    tokens_total = Column(Integer, default=10000)

    # Token reset tracking
    last_token_reset = Column(DateTime, default=datetime.utcnow)
    next_token_reset = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    articles = relationship("Article", back_populates="user", cascade="all, delete-orphan")
    translations = relationship("Translation", back_populates="user", cascade="all, delete-orphan")
    enhancements = relationship("Enhancement", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    token_usages = relationship("TokenUsage", back_populates="user", cascade="all, delete-orphan")
    config = relationship("UserConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

    def deduct_tokens(self, amount: int) -> bool:
        """
        Deduct tokens from user's balance
        Returns True if successful, False if insufficient tokens
        """
        if self.tokens_remaining >= amount:
            self.tokens_remaining -= amount
            return True
        return False

    def has_tokens(self, amount: int) -> bool:
        """Check if user has enough tokens"""
        return self.tokens_remaining >= amount

    def reset_monthly_tokens(self):
        """Reset user tokens based on subscription tier"""
        from app.config import get_settings
        settings = get_settings()

        tier_config = settings.SUBSCRIPTION_TIERS.get(self.subscription_tier, {})
        self.tokens_total = tier_config.get("monthly_tokens", 10000)
        self.tokens_remaining = self.tokens_total
        self.last_token_reset = datetime.utcnow()

        # Calculate next reset date
        from dateutil.relativedelta import relativedelta
        self.next_token_reset = datetime.utcnow() + relativedelta(months=1)
