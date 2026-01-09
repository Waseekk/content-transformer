"""
Scheduler Service
Manages automated scraping schedule using APScheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging

from app.core.scraper import MultiSiteScraper

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Manages automated scraping schedule
    Singleton pattern - only one scheduler instance per application
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.interval_hours: Optional[float] = None
        self.run_count = 0
        self.last_run_time: Optional[datetime] = None
        self.last_run_articles: Optional[int] = None
        self.history: List[Dict] = []
        self.current_user_id: Optional[int] = None

        self._initialized = True
        logger.info("Scheduler service initialized")

    def start(self, interval_hours: float, user_id: int):
        """Start the scheduler with given interval"""

        if self.is_running:
            self.stop()

        self.interval_hours = interval_hours
        self.current_user_id = user_id

        # Convert hours to minutes for more precision
        interval_minutes = int(interval_hours * 60)
        if interval_minutes < 1:
            interval_minutes = 1  # Minimum 1 minute

        # Add job with interval trigger (use minutes for precision)
        self.scheduler.add_job(
            func=self._run_scraper_job,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id='scraper_job',
            replace_existing=True,
            max_instances=1,
        )

        if not self.scheduler.running:
            self.scheduler.start()

        self.is_running = True
        logger.info(f"Scheduler started with interval: {interval_minutes} minutes for user {user_id}")

    def stop(self):
        """Stop the scheduler"""

        if self.scheduler.running:
            try:
                self.scheduler.remove_job('scraper_job')
            except:
                pass

        self.is_running = False
        logger.info("Scheduler stopped")

    def _run_scraper_job(self):
        """Execute scraper job (called by scheduler)"""

        logger.info("Scheduled scraper job started")
        start_time = datetime.now()

        try:
            scraper = MultiSiteScraper()
            articles = scraper.scrape_all_sites()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            self.run_count += 1
            self.last_run_time = end_time
            self.last_run_articles = len(articles)

            # Add to history
            self.history.insert(0, {
                "run_time": end_time.isoformat(),
                "articles_count": len(articles),
                "duration_seconds": duration,
                "status": "success",
            })

            # Keep only last 50 runs in history
            self.history = self.history[:50]

            logger.info(f"Scheduled scraper job completed: {len(articles)} articles in {duration:.1f}s")

        except Exception as e:
            logger.error(f"Scheduled scraper job failed: {e}")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            self.history.insert(0, {
                "run_time": end_time.isoformat(),
                "articles_count": 0,
                "duration_seconds": duration,
                "status": "failed",
                "error": str(e),
            })

    def get_status(self) -> Dict:
        """Get current scheduler status"""

        next_run_time = None
        time_until_next = "N/A"

        if self.is_running and self.scheduler.running:
            try:
                job = self.scheduler.get_job('scraper_job')
                if job and job.next_run_time:
                    next_run_time = job.next_run_time.isoformat()

                    # Calculate time until next run
                    delta = job.next_run_time - datetime.now(job.next_run_time.tzinfo)
                    hours = int(delta.total_seconds() // 3600)
                    minutes = int((delta.total_seconds() % 3600) // 60)

                    if hours > 0:
                        time_until_next = f"{hours}h {minutes}m"
                    else:
                        time_until_next = f"{minutes}m"

            except:
                pass

        return {
            "is_running": self.is_running,
            "interval_hours": self.interval_hours,
            "next_run_time": next_run_time,
            "time_until_next": time_until_next,
            "run_count": self.run_count,
            "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
            "last_run_articles": self.last_run_articles,
        }

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get scheduler run history"""
        return self.history[:limit]
