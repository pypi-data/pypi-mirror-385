"""
Status aggregator for collecting system status from all components.

Phase 2 SOLID Refactoring: Extracted from MarketDataOrchestrator to follow SRP.
This class is responsible ONLY for aggregating status information.
"""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from ..settings import OrchestratorSettings
    from .lifecycle import LifecycleManager
    from .control_service import ControlPlaneService
    from .registry import ComponentRegistry

log = logging.getLogger(__name__)


class StatusAggregator:
    """
    Aggregates status information from all orchestrator components.
    
    Responsibilities (SRP):
    - Collect status from all components
    - Format status into consistent structure
    - Handle errors when components are unavailable
    
    Does NOT:
    - Start/stop components (that's LifecycleManager)
    - Initialize components (that's ComponentRegistry)
    - Handle control operations (that's ControlPlaneService)
    """
    
    def __init__(
        self,
        settings: OrchestratorSettings,
        lifecycle: LifecycleManager,
        control: ControlPlaneService,
        registry: ComponentRegistry
    ):
        """
        Initialize status aggregator.
        
        Args:
            settings: Orchestrator settings
            lifecycle: Lifecycle manager
            control: Control plane service
            registry: Component registry
        """
        self.settings = settings
        self.lifecycle = lifecycle
        self.control = control
        self.registry = registry
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect status from all components.
        
        Returns:
            Dictionary with comprehensive status information
        """
        status_data = {
            "running": self.lifecycle.is_running,
            "started": self.lifecycle.is_started,
            "paused": self.control.is_paused,
            "settings": {
                "runtime_mode": self.settings.runtime_mode,
                "feedback_enabled": self.settings.feedback_enabled,
                "autoscale_enabled": self.settings.autoscale_enabled,
            }
        }
        
        # Add runtime status if available
        # FIXED Issue #15: UnifiedRuntime doesn't have status() method
        # Instead, provide basic state information based on lifecycle
        if self.registry.is_initialized and self.registry.runtime:
            try:
                status_data["runtime"] = {
                    "state": "running" if self.lifecycle.is_running else "stopped",
                    "mode": self.settings.runtime_mode
                }
            except Exception as e:
                status_data["runtime"] = {"error": str(e)}
                log.warning(f"Error getting runtime status: {e}")
        
        # Add provider status if available
        # FIXED Issue #16: IBKRProvider doesn't have is_connected attribute
        # Check if session exists as proxy for connection status
        if self.registry.is_initialized and self.registry.provider:
            try:
                # IBKRProvider has 'session' attribute when connected
                has_session = hasattr(self.registry.provider, 'session') and \
                              self.registry.provider.session is not None
                status_data["provider"] = {
                    "initialized": True,
                    "has_session": has_session,
                    "type": "IBKR"
                }
            except Exception as e:
                status_data["provider"] = {"error": str(e)}
                log.warning(f"Error getting provider status: {e}")
        
        # Add feedback bus status
        # FIXED: FeedbackBus doesn't have is_connected attribute
        # Check subscriber_count instead
        if self.registry.is_initialized and self.registry.feedback_bus:
            try:
                subscriber_count = getattr(self.registry.feedback_bus, 'subscriber_count', 0)
                status_data["feedback"] = {
                    "initialized": True,
                    "subscriber_count": subscriber_count,
                    "subscribed": self.registry.feedback_subscriber._subscribed if self.registry.feedback_subscriber else False
                }
            except Exception as e:
                status_data["feedback"] = {"error": str(e)}
                log.warning(f"Error getting feedback status: {e}")
        
        # Phase 10.1: Add Pulse observer status
        if self.registry.is_initialized and self.registry.pulse_observer:
            try:
                status_data["pulse"] = self.registry.pulse_observer.status()
            except Exception as e:
                status_data["pulse"] = {"error": str(e)}
                log.warning(f"Error getting pulse status: {e}")
        
        return status_data


