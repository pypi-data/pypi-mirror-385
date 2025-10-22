"""
Control plane service for orchestrator pause/resume/reload operations.

Phase 2 SOLID Refactoring: Extracted from MarketDataOrchestrator to follow SRP.
This class is responsible ONLY for control plane operations.
"""

from __future__ import annotations
import logging

log = logging.getLogger(__name__)


class ControlPlaneService:
    """
    Handles orchestrator control plane operations.
    
    Responsibilities (SRP):
    - Pause/resume ingestion control
    - Configuration reload
    - Manage pause state
    
    Does NOT:
    - Start/stop components (that's LifecycleManager)
    - Initialize components (that's ComponentRegistry)
    - Aggregate status (that's StatusAggregator)
    """
    
    def __init__(self):
        """Initialize control plane service."""
        self._paused = False
    
    async def pause(self) -> None:
        """
        Pause orchestrator ingestion (soft control).
        
        Sets a pause flag that can be checked by providers/operators.
        Does not immediately stop the pipeline but signals it should slow/stop.
        """
        if not self._paused:
            self._paused = True
            log.info("Orchestrator paused (soft control)")
        else:
            log.warning("Orchestrator already paused")
    
    async def resume(self) -> None:
        """
        Resume orchestrator ingestion after pause.
        
        Clears the pause flag, allowing providers/operators to continue.
        """
        if self._paused:
            self._paused = False
            log.info("Orchestrator resumed")
        else:
            log.warning("Orchestrator not paused, nothing to resume")
    
    async def reload(self) -> None:
        """
        Reload configuration.
        
        For v0.4.0, this is a no-op placeholder.
        Future versions can re-read settings and apply non-breaking changes.
        """
        log.info("Reload requested (no-op in v0.4.0)")
        # TODO: Implement configuration reload in future version
        # Could re-read environment variables, update rate limits, etc.
    
    @property
    def is_paused(self) -> bool:
        """Check if orchestrator is paused."""
        return self._paused


