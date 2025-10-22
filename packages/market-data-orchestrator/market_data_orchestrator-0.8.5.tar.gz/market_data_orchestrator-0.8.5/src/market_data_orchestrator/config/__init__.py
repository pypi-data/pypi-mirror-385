"""
Configuration module with focused settings groups.

Phase 3 SOLID Refactoring: Addresses Interface Segregation Principle (ISP) violation.
Settings split into cohesive groups so components only depend on what they need.
"""

from .runtime import RuntimeSettings
from .feedback import FeedbackSettings
from .security import SecuritySettings
from .provider import ProviderSettings
from .infrastructure import InfrastructureSettings
from .unified import OrchestratorSettings

__all__ = [
    "RuntimeSettings",
    "FeedbackSettings",
    "SecuritySettings",
    "ProviderSettings",
    "InfrastructureSettings",
    "OrchestratorSettings",
]

