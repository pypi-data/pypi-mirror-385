"""
Unified settings for the Market Data Orchestrator.

Phase 3 SOLID Refactoring: Settings now split into focused groups following ISP.
This module maintains backward compatibility while using the new structure internally.
"""

# Phase 3: Import from new config module
from .config import (
    OrchestratorSettings,
    RuntimeSettings,
    FeedbackSettings,
    SecuritySettings,
    ProviderSettings,
    InfrastructureSettings,
)

# Backward compatibility: export OrchestratorSettings as before
__all__ = [
    "OrchestratorSettings",
    # Phase 3: Also export focused groups for new code
    "RuntimeSettings",
    "FeedbackSettings",
    "SecuritySettings",
    "ProviderSettings",
    "InfrastructureSettings",
]

