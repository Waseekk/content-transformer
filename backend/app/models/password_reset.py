"""
Password Reset Token Model
Database model for password reset tokens
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from app.database import Base
from app.config import get_settings

settings = get_settings()


class PasswordResetToken(Base):
    """
    Password reset token for forgot password functionality
    """
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(100), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship
    user = relationship("User", backref="password_reset_tokens")

    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, used={self.used})>"

    @classmethod
    def create_token(cls, user_id: int) -> "PasswordResetToken":
        """
        Create a new password reset token

        Args:
            user_id: ID of the user requesting password reset

        Returns:
            PasswordResetToken: New token instance
        """
        return cls(
            user_id=user_id,
            token=str(uuid.uuid4()),
            expires_at=datetime.utcnow() + timedelta(hours=settings.PASSWORD_RESET_EXPIRE_HOURS)
        )

    def is_valid(self) -> bool:
        """
        Check if token is valid (not used and not expired)

        Returns:
            bool: True if token is valid
        """
        if self.used:
            return False
        if datetime.utcnow() > self.expires_at.replace(tzinfo=None):
            return False
        return True

    def mark_used(self):
        """Mark token as used"""
        self.used = True
