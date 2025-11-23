"""
Job Model
Tracks background job status for async operations
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Job(Base):
    """Background job tracking model"""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Job details
    job_type = Column(String(50), nullable=False, index=True)  # scrape, translate, enhance
    task_id = Column(String(255), unique=True, index=True, nullable=True)  # Celery task ID

    # Status tracking
    status = Column(String(50), default="pending", index=True)  # pending, running, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    status_message = Column(Text, nullable=True)

    # Results
    result = Column(JSON, nullable=True)  # Store job result
    error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="jobs")

    def __repr__(self):
        return f"<Job {self.id}: {self.job_type} - {self.status}>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "job_type": self.job_type,
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "status_message": self.status_message,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def update_status(self, status: str, progress: int = None, message: str = None):
        """Update job status"""
        self.status = status
        if progress is not None:
            self.progress = progress
        if message:
            self.status_message = message

        if status == "running" and not self.started_at:
            self.started_at = datetime.utcnow()
        elif status in ["completed", "failed"]:
            self.completed_at = datetime.utcnow()
