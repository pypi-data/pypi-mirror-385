"""
Core orchestrator class that coordinates providers, pipeline, and store.

Phase 2 SOLID Refactoring: Now uses composition to delegate to specialized services.
This class serves as a facade that maintains backward compatibility while using
properly separated concerns internally.

Integrates:
- UnifiedRuntime from market-data-pipeline
- FeedbackBus from market-data-store
- IBKRProvider from market-data-ibkr
"""

import logging
from typing import Any, Dict
from .settings import OrchestratorSettings

# Phase 2: Import internal services
from ._internal.lifecycle import LifecycleManager
from ._internal.registry import ComponentRegistry
from ._internal.control_service import ControlPlaneService
from ._internal.status_aggregator import StatusAggregator

log = logging.getLogger(__name__)


class MarketDataOrchestrator:
    """
    Main orchestrator facade that manages the market data pipeline lifecycle.
    
    Phase 2 Refactoring: This class now delegates to specialized services:
    - LifecycleManager: Start/stop/cleanup operations
    - ComponentRegistry: Component initialization
    - ControlPlaneService: Pause/resume/reload
    - StatusAggregator: Status collection
    
    Public API remains unchanged for backward compatibility.
    
    Responsibilities:
    - Provide stable public API
    - Coordinate internal services
    - Maintain backward compatibility
    """
    
    def __init__(self, settings: OrchestratorSettings):
        """
        Initialize the orchestrator with configuration.
        
        Phase 2: Now creates and coordinates internal services.
        
        Args:
            settings: OrchestratorSettings instance with all configuration
        """
        self.settings = settings
        
        log.info("Initializing Market Data Orchestrator", extra={"version": "0.7.0"})
        
        # Phase 2: Create internal services (dependency injection)
        self._registry = ComponentRegistry(settings)
        self._lifecycle = LifecycleManager(settings)
        self._control = ControlPlaneService()
        self._status = StatusAggregator(settings, self._lifecycle, self._control, self._registry)
        
        log.info("Orchestrator services initialized (Phase 2 architecture)")
    
    def _init_components(self) -> None:
        """
        Initialize pipeline components (lazy initialization).
        
        Phase 2: Delegates to ComponentRegistry.
        Kept for backward compatibility with code that might call this directly.
        """
        try:
            log.info("Initializing pipeline components...")
            
            # Phase 2: Delegate to ComponentRegistry
            # Phase 10.1: Now also returns pulse_observer
            runtime, provider, feedback_bus, feedback_subscriber, pulse_observer = self._registry.initialize()
            
            # Phase 2: Give components to LifecycleManager
            # Phase 10.1: Now also includes pulse_observer
            self._lifecycle.set_components(
                runtime=runtime,
                provider=provider,
                feedback_bus=feedback_bus,
                feedback_subscriber=feedback_subscriber,
                pulse_observer=pulse_observer
            )
            
            log.info("Components initialized and registered")
            
        except Exception as e:
            log.error(f"Failed to initialize components: {e}")
            raise
    
    async def start(self) -> None:
        """
        Start the orchestrator and all managed components.
        
        Phase 2: Delegates to ComponentRegistry and LifecycleManager.
        Public API unchanged for backward compatibility.
        
        Flow:
        1. Initialize components (ComponentRegistry)
        2. Start lifecycle (LifecycleManager)
        """
        if self._lifecycle.is_started:
            log.warning("Orchestrator already started")
            return
        
        log.info("Starting Market Data Orchestrator...")
        
        try:
            # Phase 2: Initialize components via registry
            self._init_components()
            
            # Phase 2: Start lifecycle
            await self._lifecycle.start()
            
            log.info("✅ Market Data Orchestrator started successfully")
            
        except Exception as e:
            log.error(f"Failed to start orchestrator: {e}", exc_info=True)
            raise
    
    async def stop(self) -> None:
        """
        Stop the orchestrator and clean up all resources.
        
        Phase 2: Delegates to LifecycleManager.
        Public API unchanged for backward compatibility.
        """
        if not self._lifecycle.is_started:
            log.warning("Orchestrator not started, nothing to stop")
            return
        
        log.info("Stopping Market Data Orchestrator...")
        
        # Phase 2: Delegate to LifecycleManager
        await self._lifecycle.stop()
        
        log.info("✅ Market Data Orchestrator stopped")
    
    async def _cleanup(self) -> None:
        """
        Clean up resources in reverse order of initialization.
        
        Phase 2: Delegates to LifecycleManager.
        Kept for backward compatibility.
        """
        await self._lifecycle.cleanup()
    
    # ---- Phase 6.2: Control Plane Methods ----
    # Phase 2: Now delegates to ControlPlaneService
    
    async def pause(self) -> None:
        """
        Pause ingestion (soft control).
        
        Phase 2: Delegates to ControlPlaneService.
        Public API unchanged for backward compatibility.
        """
        await self._control.pause()
    
    async def resume(self) -> None:
        """
        Resume ingestion after pause.
        
        Phase 2: Delegates to ControlPlaneService.
        Public API unchanged for backward compatibility.
        """
        await self._control.resume()
    
    async def reload(self) -> None:
        """
        Reload configuration.
        
        Phase 2: Delegates to ControlPlaneService.
        Public API unchanged for backward compatibility.
        """
        await self._control.reload()
    
    def status(self) -> Dict[str, Any]:
        """
        Get current orchestrator status.
        
        Phase 2: Delegates to StatusAggregator.
        Public API unchanged for backward compatibility.
        
        Returns:
            Dictionary with status information for all components
        """
        return self._status.collect()
    
    @property
    def is_running(self) -> bool:
        """
        Check if orchestrator is currently running.
        
        Phase 2: Delegates to LifecycleManager.
        Public API unchanged for backward compatibility.
        """
        return self._lifecycle.is_running

