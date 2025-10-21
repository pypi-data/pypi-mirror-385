"""
Feedback event subscribers for backpressure and health monitoring.

Phase 3 SOLID Refactoring: Now uses extensible EventRegistry following OCP.
Listens to events from the FeedbackBus and delegates to registered handlers.
"""

import logging
from typing import Any, Dict, Optional
from .events import EventRegistry, BackpressureHandler, HealthCheckHandler, ErrorHandler

log = logging.getLogger(__name__)


class FeedbackSubscriber:
    """
    Subscribes to feedback events from the Store's FeedbackBus.
    
    Phase 3: Now uses EventRegistry for extensible event handling.
    New event handlers can be registered without modifying this class (OCP).
    
    Default handlers:
    - BackpressureHandler: Monitors queue sizes and backpressure
    - HealthCheckHandler: Logs health check information
    - ErrorHandler: Logs and alerts on errors
    
    Custom handlers can be added via the registry:
        subscriber.registry.register(CustomHandler())
    """
    
    def __init__(self, bus: Any, registry: Optional[EventRegistry] = None):
        """
        Initialize feedback subscriber.
        
        Args:
            bus: FeedbackBus instance from market-data-store
            registry: Optional EventRegistry (creates default if None)
        """
        self.bus = bus
        self._subscribed = False
        
        # Phase 3: Use registry for extensible event handling
        self.registry = registry if registry is not None else self._create_default_registry()
    
    def _create_default_registry(self) -> EventRegistry:
        """
        Create registry with default handlers.
        
        Returns:
            EventRegistry with default handlers registered
        """
        registry = EventRegistry()
        
        # Register default handlers
        registry.register(BackpressureHandler())
        registry.register(HealthCheckHandler())
        registry.register(ErrorHandler())
        
        return registry
    
    async def subscribe(self) -> None:
        """
        Subscribe to all registered event types.
        
        Phase 3: Dynamically subscribes based on registered handlers.
        """
        if self._subscribed:
            log.warning("Already subscribed to feedback events")
            return
        
        log.info("Subscribing to feedback events...")
        
        # Phase 3: Subscribe to all registered event types
        for event_type in self.registry.event_types:
            handlers = self.registry.get_handlers(event_type)
            
            # Create closure for this event type
            async def handle_event(evt: Dict[str, Any], event_handlers=handlers) -> None:
                """Handle event by delegating to all registered handlers."""
                for handler in event_handlers:
                    try:
                        await handler.handle(evt)
                    except Exception as e:
                        log.error(f"Error in handler for {handler.event_type}: {e}", exc_info=True)
            
            # Subscribe to the event type
            self.bus.on(event_type)(handle_event)
            log.debug(f"Subscribed to event type: {event_type} with {len(handlers)} handler(s)")
        
        self._subscribed = True
        log.info(f"Successfully subscribed to {len(self.registry.event_types)} event types")
    
    async def unsubscribe(self) -> None:
        """Unsubscribe from feedback events."""
        if not self._subscribed:
            return
        
        log.info("Unsubscribing from feedback events...")
        # Note: Actual unsubscription depends on FeedbackBus implementation
        self._subscribed = False

