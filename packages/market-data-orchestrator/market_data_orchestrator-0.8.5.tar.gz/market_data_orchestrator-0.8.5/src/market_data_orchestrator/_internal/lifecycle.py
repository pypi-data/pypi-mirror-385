"""
Lifecycle manager for orchestrator start/stop/cleanup operations.

Phase 2 SOLID Refactoring: Extracted from MarketDataOrchestrator to follow SRP.
This class is responsible ONLY for managing the lifecycle of orchestrator components.
"""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..settings import OrchestratorSettings

log = logging.getLogger(__name__)


class LifecycleManager:
    """
    Manages the lifecycle of orchestrator components.
    
    Responsibilities (SRP):
    - Start/stop orchestrator components in correct order
    - Handle cleanup on errors or shutdown
    - Manage component state transitions
    
    Does NOT:
    - Create or configure components (that's ComponentRegistry)
    - Handle control operations like pause/resume (that's ControlPlaneService)
    - Aggregate status (that's StatusAggregator)
    """
    
    def __init__(self, settings: OrchestratorSettings):
        """
        Initialize lifecycle manager.
        
        Args:
            settings: Orchestrator settings
        """
        self.settings = settings
        self._started = False
        self._running = False
        
        # Components (set by ComponentRegistry)
        self._runtime: Optional[Any] = None
        self._provider: Optional[Any] = None
        self._feedback_bus: Optional[Any] = None
        self._feedback_subscriber: Optional[Any] = None
        self._pulse_observer: Optional[Any] = None  # Phase 10.1
    
    def set_components(
        self,
        runtime: Any,
        provider: Any,
        feedback_bus: Optional[Any] = None,
        feedback_subscriber: Optional[Any] = None,
        pulse_observer: Optional[Any] = None  # Phase 10.1
    ) -> None:
        """
        Set components to be managed.
        
        Called by ComponentRegistry after initialization.
        
        Args:
            runtime: Pipeline runtime instance
            provider: Data provider instance
            feedback_bus: Feedback bus instance (optional)
            feedback_subscriber: Feedback subscriber instance (optional)
            pulse_observer: Pulse observer instance (optional, Phase 10.1)
        """
        self._runtime = runtime
        self._provider = provider
        self._feedback_bus = feedback_bus
        self._feedback_subscriber = feedback_subscriber
        self._pulse_observer = pulse_observer  # Phase 10.1
    
    async def start(self) -> None:
        """
        Start all components in the correct order.
        
        Order:
        1. Connect to feedback bus
        2. Subscribe to feedback events
        3. Connect provider
        4. Start pipeline runtime
        
        Raises:
            RuntimeError: If start fails
        """
        if self._started:
            log.warning("Lifecycle already started")
            return
        
        log.info("Starting orchestrator lifecycle...")
        
        try:
            # Subscribe to feedback events (FeedbackBus has no connect method)
            if self._feedback_subscriber and self.settings.feedback_enabled:
                await self._feedback_subscriber.subscribe()
                log.info("Subscribed to feedback events")
            
            # Start pipeline runtime (provider is configured via settings)
            if self._runtime:
                await self._runtime.start()
                log.info("Pipeline runtime started")
            
            # Phase 10.1: Start Pulse observer
            if self._pulse_observer:
                await self._pulse_observer.start()
                log.info("Pulse observer started")
            
            self._running = True
            self._started = True
            log.info("✅ Orchestrator lifecycle started successfully")
            
        except Exception as e:
            log.error(f"Failed to start lifecycle: {e}", exc_info=True)
            # Cleanup on failure
            await self.cleanup()
            raise
    
    async def stop(self) -> None:
        """
        Stop all components gracefully.
        
        Delegates to cleanup() which handles the actual stopping logic.
        """
        if not self._started:
            log.warning("Lifecycle not started, nothing to stop")
            return
        
        log.info("Stopping orchestrator lifecycle...")
        await self.cleanup()
        log.info("✅ Orchestrator lifecycle stopped")
    
    async def cleanup(self) -> None:
        """
        Clean up resources in reverse order of initialization.
        
        Order:
        1. Stop runtime
        2. Close provider
        3. Unsubscribe from feedback
        4. Disconnect feedback bus
        
        This method is safe to call multiple times and handles errors gracefully.
        """
        self._running = False
        
        # Phase 10.1: Stop Pulse observer first
        if self._pulse_observer:
            try:
                await self._pulse_observer.stop()
                log.info("Pulse observer stopped")
            except Exception as e:
                log.error(f"Error stopping pulse observer: {e}")
        
        # Stop runtime
        if self._runtime:
            try:
                await self._runtime.stop()
                log.info("Pipeline runtime stopped")
            except Exception as e:
                log.error(f"Error stopping runtime: {e}")
        
        # Close provider
        if self._provider:
            try:
                await self._provider.close()
                log.info("Provider disconnected")
            except Exception as e:
                log.error(f"Error closing provider: {e}")
        
        # Unsubscribe from feedback
        if self._feedback_subscriber:
            try:
                await self._feedback_subscriber.unsubscribe()
                log.info("Unsubscribed from feedback")
            except Exception as e:
                log.error(f"Error unsubscribing from feedback: {e}")
        
        # Feedback bus cleanup (no disconnect method needed)
        
        self._started = False
    
    @property
    def is_started(self) -> bool:
        """Check if lifecycle is started."""
        return self._started
    
    @property
    def is_running(self) -> bool:
        """Check if lifecycle is running."""
        return self._running


