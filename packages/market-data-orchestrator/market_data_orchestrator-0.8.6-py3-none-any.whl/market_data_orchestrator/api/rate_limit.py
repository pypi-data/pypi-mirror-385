"""
Redis-backed rate limiter for control endpoints.

Uses token bucket algorithm with automatic expiration.
Falls back to allowing requests if Redis is unavailable (fail-open).

Phase 6.3 Day 3 implementation.
Phase 1 Refactoring: Now uses ServiceContainer instead of module-level global.
"""

from __future__ import annotations
import logging
from typing import Optional

import redis.asyncio as redis
from prometheus_client import Counter
from fastapi import HTTPException

from .._internal.container import ServiceContainer

log = logging.getLogger(__name__)

# Backward compatibility: Keep module-level reference
# Will be removed in v1.0.0 after deprecation period
_redis_client: redis.Redis | None = None
_container: ServiceContainer | None = None

# Prometheus metrics
rate_limit_hits = Counter(
    "orchestrator_rate_limit_hits_total",
    "Total rate limit checks",
    ["action", "result"]  # result: allowed, denied, redis_error
)

rate_limit_redis_errors = Counter(
    "orchestrator_rate_limit_redis_errors_total",
    "Redis errors during rate limiting"
)


def set_container(container: ServiceContainer) -> None:
    """
    Set the service container for rate limiting.
    
    Phase 1: New preferred way to manage rate limiter.
    
    Args:
        container: ServiceContainer instance
    """
    global _container
    _container = container


async def init_rate_limiter(redis_url: str) -> None:
    """
    Initialize Redis client for rate limiting.
    
    Called during FastAPI startup.
    
    Phase 1: Now creates RedisRateLimiter and registers with container if available.
    
    Args:
        redis_url: Redis connection URL (e.g., redis://localhost:6379/1)
    """
    global _redis_client
    
    # Import here to avoid circular dependency
    from .._internal.rate_limiter import RedisRateLimiter
    
    # Create new rate limiter
    limiter = RedisRateLimiter(redis_url)
    await limiter.connect()
    
    # Register with container if available
    if _container is not None:
        _container.register_rate_limiter(limiter)
    
    # Also store Redis client directly for backward compatibility
    _redis_client = limiter._client


async def close_rate_limiter() -> None:
    """
    Close Redis connection.
    
    Called during FastAPI shutdown.
    
    Phase 1: Now closes rate limiter from container if available.
    """
    global _redis_client
    
    # Try to close via container first
    if _container is not None:
        limiter = _container.get_rate_limiter()
        if limiter:
            await limiter.close()
    
    # Also close module-level client for backward compatibility
    if _redis_client:
        try:
            await _redis_client.close()
            log.info("Rate limiter Redis disconnected")
        except Exception as e:
            log.error(f"Error closing rate limiter Redis: {e}")
        finally:
            _redis_client = None


async def is_allowed(action: str, limit: int = 5, period: int = 60) -> bool:
    """
    Check if action is allowed under rate limit.
    
    Uses Redis INCR with EXPIRE for atomic rate limiting.
    Falls back to allowing requests if Redis is unavailable (fail-open).
    
    Phase 1: Tries ServiceContainer first, falls back to module-level global.
    
    Args:
        action: Action name (e.g., 'pause', 'resume', 'reload')
        limit: Maximum actions per period
        period: Time period in seconds
        
    Returns:
        True if action is allowed, False if rate limit exceeded
    """
    # Try container first (new way)
    if _container is not None:
        limiter = _container.get_rate_limiter()
        if limiter:
            return await limiter.is_allowed(action, limit, period)
    
    # Fall back to module-level client (backward compatibility)
    if not _redis_client:
        log.debug("Redis not available, allowing action (fail-open)")
        rate_limit_hits.labels(action=action, result="redis_error").inc()
        return True
    
    key = f"orch:rl:{action}"
    
    try:
        # Atomic increment
        current = await _redis_client.incr(key)
        
        # Set expiration on first increment
        if current == 1:
            await _redis_client.expire(key, period)
        
        allowed = current <= limit
        
        # Update metrics
        result = "allowed" if allowed else "denied"
        rate_limit_hits.labels(action=action, result=result).inc()
        
        log.debug(
            f"Rate limit check: action={action}, count={current}/{limit}, allowed={allowed}"
        )
        
        return allowed
    
    except Exception as e:
        log.error(f"Redis rate limit error: {e}")
        rate_limit_redis_errors.inc()
        # Fail-open: allow action if Redis fails
        rate_limit_hits.labels(action=action, result="redis_error").inc()
        return True


async def enforce_rate(action: str, limit: int = 5, period: int = 60) -> None:
    """
    Check rate limit and raise HTTPException if exceeded.
    
    Convenience wrapper around is_allowed() for FastAPI endpoints.
    
    Phase 1: Tries ServiceContainer first, falls back to module-level function.
    
    Args:
        action: Action name
        limit: Maximum actions per period (default: 5)
        period: Time period in seconds (default: 60)
        
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    # Try container first (new way)
    if _container is not None:
        limiter = _container.get_rate_limiter()
        if limiter:
            await limiter.enforce(action, limit, period)
            return
    
    # Fall back to is_allowed check (backward compatibility)
    allowed = await is_allowed(action, limit=limit, period=period)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: max {limit} '{action}' actions per {period} seconds"
        )

