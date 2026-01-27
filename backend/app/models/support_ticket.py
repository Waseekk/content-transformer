"""
Support Ticket Models
Database models for the support/contact system
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class SupportTicket(Base):
    """
    Support ticket model for user support requests
    """
    __tablename__ = "support_tickets"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Ticket details
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="open", nullable=False)  # open, in_progress, resolved, closed
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="support_tickets")
    replies = relationship("TicketReply", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketReply.created_at")
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SupportTicket(id={self.id}, subject={self.subject[:30]}, status={self.status})>"

    @property
    def is_open(self) -> bool:
        """Check if ticket is still open"""
        return self.status in ["open", "in_progress"]

    def close(self):
        """Close the ticket"""
        self.status = "closed"

    def mark_in_progress(self):
        """Mark ticket as in progress"""
        self.status = "in_progress"

    def mark_resolved(self):
        """Mark ticket as resolved"""
        self.status = "resolved"


class TicketReply(Base):
    """
    Ticket reply model for responses to support tickets
    """
    __tablename__ = "ticket_replies"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    ticket_id = Column(Integer, ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Reply details
    message = Column(Text, nullable=False)
    is_admin_reply = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    ticket = relationship("SupportTicket", back_populates="replies")
    user = relationship("User")

    # Relationships
    attachments = relationship("TicketAttachment", back_populates="reply", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TicketReply(id={self.id}, ticket_id={self.ticket_id}, is_admin={self.is_admin_reply})>"


class TicketAttachment(Base):
    """
    File attachment for support tickets and replies
    """
    __tablename__ = "ticket_attachments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=True, index=True)
    reply_id = Column(Integer, ForeignKey("ticket_replies.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    ticket = relationship("SupportTicket", back_populates="attachments")
    reply = relationship("TicketReply", back_populates="attachments")
    user = relationship("User")

    def __repr__(self):
        return f"<TicketAttachment(id={self.id}, filename={self.filename})>"
