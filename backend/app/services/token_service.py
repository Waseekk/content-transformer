"""
Token Management Service
Business logic for AI token tracking and management
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.token_usage import TokenUsage
from app.config import get_settings

settings = get_settings()


class TokenService:
    """Token management service"""

    @staticmethod
    def check_token_balance(user: User, required_tokens: int) -> bool:
        """
        Check if user has sufficient token balance

        Args:
            user: User object
            required_tokens: Number of tokens required

        Returns:
            True if user has enough tokens, False otherwise
        """
        return user.tokens_remaining >= required_tokens

    @staticmethod
    def deduct_tokens(db: Session, user: User, tokens_used: int, operation: str,
                     provider: str, model: str, translation_id: Optional[int] = None,
                     enhancement_id: Optional[int] = None) -> bool:
        """
        Deduct tokens from user balance and log usage

        Args:
            db: Database session
            user: User object
            tokens_used: Number of tokens to deduct
            operation: Operation type (translate, enhance, scrape)
            provider: AI provider (openai)
            model: Model used
            translation_id: Related translation ID (optional)
            enhancement_id: Related enhancement ID (optional)

        Returns:
            True if tokens deducted successfully, False if insufficient balance
        """
        # Check balance
        if not user.has_tokens(tokens_used):
            return False

        # Deduct tokens
        if not user.deduct_tokens(tokens_used):
            return False

        # Calculate cost
        cost = TokenUsage.calculate_cost(provider, model, tokens_used)

        # Log usage
        token_usage = TokenUsage(
            user_id=user.id,
            operation=operation,
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            cost=cost,
            translation_id=translation_id,
            enhancement_id=enhancement_id,
            timestamp=datetime.utcnow()
        )

        db.add(token_usage)
        db.commit()
        db.refresh(user)

        return True

    @staticmethod
    def get_token_balance(user: User) -> dict:
        """
        Get user's current token balance and info

        Args:
            user: User object

        Returns:
            Dictionary with token balance information
        """
        return {
            "tokens_remaining": user.tokens_remaining,
            "tokens_total": user.tokens_total,
            "subscription_tier": user.subscription_tier,
            "next_reset": user.next_token_reset,
            "can_use_tokens": user.tokens_remaining > 0,
            "last_reset": user.last_token_reset
        }

    @staticmethod
    def reset_user_tokens(db: Session, user: User) -> None:
        """
        Reset user's monthly token balance

        Args:
            db: Database session
            user: User object
        """
        user.reset_monthly_tokens()
        db.commit()
        db.refresh(user)

    @staticmethod
    def get_usage_stats(db: Session, user: User, days: int = 30) -> dict:
        """
        Get token usage statistics for user

        Args:
            db: Database session
            user: User object
            days: Number of days to look back

        Returns:
            Dictionary with usage statistics
        """
        from datetime import timedelta
        from sqlalchemy import func

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Total tokens used
        total_used = db.query(func.sum(TokenUsage.tokens_used))\
            .filter(TokenUsage.user_id == user.id)\
            .filter(TokenUsage.timestamp >= cutoff_date)\
            .scalar() or 0

        # Total cost
        total_cost = db.query(func.sum(TokenUsage.cost))\
            .filter(TokenUsage.user_id == user.id)\
            .filter(TokenUsage.timestamp >= cutoff_date)\
            .scalar() or 0.0

        # Usage by operation
        usage_by_operation = db.query(
            TokenUsage.operation,
            func.sum(TokenUsage.tokens_used).label('tokens'),
            func.count(TokenUsage.id).label('count')
        ).filter(TokenUsage.user_id == user.id)\
         .filter(TokenUsage.timestamp >= cutoff_date)\
         .group_by(TokenUsage.operation)\
         .all()

        return {
            "period_days": days,
            "total_tokens_used": total_used,
            "total_cost_usd": float(total_cost),
            "tokens_remaining": user.tokens_remaining,
            "usage_by_operation": [
                {
                    "operation": op,
                    "tokens_used": tokens,
                    "operation_count": count
                }
                for op, tokens, count in usage_by_operation
            ]
        }

    @staticmethod
    def estimate_token_cost(operation: str, provider: str = "openai", model: str = "gpt-4o-mini") -> int:
        """
        Estimate token cost for an operation

        Args:
            operation: Operation type (translate, enhance_newspaper, etc.)
            provider: AI provider
            model: Model to use

        Returns:
            Estimated token count
        """
        # Rough estimates based on typical usage
        estimates = {
            "translate": 500,  # Average for article translation
            "enhance_newspaper": 300,
            "enhance_blog": 300,
            "enhance_facebook": 150,
            "enhance_instagram": 100,
            "enhance_hard_news": 400,
            "enhance_soft_news": 350,
        }

        return estimates.get(operation, 500)
