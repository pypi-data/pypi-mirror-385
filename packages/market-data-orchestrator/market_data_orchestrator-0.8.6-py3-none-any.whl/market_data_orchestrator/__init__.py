"""
Market Data Orchestrator

A deployable orchestration service that wires providers → pipeline → store,
subscribes to feedback events, and exposes health/metrics endpoints.
"""

__version__ = "0.1.0"

from .orchestrator import MarketDataOrchestrator
from .settings import OrchestratorSettings

__all__ = ["MarketDataOrchestrator", "OrchestratorSettings"]

