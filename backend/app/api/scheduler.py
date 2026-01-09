"""
Scheduler API Endpoints
Manages automated scraping schedule
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.services.scheduler_service import SchedulerService

router = APIRouter()

# Request/Response Models
class SchedulerStartRequest(BaseModel):
    interval_hours: float  # Allow fractional hours (e.g., 0.5 = 30 min)

class SchedulerStatusResponse(BaseModel):
    is_running: bool
    interval_hours: Optional[float] = None
    next_run_time: Optional[str] = None
    time_until_next: Optional[str] = None
    run_count: int
    last_run_time: Optional[str] = None
    last_run_articles: Optional[int] = None

class SchedulerHistoryItem(BaseModel):
    run_time: str
    articles_count: int
    duration_seconds: float
    status: str

# Global scheduler service instance
scheduler_service = SchedulerService()

@router.post("/start")
async def start_scheduler(
    request: SchedulerStartRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Start the automated scraping scheduler"""

    if request.interval_hours < 0.0167 or request.interval_hours > 24:  # Min 1 minute for testing
        raise HTTPException(status_code=400, detail="Interval must be between 1 minute and 24 hours")

    try:
        scheduler_service.start(interval_hours=request.interval_hours, user_id=current_user.id)

        status = scheduler_service.get_status()

        return {
            "message": "Scheduler started successfully",
            "is_running": status["is_running"],
            "interval_hours": status["interval_hours"],
            "next_run_time": status.get("next_run_time"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")


@router.post("/stop")
async def stop_scheduler(
    current_user: User = Depends(get_current_active_user),
):
    """Stop the automated scraping scheduler"""

    try:
        scheduler_service.stop()

        return {
            "message": "Scheduler stopped successfully",
            "is_running": False,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")


@router.get("/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status(
    current_user: User = Depends(get_current_active_user),
):
    """Get current scheduler status"""

    status = scheduler_service.get_status()

    return SchedulerStatusResponse(
        is_running=status["is_running"],
        interval_hours=status.get("interval_hours"),
        next_run_time=status.get("next_run_time"),
        time_until_next=status.get("time_until_next", "N/A"),
        run_count=status.get("run_count", 0),
        last_run_time=status.get("last_run_time"),
        last_run_articles=status.get("last_run_articles"),
    )


@router.get("/history")
async def get_scheduler_history(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
):
    """Get scheduler run history"""

    history = scheduler_service.get_history(limit=limit)

    return {
        "history": history,
        "total": len(history),
    }
