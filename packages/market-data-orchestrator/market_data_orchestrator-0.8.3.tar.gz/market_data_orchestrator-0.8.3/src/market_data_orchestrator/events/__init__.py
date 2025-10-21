"""
Extensible event handling system.

Phase 3 SOLID Refactoring: Addresses Open/Closed Principle (OCP) violation.
Event handlers are now extensible without modifying core code.
"""

from .handler import EventHandler
from .registry import EventRegistry
from .handlers import BackpressureHandler, HealthCheckHandler, ErrorHandler

__all__ = [
    "EventHandler",
    "EventRegistry",
    "BackpressureHandler",
    "HealthCheckHandler",
    "ErrorHandler",
]

