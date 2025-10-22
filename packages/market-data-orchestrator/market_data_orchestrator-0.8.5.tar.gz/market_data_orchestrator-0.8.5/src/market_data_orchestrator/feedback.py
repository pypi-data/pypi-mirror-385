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
        
        FIXED Issue #14: FeedbackBus uses subscribe(callback) API, not on(event_type) decorator.
        The callback receives FeedbackEvent objects and routes them to registered handlers.
        """
        if self._subscribed:
            log.warning("Already subscribed to feedback events")
            return
        
        log.info("Subscribing to feedback events...")
        
        # Create a single callback that routes events to all registered handlers
        async def route_event(event: Any) -> None:
            """
            Route incoming FeedbackEvent to appropriate handlers.
            
            FeedbackBus publishes FeedbackEvent objects with fields like:
            - level: BackpressureLevel
            - source: str
            - ts: datetime
            - coordinator_id, queue_size, capacity, reason, etc.
            
            We route based on event characteristics to matching handlers.
            """
            try:
                # Convert event to dict if needed
                if hasattr(event, 'model_dump'):
                    evt_dict = event.model_dump()
                elif hasattr(event, 'dict'):
                    evt_dict = event.dict()
                else:
                    evt_dict = event if isinstance(event, dict) else {}
                
                # Route to handlers based on event type matching
                for event_type in self.registry.event_types:
                    handlers = self.registry.get_handlers(event_type)
                    
                    # Simple routing logic: match handler's event_type to event characteristics
                    # For now, route all events to all handlers (they can filter internally)
                    # TODO: More sophisticated routing based on event.level, event.source, etc.
                    for handler in handlers:
                        try:
                            await handler.handle(evt_dict)
                        except Exception as e:
                            log.error(f"Error in handler {handler.event_type}: {e}", exc_info=True)
            
            except Exception as e:
                log.error(f"Error routing feedback event: {e}", exc_info=True)
        
        # Subscribe to FeedbackBus with our routing callback
        # FIXED: Use subscribe(callback), NOT on(event_type) decorator
        self.bus.subscribe(route_event)
        
        self._subscribed = True
        log.info(f"Successfully subscribed to FeedbackBus with {len(self.registry.event_types)} handler types")
    
    async def unsubscribe(self) -> None:
        """
        Unsubscribe from feedback events.
        
        Note: FeedbackBus.unsubscribe(callback) requires the same callback instance
        that was used in subscribe(). For now, we just mark as unsubscribed.
        A full implementation would store the callback and call bus.unsubscribe(callback).
        """
        if not self._subscribed:
            return
        
        log.info("Unsubscribing from feedback events...")
        # TODO: Store callback reference and call self.bus.unsubscribe(callback)
        self._subscribed = False

