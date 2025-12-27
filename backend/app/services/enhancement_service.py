
"""
Enhancement Service
Multi-format content generation with job tracking
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from pathlib import Path
from math import ceil

from app.models.user import User
from app.models.translation import Translation
from app.models.enhancement import Enhancement
from app.models.job import Job
from app.models.token_usage import TokenUsage
from app.models.user_config import UserConfig
from app.core.enhancer import ContentEnhancer
from app.config import get_settings

settings = get_settings()


class EnhancementService:
    """Service for content enhancement operations"""

    @staticmethod
    def get_user_allowed_formats(db: Session, user: User) -> List[str]:
        """
        Get formats user has access to based on subscription tier

        Args:
            db: Database session
            user: User object

        Returns:
            List of allowed format names
        """
        config = db.query(UserConfig).filter(UserConfig.user_id == user.id).first()

        if config and config.allowed_formats:
            return config.allowed_formats

        # Default based on tier
        return UserConfig.get_default_formats(user.subscription_tier)

    @staticmethod
    def validate_formats(db: Session, user: User, requested_formats: List[str]) -> Dict[str, Any]:
        """
        Validate if user has access to requested formats

        Args:
            db: Database session
            user: User object
            requested_formats: List of format names

        Returns:
            Dictionary with validation result
        """
        allowed_formats = EnhancementService.get_user_allowed_formats(db, user)

        invalid_formats = [f for f in requested_formats if f not in allowed_formats]

        if invalid_formats:
            return {
                'valid': False,
                'error': f"Formats not available in your plan: {', '.join(invalid_formats)}",
                'allowed_formats': allowed_formats
            }

        return {
            'valid': True,
            'allowed_formats': allowed_formats
        }

    @staticmethod
    def create_enhancement_job(
        db: Session,
        user: User,
        translation_id: int,
        formats: List[str]
    ) -> Job:
        """
        Create enhancement job in database

        Args:
            db: Database session
            user: User object
            translation_id: Translation ID
            formats: List of formats to generate

        Returns:
            Job object
        """
        job = Job(
            user_id=user.id,
            job_type="enhance",
            status="pending",
            progress=0,
            status_message="Initializing enhancement...",
            result={
                "translation_id": translation_id,
                "formats": formats,
                "formats_completed": []
            }
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def run_enhancement_sync(
        db: Session,
        user: User,
        job: Job,
        translation_id: int,
        formats: List[str],
        provider: str = 'openai',
        model: Optional[str] = None,
        save_to_files: bool = True
    ) -> Dict[str, Any]:
        """
        Run enhancement synchronously

        Args:
            db: Database session
            user: User object
            job: Job object
            translation_id: Translation ID
            formats: List of formats to generate
            provider: AI provider
            model: Model name
            save_to_files: Save to files flag

        Returns:
            Dictionary with enhancement results
        """
        try:
            # Update job to running
            job.update_status("running", 0, "Loading translation...")
            db.commit()

            # Get translation
            translation = db.query(Translation).filter(
                Translation.id == translation_id,
                Translation.user_id == user.id
            ).first()

            if not translation:
                job.update_status("failed", 0, error="Translation not found")
                db.commit()
                return {"success": False, "error": "Translation not found"}

            # Estimate total tokens needed
            estimated_tokens_per_format = 500
            estimated_total = estimated_tokens_per_format * len(formats)

            if not user.has_tokens(estimated_total):
                job.update_status("failed", 0, error="Insufficient tokens")
                db.commit()
                return {
                    "success": False,
                    "error": f"Insufficient tokens. Need ~{estimated_total}, have {user.tokens_remaining}"
                }

            # Prepare article info
            extra_data = translation.extra_data or {}
            article_info = {
                'headline': extra_data.get('headline', 'Untitled'),
                'publisher': extra_data.get('publisher', 'Unknown'),
                'country': extra_data.get('country', 'Bangladesh'),
                'article_url': extra_data.get('article_url', '')
            }

            translated_text = translation.translated_text

            # Initialize enhancer
            enhancer = ContentEnhancer(provider_name=provider, model=model)

            # Progress callback
            def progress_callback(format_type, progress, result):
                job.update_status("running", progress, f"Generating {format_type}...")
                db.commit()

            # Generate enhancements
            job.update_status("running", 10, "Starting content generation...")
            db.commit()

            results = enhancer.enhance_all_formats(
                translated_text=translated_text,
                article_info=article_info,
                formats=formats,
                progress_callback=progress_callback
            )

            # Save to database
            job.update_status("running", 90, "Saving to database...")
            db.commit()

            total_tokens = 0
            saved_enhancements = []

            for format_type, result in results.items():
                if not result.success:
                    continue

                enhancement = Enhancement(
                    user_id=user.id,
                    translation_id=translation_id,
                    format_type=format_type,
                    content=result.content,
                    provider=provider,
                    model=model or enhancer.model,
                    tokens_used=result.tokens_used
                )

                db.add(enhancement)
                saved_enhancements.append(enhancement)
                total_tokens += result.tokens_used

                # Log token usage
                token_log = TokenUsage(
                    user_id=user.id,
                    operation='enhance',
                    provider=provider,
                    model=model or enhancer.model,
                    tokens_used=result.tokens_used,
                    cost_usd=TokenUsage.calculate_cost(
                        provider,
                        model or enhancer.model,
                        result.tokens_used
                    )
                )
                db.add(token_log)

            # Deduct tokens
            if not user.deduct_tokens(total_tokens):
                job.update_status("failed", 90, error="Failed to deduct tokens")
                db.rollback()
                return {"success": False, "error": "Token deduction failed"}

            db.commit()

            # Save to files if requested
            saved_files = {}
            if save_to_files:
                job.update_status("running", 95, "Saving files...")
                db.commit()

                save_dir = Path(settings.ENHANCED_DATA_DIR)
                saved_files = enhancer.save_results(save_dir, article_info)

            # Update job to completed
            job.result = {
                "translation_id": translation_id,
                "formats": formats,
                "formats_completed": list(results.keys()),
                "total_tokens": total_tokens,
                "total_cost_usd": sum(
                    TokenUsage.calculate_cost(provider, model or enhancer.model, r.tokens_used)
                    for r in results.values() if r.success
                ),
                "saved_files": saved_files
            }

            job.update_status("completed", 100, "Enhancement completed successfully!")
            db.commit()

            return {
                "success": True,
                "job_id": job.id,
                "total_tokens": total_tokens,
                "formats_generated": len(results),
                "saved_files": saved_files
            }

        except Exception as e:
            job.update_status("failed", job.progress, error=str(e))
            db.commit()
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_enhancement_by_id(
        db: Session,
        user: User,
        enhancement_id: int
    ) -> Optional[Enhancement]:
        """
        Get enhancement by ID

        Args:
            db: Database session
            user: User object
            enhancement_id: Enhancement ID

        Returns:
            Enhancement object or None
        """
        return db.query(Enhancement).filter(
            Enhancement.id == enhancement_id,
            Enhancement.user_id == user.id
        ).first()

    @staticmethod
    def get_user_enhancements(
        db: Session,
        user: User,
        translation_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get user's enhancement history with pagination

        Args:
            db: Database session
            user: User object
            translation_id: Filter by translation ID (optional)
            page: Page number
            per_page: Items per page

        Returns:
            Dictionary with enhancements and pagination info
        """
        query = db.query(Enhancement).filter(Enhancement.user_id == user.id)

        if translation_id:
            query = query.filter(Enhancement.translation_id == translation_id)

        total = query.count()
        total_pages = ceil(total / per_page)

        enhancements = query.order_by(
            Enhancement.generated_at.desc()
        ).offset((page - 1) * per_page).limit(per_page).all()

        return {
            'enhancements': enhancements,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }

    @staticmethod
    def get_job_status(db: Session, user: User, job_id: int) -> Optional[Job]:
        """
        Get enhancement job status

        Args:
            db: Database session
            user: User object
            job_id: Job ID

        Returns:
            Job object or None
        """
        return db.query(Job).filter(
            Job.id == job_id,
            Job.user_id == user.id,
            Job.job_type == "enhance"
        ).first()
