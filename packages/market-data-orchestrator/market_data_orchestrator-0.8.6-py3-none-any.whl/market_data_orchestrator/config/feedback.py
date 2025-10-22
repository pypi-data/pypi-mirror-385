"""
Feedback bus configuration settings.

Phase 3 SOLID Refactoring: Focused settings group for feedback event system.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FeedbackSettings(BaseSettings):
    """
    Feedback bus configuration.
    
    Controls the Redis-backed event bus for pipeline feedback.
    """
    
    model_config = SettingsConfigDict(
        env_prefix="ORCH_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    feedback_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for feedback bus"
    )
    
    feedback_enabled: bool = Field(
        default=True,
        description="Enable feedback event subscription"
    )

