"""
FormatConfig Model
Database model for content format configurations (hard_news, soft_news, ai_content, etc.)
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class FormatConfig(Base):
    """
    FormatConfig model for storing content generation format configurations.
    Each format defines how AI generates content (prompts, settings, rules).
    """
    __tablename__ = "format_configs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Identification
    slug = Column(String(50), unique=True, nullable=False, index=True)  # "hard_news", "soft_news", "ai_content"
    display_name = Column(String(100), nullable=False)  # "Hard News", "AI Content"
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="newspaper")  # "newspaper", "book", "sparkles"

    # AI Settings
    system_prompt = Column(Text, nullable=False)
    temperature = Column(Float, default=0.5)
    max_tokens = Column(Integer, default=4096)

    # Rules (JSON)
    # Example: {
    #   "max_sentences_per_paragraph": 2,  # null = no limit
    #   "quotation_on_last_line": false,
    #   "allow_subheads": false,
    #   "min_words": 220,
    #   "max_words": 450
    # }
    rules = Column(JSON, default=dict)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by], backref="created_formats")

    def __repr__(self):
        return f"<FormatConfig(id={self.id}, slug={self.slug}, name={self.display_name})>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "slug": self.slug,
            "display_name": self.display_name,
            "description": self.description,
            "icon": self.icon,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "rules": self.rules or {},
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_config_for_enhancer(self):
        """Get configuration dict for ContentEnhancer"""
        return {
            "name": self.display_name,
            "icon": self.icon,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "description": self.description,
            "rules": self.rules or {},
        }
