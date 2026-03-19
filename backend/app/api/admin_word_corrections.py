"""
Admin API Endpoints for Word Corrections Configuration
Manage user-editable word corrections stored in config/word_corrections.json
"""

import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List, Optional

from app.models.user import User
from app.middleware.auth import get_admin_user, get_current_active_user
from app.config import get_settings

router = APIRouter()


class BengaliCorrection(BaseModel):
    pattern: str
    replacement: str


class WordCorrectionsData(BaseModel):
    english_to_bengali: Dict[str, str] = {}
    bengali_corrections: List[BengaliCorrection] = []


class WordSuggestion(BaseModel):
    english: str
    bengali: str


def _read_corrections_file() -> dict:
    settings = get_settings()
    path = settings.WORD_CORRECTIONS_PATH
    if not path.exists():
        return {"english_to_bengali": {}, "bengali_corrections": [], "pending_suggestions": []}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if "pending_suggestions" not in data:
        data["pending_suggestions"] = []
    return data


def _write_corrections_file(data: dict):
    settings = get_settings()
    path = settings.WORD_CORRECTIONS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@router.get("", response_model=WordCorrectionsData)
async def get_word_corrections(admin: User = Depends(get_admin_user)):
    """Get current word corrections config (Admin only)"""
    data = _read_corrections_file()
    return WordCorrectionsData(
        english_to_bengali=data.get("english_to_bengali", {}),
        bengali_corrections=[
            BengaliCorrection(pattern=e["pattern"], replacement=e.get("replacement", ""))
            for e in data.get("bengali_corrections", [])
        ]
    )


@router.post("", response_model=WordCorrectionsData)
async def save_word_corrections(
    corrections: WordCorrectionsData,
    admin: User = Depends(get_admin_user)
):
    """Save updated word corrections config (Admin only). Changes apply on next server restart."""
    existing = _read_corrections_file()
    data = {
        "english_to_bengali": corrections.english_to_bengali,
        "bengali_corrections": [
            {"pattern": c.pattern, "replacement": c.replacement}
            for c in corrections.bengali_corrections
        ],
        "pending_suggestions": existing.get("pending_suggestions", []),
    }
    _write_corrections_file(data)
    return corrections


@router.delete("/english/{word}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_english_correction(word: str, admin: User = Depends(get_admin_user)):
    """Delete a single english_to_bengali entry (Admin only)"""
    data = _read_corrections_file()
    e2b = data.get("english_to_bengali", {})
    if word not in e2b:
        raise HTTPException(status_code=404, detail=f"Word '{word}' not found")
    del e2b[word]
    data["english_to_bengali"] = e2b
    _write_corrections_file(data)


@router.delete("/bengali/{index}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bengali_correction(index: int, admin: User = Depends(get_admin_user)):
    """Delete a bengali correction by index (Admin only)"""
    data = _read_corrections_file()
    corrections = data.get("bengali_corrections", [])
    if index < 0 or index >= len(corrections):
        raise HTTPException(status_code=404, detail=f"Index {index} out of range")
    corrections.pop(index)
    data["bengali_corrections"] = corrections
    _write_corrections_file(data)


@router.post("/suggest")
async def suggest_word(
    suggestion: WordSuggestion,
    current_user: User = Depends(get_current_active_user),
):
    """Submit an English→Bengali word suggestion (any authenticated user)"""
    english = suggestion.english.strip()
    bengali = suggestion.bengali.strip()
    if not english or not bengali:
        raise HTTPException(status_code=400, detail="Both english and bengali fields are required")

    data = _read_corrections_file()
    entry = {
        "id": str(uuid.uuid4()),
        "english": english,
        "bengali": bengali,
        "suggested_by": current_user.email,
        "suggested_at": datetime.now(timezone.utc).isoformat(),
    }
    data["pending_suggestions"].append(entry)
    _write_corrections_file(data)
    return {"success": True, "message": "Suggestion submitted"}


@router.get("/suggestions")
async def get_suggestions(admin: User = Depends(get_admin_user)):
    """Get all pending word suggestions (Admin only)"""
    data = _read_corrections_file()
    return data.get("pending_suggestions", [])


@router.post("/suggestions/{suggestion_id}/approve")
async def approve_suggestion(suggestion_id: str, admin: User = Depends(get_admin_user)):
    """Approve a pending suggestion — moves it to english_to_bengali (Admin only)"""
    data = _read_corrections_file()
    suggestions = data.get("pending_suggestions", [])
    match = next((s for s in suggestions if s["id"] == suggestion_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    data["english_to_bengali"][match["english"]] = match["bengali"]
    data["pending_suggestions"] = [s for s in suggestions if s["id"] != suggestion_id]
    _write_corrections_file(data)

    # Reload text_processor corrections so the new word is applied immediately
    try:
        from app.core.text_processor import _load_user_word_corrections
        _load_user_word_corrections()
    except Exception:
        pass  # Non-fatal — takes effect on next request anyway

    return {"success": True, "message": "Suggestion approved and added to corrections"}


@router.delete("/suggestions/{suggestion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def reject_suggestion(suggestion_id: str, admin: User = Depends(get_admin_user)):
    """Reject (delete) a pending suggestion (Admin only)"""
    data = _read_corrections_file()
    suggestions = data.get("pending_suggestions", [])
    if not any(s["id"] == suggestion_id for s in suggestions):
        raise HTTPException(status_code=404, detail="Suggestion not found")
    data["pending_suggestions"] = [s for s in suggestions if s["id"] != suggestion_id]
    _write_corrections_file(data)
