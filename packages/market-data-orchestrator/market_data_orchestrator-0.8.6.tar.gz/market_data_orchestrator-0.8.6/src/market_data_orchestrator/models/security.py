"""
Security-related Pydantic models for JWT authentication and RBAC.

Phase 6.3 implementation.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Role(str, Enum):
    """
    User roles for RBAC.
    
    Role hierarchy (from lowest to highest):
    - viewer: Read-only access (GET endpoints)
    - operator: Control actions (pause/resume)
    - admin: Full access (reload, federation)
    """
    viewer = "viewer"
    operator = "operator"
    admin = "admin"


class JWTClaims(BaseModel):
    """
    Parsed JWT token claims.
    
    Represents validated claims from a JWT access token after verification.
    """
    sub: str = Field(..., description="Subject (user ID)")
    email: Optional[str] = Field(None, description="User email")
    role: Role = Field(Role.viewer, description="User role for RBAC")
    iss: str = Field(..., description="Token issuer")
    aud: str = Field(..., description="Token audience")
    exp: int = Field(..., description="Expiration timestamp (Unix epoch)")
    iat: int = Field(..., description="Issued at timestamp (Unix epoch)")
    
    @classmethod
    def from_jwt(cls, payload: dict, role_claim: str = "roles") -> "JWTClaims":
        """
        Parse JWT payload into JWTClaims.
        
        Handles different OIDC provider claim formats:
        - Auth0: roles array with namespace
        - Keycloak: roles array or realm_access.roles
        - Generic: roles or groups
        
        Args:
            payload: Decoded JWT dictionary
            role_claim: Name of claim containing role (e.g., 'roles', 'groups')
        
        Returns:
            JWTClaims instance with validated data
        """
        # Extract role from claim (handles both string and list)
        role_value = payload.get(role_claim, "viewer")
        
        # Handle list of roles (take first one)
        if isinstance(role_value, list):
            role_value = role_value[0] if role_value else "viewer"
        
        # Map to Role enum (default to viewer if invalid)
        try:
            role = Role(role_value)
        except ValueError:
            role = Role.viewer
        
        return cls(
            sub=payload["sub"],
            email=payload.get("email"),
            role=role,
            iss=payload["iss"],
            aud=payload["aud"],
            exp=payload["exp"],
            iat=payload["iat"]
        )

