"""
Support API Endpoints
Ticket creation, management, and admin responses
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User
from app.models.support_ticket import SupportTicket, TicketReply
from app.middleware.auth import get_current_active_user

router = APIRouter()

# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class CreateTicketRequest(BaseModel):
    """Create support ticket request"""
    subject: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=20, max_length=5000)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")

    class Config:
        json_schema_extra = {
            "example": {
                "subject": "Issue with translation feature",
                "message": "I'm experiencing problems when trying to translate long articles...",
                "priority": "medium"
            }
        }


class TicketReplyRequest(BaseModel):
    """Reply to ticket request"""
    message: str = Field(..., min_length=10, max_length=5000)


class UpdateTicketStatusRequest(BaseModel):
    """Update ticket status request"""
    status: str = Field(..., pattern="^(open|in_progress|resolved|closed)$")


class ReplyResponse(BaseModel):
    """Ticket reply response"""
    id: int
    message: str
    is_admin_reply: bool
    user_email: Optional[str]
    user_name: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    """Support ticket response"""
    id: int
    subject: str
    message: str
    status: str
    priority: str
    created_at: str
    updated_at: str
    replies: List[ReplyResponse] = []

    class Config:
        from_attributes = True


class TicketWithUserResponse(BaseModel):
    """Support ticket with user info (for admin)"""
    id: int
    subject: str
    message: str
    status: str
    priority: str
    user_id: int
    user_email: str
    user_name: Optional[str]
    created_at: str
    updated_at: str
    reply_count: int

    class Config:
        from_attributes = True


class TicketDetailResponse(BaseModel):
    """Detailed ticket response with replies"""
    id: int
    subject: str
    message: str
    status: str
    priority: str
    user_id: int
    user_email: str
    user_name: Optional[str]
    created_at: str
    updated_at: str
    replies: List[ReplyResponse]

    class Config:
        from_attributes = True


# ============================================================================
# USER ENDPOINTS
# ============================================================================

@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    request: CreateTicketRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new support ticket

    - **subject**: Brief description of the issue (5-200 chars)
    - **message**: Detailed description (20-5000 chars)
    - **priority**: low, medium, or high (default: medium)
    """
    ticket = SupportTicket(
        user_id=current_user.id,
        subject=request.subject,
        message=request.message,
        priority=request.priority,
        status="open"
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "id": ticket.id,
        "subject": ticket.subject,
        "message": ticket.message,
        "status": ticket.status,
        "priority": ticket.priority,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else "",
        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else "",
        "replies": []
    }


