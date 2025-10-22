"""
Event handler protocol definition.

Phase 3 SOLID Refactoring: Protocol for extensible event handling (OCP).
"""

from typing import Protocol, Any, Dict


class EventHandler(Protocol):
    """
    Protocol for feedback event handlers.
    
    Implementations can handle specific event types and can be registered
    with the EventRegistry without modifying core code (Open/Closed Principle).
    """
    
    async def handle(self, event_data: Dict[str, Any]) -> None:
        """
        Handle a feedback event.
        
        Args:
            event_data: Event payload from the feedback bus
        """
        ...
    
    @property
    def event_type(self) -> str:
        """
        Get the event type this handler processes.
        
        Returns:
            Event type string (e.g., "backpressure", "error")
        """
        ...

