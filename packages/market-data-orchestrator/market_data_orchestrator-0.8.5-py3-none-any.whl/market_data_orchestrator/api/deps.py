"""
FastAPI dependency injection for orchestrator instance.

Phase 1 Refactoring: Now uses ServiceContainer instead of module-level global.
Maintains backward compatibility with existing code.
"""

from __future__ import annotations
from typing import Optional
from fastapi import HTTPException, Request, status

from .._internal.container import ServiceContainer

# Backward compatibility: Keep module-level reference
# Will be removed in v1.0.0 after deprecation period
_ORCH: Optional["MarketDataOrchestrator"] = None  # type: ignore
_CONTAINER: Optional[ServiceContainer] = None


def set_container(container: ServiceContainer) -> None:
    """
    Set the service container for dependency injection.
    
    Phase 1: New preferred way to register dependencies.
    
    Args:
        container: ServiceContainer instance
    """
    global _CONTAINER
    _CONTAINER = container


def get_container() -> ServiceContainer:
    """
    Get the service container.
    
    Returns:
        ServiceContainer instance
        
    Raises:
        RuntimeError: If container not initialized
    """
    if _CONTAINER is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service container not initialized"
        )
    return _CONTAINER


def set_orchestrator_instance(orch: "MarketDataOrchestrator") -> None:  # type: ignore
    """
    Set the global orchestrator instance for dependency injection.
    
    Called once during FastAPI app startup.
    
    Phase 1: Now registers with ServiceContainer if available,
    falls back to module-level global for backward compatibility.
    
    Args:
        orch: MarketDataOrchestrator instance
    """
    global _ORCH
    _ORCH = orch
    
    # Also register with container if available
    if _CONTAINER is not None:
        _CONTAINER.register_orchestrator(orch)


def get_orchestrator() -> "MarketDataOrchestrator":  # type: ignore
    """
    FastAPI dependency to retrieve the orchestrator instance.
    
    Phase 1: Tries ServiceContainer first, falls back to module-level global.
    
    Returns:
        Active MarketDataOrchestrator instance
        
    Raises:
        HTTPException: If orchestrator not initialized
    """
    # Try container first (new way)
    if _CONTAINER is not None:
        try:
            return _CONTAINER.get_orchestrator()
        except RuntimeError:
            pass  # Fall through to old way
    
    # Fall back to module-level global (backward compatibility)
    if _ORCH is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Orchestrator not initialized"
        )
    return _ORCH


def get_settings() -> "OrchestratorSettings":  # type: ignore
    """
    FastAPI dependency to retrieve orchestrator settings.
    
    Phase 6.3: Used by auth_jwt and other modules that need settings.
    Phase 1: Now uses ServiceContainer when available.
    
    Returns:
        OrchestratorSettings instance
        
    Raises:
        HTTPException: If orchestrator not initialized
    """
    # Try container first (new way)
    if _CONTAINER is not None:
        try:
            return _CONTAINER.get_settings()
        except RuntimeError:
            pass  # Fall through to old way
    
    # Fall back to getting from orchestrator (backward compatibility)
    orch = get_orchestrator()
    return orch.settings
