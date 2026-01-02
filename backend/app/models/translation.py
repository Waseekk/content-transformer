"""
Translation Model
Database model for translation history
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Translation(Base):
    """
    Translation model for storing translation history
    """
    __tablename__ = "translations"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="SET NULL"), nullable=True)

    # Source content
    original_url = Column(Text, nullable=True)  # If translated from URL
    original_text = Column(Text, nullable=False)
    original_language = Column(String(10), default="en", nullable=False)

    # Translated content
    translated_text = Column(Text, nullable=False)
    target_language = Column(String(10), default="bn", nullable=False)  # Bengali

    # Metadata
    extraction_method = Column(String(50), nullable=True)  # trafilatura, newspaper3k, manual
    title = Column(String(500), nullable=True)
    author = Column(String(255), nullable=True)
    publish_date = Column(String(100), nullable=True)

    # AI provider info
    provider = Column(String(50), default="openai", nullable=False)
    model = Column(String(100), nullable=True)

    # Token tracking
    tokens_used = Column(Integer, default=0, nullable=False)

    # Quality metrics
    word_count_original = Column(Integer, nullable=True)
    word_count_translated = Column(Integer, nullable=True)
    translation_quality_score = Column(Integer, nullable=True)  # 0-100 if available

    # Status
    is_favorite = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="translations")
    article = relationship("Article", back_populates="translations")
    enhancements = relationship("Enhancement", back_populates="translation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Translation(id={self.id}, user_id={self.user_id}, lang={self.target_language})>"

    def to_dict(self):
        """Convert translation to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "article_id": self.article_id,
            "original_url": self.original_url,
            "original_text": self.original_text[:200] + "..." if len(self.original_text) > 200 else self.original_text,
            "original_language": self.original_language,
            "translated_text": self.translated_text[:200] + "..." if len(self.translated_text) > 200 else self.translated_text,
            "target_language": self.target_language,
            "extraction_method": self.extraction_method,
            "title": self.title,
            "author": self.author,
            "publish_date": self.publish_date,
            "provider": self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "word_count_original": self.word_count_original,
            "word_count_translated": self.word_count_translated,
            "is_favorite": self.is_favorite,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def preview_text(self) -> str:
        """Get preview of translated text (first 200 chars)"""
        if len(self.translated_text) > 200:
            return self.translated_text[:200] + "..."
        return self.translated_text
