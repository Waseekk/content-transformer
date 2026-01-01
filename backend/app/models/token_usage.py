"""
TokenUsage Model
Database model for detailed token usage tracking and analytics
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class TokenUsage(Base):
    """
    Token usage model for tracking detailed AI API usage
    """
    __tablename__ = "token_usage"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Operation details
    operation = Column(String(50), nullable=False, index=True)  # translate, enhance, scrape
    operation_type = Column(String(100), nullable=True)  # e.g., "hard_news", "soft_news"

    # AI provider details
    provider = Column(String(50), nullable=False)  # openai
    model = Column(String(100), nullable=False)  # gpt-4, gpt-3.5-turbo, etc.

    # Token metrics
    tokens_used = Column(Integer, nullable=False)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)

    # Cost tracking
    cost_usd = Column(Float, nullable=True)  # Cost in USD
    cost_per_token = Column(Float, nullable=True)  # Rate used for calculation

    # Context
    request_id = Column(String(255), nullable=True)  # API request ID if available
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="token_usage")
    job = relationship("Job")

    def __repr__(self):
        return f"<TokenUsage(id={self.id}, user_id={self.user_id}, operation={self.operation}, tokens={self.tokens_used})>"

    @staticmethod
    def calculate_cost(
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Calculate cost based on provider and model

        Args:
            provider: AI provider name
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            float: Cost in USD
        """
        # OpenAI pricing (as of Dec 2024)
        pricing = {
            "openai": {
                "gpt-4": {
                    "prompt": 0.03 / 1000,  # $0.03 per 1K tokens
                    "completion": 0.06 / 1000  # $0.06 per 1K tokens
                },
                "gpt-4-turbo": {
                    "prompt": 0.01 / 1000,
                    "completion": 0.03 / 1000
                },
                "gpt-3.5-turbo": {
                    "prompt": 0.0005 / 1000,
                    "completion": 0.0015 / 1000
                },
                "gpt-3.5-turbo-16k": {
                    "prompt": 0.003 / 1000,
                    "completion": 0.004 / 1000
                }
            }
        }

        # Get pricing for provider and model
        provider_pricing = pricing.get(provider.lower(), {})
        model_pricing = provider_pricing.get(model.lower(), provider_pricing.get("default", {}))

        if not model_pricing:
            # Unknown model, return 0
            return 0.0

        # Calculate cost
        prompt_cost = prompt_tokens * model_pricing.get("prompt", 0)
        completion_cost = completion_tokens * model_pricing.get("completion", 0)

        return round(prompt_cost + completion_cost, 6)

    def to_dict(self):
        """Convert token usage to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "operation": self.operation,
            "operation_type": self.operation_type,
            "provider": self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cost_usd": self.cost_usd,
            "cost_per_token": self.cost_per_token,
            "request_id": self.request_id,
            "job_id": self.job_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def log_usage(
        cls,
        db,
        user_id: int,
        operation: str,
        provider: str,
        model: str,
        tokens_used: int,
        prompt_tokens: int = None,
        completion_tokens: int = None,
        operation_type: str = None,
        job_id: int = None
    ):
        """
        Create a new token usage log entry

        Args:
            db: Database session
            user_id: User ID
            operation: Operation type
            provider: AI provider
            model: Model name
            tokens_used: Total tokens used
            prompt_tokens: Prompt tokens
            completion_tokens: Completion tokens
            operation_type: Specific operation type
            job_id: Associated job ID

        Returns:
            TokenUsage: Created token usage entry
        """
        # Calculate cost
        cost = cls.calculate_cost(
            provider,
            model,
            prompt_tokens or 0,
            completion_tokens or 0
        )

        # Create entry
        usage = cls(
            user_id=user_id,
            operation=operation,
            operation_type=operation_type,
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost,
            cost_per_token=cost / tokens_used if tokens_used > 0 else 0,
            job_id=job_id
        )

        db.add(usage)
        db.commit()
        db.refresh(usage)

        return usage
