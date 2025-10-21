"""
Infrastructure configuration settings.

Phase 3 SOLID Refactoring: Focused settings group for infra concerns.
"""

from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class InfrastructureSettings(BaseSettings):
    """
    Infrastructure configuration.
    
    Controls health API, logging, and federation settings.
    """
    
    model_config = SettingsConfigDict(
        env_prefix="ORCH_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Health/Metrics API
    health_port: int = Field(
        default=8501,
        description="Health and metrics API port"
    )
    health_host: str = Field(
        default="0.0.0.0",
        description="Health and metrics API host"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: str = Field(
        default="json",
        description="Log format: 'json' or 'text'"
    )
    
    # Federation
    federation_peers: str = Field(
        default="",
        description="Comma-separated list of peer orchestrator URLs"
    )
    
    # Phase 11.0E: Schema Registry Integration
    registry_url: str = Field(
        default="https://schema-registry-service.fly.dev",
        description="Schema registry service base URL"
    )
    registry_track: str = Field(
        default="v1",
        description="Schema track to use (v1=stable, v2=preview)"
    )
    registry_monitor_enabled: bool = Field(
        default=True,
        description="Enable registry monitoring and metrics"
    )
    registry_poll_interval: int = Field(
        default=60,
        description="Seconds between registry health checks"
    )
    
    # Service URLs (for compose orchestration)
    # Note: These use unprefixed env vars to match docker-compose convention
    store_url: str = Field(
        default="http://localhost:8082",
        description="Market Data Store service URL",
        validation_alias=AliasChoices("STORE_URL", "store_url", "ORCH_STORE_URL")
    )
    pipeline_url: str = Field(
        default="http://localhost:8083",
        description="Market Data Pipeline service URL",
        validation_alias=AliasChoices("PIPELINE_URL", "pipeline_url", "ORCH_PIPELINE_URL")
    )
    prometheus_url: str = Field(
        default="http://localhost:9090",
        description="Prometheus monitoring service URL",
        validation_alias=AliasChoices("PROMETHEUS_URL", "prometheus_url", "ORCH_PROMETHEUS_URL")
    )

