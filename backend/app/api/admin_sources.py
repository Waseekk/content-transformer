"""
Admin API Endpoints for Source (Sites) Management
Manage news sources in config/sites_config.json
"""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.article import Article
from app.middleware.auth import get_admin_user
from app.config import get_settings

router = APIRouter()


def _read_sites_config() -> list:
    settings = get_settings()
    path = settings.SITES_CONFIG_PATH
    if not path.exists():
        return []
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data if isinstance(data, list) else data.get('sites', [])


def _write_sites_config(sites: list):
    settings = get_settings()
    path = settings.SITES_CONFIG_PATH
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sites, f, ensure_ascii=False, indent=2)


@router.get("", response_model=dict)
async def list_sources(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List all configured news sources with article counts (Admin only)"""
    sites = _read_sites_config()

    # Count articles per source across all users
    counts_rows = db.query(
        Article.source,
        func.count(Article.id).label('count')
    ).group_by(Article.source).all()
    count_map = {source: count for source, count in counts_rows}

    result = []
    for site in sites:
        result.append({
            "name": site["name"],
            "description": site.get("description", ""),
            "url": site.get("url", ""),
            "language": site.get("language", "en"),
            "disabled": site.get("disabled", False),
            "article_count": count_map.get(site["name"], 0),
        })

    return {"sources": result, "total": len(result)}


@router.patch("/{name}/disable", response_model=dict)
async def disable_source(name: str, admin: User = Depends(get_admin_user)):
    """Disable a source (Admin only) — won't be scraped or shown in filters"""
    sites = _read_sites_config()
    for site in sites:
        if site["name"] == name:
            site["disabled"] = True
            _write_sites_config(sites)
            return {"success": True, "name": name, "disabled": True}
    raise HTTPException(status_code=404, detail=f"Source '{name}' not found")


@router.patch("/{name}/enable", response_model=dict)
async def enable_source(name: str, admin: User = Depends(get_admin_user)):
    """Enable a disabled source (Admin only)"""
    sites = _read_sites_config()
    for site in sites:
        if site["name"] == name:
            site["disabled"] = False
            _write_sites_config(sites)
            return {"success": True, "name": name, "disabled": False}
    raise HTTPException(status_code=404, detail=f"Source '{name}' not found")


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(name: str, admin: User = Depends(get_admin_user)):
    """Permanently remove a source from sites_config.json (Admin only)"""
    sites = _read_sites_config()
    filtered = [s for s in sites if s["name"] != name]
    if len(filtered) == len(sites):
        raise HTTPException(status_code=404, detail=f"Source '{name}' not found")
    _write_sites_config(filtered)
