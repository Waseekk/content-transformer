"""
Article Model
Stores scraped news articles (user-specific)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Article(Base):
    """Scraped article model"""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Article content
    source = Column(String(100), index=True)  # newsuk_travel, tourism_review, etc.
    publisher = Column(String(255))
    headline = Column(Text, nullable=False)
    article_url = Column(Text, nullable=False)

    # Metadata
    published_time = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    view = Column(String(50), nullable=True)  # top, latest, popular

    # Additional metadata stored as JSON
    extra_data = Column(JSON, nullable=True)

    # Timestamps
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="articles")
    translations = relationship("Translation", back_populates="article", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Article {self.id}: {self.headline[:50]}...>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "source": self.source,
            "publisher": self.publisher,
            "headline": self.headline,
            "article_url": self.article_url,
            "published_time": self.published_time,
            "country": self.country,
            "view": self.view,
            "extra_data": self.extra_data,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
        }
