"""
Scraper Service
User-specific scraping with job tracking and database storage
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any, Callable
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.article import Article
from app.models.job import Job
from app.models.user_config import UserConfig
from app.config import get_settings  # Backend-specific Pydantic settings

# Import scraper from backend's core module
from app.core.scraper import MultiSiteScraper

settings = get_settings()


class ScraperService:
    """Service for user-specific news scraping"""

    @staticmethod
    def get_user_sites(db: Session, user: User) -> List[str]:
        """
        Get list of sites enabled for user

        Args:
            db: Database session
            user: User object

        Returns:
            List of enabled site names
        """
        config = db.query(UserConfig).filter(UserConfig.user_id == user.id).first()
        if config and config.enabled_sites:
            return config.enabled_sites
        return []

    @staticmethod
    def get_all_available_sites() -> List[Dict[str, Any]]:
        """
        Get all available scraper sites from configuration

        Returns:
            List of site configurations
        """
        import json

        if settings.SITES_CONFIG_PATH.exists():
            with open(settings.SITES_CONFIG_PATH, 'r', encoding='utf-8') as f:
                sites_config = json.load(f)
                # sites_config can be either a list or a dict with 'sites' key
                if isinstance(sites_config, list):
                    return sites_config
                return sites_config.get('sites', [])
        return []

    @staticmethod
    def create_scraper_job(db: Session, user: User, sites: Optional[List[str]] = None) -> Job:
        """
        Create a scraper job in the database

        Args:
            db: Database session
            user: User object
            sites: Specific sites to scrape (optional)

        Returns:
            Job object
        """
        job = Job(
            user_id=user.id,
            job_type="scrape",
            status="pending",
            progress=0,
            status_message="Initializing scraper...",
            result={"sites": sites or ScraperService.get_user_sites(db, user)}
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def update_job_status(db: Session, job: Job, status: str, progress: int = None,
                         message: str = None, error: str = None):
        """
        Update job status

        Args:
            db: Database session
            job: Job object
            status: New status
            progress: Progress percentage
            message: Status message
            error: Error message if failed
        """
        job.update_status(status, progress, message)
        if error:
            job.error = error
        db.commit()
        db.refresh(job)

    @staticmethod
    def run_scraper_sync(db: Session, user: User, job: Job, sites: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run scraper synchronously and save results

        Args:
            db: Database session
            user: User object
            job: Job object
            sites: Specific sites to scrape

        Returns:
            Dictionary with scraping results
        """
        try:
            # Update job to running
            ScraperService.update_job_status(db, job, "running", 0, "Starting scraper...")

            # Get user's enabled sites
            user_sites = sites or ScraperService.get_user_sites(db, user)

            if not user_sites:
                ScraperService.update_job_status(
                    db, job, "failed", 0,
                    error="No sites enabled for this user. Please contact admin."
                )
                return {"success": False, "error": "No sites enabled"}

            # Initialize scraper first to get actual site count
            scraper = MultiSiteScraper(
                status_callback=None,  # Set callback after
                enabled_sites=user_sites  # Only scrape user's enabled sites
            )

            # Get actual total sites from scraper config
            total_sites_count = len(scraper.sites_config)

            # Set initial result with total_sites
            initial_result = job.result or {}
            initial_result['sites'] = [s['name'] for s in scraper.sites_config]
            initial_result['total_sites'] = total_sites_count
            initial_result['sites_completed'] = 0
            initial_result['site_stats'] = {}
            job.result = initial_result
            db.commit()

            # Create status callback to update job progress
            def status_callback(status_obj):
                """Update job progress from scraper status"""
                # Update job with current progress and site stats
                job.progress = status_obj.progress
                job.status_message = status_obj.status_message

                # Store real-time stats in result for SSE to read
                current_result = job.result or {}
                current_result['current_site'] = status_obj.current_site
                current_result['articles_count'] = status_obj.articles_count
                current_result['site_stats'] = status_obj.site_stats
                current_result['sites_completed'] = len(status_obj.site_stats)
                current_result['total_sites'] = total_sites_count  # Keep total_sites
                job.result = current_result

                db.commit()

            # Set the callback on the scraper
            scraper.status_callback = status_callback

            # Run scraping (this will only scrape enabled sites)
            articles_list, filepath = scraper.scrape_all_sites()

            # Articles are already filtered by enabled sites in the scraper
            filtered_articles = articles_list

            ScraperService.update_job_status(
                db, job, "running", 80,
                f"Saving {len(filtered_articles)} articles to database..."
            )

            # Save articles to database
            saved_count = 0
            for article_data in filtered_articles:
                article = Article(
                    user_id=user.id,
                    job_id=job.id,  # Link article to this scraping job
                    source=article_data.get('source'),
                    publisher=article_data.get('publisher'),
                    headline=article_data.get('headline', article_data.get('title')),
                    article_url=article_data.get('article_url', article_data.get('link')),
                    published_time=article_data.get('published_time'),
                    country=article_data.get('country'),
                    view=article_data.get('view'),
                    extra_data=article_data,
                    scraped_at=datetime.utcnow()
                )
                db.add(article)
                saved_count += 1

            db.commit()

            # Prepare result
            articles_by_site = {}
            for article in filtered_articles:
                source = article.get('source', 'unknown')
                articles_by_site[source] = articles_by_site.get(source, 0) + 1

            result = {
                "success": True,
                "total_articles": len(filtered_articles),
                "articles_saved": saved_count,
                "articles_by_site": articles_by_site,
                "file_path": str(filepath) if filepath else None
            }

            # Update job to completed
            job.result = result
            ScraperService.update_job_status(
                db, job, "completed", 100,
                f"Scraping completed! Saved {saved_count} articles."
            )

            return result

        except Exception as e:
            # Update job to failed
            ScraperService.update_job_status(
                db, job, "failed", job.progress,
                error=str(e)
            )
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_job_status(db: Session, user: User, job_id: int) -> Optional[Job]:
        """
        Get job status for user

        Args:
            db: Database session
            user: User object
            job_id: Job ID

        Returns:
            Job object or None
        """
        return db.query(Job).filter(
            Job.id == job_id,
            Job.user_id == user.id
        ).first()

    @staticmethod
    def get_user_jobs(db: Session, user: User, job_type: str = None, limit: int = 10) -> List[Job]:
        """
        Get user's recent jobs

        Args:
            db: Database session
            user: User object
            job_type: Filter by job type (optional)
            limit: Maximum jobs to return

        Returns:
            List of Job objects
        """
        query = db.query(Job).filter(Job.user_id == user.id)

        if job_type:
            query = query.filter(Job.job_type == job_type)

        return query.order_by(Job.created_at.desc()).limit(limit).all()
