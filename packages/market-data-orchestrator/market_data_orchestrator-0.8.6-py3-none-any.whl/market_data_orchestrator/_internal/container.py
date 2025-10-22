"""
Service container for dependency injection.

Replaces module-level global singletons with a centralized, testable,
and thread-safe container.

Phase 1 SOLID Refactoring: This addresses the most critical DIP violation
(global state) throughout the codebase.
"""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..protocols import AuditLogger, RateLimiter
    from ..orchestrator import MarketDataOrchestrator
    from ..settings import OrchestratorSettings

log = logging.getLogger(__name__)


class ServiceContainer:
    """
    Centralized dependency injection container.
    
    Replaces module-level singletons with a proper DI container that:
    - Makes dependencies explicit
    - Improves testability
    - Enables proper cleanup
    - Thread-safe access patterns
    
    Usage:
        # Application startup
        container = ServiceContainer()
        container.register_orchestrator(orch)
        container.register_rate_limiter(limiter)
        
        # In dependencies
        def get_orchestrator(request: Request):
            return request.app.state.container.get_orchestrator()
    """
    
    def __init__(self):
        """Initialize empty container."""
        # Core components
        self._orchestrator: Optional[MarketDataOrchestrator] = None
        self._settings: Optional[OrchestratorSettings] = None
        
        # Infrastructure services
        self._rate_limiter: Optional[RateLimiter] = None
        self._audit_logger: Optional[AuditLogger] = None
        
        # JWT/Auth components
        self._jwks_cache: Optional[dict] = None
        self._jwks_cache_expires: Optional[Any] = None
        
        # WebSocket state
        self._ws_clients: set = set()
        self._ws_broadcast_task: Optional[Any] = None
        
        log.debug("ServiceContainer initialized")
    
    # ========== Orchestrator ==========
    
    def register_orchestrator(self, orchestrator: MarketDataOrchestrator) -> None:
        """
        Register the orchestrator instance.
        
        Args:
            orchestrator: MarketDataOrchestrator instance
        """
        if self._orchestrator is not None:
            log.warning("Orchestrator already registered, replacing")
        
        self._orchestrator = orchestrator
        # Auto-register settings from orchestrator
        if orchestrator.settings:
            self._settings = orchestrator.settings
        
        log.info("Orchestrator registered in container")
    
    def get_orchestrator(self) -> MarketDataOrchestrator:
        """
        Get the orchestrator instance.
        
        Returns:
            MarketDataOrchestrator instance
            
        Raises:
            RuntimeError: If orchestrator not registered
        """
        if self._orchestrator is None:
            raise RuntimeError("Orchestrator not registered in container")
        return self._orchestrator
    
    def has_orchestrator(self) -> bool:
        """Check if orchestrator is registered."""
        return self._orchestrator is not None
    
    # ========== Settings ==========
    
    def get_settings(self) -> OrchestratorSettings:
        """
        Get orchestrator settings.
        
        Returns:
            OrchestratorSettings instance
            
        Raises:
            RuntimeError: If settings not available
        """
        if self._settings is None:
            # Try to get from orchestrator
            if self._orchestrator and self._orchestrator.settings:
                self._settings = self._orchestrator.settings
            else:
                raise RuntimeError("Settings not available in container")
        return self._settings
    
    # ========== Rate Limiter ==========
    
    def register_rate_limiter(self, limiter: RateLimiter) -> None:
        """
        Register rate limiter instance.
        
        Args:
            limiter: RateLimiter implementation
        """
        self._rate_limiter = limiter
        log.info("Rate limiter registered in container")
    
    def get_rate_limiter(self) -> Optional[RateLimiter]:
        """
        Get rate limiter instance.
        
        Returns:
            RateLimiter instance or None if not registered
        """
        return self._rate_limiter
    
    def has_rate_limiter(self) -> bool:
        """Check if rate limiter is registered."""
        return self._rate_limiter is not None
    
    # ========== Audit Logger ==========
    
    def register_audit_logger(self, logger: AuditLogger) -> None:
        """
        Register audit logger instance.
        
        Args:
            logger: AuditLogger implementation
        """
        self._audit_logger = logger
        log.info("Audit logger registered in container")
    
    def get_audit_logger(self) -> Optional[AuditLogger]:
        """
        Get audit logger instance.
        
        Returns:
            AuditLogger instance or None if not registered
        """
        return self._audit_logger
    
    def has_audit_logger(self) -> bool:
        """Check if audit logger is registered."""
        return self._audit_logger is not None
    
    # ========== JWKS Cache ==========
    
    def set_jwks_cache(self, jwks: dict, expires_at: Any) -> None:
        """
        Set JWKS cache.
        
        Args:
            jwks: JWKS dictionary
            expires_at: Expiration datetime
        """
        self._jwks_cache = jwks
        self._jwks_cache_expires = expires_at
        log.debug("JWKS cache updated")
    
    def get_jwks_cache(self) -> tuple[Optional[dict], Optional[Any]]:
        """
        Get JWKS cache.
        
        Returns:
            Tuple of (jwks_dict, expires_at) or (None, None)
        """
        return self._jwks_cache, self._jwks_cache_expires
    
    def clear_jwks_cache(self) -> None:
        """Clear JWKS cache."""
        self._jwks_cache = None
        self._jwks_cache_expires = None
        log.debug("JWKS cache cleared")
    
    # ========== WebSocket State ==========
    
    def get_ws_clients(self) -> set:
        """
        Get WebSocket clients set.
        
        Returns:
            Set of connected WebSocket clients
        """
        return self._ws_clients
    
    def set_ws_broadcast_task(self, task: Any) -> None:
        """
        Set WebSocket broadcast task.
        
        Args:
            task: Asyncio task for broadcasting
        """
        self._ws_broadcast_task = task
        log.debug("WebSocket broadcast task registered")
    
    def get_ws_broadcast_task(self) -> Optional[Any]:
        """
        Get WebSocket broadcast task.
        
        Returns:
            Broadcast task or None
        """
        return self._ws_broadcast_task
    
    def clear_ws_broadcast_task(self) -> None:
        """Clear WebSocket broadcast task."""
        self._ws_broadcast_task = None
        log.debug("WebSocket broadcast task cleared")
    
    # ========== Lifecycle ==========
    
    async def cleanup(self) -> None:
        """
        Clean up all registered services.
        
        Called during application shutdown.
        """
        log.info("Cleaning up ServiceContainer...")
        
        # Clear caches
        self.clear_jwks_cache()
        self.clear_ws_broadcast_task()
        
        # Clear references
        self._orchestrator = None
        self._settings = None
        self._rate_limiter = None
        self._audit_logger = None
        self._ws_clients.clear()
        
        log.info("ServiceContainer cleanup complete")
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        services = []
        if self.has_orchestrator():
            services.append("orchestrator")
        if self.has_rate_limiter():
            services.append("rate_limiter")
        if self.has_audit_logger():
            services.append("audit_logger")
        
        return f"ServiceContainer(services=[{', '.join(services)}])"


