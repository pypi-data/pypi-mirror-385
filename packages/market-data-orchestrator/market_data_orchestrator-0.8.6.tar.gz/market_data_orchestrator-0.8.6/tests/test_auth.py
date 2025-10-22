"""
Tests for API key authentication.
"""

import pytest


def test_auth_ping_success(client, api_key):
    """Test successful authentication with valid API key."""
    response = client.get("/auth/ping", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Authentication successful" in data["message"]


def test_auth_ping_invalid_key(client, api_key):
    """Test authentication failure with invalid API key."""
    response = client.get("/auth/ping", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401
    data = response.json()
    assert "Invalid API key" in data["detail"]


def test_auth_ping_missing_key(client, api_key):
    """Test authentication failure with missing API key."""
    response = client.get("/auth/ping")  # No header
    assert response.status_code == 401


def test_auth_ping_no_env_key(client, monkeypatch):
    """Test that endpoints are denied when ORCH_API_KEY not set."""
    monkeypatch.delenv("ORCH_API_KEY", raising=False)
    response = client.get("/auth/ping", headers={"X-API-Key": "any-key"})
    assert response.status_code == 401
    data = response.json()
    assert "not configured" in data["detail"]


def test_auth_ping_empty_env_key(client, monkeypatch):
    """Test that empty ORCH_API_KEY is treated as not configured."""
    monkeypatch.setenv("ORCH_API_KEY", "")
    response = client.get("/auth/ping", headers={"X-API-Key": "any-key"})
    assert response.status_code == 401

