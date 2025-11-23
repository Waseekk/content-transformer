"""
Enhancement Model
Stores AI-enhanced content in multiple formats
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Enhancement(Base):
    """Enhanced content model"""

    __tablename__ = "enhancements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    translation_id = Column(Integer, ForeignKey("translations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Enhancement details
    format_type = Column(String(50), nullable=False, index=True)  # newspaper, blog, facebook, instagram, hard_news, soft_news
    content = Column(Text, nullable=False)

    # AI metadata
    provider = Column(String(50), default="openai")
    model = Column(String(100), nullable=True)
    tokens_used = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="enhancements")
    translation = relationship("Translation", back_populates="enhancements")

    def __repr__(self):
        return f"<Enhancement {self.id}: {self.format_type}>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "format_type": self.format_type,
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
