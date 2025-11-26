"""
Translation Service
User-specific translation with token tracking
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from math import ceil

from app.models.user import User
from app.models.translation import Translation
from app.models.token_usage import TokenUsage
from app.core.translator import OpenAITranslator
from app.services.token_service import TokenService


class TranslationService:
    """Service for translation operations"""

    @staticmethod
    def translate_content(
        db: Session,
        user: User,
        pasted_content: str,
        target_lang: str = 'bn',
        provider: str = 'openai',
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate pasted content and save to database

        Args:
            db: Database session
            user: User object
            pasted_content: Webpage content to translate
            target_lang: Target language code
            provider: AI provider name
            model: Model name (optional)

        Returns:
            Dictionary with translation result and database record
        """
        # Check if user has sufficient tokens (estimate: ~1000 tokens for typical article)
        estimated_tokens = 1500
        if not user.has_tokens(estimated_tokens):
            return {
                'success': False,
                'error': 'Insufficient tokens. Please upgrade your plan or wait for monthly reset.',
                'tokens_remaining': user.tokens_remaining
            }

        # Initialize translator
        translator = OpenAITranslator(provider_name=provider, model=model)

        # Perform translation
        result = translator.extract_and_translate(pasted_content, target_lang)

        if not result.get('success', False):
            return {
                'success': False,
                'error': result.get('error', 'Translation failed'),
                'tokens_used': 0
            }

        tokens_used = result.get('tokens_used', 0)

        # Deduct tokens from user
        if not user.deduct_tokens(tokens_used):
            return {
                'success': False,
                'error': 'Failed to deduct tokens. Transaction rolled back.',
                'tokens_used': tokens_used
            }

        # Save translation to database
        translation = Translation(
            user_id=user.id,
            original_text=pasted_content[:1000],  # Store first 1000 chars of original
            translated_text=result.get('translated_text', ''),
            source_language='en',
            target_language=target_lang,
            provider=provider,
            model=model or translator.model,
            tokens_used=tokens_used,
            extra_data={
                'headline': result.get('headline'),
                'original_headline': result.get('original_headline'),
                'author': result.get('author'),
                'date': result.get('date'),
                'content': result.get('content')
            }
        )

        db.add(translation)

        # Log token usage
        token_log = TokenUsage(
            user_id=user.id,
            operation='translate',
            provider=provider,
            model=model or translator.model,
            tokens_used=tokens_used,
            cost_usd=TokenUsage.calculate_cost(provider, model or translator.model, tokens_used)
        )

        db.add(token_log)
        db.commit()
        db.refresh(translation)

        return {
            'success': True,
            'translation_id': translation.id,
            'headline': result.get('headline'),
            'content': result.get('content'),
            'author': result.get('author'),
            'date': result.get('date'),
            'original_headline': result.get('original_headline'),
            'translated_text': result.get('translated_text'),
            'tokens_used': tokens_used,
            'tokens_remaining': user.tokens_remaining,
            'provider': provider,
            'model': model or translator.model,
            'created_at': translation.created_at
        }

    @staticmethod
    def get_translation_by_id(
        db: Session,
        user: User,
        translation_id: int
    ) -> Optional[Translation]:
        """
        Get translation by ID (user-specific)

        Args:
            db: Database session
            user: User object
            translation_id: Translation ID

        Returns:
            Translation object or None
        """
        return db.query(Translation).filter(
            Translation.id == translation_id,
            Translation.user_id == user.id
        ).first()

    @staticmethod
    def get_user_translations(
        db: Session,
        user: User,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get user's translation history with pagination

        Args:
            db: Database session
            user: User object
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            Dictionary with translations and pagination info
        """
        query = db.query(Translation).filter(Translation.user_id == user.id)

        total = query.count()
        total_pages = ceil(total / per_page)

        translations = query.order_by(
            Translation.created_at.desc()
        ).offset((page - 1) * per_page).limit(per_page).all()

        return {
            'translations': translations,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }

    @staticmethod
    def delete_translation(
        db: Session,
        user: User,
        translation_id: int
    ) -> Dict[str, Any]:
        """
        Delete translation (user-specific)

        Args:
            db: Database session
            user: User object
            translation_id: Translation ID

        Returns:
            Dictionary with success status
        """
        translation = TranslationService.get_translation_by_id(db, user, translation_id)

        if not translation:
            return {
                'success': False,
                'error': 'Translation not found or access denied'
            }

        # Delete associated enhancements (cascade should handle this, but explicit is better)
        from app.models.enhancement import Enhancement
        db.query(Enhancement).filter(Enhancement.translation_id == translation_id).delete()

        db.delete(translation)
        db.commit()

        return {
            'success': True,
            'message': 'Translation and associated enhancements deleted successfully',
            'deleted_id': translation_id
        }
