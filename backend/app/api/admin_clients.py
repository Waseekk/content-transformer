"""
Admin API Endpoints for Client Configuration
CRUD operations for managing client configurations and user assignments
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.client_config import ClientConfig
from app.models.format_config import FormatConfig
from app.models.user import User
from app.middleware.auth import get_admin_user
from app.schemas.client_config import (
    ClientConfigCreate,
    ClientConfigUpdate,
    ClientConfigResponse,
    ClientConfigListResponse,
    UserAssignClientRequest,
)

router = APIRouter()


@router.get("", response_model=ClientConfigListResponse)
async def list_clients(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    List all client configurations (Admin only)

    Args:
        include_inactive: Include inactive clients
        db: Database session
        admin: Admin user

    Returns:
        List of client configurations
    """
    query = db.query(ClientConfig)

    if not include_inactive:
        query = query.filter(ClientConfig.is_active == True)

    clients = query.order_by(ClientConfig.id).all()

    return ClientConfigListResponse(
        clients=[ClientConfigResponse.model_validate(c) for c in clients],
        total=len(clients)
    )


@router.post("", response_model=ClientConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientConfigCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Create a new client configuration (Admin only)

    Args:
        client_data: Client configuration data
        db: Database session
        admin: Admin user

    Returns:
        Created client configuration
    """
    # Check if slug already exists
    existing = db.query(ClientConfig).filter(ClientConfig.slug == client_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Client with slug '{client_data.slug}' already exists"
        )

    # Validate allowed_format_ids exist
    if client_data.allowed_format_ids:
        existing_formats = db.query(FormatConfig.id).filter(
            FormatConfig.id.in_(client_data.allowed_format_ids)
        ).all()
        existing_ids = {f.id for f in existing_formats}
        invalid_ids = set(client_data.allowed_format_ids) - existing_ids
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid format IDs: {invalid_ids}"
            )

    # Validate default_format_id exists and is in allowed list
    if client_data.default_format_id:
        if client_data.allowed_format_ids and client_data.default_format_id not in client_data.allowed_format_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Default format must be in allowed formats list"
            )
        default_format = db.query(FormatConfig).filter(FormatConfig.id == client_data.default_format_id).first()
        if not default_format:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Default format ID {client_data.default_format_id} not found"
            )

    # Create client config
    client_config = ClientConfig(
        name=client_data.name,
        slug=client_data.slug,
        allowed_format_ids=client_data.allowed_format_ids,
        default_format_id=client_data.default_format_id,
        ui_settings=client_data.ui_settings,
        display_overrides=client_data.display_overrides,
        is_active=client_data.is_active
    )

    db.add(client_config)
    db.commit()
    db.refresh(client_config)

    return ClientConfigResponse.model_validate(client_config)


@router.get("/{client_id}", response_model=ClientConfigResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get a specific client configuration (Admin only)

    Args:
        client_id: Client ID
        db: Database session
        admin: Admin user

    Returns:
        Client configuration
    """
    client_config = db.query(ClientConfig).filter(ClientConfig.id == client_id).first()

    if not client_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    return ClientConfigResponse.model_validate(client_config)


@router.put("/{client_id}", response_model=ClientConfigResponse)
async def update_client(
    client_id: int,
    client_data: ClientConfigUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Update a client configuration (Admin only)

    Args:
        client_id: Client ID
        client_data: Updated client data
        db: Database session
        admin: Admin user

    Returns:
        Updated client configuration
    """
    client_config = db.query(ClientConfig).filter(ClientConfig.id == client_id).first()

    if not client_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    # Check slug uniqueness if being changed
    if client_data.slug and client_data.slug != client_config.slug:
        existing = db.query(ClientConfig).filter(ClientConfig.slug == client_data.slug).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Client with slug '{client_data.slug}' already exists"
            )

    # Validate allowed_format_ids if provided
    if client_data.allowed_format_ids is not None:
        existing_formats = db.query(FormatConfig.id).filter(
            FormatConfig.id.in_(client_data.allowed_format_ids)
        ).all()
        existing_ids = {f.id for f in existing_formats}
        invalid_ids = set(client_data.allowed_format_ids) - existing_ids
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid format IDs: {invalid_ids}"
            )

    # Validate default_format_id if provided
    if client_data.default_format_id is not None:
        allowed_ids = client_data.allowed_format_ids if client_data.allowed_format_ids is not None else client_config.allowed_format_ids
        if allowed_ids and client_data.default_format_id not in allowed_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Default format must be in allowed formats list"
            )

    # Update fields
    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client_config, field, value)

    db.commit()
    db.refresh(client_config)

    return ClientConfigResponse.model_validate(client_config)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    hard_delete: bool = False,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Delete a client configuration (Admin only)

    By default, performs soft delete (sets is_active=False).
    Use hard_delete=True to permanently remove.

    Args:
        client_id: Client ID
        hard_delete: Permanently delete instead of soft delete
        db: Database session
        admin: Admin user
    """
    client_config = db.query(ClientConfig).filter(ClientConfig.id == client_id).first()

    if not client_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    if hard_delete:
        # Unassign users from this client first
        db.query(User).filter(User.client_config_id == client_id).update(
            {User.client_config_id: None}
        )
        db.delete(client_config)
    else:
        client_config.is_active = False

    db.commit()


@router.get("/users/all")
async def list_all_users_with_clients(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    List all users with their client assignments (Admin only)

    Returns all users with their current client config info.
    """
    users = db.query(User).order_by(User.id).all()

    result = []
    for u in users:
        client_info = None
        if u.client_config_id:
            client = db.query(ClientConfig).filter(ClientConfig.id == u.client_config_id).first()
            if client:
                client_info = {
                    "id": client.id,
                    "name": client.name,
                    "slug": client.slug,
                }

        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "is_admin": u.is_admin,
            "client_config_id": u.client_config_id,
            "client": client_info,
        })

    return result


@router.get("/{client_id}/users", response_model=List[dict])
async def list_client_users(
    client_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    List users assigned to a client (Admin only)

    Args:
        client_id: Client ID
        db: Database session
        admin: Admin user

    Returns:
        List of users assigned to this client
    """
    client_config = db.query(ClientConfig).filter(ClientConfig.id == client_id).first()

    if not client_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    users = db.query(User).filter(User.client_config_id == client_id).all()

    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "is_admin": u.is_admin,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.post("/users/{user_id}/assign")
async def assign_user_to_client(
    user_id: int,
    request: UserAssignClientRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Assign a user to a client configuration (Admin only)

    Args:
        user_id: User ID to assign
        request: Client config ID (null to unassign)
        db: Database session
        admin: Admin user

    Returns:
        Success message
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    if request.client_config_id is not None:
        # Validate client config exists
        client_config = db.query(ClientConfig).filter(ClientConfig.id == request.client_config_id).first()
        if not client_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client config with ID {request.client_config_id} not found"
            )
        if not client_config.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign user to inactive client"
            )

    user.client_config_id = request.client_config_id
    db.commit()

    return {
        "message": "User assigned successfully" if request.client_config_id else "User unassigned successfully",
        "user_id": user_id,
        "client_config_id": request.client_config_id
    }
