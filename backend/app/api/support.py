"""
Support API Endpoints
Ticket creation, management, admin responses, and file attachments
"""

import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User
from app.models.support_ticket import SupportTicket, TicketReply, TicketAttachment
from app.middleware.auth import get_current_active_user
from app.config import get_settings

router = APIRouter()
settings = get_settings()

# File upload constraints
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg', '.gif'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/png', 'image/jpeg', 'image/gif',
}

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


class AttachmentResponse(BaseModel):
    """File attachment response"""
    id: int
    filename: str
    file_type: str
    file_size: int
    created_at: str
    download_url: str

    class Config:
        from_attributes = True


class ReplyResponse(BaseModel):
    """Ticket reply response"""
    id: int
    message: str
    is_admin_reply: bool
    user_email: Optional[str]
    user_name: Optional[str]
    created_at: str
    attachments: List[AttachmentResponse] = []

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
    attachments: List[AttachmentResponse] = []

    class Config:
        from_attributes = True


class TicketWithUserResponse(BaseModel):
    """Support ticket with user info (for admin) - includes replies"""
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
    replies: List[ReplyResponse] = []
    attachments: List[AttachmentResponse] = []

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
    attachments: List[AttachmentResponse] = []

    class Config:
        from_attributes = True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _serialize_attachment(att: TicketAttachment) -> dict:
    """Serialize a TicketAttachment to a response dict"""
    return {
        "id": att.id,
        "filename": att.filename,
        "file_type": att.file_type,
        "file_size": att.file_size,
        "created_at": att.created_at.isoformat() if att.created_at else "",
        "download_url": f"/api/support/attachments/{att.id}"
    }


def _serialize_reply(reply: TicketReply) -> dict:
    """Serialize a TicketReply to a response dict"""
    return {
        "id": reply.id,
        "message": reply.message,
        "is_admin_reply": reply.is_admin_reply,
        "user_email": reply.user.email if reply.user else None,
        "user_name": reply.user.full_name if reply.user else None,
        "created_at": reply.created_at.isoformat() if reply.created_at else "",
        "attachments": [_serialize_attachment(a) for a in (reply.attachments or [])]
    }


def _serialize_ticket(ticket: SupportTicket) -> dict:
    """Serialize a SupportTicket for user response"""
    return {
        "id": ticket.id,
        "subject": ticket.subject,
        "message": ticket.message,
        "status": ticket.status,
        "priority": ticket.priority,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else "",
        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else "",
        "replies": [_serialize_reply(r) for r in ticket.replies],
        "attachments": [_serialize_attachment(a) for a in (ticket.attachments or [])]
    }


def _serialize_ticket_admin(ticket: SupportTicket) -> dict:
    """Serialize a SupportTicket for admin response (includes user info + replies)"""
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
        "reply_count": len(ticket.replies),
        "replies": [_serialize_reply(r) for r in ticket.replies],
        "attachments": [_serialize_attachment(a) for a in (ticket.attachments or [])]
    }


def _validate_file(file: UploadFile):
    """Validate uploaded file type and extension"""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )


async def _save_file(file: UploadFile, user_id: int, ticket_id: int, reply_id: int = None, db: Session = None) -> TicketAttachment:
    """Save uploaded file and create attachment record"""
    _validate_file(file)

    # Read file content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Generate unique stored filename
    ext = os.path.splitext(file.filename or "")[1].lower()
    stored_filename = f"{uuid.uuid4().hex}{ext}"

    # Save to disk
    file_path = settings.UPLOADS_DIR / stored_filename
    with open(file_path, "wb") as f:
        f.write(content)

    # Create DB record
    attachment = TicketAttachment(
        ticket_id=ticket_id,
        reply_id=reply_id,
        user_id=user_id,
        filename=file.filename or "unnamed",
        stored_filename=stored_filename,
        file_type=file.content_type or "application/octet-stream",
        file_size=len(content)
    )
    db.add(attachment)

    return attachment


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

    return _serialize_ticket(ticket)


