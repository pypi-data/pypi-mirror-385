"""
Phase 10.1: Pulse Configuration.

Environment variables:
- PULSE_ENABLED: Enable/disable Pulse (default: true)
- EVENT_BUS_BACKEND: Backend type (inmem or redis, default: inmem)
- REDIS_URL: Redis connection URL (default: redis://localhost:6379/0)
- MD_NAMESPACE: Namespace prefix for streams (default: mdp)
- SCHEMA_TRACK: Schema track version (default: v1)
- PUBLISHER_TOKEN: Optional auth token (default: unset)
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class PulseConfig:
    """Configuration for Pulse event bus integration."""
    
    enabled: bool = os.getenv("PULSE_ENABLED", "true").lower() == "true"
    backend: str = os.getenv("EVENT_BUS_BACKEND", "inmem")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ns: str = os.getenv("MD_NAMESPACE", "mdp")
    track: str = os.getenv("SCHEMA_TRACK", "v1")
    publisher_token: str = os.getenv("PUBLISHER_TOKEN", "unset")
    
    @property
    def is_redis(self) -> bool:
        """Check if using Redis backend."""
        return self.backend == "redis"
    
    @property
    def is_inmem(self) -> bool:
        """Check if using in-memory backend."""
        return self.backend == "inmem"

