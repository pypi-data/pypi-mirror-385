"""
Unified orchestrator settings (aggregates focused groups).

Phase 3 SOLID Refactoring: Maintains backward compatibility while using ISP-compliant groups.
"""

from typing import Any, Dict
from .runtime import RuntimeSettings
from .feedback import FeedbackSettings
from .security import SecuritySettings
from .provider import ProviderSettings
from .infrastructure import InfrastructureSettings


class OrchestratorSettings:
    """
    Unified orchestrator settings that aggregate focused groups.
    
    Phase 3: This class now composes focused settings groups following ISP.
    The public API remains unchanged for backward compatibility.
    
    Components can now depend only on the settings group they need:
    - Runtime components → RuntimeSettings
    - Feedback components → FeedbackSettings  
    - Security components → SecuritySettings
    - Provider components → ProviderSettings
    - Infrastructure components → InfrastructureSettings
    """
    
    def __init__(self, **kwargs):
        """
        Initialize all settings groups.
        
        Phase 3: Accepts keyword arguments for backward compatibility.
        Arguments are routed to the appropriate settings group.
        
        Args:
            **kwargs: Settings values (e.g., feedback_enabled=False)
        """
        # Extract kwargs for each settings group
        runtime_kwargs = {}
        feedback_kwargs = {}
        security_kwargs = {}
        provider_kwargs = {}
        infra_kwargs = {}
        
        # Map kwargs to appropriate groups
        runtime_fields = {"runtime_mode", "autoscale_enabled"}
        feedback_fields = {"feedback_url", "feedback_enabled"}
        security_fields = {
            "oidc_issuer", "oidc_audience", "jwks_url", "jwt_role_claim",
            "jwt_cache_ttl", "jwt_enabled", "dual_auth", "redis_rate_limit_url",
            "rate_limit_enabled", "rate_limit_max_per_minute",
            "audit_log_path", "audit_log_enabled"
        }
        provider_fields = {"provider_host", "provider_port", "provider_client_id"}
        infra_fields = {
            "health_port", "health_host", "log_level", "log_format", "federation_peers",
            "registry_url", "registry_track", "registry_monitor_enabled", "registry_poll_interval",
            "store_url", "pipeline_url", "prometheus_url"
        }
        
        # Route kwargs to appropriate dictionaries
        for key, value in kwargs.items():
            if key in runtime_fields:
                runtime_kwargs[key] = value
            elif key in feedback_fields:
                feedback_kwargs[key] = value
            elif key in security_fields:
                security_kwargs[key] = value
            elif key in provider_fields:
                provider_kwargs[key] = value
            elif key in infra_fields:
                infra_kwargs[key] = value
        
        # Initialize settings groups with their kwargs
        self.runtime = RuntimeSettings(**runtime_kwargs)
        self.feedback = FeedbackSettings(**feedback_kwargs)
        self.security = SecuritySettings(**security_kwargs)
        self.provider = ProviderSettings(**provider_kwargs)
        self.infra = InfrastructureSettings(**infra_kwargs)
    
    # ========================================================================
    # Backward Compatibility Properties
    # These proxy to the focused groups to maintain the old API
    # ========================================================================
    
    # Runtime settings
    @property
    def runtime_mode(self) -> str:
        return self.runtime.runtime_mode
    
    @runtime_mode.setter
    def runtime_mode(self, value: str) -> None:
        self.runtime.runtime_mode = value
    
    @property
    def autoscale_enabled(self) -> bool:
        return self.runtime.autoscale_enabled
    
    @autoscale_enabled.setter
    def autoscale_enabled(self, value: bool) -> None:
        self.runtime.autoscale_enabled = value
    
    # Feedback settings
    @property
    def feedback_url(self) -> str:
        return self.feedback.feedback_url
    
    @property
    def feedback_enabled(self) -> bool:
        return self.feedback.feedback_enabled
    
    # Security settings
    @property
    def oidc_issuer(self) -> str:
        return self.security.oidc_issuer
    
    @oidc_issuer.setter
    def oidc_issuer(self, value: str) -> None:
        self.security.oidc_issuer = value
    
    @property
    def oidc_audience(self) -> str:
        return self.security.oidc_audience
    
    @oidc_audience.setter
    def oidc_audience(self, value: str) -> None:
        self.security.oidc_audience = value
    
    @property
    def jwks_url(self) -> str:
        return self.security.jwks_url
    
    @jwks_url.setter
    def jwks_url(self, value: str) -> None:
        self.security.jwks_url = value
    
    @property
    def jwt_role_claim(self) -> str:
        return self.security.jwt_role_claim
    
    @jwt_role_claim.setter
    def jwt_role_claim(self, value: str) -> None:
        self.security.jwt_role_claim = value
    
    @property
    def jwt_cache_ttl(self) -> int:
        return self.security.jwt_cache_ttl
    
    @jwt_cache_ttl.setter
    def jwt_cache_ttl(self, value: int) -> None:
        self.security.jwt_cache_ttl = value
    
    @property
    def jwt_enabled(self) -> bool:
        return self.security.jwt_enabled
    
    @jwt_enabled.setter
    def jwt_enabled(self, value: bool) -> None:
        self.security.jwt_enabled = value
    
    @property
    def dual_auth(self) -> bool:
        return self.security.dual_auth
    
    @dual_auth.setter
    def dual_auth(self, value: bool) -> None:
        self.security.dual_auth = value
    
    @property
    def redis_rate_limit_url(self) -> str:
        return self.security.redis_rate_limit_url
    
    @property
    def rate_limit_enabled(self) -> bool:
        return self.security.rate_limit_enabled
    
    @property
    def rate_limit_max_per_minute(self) -> int:
        return self.security.rate_limit_max_per_minute
    
    @property
    def audit_log_path(self) -> str:
        return self.security.audit_log_path
    
    @property
    def audit_log_enabled(self) -> bool:
        return self.security.audit_log_enabled
    
    # Provider settings
    @property
    def provider_host(self) -> str:
        return self.provider.provider_host
    
    @property
    def provider_port(self) -> int:
        return self.provider.provider_port
    
    @property
    def provider_client_id(self) -> int:
        return self.provider.provider_client_id
    
    def get_provider_config(self) -> Dict[str, Any]:
        """Backward compatibility: delegate to provider settings."""
        return self.provider.get_provider_config()
    
    # Infrastructure settings
    @property
    def health_port(self) -> int:
        return self.infra.health_port
    
    @property
    def health_host(self) -> str:
        return self.infra.health_host
    
    @property
    def log_level(self) -> str:
        return self.infra.log_level
    
    @property
    def log_format(self) -> str:
        return self.infra.log_format
    
    @property
    def federation_peers(self) -> str:
        return self.infra.federation_peers
    
    @federation_peers.setter
    def federation_peers(self, value: str) -> None:
        self.infra.federation_peers = value
    
    # Phase 11.0E: Registry settings
    @property
    def registry_url(self) -> str:
        return self.infra.registry_url
    
    @registry_url.setter
    def registry_url(self, value: str) -> None:
        self.infra.registry_url = value
    
    @property
    def registry_track(self) -> str:
        return self.infra.registry_track
    
    @registry_track.setter
    def registry_track(self, value: str) -> None:
        self.infra.registry_track = value
    
    @property
    def registry_monitor_enabled(self) -> bool:
        return self.infra.registry_monitor_enabled
    
    @registry_monitor_enabled.setter
    def registry_monitor_enabled(self, value: bool) -> None:
        self.infra.registry_monitor_enabled = value
    
    @property
    def registry_poll_interval(self) -> int:
        return self.infra.registry_poll_interval
    
    @registry_poll_interval.setter
    def registry_poll_interval(self, value: int) -> None:
        self.infra.registry_poll_interval = value
    
    # Service URLs
    @property
    def store_url(self) -> str:
        return self.infra.store_url
    
    @store_url.setter
    def store_url(self, value: str) -> None:
        self.infra.store_url = value
    
    @property
    def pipeline_url(self) -> str:
        return self.infra.pipeline_url
    
    @pipeline_url.setter
    def pipeline_url(self, value: str) -> None:
        self.infra.pipeline_url = value
    
    @property
    def prometheus_url(self) -> str:
        return self.infra.prometheus_url
    
    @prometheus_url.setter
    def prometheus_url(self, value: str) -> None:
        self.infra.prometheus_url = value

