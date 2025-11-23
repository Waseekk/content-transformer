"""
Translation Model
Stores translation history for users
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Translation(Base):
    """Translation record model"""

    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="SET NULL"), nullable=True, index=True)

    # Translation content
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    headline = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)

    # AI metadata
    provider = Column(String(50), default="openai")  # openai, google
    model = Column(String(100), nullable=True)
    tokens_used = Column(Integer, default=0)

    # Additional data (extracted metadata from OpenAI)
    extra_data = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="translations")
    article = relationship("Article", back_populates="translations")
    enhancements = relationship("Enhancement", back_populates="translation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Translation {self.id}: {self.headline[:50] if self.headline else 'No title'}...>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "headline": self.headline,
            "original_text": self.original_text[:200] + "..." if len(self.original_text) > 200 else self.original_text,
            "translated_text": self.translated_text[:200] + "..." if len(self.translated_text) > 200 else self.translated_text,
            "author": self.author,
            "provider": self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
