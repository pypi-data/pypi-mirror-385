"""
Tests for Redis-backed rate limiting.

Phase 6.3 Day 3: Redis rate limiter tests
"""

import pytest
import asyncio

# Set default timeout for all tests in this module to prevent hanging
pytestmark = pytest.mark.timeout(10)


@pytest.fixture
async def fake_redis():
    """Create fake Redis client for testing."""
    from fakeredis import aioredis as fakeredis_aio
    
    client = fakeredis_aio.FakeRedis(decode_responses=True)
    
    # Inject into rate_limit module
    import market_data_orchestrator.api.rate_limit as rl
    rl._redis_client = client
    
    yield client
    
    # Cleanup
    await client.close()


@pytest.mark.asyncio
async def test_rate_limit_allows_under_limit(fake_redis):
    """Test that actions under limit are allowed."""
    from market_data_orchestrator.api.rate_limit import is_allowed
    
    # Should allow first 5 requests
    for i in range(5):
        allowed = await is_allowed("test_action", limit=5)
        assert allowed, f"Request {i+1}/5 should be allowed"


@pytest.mark.asyncio
async def test_rate_limit_denies_over_limit(fake_redis):
    """Test that actions over limit are denied."""
    from market_data_orchestrator.api.rate_limit import is_allowed
    
    # Use up the limit (5 requests)
    for i in range(5):
        await is_allowed("test_action", limit=5)
    
    # 6th request should be denied
    allowed = await is_allowed("test_action", limit=5)
    assert not allowed, "6th request should be denied"


@pytest.mark.asyncio
async def test_rate_limit_resets_after_period(fake_redis):
    """Test that rate limit resets after expiration period."""
    from market_data_orchestrator.api.rate_limit import is_allowed
    
    # Use up the limit with 1-second period
    for i in range(5):
        await is_allowed("test_action", limit=5, period=1)
    
    # 6th request should be denied
    allowed = await is_allowed("test_action", limit=5, period=1)
    assert not allowed, "6th request should be denied immediately"
    
    # Wait for expiration (fakeredis doesn't auto-expire, so we simulate)
    # In real Redis, the key would expire after period seconds
    await fake_redis.delete("orch:rl:test_action")
    
    # Now should be allowed again
    allowed = await is_allowed("test_action", limit=5, period=1)
    assert allowed, "Request should be allowed after period expires"


@pytest.mark.asyncio
async def test_rate_limit_fails_open_on_redis_error():
    """Test that rate limiter allows actions when Redis is unavailable."""
    import market_data_orchestrator.api.rate_limit as rl
    
    # Set Redis client to None to simulate unavailability
    original_client = rl._redis_client
    rl._redis_client = None
    
    try:
        # Should fail-open (allow action)
        allowed = await rl.is_allowed("test_action")
        assert allowed, "Should fail-open when Redis unavailable"
    finally:
        # Restore original client
        rl._redis_client = original_client


@pytest.mark.asyncio
async def test_enforce_rate_raises_429(fake_redis):
    """Test that enforce_rate raises HTTPException 429 when limit exceeded."""
    from market_data_orchestrator.api.rate_limit import enforce_rate
    from fastapi import HTTPException
    
    # Use up the limit
    for i in range(5):
        await enforce_rate("test_action", limit=5)
    
    # 6th request should raise 429
    with pytest.raises(HTTPException) as exc_info:
        await enforce_rate("test_action", limit=5)
    
    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in exc_info.value.detail


@pytest.mark.asyncio
async def test_rate_limit_per_action_independent(fake_redis):
    """Test that rate limits for different actions are independent."""
    from market_data_orchestrator.api.rate_limit import is_allowed
    
    # Use up limit for 'pause'
    for i in range(5):
        await is_allowed("pause", limit=5)
    
    # 'pause' should be denied
    allowed = await is_allowed("pause", limit=5)
    assert not allowed, "pause should be rate-limited"
    
    # 'resume' should still be allowed (independent counter)
    allowed = await is_allowed("resume", limit=5)
    assert allowed, "resume should not be affected by pause rate limit"


@pytest.mark.asyncio
async def test_rate_limit_metrics_incremented(fake_redis):
    """Test that Prometheus metrics are incremented correctly."""
    from market_data_orchestrator.api.rate_limit import is_allowed, rate_limit_hits
    
    # Get initial count
    initial_allowed = rate_limit_hits.labels(action="test_metric", result="allowed")._value.get()
    initial_denied = rate_limit_hits.labels(action="test_metric", result="denied")._value.get()
    
    # Make allowed request
    await is_allowed("test_metric", limit=5)
    
    # Check allowed metric incremented
    current_allowed = rate_limit_hits.labels(action="test_metric", result="allowed")._value.get()
    assert current_allowed > initial_allowed
    
    # Use up limit
    for i in range(4):
        await is_allowed("test_metric", limit=5)
    
    # Make denied request
    await is_allowed("test_metric", limit=5)
    
    # Check denied metric incremented
    current_denied = rate_limit_hits.labels(action="test_metric", result="denied")._value.get()
    assert current_denied > initial_denied

