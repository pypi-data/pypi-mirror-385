"""
Tests for federation API.

Phase 6.3 Day 5: Multi-orchestrator federation tests
"""

import pytest
import respx
import httpx

# Set default timeout for all tests in this module to prevent hanging
pytestmark = pytest.mark.timeout(10)


@pytest.mark.asyncio
@respx.mock
async def test_list_peers_empty(client, jwt_enabled_settings, mock_jwks, test_jwt_viewer, monkeypatch):
    """Test listing peers when none are configured."""
    from market_data_orchestrator.api.auth_jwt import init_jwt_auth
    from market_data_orchestrator.settings import OrchestratorSettings
    
    # No peers configured
    monkeypatch.setenv("ORCH_FEDERATION_PEERS", "")
    
    settings = OrchestratorSettings()
    init_jwt_auth(settings)
    
    # Request with viewer token
    response = client.get(
        "/federation/list",
        headers={"Authorization": f"Bearer {test_jwt_viewer}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "peers" in data
    assert data["peers"] == []


@pytest.mark.asyncio
@respx.mock
async def test_list_peers_configured(test_orchestrator, mock_jwks, test_jwt_viewer):
    """Test listing configured peers."""
    from tests.conftest import make_federation_client
    
    client = make_federation_client(
        test_orchestrator,
        federation_peers="http://peer1:8080,http://peer2:8080,http://peer3:8080"
    )
    
    response = client.get(
        "/federation/list",
        headers={"Authorization": f"Bearer {test_jwt_viewer}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["peers"]) == 3
    assert "http://peer1:8080" in data["peers"]
    assert "http://peer2:8080" in data["peers"]
    assert "http://peer3:8080" in data["peers"]


@pytest.mark.asyncio
@respx.mock
async def test_forward_success(test_orchestrator, mock_jwks, test_jwt_admin):
    """Test successful command forwarding to peer."""
    from tests.conftest import make_federation_client
    
    client = make_federation_client(test_orchestrator, federation_peers="http://peer1:8080")
    
    # Mock peer response
    respx.post("http://peer1:8080/control/pause").mock(
        return_value=httpx.Response(200, json={"status": "ok", "detail": "Paused"})
    )
    
    # Forward command
    response = client.post(
        "/federation/forward/peer1",
        headers={"Authorization": f"Bearer {test_jwt_admin}"},
        json={
            "path": "/control/pause",
            "method": "POST",
            "payload": {}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["target"] == "peer1"
    assert data["status_code"] == 200
    assert data["data"]["status"] == "ok"


@pytest.mark.asyncio
@respx.mock
async def test_forward_peer_not_found(test_orchestrator, mock_jwks, test_jwt_admin):
    """Test forwarding to unknown peer returns 404."""
    from tests.conftest import make_federation_client
    
    client = make_federation_client(test_orchestrator, federation_peers="http://peer1:8080")
    
    # Try to forward to unknown peer
    response = client.post(
        "/federation/forward/unknown-peer",
        headers={"Authorization": f"Bearer {test_jwt_admin}"},
        json={
            "path": "/control/pause",
            "method": "POST"
        }
    )
    
    assert response.status_code == 404
    assert "unknown peer" in response.json()["detail"].lower()


@pytest.mark.asyncio
@respx.mock
async def test_forward_connection_error(test_orchestrator, mock_jwks, test_jwt_admin):
    """Test forwarding with connection error returns 502."""
    from tests.conftest import make_federation_client
    
    client = make_federation_client(test_orchestrator, federation_peers="http://peer1:8080")
    
    # Mock connection error
    respx.post("http://peer1:8080/control/pause").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )
    
    response = client.post(
        "/federation/forward/peer1",
        headers={"Authorization": f"Bearer {test_jwt_admin}"},
        json={
            "path": "/control/pause",
            "method": "POST"
        }
    )
    
    assert response.status_code == 502
    assert "failed" in response.json()["detail"].lower()


@pytest.mark.asyncio
@respx.mock
async def test_forward_timeout(test_orchestrator, mock_jwks, test_jwt_admin):
    """Test forwarding with timeout returns 504."""
    from tests.conftest import make_federation_client
    
    client = make_federation_client(test_orchestrator, federation_peers="http://peer1:8080")
    
    # Mock timeout
    respx.post("http://peer1:8080/control/pause").mock(
        side_effect=httpx.TimeoutException("Request timeout")
    )
    
    response = client.post(
        "/federation/forward/peer1",
        headers={"Authorization": f"Bearer {test_jwt_admin}"},
        json={
            "path": "/control/pause",
            "method": "POST"
        }
    )
    
    assert response.status_code == 504
    assert "timed out" in response.json()["detail"].lower()


@pytest.mark.asyncio
@respx.mock
async def test_forward_requires_admin_role(test_orchestrator, mock_jwks, test_jwt_operator):
    """Test that forwarding requires admin role (operator should be denied)."""
    from tests.conftest import make_federation_client
    
    client = make_federation_client(test_orchestrator, federation_peers="http://peer1:8080")
    
    # Mock peer (won't be called due to role check)
    respx.post("http://peer1:8080/control/pause").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    
    # Try with operator token (should fail)
    response = client.post(
        "/federation/forward/peer1",
        headers={"Authorization": f"Bearer {test_jwt_operator}"},
        json={
            "path": "/control/pause",
            "method": "POST"
        }
    )
    
    assert response.status_code == 403
    detail = response.json()["detail"].lower()
    assert "forbidden" in detail or "admin" in detail


@pytest.mark.asyncio
@respx.mock
async def test_forward_metrics_incremented(test_orchestrator, mock_jwks, test_jwt_admin):
    """Test that federation metrics are incremented correctly."""
    from tests.conftest import make_federation_client
    from market_data_orchestrator.api.federation import federation_requests_total
    
    client = make_federation_client(test_orchestrator, federation_peers="http://peer1:8080")
    
    # Get initial metric value
    initial_count = federation_requests_total.labels(
        target="peer1",
        action="/control/pause",
        status="200"
    )._value.get()
    
    # Mock successful peer response
    respx.post("http://peer1:8080/control/pause").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    
    # Forward command
    response = client.post(
        "/federation/forward/peer1",
        headers={"Authorization": f"Bearer {test_jwt_admin}"},
        json={
            "path": "/control/pause",
            "method": "POST"
        }
    )
    
    assert response.status_code == 200
    
    # Verify metric incremented
    current_count = federation_requests_total.labels(
        target="peer1",
        action="/control/pause",
        status="200"
    )._value.get()
    
    assert current_count > initial_count

