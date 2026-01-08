"""
Job Model
Database model for background job tracking (Celery tasks)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Job(Base):
    """
    Job model for tracking background tasks
    """
    __tablename__ = "jobs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Job metadata
    job_type = Column(String(50), nullable=False, index=True)  # scrape, translate, enhance
    status = Column(String(50), nullable=False, index=True, default="pending")  # pending, running, completed, failed
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    status_message = Column(String(500), nullable=True)

    # Result data (store as JSON)
    result = Column(JSON, nullable=True)

    # Error handling
    error = Column(Text, nullable=True)

    # Celery task ID (optional)
    celery_task_id = Column(String(255), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="jobs")
    articles = relationship("Article", back_populates="job")

    def __repr__(self):
        return f"<Job(id={self.id}, type={self.job_type}, status={self.status}, progress={self.progress}%)>"

    def update_status(
        self,
        status: str,
        progress: int = None,
        message: str = None,
        error: str = None,
        result: dict = None
    ):
        """
        Update job status and metadata

        Args:
            status: New status (pending, running, completed, failed)
            progress: Progress percentage (0-100)
            message: Status message
            error: Error message if failed
            result: Result data as dictionary
        """
        self.status = status

        if progress is not None:
            self.progress = min(100, max(0, progress))

        if message is not None:
            self.status_message = message

        if error is not None:
            self.error = error

        if result is not None:
            self.result = result

        # Update timestamps
        if status == "running" and not self.started_at:
            self.started_at = datetime.utcnow()

        if status in ("completed", "failed"):
            self.completed_at = datetime.utcnow()

    def mark_as_running(self, message: str = None):
        """Mark job as running"""
        self.update_status("running", progress=0, message=message or "Job started")

    def mark_as_completed(self, result: dict = None, message: str = None):
        """Mark job as completed"""
        self.update_status(
            "completed",
            progress=100,
            message=message or "Job completed successfully",
            result=result
        )

    def mark_as_failed(self, error: str):
        """Mark job as failed"""
        self.update_status("failed", message="Job failed", error=error)

    def to_dict(self):
        """Convert job to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_type": self.job_type,
            "status": self.status,
            "progress": self.progress,
            "status_message": self.status_message,
            "result": self.result,
            "error": self.error,
            "celery_task_id": self.celery_task_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def duration(self):
        """Calculate job duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.utcnow() - self.started_at).total_seconds()
        return None

    @property
    def is_complete(self) -> bool:
        """Check if job is complete (success or failure)"""
        return self.status in ("completed", "failed")

    @property
    def is_active(self) -> bool:
        """Check if job is currently active"""
        return self.status in ("pending", "running")
