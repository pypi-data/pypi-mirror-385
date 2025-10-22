"""
Tests for control API endpoints.

Phase 6.3: Updated to use JWT authentication instead of API keys.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def jwt_client(test_orchestrator, test_container, jwt_enabled_settings, mock_jwks):
    """Create test client with JWT authentication enabled."""
    from market_data_orchestrator.health import build_app
    from market_data_orchestrator.api.deps import set_orchestrator_instance, set_container
    from market_data_orchestrator.api.auth_jwt import init_jwt_auth
    
    # Configure JWT settings on orchestrator
    test_orchestrator.settings.jwt_enabled = True
    test_orchestrator.settings.oidc_issuer = "http://localhost-test/"
    test_orchestrator.settings.oidc_audience = "market-data-orchestrator"
    test_orchestrator.settings.jwks_url = "http://localhost-test/.well-known/jwks.json"
    test_orchestrator.settings.dual_auth = False
    
    # Initialize container and orchestrator
    set_container(test_container)
    set_orchestrator_instance(test_orchestrator)
    
    # Initialize JWT auth
    init_jwt_auth(test_orchestrator.settings)
    
    # Build app
    app = build_app(test_orchestrator)
    
    return TestClient(app)


def test_control_status_no_auth(client):
    """Test that /control/status doesn't require authentication."""
    response = client.get("/control/status")
    assert response.status_code == 200
    data = response.json()
    assert "running" in data
    assert "paused" in data


def test_pause_requires_auth(client):
    """Test that pause endpoint requires authentication."""
    response = client.post("/control/pause")
    assert response.status_code == 401


def test_pause_success(jwt_client, test_jwt_operator):
    """Test successful pause operation with JWT auth."""
    response = jwt_client.post(
        "/control/pause",
        headers={"Authorization": f"Bearer {test_jwt_operator}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "paused" in data["detail"].lower()
    
    # Verify status reflects pause
    status = jwt_client.get("/control/status").json()
    assert status["paused"] is True


def test_resume_success(jwt_client, test_jwt_operator):
    """Test successful resume operation with JWT auth."""
    # Pause first
    jwt_client.post(
        "/control/pause",
        headers={"Authorization": f"Bearer {test_jwt_operator}"}
    )
    
    # Then resume
    response = jwt_client.post(
        "/control/resume",
        headers={"Authorization": f"Bearer {test_jwt_operator}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "resumed" in data["detail"].lower()
    
    # Verify status reflects resume
    status = jwt_client.get("/control/status").json()
    assert status["paused"] is False


def test_reload_success(jwt_client, test_jwt_admin):
    """Test successful reload operation with JWT auth (admin only)."""
    response = jwt_client.post(
        "/control/reload",
        headers={"Authorization": f"Bearer {test_jwt_admin}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "reload" in data["detail"].lower()


def test_pause_resume_cycle(jwt_client, test_jwt_operator):
    """Test complete pause/resume cycle with JWT auth."""
    # Initial state
    status = jwt_client.get("/control/status").json()
    assert status["paused"] is False
    
    # Pause
    response = jwt_client.post(
        "/control/pause",
        headers={"Authorization": f"Bearer {test_jwt_operator}"}
    )
    assert response.status_code == 200
    status = jwt_client.get("/control/status").json()
    assert status["paused"] is True
    
    # Resume
    response = jwt_client.post(
        "/control/resume",
        headers={"Authorization": f"Bearer {test_jwt_operator}"}
    )
    assert response.status_code == 200
    status = jwt_client.get("/control/status").json()
    assert status["paused"] is False


def test_rate_limiting_with_redis(jwt_client, test_jwt_operator):
    """
    Test that control endpoints handle rate limiting gracefully.
    
    Note: Full rate limiting tests are in test_rate_limit.py with proper fakeredis setup.
    This test verifies endpoints don't crash when rate limiting is configured.
    Since Redis isn't available in this test context, it should fail-open (allow requests).
    """
    # Make multiple requests - should all succeed in fail-open mode
    for i in range(6):
        response = jwt_client.post(
            "/control/pause",
            headers={"Authorization": f"Bearer {test_jwt_operator}"}
        )
        # In fail-open mode (no Redis), all requests succeed
        assert response.status_code == 200, f"Request {i+1} failed unexpectedly"
    
    # Verify endpoint still works correctly
    assert response.json()["status"] == "ok"


def test_invalid_jwt(jwt_client):
    """Test that invalid JWT is rejected."""
    response = jwt_client.post(
        "/control/pause",
        headers={"Authorization": "Bearer invalid-token-here"}
    )
    assert response.status_code == 401


def test_control_status_includes_all_fields(client):
    """Test that status endpoint returns all expected fields."""
    response = client.get("/control/status")
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "running" in data
    assert "started" in data
    assert "paused" in data
    assert "settings" in data
    
    # Check settings fields
    assert "runtime_mode" in data["settings"]
    assert "feedback_enabled" in data["settings"]

