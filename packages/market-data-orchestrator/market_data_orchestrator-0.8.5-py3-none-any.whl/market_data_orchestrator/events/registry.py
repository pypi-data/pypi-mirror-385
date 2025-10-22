"""
Event handler registry for managing event subscriptions.

Phase 3 SOLID Refactoring: Central registry for extensible event handling (OCP).
"""

import logging
from typing import Dict, List
from .handler import EventHandler

log = logging.getLogger(__name__)


class EventRegistry:
    """
    Registry for event handlers.
    
    Allows registering custom event handlers without modifying core code.
    This enables the system to be open for extension but closed for modification (OCP).
    
    Example:
        registry = EventRegistry()
        registry.register(BackpressureHandler())
        registry.register(CustomHandler())  # User-defined handler
        
        for event_type, handlers in registry.get_all_handlers():
            for handler in handlers:
                await handler.handle(event_data)
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._handlers: Dict[str, List[EventHandler]] = {}
    
    def register(self, handler: EventHandler) -> None:
        """
        Register an event handler.
        
        Multiple handlers can be registered for the same event type.
        
        Args:
            handler: EventHandler instance to register
        """
        event_type = handler.event_type
        
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        log.info(f"Registered handler for event type: {event_type}")
    
    def get_handlers(self, event_type: str) -> List[EventHandler]:
        """
        Get all handlers for a specific event type.
        
        Args:
            event_type: Event type to get handlers for
            
        Returns:
            List of handlers (empty if none registered)
        """
        return self._handlers.get(event_type, [])
    
    def get_all_handlers(self) -> Dict[str, List[EventHandler]]:
        """
        Get all registered handlers.
        
        Returns:
            Dictionary mapping event types to handler lists
        """
        return self._handlers.copy()
    
    def unregister(self, handler: EventHandler) -> None:
        """
        Unregister a specific handler.
        
        Args:
            handler: Handler instance to remove
        """
        event_type = handler.event_type
        
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                log.info(f"Unregistered handler for event type: {event_type}")
                
                # Clean up empty lists
                if not self._handlers[event_type]:
                    del self._handlers[event_type]
            except ValueError:
                log.warning(f"Handler not found for event type: {event_type}")
    
    def clear(self) -> None:
        """Clear all registered handlers."""
        self._handlers.clear()
        log.info("Cleared all event handlers")
    
    @property
    def event_types(self) -> List[str]:
        """Get list of all registered event types."""
        return list(self._handlers.keys())

