"""
Redis-backed rate limiter implementation.

Phase 1 Refactoring: Extracted from api/rate_limit.py to implement RateLimiter protocol.
"""

from __future__ import annotations
import logging
from typing import Optional

import redis.asyncio as redis
from fastapi import HTTPException

log = logging.getLogger(__name__)

# Note: Prometheus metrics are defined in api/rate_limit.py to avoid duplication
# We'll import them when needed


class RedisRateLimiter:
    """
    Redis-backed rate limiter using token bucket algorithm.
    
    Implements the RateLimiter protocol.
    Falls back to fail-open if Redis is unavailable.
    """
    
    def __init__(self, redis_url: str):
        """
        Initialize rate limiter.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self) -> None:
        """
        Connect to Redis.
        
        Raises:
            Exception: If connection fails (logged, not raised)
        """
        try:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connection
            await self._client.ping()
            self._connected = True
            log.info(f"Rate limiter Redis connected: {self.redis_url}")
        except Exception as e:
            log.error(f"Failed to connect to rate limiter Redis: {e}")
            log.warning("Rate limiter will fail-open (allow all requests)")
            self._client = None
            self._connected = False
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            try:
                await self._client.close()
                log.info("Rate limiter Redis disconnected")
            except Exception as e:
                log.error(f"Error closing rate limiter Redis: {e}")
            finally:
                self._client = None
                self._connected = False
    
    async def is_allowed(
        self,
        action: str,
        limit: int = 5,
        period: int = 60
    ) -> bool:
        """
        Check if action is allowed under rate limit.
        
        Args:
            action: Action identifier
            limit: Maximum actions per period
            period: Time period in seconds
            
        Returns:
            True if allowed, False if rate limit exceeded
        """
        # Import metrics from api/rate_limit to avoid duplication
        from ..api.rate_limit import rate_limit_hits, rate_limit_redis_errors
        
        if not self._client:
            log.debug("Redis not available, allowing action (fail-open)")
            rate_limit_hits.labels(action=action, result="redis_error").inc()
            return True
        
        key = f"orch:rl:{action}"
        
        try:
            # Atomic increment
            current = await self._client.incr(key)
            
            # Set expiration on first increment
            if current == 1:
                await self._client.expire(key, period)
            
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
            HTTPException: 429 if rate limit exceeded
        """
        allowed = await self.is_allowed(action, limit=limit, period=period)
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: max {limit} '{action}' actions per {period} seconds"
            )
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._connected


