"""
Admin API Endpoints for Format Configuration
CRUD operations for managing content format configurations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.format_config import FormatConfig
from app.models.user import User
from app.middleware.auth import get_admin_user
from app.schemas.format_config import (
    FormatConfigCreate,
    FormatConfigUpdate,
    FormatConfigResponse,
    FormatConfigListResponse,
)

router = APIRouter()


@router.get("", response_model=FormatConfigListResponse)
async def list_formats(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    List all format configurations (Admin only)

    Args:
        include_inactive: Include inactive formats
        db: Database session
        admin: Admin user

    Returns:
        List of format configurations
    """
    query = db.query(FormatConfig)

    if not include_inactive:
        query = query.filter(FormatConfig.is_active == True)

    formats = query.order_by(FormatConfig.id).all()

    return FormatConfigListResponse(
        formats=[FormatConfigResponse.model_validate(f) for f in formats],
        total=len(formats)
    )


@router.post("", response_model=FormatConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_format(
    format_data: FormatConfigCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Create a new format configuration (Admin only)

    Args:
        format_data: Format configuration data
        db: Database session
        admin: Admin user

    Returns:
        Created format configuration
    """
    # Check if slug already exists
    existing = db.query(FormatConfig).filter(FormatConfig.slug == format_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format with slug '{format_data.slug}' already exists"
        )

    # Create format
    format_config = FormatConfig(
        slug=format_data.slug,
        display_name=format_data.display_name,
        description=format_data.description,
        icon=format_data.icon,
        system_prompt=format_data.system_prompt,
        temperature=format_data.temperature,
        max_tokens=format_data.max_tokens,
        rules=format_data.rules,
        is_active=format_data.is_active,
        created_by=admin.id
    )

    db.add(format_config)
    db.commit()
    db.refresh(format_config)

    return FormatConfigResponse.model_validate(format_config)


@router.get("/{format_id}", response_model=FormatConfigResponse)
async def get_format(
    format_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get a specific format configuration (Admin only)

    Args:
        format_id: Format ID
        db: Database session
        admin: Admin user

    Returns:
        Format configuration
    """
    format_config = db.query(FormatConfig).filter(FormatConfig.id == format_id).first()

    if not format_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format with ID {format_id} not found"
        )

    return FormatConfigResponse.model_validate(format_config)


@router.put("/{format_id}", response_model=FormatConfigResponse)
async def update_format(
    format_id: int,
    format_data: FormatConfigUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Update a format configuration (Admin only)

    Args:
        format_id: Format ID
        format_data: Updated format data
        db: Database session
        admin: Admin user

    Returns:
        Updated format configuration
    """
    format_config = db.query(FormatConfig).filter(FormatConfig.id == format_id).first()

    if not format_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format with ID {format_id} not found"
        )

    # Check slug uniqueness if being changed
    if format_data.slug and format_data.slug != format_config.slug:
        existing = db.query(FormatConfig).filter(FormatConfig.slug == format_data.slug).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Format with slug '{format_data.slug}' already exists"
            )

    # Update fields
    update_data = format_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(format_config, field, value)

    db.commit()
    db.refresh(format_config)

    return FormatConfigResponse.model_validate(format_config)


@router.delete("/{format_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_format(
    format_id: int,
    hard_delete: bool = False,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Delete a format configuration (Admin only)

    By default, performs soft delete (sets is_active=False).
    Use hard_delete=True to permanently remove.

    Args:
        format_id: Format ID
        hard_delete: Permanently delete instead of soft delete
        db: Database session
        admin: Admin user
    """
    format_config = db.query(FormatConfig).filter(FormatConfig.id == format_id).first()

    if not format_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format with ID {format_id} not found"
        )

    if hard_delete:
        db.delete(format_config)
    else:
        format_config.is_active = False

    db.commit()


@router.post("/{format_id}/restore", response_model=FormatConfigResponse)
async def restore_format(
    format_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Restore a soft-deleted format configuration (Admin only)

    Args:
        format_id: Format ID
        db: Database session
        admin: Admin user

    Returns:
        Restored format configuration
    """
    format_config = db.query(FormatConfig).filter(FormatConfig.id == format_id).first()

    if not format_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format with ID {format_id} not found"
        )

    format_config.is_active = True
    db.commit()
    db.refresh(format_config)

    return FormatConfigResponse.model_validate(format_config)


@router.get("/{format_id}/clients")
async def get_format_clients(
    format_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get all clients that have access to a specific format (Admin only)

    Args:
        format_id: Format ID
        db: Database session
        admin: Admin user

    Returns:
        List of clients using this format
    """
    from app.models.client_config import ClientConfig

    format_config = db.query(FormatConfig).filter(FormatConfig.id == format_id).first()

    if not format_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format with ID {format_id} not found"
        )

    # Get all clients that have this format in their allowed_format_ids
    all_clients = db.query(ClientConfig).filter(ClientConfig.is_active == True).all()

    clients_using_format = []
    for client in all_clients:
        if client.allowed_format_ids and format_id in client.allowed_format_ids:
            clients_using_format.append({
                "id": client.id,
                "name": client.name,
                "slug": client.slug,
                "is_default": client.default_format_id == format_id,
                "display_override": client.display_overrides.get(format_config.slug) if client.display_overrides else None,
            })

    return {
        "format_id": format_id,
        "format_name": format_config.display_name,
        "clients": clients_using_format,
        "total": len(clients_using_format)
    }
