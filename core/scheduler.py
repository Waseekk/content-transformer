"""
Automated Scraping Scheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from pathlib import Path
import threading

# Import settings and logger
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import SCHEDULER_CONFIG
from utils.logger import get_scheduler_logger
from core.scraper import run_scraper

logger = get_scheduler_logger()


class ScraperScheduler:
    """Manage automated scraping schedules"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=SCHEDULER_CONFIG['timezone'])
        self.is_running = False
        self.current_job = None
        self.interval_hours = SCHEDULER_CONFIG['default_interval']
        self.next_run_time = None
        self.last_run_time = None
        self.run_count = 0
        self.status_callback = None
        
        logger.info("ScraperScheduler initialized")
    
    def set_status_callback(self, callback):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def _run_scraping_job(self):
        """Internal method to run scraping job"""
        self.last_run_time = datetime.now()
        self.run_count += 1
        
        logger.info(f"Scheduled scraping job #{self.run_count} started")
        
        try:
            # Run scraper in separate thread
            articles, filepath = run_scraper(status_callback=self.status_callback)
            
            logger.info(f"Scheduled job completed: {len(articles)} articles scraped")
            
            # Update next run time
            if self.current_job:
                self.next_run_time = self.current_job.next_run_time
            
        except Exception as e:
            logger.error(f"Scheduled job failed: {e}", exc_info=True)
    
    def start(self, interval_hours=None):
        """
        Start scheduler
        
        Args:
            interval_hours: Scraping interval in hours
        """
        if self.is_running:
            logger.warning("Scheduler already running")
            return False
        
        if interval_hours:
            self.interval_hours = interval_hours
        
        # Remove existing job if any
        if self.current_job:
            self.current_job.remove()
        
        # Add new job
        self.current_job = self.scheduler.add_job(
            func=self._run_scraping_job,
            trigger=IntervalTrigger(hours=self.interval_hours),
            id='scraping_job',
            name=f'Scrape every {self.interval_hours}h',
            replace_existing=True
        )
        
        # Start scheduler
        if not self.scheduler.running:
            self.scheduler.start()
        
        self.is_running = True
        self.next_run_time = self.current_job.next_run_time
        
        logger.info(f"Scheduler started: Interval={self.interval_hours}h, Next run={self.next_run_time}")
        
        return True
    
    def stop(self):
        """Stop scheduler"""
        if not self.is_running:
            logger.warning("Scheduler not running")
            return False
        
        if self.current_job:
            self.current_job.remove()
            self.current_job = None
        
        self.is_running = False
        self.next_run_time = None
        
        logger.info("Scheduler stopped")
        
        return True
    
    def change_interval(self, new_interval_hours):
        """
        Change scraping interval
        
        Args:
            new_interval_hours: New interval in hours
        """
        if not self.is_running:
            logger.warning("Scheduler not running. Start it first.")
            return False
        
        logger.info(f"Changing interval from {self.interval_hours}h to {new_interval_hours}h")
        
        # Stop and restart with new interval
        self.stop()
        self.start(interval_hours=new_interval_hours)
        
        return True
    
    def run_now(self):
        """Trigger immediate scraping (doesn't affect schedule)"""
        logger.info("Manual scraping triggered")
        
        # Run in separate thread so it doesn't block
        thread = threading.Thread(target=self._run_scraping_job)
        thread.start()
        
        return True
    
    def get_status(self):
        """Get scheduler status"""
        return {
            'is_running': self.is_running,
            'interval_hours': self.interval_hours,
            'next_run': self.next_run_time.isoformat() if self.next_run_time else None,
            'last_run': self.last_run_time.isoformat() if self.last_run_time else None,
            'run_count': self.run_count,
            'time_until_next': self._time_until_next_run()
        }
    
    def _time_until_next_run(self):
        """Calculate time until next run"""
        if not self.next_run_time:
            return None
        
        delta = self.next_run_time - datetime.now(self.next_run_time.tzinfo)
        
        if delta.total_seconds() < 0:
            return "Overdue"
        
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def shutdown(self):
        """Shutdown scheduler completely"""
        if self.scheduler.running:
            self.scheduler.shutdown()
        
        self.is_running = False
        logger.info("Scheduler shutdown")


# Global scheduler instance
_scheduler_instance = None

def get_scheduler():
    """Get global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = ScraperScheduler()
    return _scheduler_instance


if __name__ == "__main__":
    # Test scheduler
    print("Testing scheduler...")
    
    scheduler = get_scheduler()
    
    # Start with 1 hour interval for testing
    scheduler.start(interval_hours=0.1)  # 6 minutes for testing
    
    print(f"Scheduler started: {scheduler.get_status()}")
    print("Scheduler is running. Press Ctrl+C to stop.")
    
    try:
        # Keep running
        import time
        while True:
            time.sleep(10)
            status = scheduler.get_status()
            print(f"Status: {status}")
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.shutdown()
        print("Scheduler stopped")