@router.get("/tickets", response_model=List[TicketResponse])
async def get_my_tickets(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = None
):
    """
    Get all tickets for the current user

    - **status_filter**: Optional filter by status (open, in_progress, resolved, closed)
    """
    query = db.query(SupportTicket).filter(SupportTicket.user_id == current_user.id)

    if status_filter:
        query = query.filter(SupportTicket.status == status_filter)

    tickets = query.order_by(SupportTicket.created_at.desc()).all()

    result = []
    for ticket in tickets:
        replies = []
        for reply in ticket.replies:
            replies.append({
                "id": reply.id,
                "message": reply.message,
                "is_admin_reply": reply.is_admin_reply,
                "user_email": reply.user.email if reply.user else None,
                "user_name": reply.user.full_name if reply.user else None,
                "created_at": reply.created_at.isoformat() if reply.created_at else ""
            })

        result.append({
            "id": ticket.id,
            "subject": ticket.subject,
            "message": ticket.message,
            "status": ticket.status,
            "priority": ticket.priority,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else "",
            "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else "",
            "replies": replies
        })

    return result


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific ticket by ID

    Users can only access their own tickets.
    Admins can access any ticket.
    """
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Check permission: user can only see their own tickets (unless admin)
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this ticket"
        )

    replies = []
    for reply in ticket.replies:
        replies.append({
            "id": reply.id,
            "message": reply.message,
            "is_admin_reply": reply.is_admin_reply,
            "user_email": reply.user.email if reply.user else None,
            "user_name": reply.user.full_name if reply.user else None,
            "created_at": reply.created_at.isoformat() if reply.created_at else ""
        })

    return {
        "id": ticket.id,
        "subject": ticket.subject,
        "message": ticket.message,
        "status": ticket.status,
        "priority": ticket.priority,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else "",
        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else "",
        "replies": replies
    }


@router.post("/tickets/{ticket_id}/reply", response_model=ReplyResponse)
async def reply_to_ticket(
    ticket_id: int,
    request: TicketReplyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reply to a ticket (user adding more info)

    Users can only reply to their own tickets.
    """
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Check permission
    if ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reply to this ticket"
        )

    # Check if ticket is still open
    if ticket.status == "closed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reply to a closed ticket"
        )

    reply = TicketReply(
        ticket_id=ticket.id,
        user_id=current_user.id,
        message=request.message,
        is_admin_reply=False
    )

    db.add(reply)
    db.commit()
    db.refresh(reply)

    return {
        "id": reply.id,
        "message": reply.message,
        "is_admin_reply": reply.is_admin_reply,
        "user_email": current_user.email,
        "user_name": current_user.full_name,
        "created_at": reply.created_at.isoformat() if reply.created_at else ""
    }


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@router.get("/admin/tickets", response_model=List[TicketWithUserResponse])
async def admin_get_all_tickets(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None
):
    """
    Admin only: Get all support tickets

    - **status_filter**: Filter by status (open, in_progress, resolved, closed)
    - **priority_filter**: Filter by priority (low, medium, high)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    query = db.query(SupportTicket)

    if status_filter:
        query = query.filter(SupportTicket.status == status_filter)
    if priority_filter:
        query = query.filter(SupportTicket.priority == priority_filter)

    tickets = query.order_by(SupportTicket.created_at.desc()).all()

    result = []
    for ticket in tickets:
        result.append({
            "id": ticket.id,
            "subject": ticket.subject,
            "message": ticket.message,
            "status": ticket.status,
            "priority": ticket.priority,
            "user_id": ticket.user_id,
            "user_email": ticket.user.email,
            "user_name": ticket.user.full_name,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else "",
            "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else "",
            "reply_count": len(ticket.replies)
        })

    return result


@router.get("/admin/tickets/{ticket_id}", response_model=TicketDetailResponse)
async def admin_get_ticket_detail(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Get detailed ticket information with all replies
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    replies = []
    for reply in ticket.replies:
        replies.append({
            "id": reply.id,
            "message": reply.message,
            "is_admin_reply": reply.is_admin_reply,
            "user_email": reply.user.email if reply.user else None,
            "user_name": reply.user.full_name if reply.user else None,
            "created_at": reply.created_at.isoformat() if reply.created_at else ""
        })

    return {
        "id": ticket.id,
        "subject": ticket.subject,
        "message": ticket.message,
        "status": ticket.status,
        "priority": ticket.priority,
        "user_id": ticket.user_id,
        "user_email": ticket.user.email,
        "user_name": ticket.user.full_name,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else "",
        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else "",
        "replies": replies
    }


@router.post("/admin/tickets/{ticket_id}/respond", response_model=ReplyResponse)
async def admin_respond_to_ticket(
    ticket_id: int,
    request: TicketReplyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Respond to a support ticket

    This creates an admin reply to the ticket.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Auto-update status to in_progress if it was open
    if ticket.status == "open":
        ticket.status = "in_progress"

    reply = TicketReply(
        ticket_id=ticket.id,
        user_id=current_user.id,
        message=request.message,
        is_admin_reply=True
    )

    db.add(reply)
    db.commit()
    db.refresh(reply)

    return {
        "id": reply.id,
        "message": reply.message,
        "is_admin_reply": reply.is_admin_reply,
        "user_email": current_user.email,
        "user_name": current_user.full_name,
        "created_at": reply.created_at.isoformat() if reply.created_at else ""
    }


@router.patch("/admin/tickets/{ticket_id}/status")
async def admin_update_ticket_status(
    ticket_id: int,
    request: UpdateTicketStatusRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Update ticket status

    - **status**: New status (open, in_progress, resolved, closed)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    old_status = ticket.status
    ticket.status = request.status
    db.commit()

    return {
        "success": True,
        "message": f"Ticket status changed from {old_status} to {request.status}",
        "ticket_id": ticket.id,
        "new_status": ticket.status
    }


@router.get("/admin/stats")
async def admin_get_support_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Get support ticket statistics
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    from sqlalchemy import func

    total = db.query(SupportTicket).count()
    open_count = db.query(SupportTicket).filter(SupportTicket.status == "open").count()
    in_progress_count = db.query(SupportTicket).filter(SupportTicket.status == "in_progress").count()
    resolved_count = db.query(SupportTicket).filter(SupportTicket.status == "resolved").count()
    closed_count = db.query(SupportTicket).filter(SupportTicket.status == "closed").count()

    high_priority = db.query(SupportTicket).filter(
        SupportTicket.priority == "high",
        SupportTicket.status.in_(["open", "in_progress"])
    ).count()

    return {
        "total_tickets": total,
        "open": open_count,
        "in_progress": in_progress_count,
        "resolved": resolved_count,
        "closed": closed_count,
        "high_priority_pending": high_priority
    }
