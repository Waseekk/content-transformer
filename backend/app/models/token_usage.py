"""
Token Usage Model
Tracks AI token consumption per operation for billing and analytics
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class TokenUsage(Base):
    """Token usage tracking model"""

    __tablename__ = "token_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Operation details
    operation = Column(String(50), nullable=False, index=True)  # translate, enhance, scrape
    provider = Column(String(50), nullable=False)  # openai
    model = Column(String(100), nullable=False)

    # Token tracking
    tokens_used = Column(Integer, nullable=False)
    cost = Column(Float, default=0.0)  # Calculated cost in USD

    # Related records
    translation_id = Column(Integer, ForeignKey("translations.id", ondelete="SET NULL"), nullable=True)
    enhancement_id = Column(Integer, ForeignKey("enhancements.id", ondelete="SET NULL"), nullable=True)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="token_usages")

    def __repr__(self):
        return f"<TokenUsage {self.id}: {self.operation} - {self.tokens_used} tokens>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "operation": self.operation,
            "provider": self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @staticmethod
    def calculate_cost(provider: str, model: str, tokens: int) -> float:
        """
        Calculate cost based on provider pricing
        OpenAI pricing (as of 2024):
        - gpt-4o-mini: $0.150 / 1M input tokens, $0.600 / 1M output tokens
        - gpt-4-turbo: $10.00 / 1M input tokens, $30.00 / 1M output tokens
        """
        # Simplified calculation (average of input/output)
        # In production, track input/output separately
        pricing = {
            "openai": {
                "gpt-4o-mini": 0.375 / 1_000_000,  # Average
                "gpt-4-turbo": 20.0 / 1_000_000,  # Average
                "gpt-3.5-turbo": 1.5 / 1_000_000,  # Average
            }
        }

        rate = pricing.get(provider, {}).get(model, 0.0)
        return tokens * rate
