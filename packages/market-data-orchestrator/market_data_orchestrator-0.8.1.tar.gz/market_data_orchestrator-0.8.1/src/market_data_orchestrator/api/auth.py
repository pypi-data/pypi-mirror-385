"""
API Key authentication for control endpoints.

Simple header-based auth suitable for v0.2.0.
For production, migrate to JWT/OAuth2.
"""

from __future__ import annotations
import os
from fastapi import APIRouter, Depends, Header, HTTPException, status

router = APIRouter(tags=["auth"])


class RequireAPIKey:
    """
    FastAPI dependency for API key authentication.
    
    Checks X-API-Key header against ORCH_API_KEY environment variable.
    If ORCH_API_KEY is not set, denies all requests (secure by default).
    
    Usage:
        @router.post("/control/pause", dependencies=[Depends(RequireAPIKey())])
        async def pause():
            ...
    """
    
    def __init__(self, header_name: str = "X-API-Key") -> None:
        self.header_name = header_name
    
    async def __call__(self, x_api_key: str = Header(default="")) -> None:
        """
        Validate API key from request header.
        
        Args:
            x_api_key: API key from X-API-Key header
            
        Raises:
            HTTPException: 401 if key invalid or not configured
        """
        expected = os.getenv("ORCH_API_KEY", "").strip()
        
        if not expected:
            # No API key configured - deny access
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Orchestrator API key not configured (set ORCH_API_KEY environment variable)",
            )
        
        if x_api_key != expected:
            # Invalid API key
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )


@router.get("/auth/ping", dependencies=[Depends(RequireAPIKey())])
async def auth_ping() -> dict:
    """
    Ping endpoint to test API key authentication.
    
    Returns:
        Simple OK response if authenticated
    """
    return {"status": "ok", "message": "Authentication successful"}

