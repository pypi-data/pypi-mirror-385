"""
Security and authentication configuration settings.

Phase 3 SOLID Refactoring: Focused settings group for security/auth.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecuritySettings(BaseSettings):
    """
    Security and authentication configuration.
    
    Controls JWT/OIDC authentication, rate limiting, and audit logging.
    """
    
    model_config = SettingsConfigDict(
        env_prefix="ORCH_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # OIDC/JWT Configuration
    oidc_issuer: str = Field(
        default="",
        description="OIDC issuer URL (e.g., https://login.auth0.com/)"
    )
    oidc_audience: str = Field(
        default="market-data-orchestrator",
        description="JWT audience claim (client ID)"
    )
    jwks_url: str = Field(
        default="",
        description="JWKS endpoint URL for token verification"
    )
    jwt_role_claim: str = Field(
        default="roles",
        description="JWT claim name containing user roles"
    )
    jwt_cache_ttl: int = Field(
        default=3600,
        description="JWKS cache TTL in seconds"
    )
    jwt_enabled: bool = Field(
        default=False,
        description="Enable JWT authentication (falls back to API key if disabled)"
    )
    dual_auth: bool = Field(
        default=True,
        description="Allow both JWT and API key during transition period"
    )
    
    # Rate Limiting
    redis_rate_limit_url: str = Field(
        default="redis://localhost:6379/1",
        description="Redis URL for rate limiting (db=1, feedback bus uses db=0)"
    )
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable Redis-backed rate limiting"
    )
    rate_limit_max_per_minute: int = Field(
        default=5,
        description="Maximum control actions per minute per action type"
    )
    
    # Audit Logging
    audit_log_path: str = Field(
        default="logs/audit.jsonl",
        description="Path to audit log file (JSONL format)"
    )
    audit_log_enabled: bool = Field(
        default=True,
        description="Enable persistent audit logging"
    )

