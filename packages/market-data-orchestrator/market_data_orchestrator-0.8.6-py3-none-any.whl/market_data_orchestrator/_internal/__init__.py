"""
Internal implementation modules.

This package contains internal refactored components. These modules are NOT
part of the public API and may change without notice between versions.

Public API users should only import from:
- market_data_orchestrator.MarketDataOrchestrator
- market_data_orchestrator.OrchestratorSettings

Phase 1: ServiceContainer for dependency injection
Phase 2: Specialized services for orchestrator responsibilities
"""

from .container import ServiceContainer
from .lifecycle import LifecycleManager
from .registry import ComponentRegistry
from .control_service import ControlPlaneService
from .status_aggregator import StatusAggregator
from .rate_limiter import RedisRateLimiter

__all__ = [
    "ServiceContainer",
    "LifecycleManager",
    "ComponentRegistry",
    "ControlPlaneService",
    "StatusAggregator",
    "RedisRateLimiter",
]

