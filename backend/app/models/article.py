"""
Article Model
Database model for scraped news articles
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Article(Base):
    """
    Article model for scraped news content
    """
    __tablename__ = "articles"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True)

    # Article metadata
    source = Column(String(255), nullable=False, index=True)  # e.g., "BBC Travel", "CNN Travel"
    publisher = Column(String(255), nullable=True)
    headline = Column(Text, nullable=False)
    article_url = Column(Text, nullable=False)

    # Article content (optional - may be fetched later)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    # Additional metadata
    published_time = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    view = Column(String(50), nullable=True)  # top, latest, popular

    # Extra data (store additional scraped fields as JSON)
    extra_data = Column(JSON, nullable=True)

    # Timestamps
    scraped_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="articles")
    job = relationship("Job", back_populates="articles")
    translations = relationship("Translation", back_populates="article", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Article(id={self.id}, source={self.source}, headline={self.headline[:50]}...)>"

    def to_dict(self):
        """Convert article to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "source": self.source,
            "publisher": self.publisher,
            "headline": self.headline,
            "article_url": self.article_url,
            "content": self.content,
            "summary": self.summary,
            "published_time": self.published_time,
            "country": self.country,
            "view": self.view,
            "extra_data": self.extra_data,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
