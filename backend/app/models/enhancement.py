"""
Enhancement Model
Database model for AI-enhanced multi-format content
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class Enhancement(Base):
    """
    Enhancement model for storing AI-generated multi-format content
    """
    __tablename__ = "enhancements"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    translation_id = Column(Integer, ForeignKey("translations.id", ondelete="CASCADE"), nullable=True)

    # Format information
    format_type = Column(String(50), nullable=False, index=True)  # hard_news, soft_news, etc.
    format_name = Column(String(100), nullable=True)  # Display name

    # Enhanced content
    content = Column(Text, nullable=False)

    # Metadata
    headline = Column(String(500), nullable=True)  # Generated headline for the format
    word_count = Column(Integer, nullable=True)

    # AI provider info
    provider = Column(String(50), default="openai", nullable=False)
    model = Column(String(100), nullable=True)

    # Token tracking
    tokens_used = Column(Integer, default=0, nullable=False)

    # File storage (optional)
    file_path = Column(String(500), nullable=True)  # Path to saved file if exported

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="enhancements")
    translation = relationship("Translation", back_populates="enhancements")

    def __repr__(self):
        return f"<Enhancement(id={self.id}, format={self.format_type}, user_id={self.user_id})>"

    def to_dict(self):
        """Convert enhancement to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "translation_id": self.translation_id,
            "format_type": self.format_type,
            "format_name": self.format_name,
            "content": self.content,
            "headline": self.headline,
            "word_count": self.word_count,
            "provider": self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "file_path": self.file_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def preview_text(self) -> str:
        """Get preview of content (first 150 chars)"""
        if len(self.content) > 150:
            return self.content[:150] + "..."
        return self.content
