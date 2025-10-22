"""
Runtime configuration settings.

Phase 3 SOLID Refactoring: Focused settings group for pipeline runtime configuration.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RuntimeSettings(BaseSettings):
    """
    Pipeline runtime configuration.
    
    Controls how the data pipeline executes and scales.
    """
    
    model_config = SettingsConfigDict(
        env_prefix="ORCH_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    runtime_mode: str = Field(
        default="dag",
        description="Pipeline runtime mode: 'dag', 'streaming', or 'batch'"
    )
    
    autoscale_enabled: bool = Field(
        default=True,
        description="Enable dynamic autoscaling based on backpressure"
    )

