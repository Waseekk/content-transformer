"""
User Configuration API Endpoints
Get user's client config, allowed formats, and UI settings
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.format_config import FormatConfig
from app.models.client_config import ClientConfig
from app.middleware.auth import get_current_active_user
from app.schemas.client_config import UserClientConfigResponse
from app.schemas.format_config import FormatConfigForEnhancer

router = APIRouter()


def get_default_formats(db: Session) -> List[FormatConfig]:
    """Get default formats when user has no client config"""
    return db.query(FormatConfig).filter(
        FormatConfig.is_active == True,
        FormatConfig.slug.in_(["hard_news", "soft_news"])
    ).order_by(FormatConfig.id).all()


def get_default_ui_settings() -> dict:
    """Get default UI settings"""
    return {
        "show_content_preview": True,
        "workflow_type": "full",
        "show_format_selection": True,
        "app_title": "Swiftor"
    }


@router.get("/config", response_model=UserClientConfigResponse)
async def get_user_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's configuration

    Returns client config, allowed formats, UI settings.
    If user has no assigned client, returns default config.
    """
    # User has a client config assigned
    if current_user.client_config_id:
        client_config = db.query(ClientConfig).filter(
            ClientConfig.id == current_user.client_config_id
        ).first()

        if client_config and client_config.is_active:
            # Get allowed formats
            formats = []
            if client_config.allowed_format_ids:
                formats = db.query(FormatConfig).filter(
                    FormatConfig.id.in_(client_config.allowed_format_ids),
                    FormatConfig.is_active == True
                ).order_by(FormatConfig.id).all()

            # Get default format
            default_format = None
            if client_config.default_format_id:
                default_format = db.query(FormatConfig).filter(
                    FormatConfig.id == client_config.default_format_id,
                    FormatConfig.is_active == True
                ).first()

            # Apply display overrides
            format_list = []
            for f in formats:
                format_data = FormatConfigForEnhancer.model_validate(f)
                # Override display name if client has custom name
                if client_config.display_overrides and f.slug in client_config.display_overrides:
                    format_data.display_name = client_config.display_overrides[f.slug]
                format_list.append(format_data)

            default_format_data = None
            if default_format:
                default_format_data = FormatConfigForEnhancer.model_validate(default_format)
                if client_config.display_overrides and default_format.slug in client_config.display_overrides:
                    default_format_data.display_name = client_config.display_overrides[default_format.slug]

            return UserClientConfigResponse(
                client=client_config,
                formats=format_list,
                default_format=default_format_data,
                ui_settings=client_config.ui_settings or get_default_ui_settings(),
                display_overrides=client_config.display_overrides or {}
            )

    # No client config - return defaults
    default_formats = get_default_formats(db)

    return UserClientConfigResponse(
        client=None,
        formats=[FormatConfigForEnhancer.model_validate(f) for f in default_formats],
        default_format=FormatConfigForEnhancer.model_validate(default_formats[0]) if default_formats else None,
        ui_settings=get_default_ui_settings(),
        display_overrides={}
    )


@router.get("/formats", response_model=List[FormatConfigForEnhancer])
async def get_user_formats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get formats available to the current user

    Returns filtered list based on user's client config.
    """
    # User has a client config assigned
    if current_user.client_config_id:
        client_config = db.query(ClientConfig).filter(
            ClientConfig.id == current_user.client_config_id
        ).first()

        if client_config and client_config.is_active and client_config.allowed_format_ids:
            formats = db.query(FormatConfig).filter(
                FormatConfig.id.in_(client_config.allowed_format_ids),
                FormatConfig.is_active == True
            ).order_by(FormatConfig.id).all()

            format_list = []
            for f in formats:
                format_data = FormatConfigForEnhancer.model_validate(f)
                if client_config.display_overrides and f.slug in client_config.display_overrides:
                    format_data.display_name = client_config.display_overrides[f.slug]
                format_list.append(format_data)

            return format_list

    # No client config - return default formats
    default_formats = get_default_formats(db)
    return [FormatConfigForEnhancer.model_validate(f) for f in default_formats]
