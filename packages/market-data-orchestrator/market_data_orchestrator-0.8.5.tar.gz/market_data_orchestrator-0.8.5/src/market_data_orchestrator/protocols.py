"""
Protocol definitions for external dependencies.

These protocols define the interfaces that the orchestrator depends on,
enabling dependency inversion and making the system more testable and extensible.

Phase 1 SOLID Refactoring: These protocols allow us to depend on abstractions
rather than concrete implementations.
"""

from __future__ import annotations
from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class Provider(Protocol):
    """
    Protocol for market data providers (IBKR, Alpaca, etc.).
    
    Any provider implementation must satisfy this interface to be used
    by the orchestrator.
    """
    
    is_connected: bool
    
    async def connect(self) -> None:
        """
        Establish connection to the data provider.
        
        Raises:
            ConnectionError: If connection fails
        """
        ...
    
    async def close(self) -> None:
        """
        Close connection to the data provider.
        
        Should handle cleanup gracefully even if not connected.
        """
        ...


@runtime_checkable
class Runtime(Protocol):
    """
    Protocol for pipeline runtime implementations.
    
    Defines the interface for different pipeline execution modes
    (dag, streaming, batch, etc.).
    """
    
    async def start_pipeline(self, source: Any) -> None:
        """
        Start the pipeline with the given data source.
        
        Args:
            source: Data source (typically a Provider)
        """
        ...
    
    async def stop(self) -> None:
        """
        Stop the pipeline and clean up resources.
        """
        ...
    
    def status(self) -> Dict[str, Any]:
        """
        Get current pipeline status.
        
        Returns:
            Dictionary with pipeline status information
        """
        ...


@runtime_checkable
class FeedbackBus(Protocol):
    """
    Protocol for feedback/event bus implementations.
    
    Supports pub/sub pattern for system events and backpressure signals.
    """
    
    async def connect(self) -> None:
        """
        Connect to the feedback bus (e.g., Redis).
        
        Raises:
            ConnectionError: If connection fails
        """
        ...
    
    async def disconnect(self) -> None:
        """
        Disconnect from the feedback bus.
        """
        ...
    
    def on(self, event: str):
        """
        Decorator to register an event handler.
        
        Args:
            event: Event name to listen for
            
        Returns:
            Decorator function
            
        Example:
            @bus.on("backpressure")
            async def handle_backpressure(data):
                ...
        """
        ...


@runtime_checkable
class RateLimiter(Protocol):
    """
    Protocol for rate limiting implementations.
    
    Supports different backends (Redis, in-memory, etc.).
    """
    
    async def is_allowed(
        self,
        action: str,
        limit: int = 5,
        period: int = 60
    ) -> bool:
        """
        Check if an action is allowed under rate limit.
        
        Args:
            action: Action identifier
            limit: Maximum actions per period
            period: Time period in seconds
            
        Returns:
            True if allowed, False if rate limit exceeded
        """
        ...
    
    async def enforce(
        self,
        action: str,
        limit: int = 5,
        period: int = 60
    ) -> None:
        """
        Enforce rate limit, raising exception if exceeded.
        
        Args:
            action: Action identifier
            limit: Maximum actions per period
            period: Time period in seconds
            
        Raises:
            HTTPException: If rate limit exceeded (429)
        """
        ...


@runtime_checkable
class AuditLogger(Protocol):
    """
    Protocol for audit logging implementations.
    
    Defines interface for persistent audit event logging.
    """
    
    async def log(
        self,
        action: str,
        user: str,
        role: str,
        status: str,
        detail: str | None = None,
        **extra_fields
    ) -> None:
        """
        Log an audit event.
        
        Args:
            action: Action performed
            user: User identifier
            role: User role
            status: Action status (success/error/denied)
            detail: Optional detail message
            **extra_fields: Additional fields to log
        """
        ...
    
    def get_recent_events(self, limit: int = 100) -> list[dict]:
        """
        Retrieve recent audit events.
        
        Args:
            limit: Maximum events to return
            
        Returns:
            List of audit event dictionaries
        """
        ...


