"""
Default event handler implementations.

Phase 3 SOLID Refactoring: Concrete handlers following OCP.
Users can create custom handlers by implementing the EventHandler protocol.
"""

import logging
from typing import Any, Dict

log = logging.getLogger(__name__)


class BackpressureHandler:
    """
    Handles backpressure events from the feedback bus.
    
    Monitors queue sizes and backpressure levels to enable autoscaling.
    """
    
    @property
    def event_type(self) -> str:
        return "backpressure"
    
    async def handle(self, event_data: Dict[str, Any]) -> None:
        """
        Handle backpressure event.
        
        Args:
            event_data: Event payload with level and queue_size
        """
        level = event_data.get("level", "unknown")
        queue_size = event_data.get("queue_size", 0)
        
        log.warning(
            f"Backpressure detected: level={level}, queue_size={queue_size}",
            extra={"event": "backpressure", "level": level, "queue_size": queue_size}
        )
        
        # TODO: Implement autoscaling logic based on backpressure
        # This could trigger scale-up/scale-down operations


class HealthCheckHandler:
    """
    Handles health check events from the feedback bus.
    
    Logs health check information for monitoring and diagnostics.
    """
    
    @property
    def event_type(self) -> str:
        return "health_check"
    
    async def handle(self, event_data: Dict[str, Any]) -> None:
        """
        Handle health check event.
        
        Args:
            event_data: Event payload with health information
        """
        log.info(
            f"Health check: {event_data}",
            extra={"event": "health_check", "data": event_data}
        )


class ErrorHandler:
    """
    Handles error events from the feedback bus.
    
    Logs errors with component context for debugging and alerting.
    """
    
    @property
    def event_type(self) -> str:
        return "error"
    
    async def handle(self, event_data: Dict[str, Any]) -> None:
        """
        Handle error event.
        
        Args:
            event_data: Event payload with error message and component
        """
        error_msg = event_data.get("message", "Unknown error")
        component = event_data.get("component", "unknown")
        
        log.error(
            f"Error in {component}: {error_msg}",
            extra={"event": "error", "component": component, "error_message": error_msg}
        )