@router.post("/tickets/with-files", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket_with_files(
    subject: str = Form(..., min_length=5, max_length=200),
    message: str = Form(..., min_length=20, max_length=5000),
    priority: str = Form(default="medium"),
    files: List[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new support ticket with optional file attachments

    - **subject**: Brief description of the issue (5-200 chars)
    - **message**: Detailed description (20-5000 chars)
    - **priority**: low, medium, or high (default: medium)
    - **files**: Optional file attachments (max 10MB each, pdf/doc/docx/png/jpg/jpeg/gif)
    """
    if priority not in ("low", "medium", "high"):
        raise HTTPException(status_code=400, detail="Priority must be low, medium, or high")

    ticket = SupportTicket(
        user_id=current_user.id,
        subject=subject,
        message=message,
        priority=priority,
        status="open"
    )
    db.add(ticket)
    db.flush()  # get ticket.id

    # Save attachments
    for file in files:
        if file.filename:  # skip empty file inputs
            await _save_file(file, current_user.id, ticket.id, db=db)

    db.commit()
    db.refresh(ticket)

    return _serialize_ticket(ticket)


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

    return [_serialize_ticket(t) for t in tickets]


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

    return _serialize_ticket(ticket)


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

    return _serialize_reply(reply)


@router.post("/tickets/{ticket_id}/reply-with-files", response_model=ReplyResponse)
async def reply_to_ticket_with_files(
    ticket_id: int,
    message: str = Form(..., min_length=10, max_length=5000),
    files: List[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reply to a ticket with optional file attachments (user)
    """
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if ticket.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to reply to this ticket")
    if ticket.status == "closed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot reply to a closed ticket")

    reply = TicketReply(
        ticket_id=ticket.id,
        user_id=current_user.id,
        message=message,
        is_admin_reply=False
    )
    db.add(reply)
    db.flush()

    for file in files:
        if file.filename:
            await _save_file(file, current_user.id, ticket.id, reply_id=reply.id, db=db)

    db.commit()
    db.refresh(reply)

    return _serialize_reply(reply)


# ============================================================================
# ATTACHMENT ENDPOINTS
# ============================================================================

@router.post("/tickets/{ticket_id}/attachments", response_model=List[AttachmentResponse])
async def upload_attachments(
    ticket_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload file attachments to an existing ticket
    """
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # User can upload to their own tickets, admin can upload to any
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if ticket.status == "closed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot add attachments to a closed ticket")

    saved = []
    for file in files:
        if file.filename:
            att = await _save_file(file, current_user.id, ticket.id, db=db)
            saved.append(att)

    db.commit()
    for att in saved:
        db.refresh(att)

    return [_serialize_attachment(a) for a in saved]


@router.get("/attachments/{attachment_id}")
async def download_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Download/serve an attachment file
    """
    from fastapi.responses import FileResponse

    attachment = db.query(TicketAttachment).filter(TicketAttachment.id == attachment_id).first()

    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    # Permission check: user owns the ticket or is admin
    ticket = db.query(SupportTicket).filter(SupportTicket.id == attachment.ticket_id).first()
    if ticket and ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    file_path = settings.UPLOADS_DIR / attachment.stored_filename
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk")

    return FileResponse(
        path=str(file_path),
        filename=attachment.filename,
        media_type=attachment.file_type
    )


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
    Admin only: Get all support tickets (with replies included)

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

    return [_serialize_ticket_admin(t) for t in tickets]


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
        "replies": [_serialize_reply(r) for r in ticket.replies],
        "attachments": [_serialize_attachment(a) for a in (ticket.attachments or [])]
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

    return _serialize_reply(reply)


@router.post("/admin/tickets/{ticket_id}/respond-with-files", response_model=ReplyResponse)
async def admin_respond_with_files(
    ticket_id: int,
    message: str = Form(..., min_length=10, max_length=5000),
    files: List[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Respond to a ticket with optional file attachments
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if ticket.status == "open":
        ticket.status = "in_progress"

    reply = TicketReply(
        ticket_id=ticket.id,
        user_id=current_user.id,
        message=message,
        is_admin_reply=True
    )
    db.add(reply)
    db.flush()

    for file in files:
        if file.filename:
            await _save_file(file, current_user.id, ticket.id, reply_id=reply.id, db=db)

    db.commit()
    db.refresh(reply)

    return _serialize_reply(reply)


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
