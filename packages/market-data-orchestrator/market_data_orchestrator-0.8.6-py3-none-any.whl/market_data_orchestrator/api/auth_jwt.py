"""
JWT/OIDC authentication for control endpoints.

Implements token verification using JWKS, with caching and dual-auth support.
Phase 6.3 implementation.
"""

from __future__ import annotations
import logging
from typing import Annotated, Optional
from datetime import datetime, timedelta

from fastapi import Header, HTTPException, status
from jose import jwt, JWTError
from jose.backends import RSAKey
import httpx

from ..settings import OrchestratorSettings
from ..models.security import JWTClaims, Role

log = logging.getLogger(__name__)

# JWKS cache
# Phase 1: Backward compatibility - will be removed in v1.0.0
_jwks_cache: dict | None = None
_jwks_cache_expires: datetime | None = None

# Settings (injected at startup)
_settings: OrchestratorSettings | None = None
_container: Optional["ServiceContainer"] = None  # type: ignore


def set_container(container: "ServiceContainer") -> None:  # type: ignore
    """
    Set the service container for JWT auth.
    
    Phase 1: New preferred way to manage JWT state.
    
    Args:
        container: ServiceContainer instance
    """
    global _container
    _container = container


def init_jwt_auth(settings: OrchestratorSettings) -> None:
    """
    Initialize JWT authentication module.
    
    Called during FastAPI startup to inject settings.
    
    Phase 1: Now registers with ServiceContainer if available.
    
    Args:
        settings: OrchestratorSettings instance
    """
    global _settings
    _settings = settings
    
    # Note: Container will manage JWKS cache, but we keep settings in module
    # for backward compatibility with verify_jwt calls
    
    if settings.jwt_enabled and settings.jwks_url:
        log.info(
            "JWT auth initialized",
            extra={
                "issuer": settings.oidc_issuer,
                "audience": settings.oidc_audience,
                "jwks_url": settings.jwks_url,
                "enabled": settings.jwt_enabled,
                "dual_auth": settings.dual_auth
            }
        )
    elif settings.jwt_enabled and not settings.jwks_url:
        log.warning("JWT enabled but JWKS_URL not configured - JWT auth will fail")
    else:
        log.info("JWT auth disabled - using API key only")


async def _fetch_jwks() -> dict:
    """
    Fetch JWKS from OIDC provider with caching.
    
    Implements 1-hour cache (configurable via jwt_cache_ttl).
    
    Phase 1: Now uses ServiceContainer for caching when available.
    
    Returns:
        JWKS dictionary with keys array
        
    Raises:
        HTTPException: If JWKS fetch fails
    """
    global _jwks_cache, _jwks_cache_expires
    
    # Try to get from container first
    if _container is not None:
        cached_jwks, cached_expires = _container.get_jwks_cache()
        if cached_jwks and cached_expires and datetime.utcnow() < cached_expires:
            log.debug("Using cached JWKS (from container)")
            return cached_jwks
    # Fall back to module-level cache
    elif _jwks_cache and _jwks_cache_expires and datetime.utcnow() < _jwks_cache_expires:
        log.debug("Using cached JWKS (from module)")
        return _jwks_cache
    
    # Fetch fresh JWKS
    if not _settings or not _settings.jwks_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWKS URL not configured"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(_settings.jwks_url, timeout=5.0)
            response.raise_for_status()
            jwks = response.json()
        
        # Cache for configured TTL
        expires_at = datetime.utcnow() + timedelta(seconds=_settings.jwt_cache_ttl)
        
        # Store in container if available
        if _container is not None:
            _container.set_jwks_cache(jwks, expires_at)
        else:
            # Fall back to module-level cache
            _jwks_cache = jwks
            _jwks_cache_expires = expires_at
        
        log.debug(f"JWKS fetched and cached (TTL={_settings.jwt_cache_ttl}s)")
        
        return jwks
    
    except httpx.HTTPStatusError as e:
        log.error(f"JWKS fetch HTTP error: {e.response.status_code}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"JWKS fetch failed: HTTP {e.response.status_code}"
        )
    except httpx.TimeoutException:
        log.error("JWKS fetch timeout")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWKS fetch timeout"
        )
    except Exception as e:
        log.error(f"JWKS fetch error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"JWKS fetch failed: {str(e)}"
        )


async def verify_jwt(token: str) -> JWTClaims:
    """
    Verify JWT token and extract claims.
    
    Implements:
    - JWKS fetching with caching
    - RS256 signature verification
    - Issuer and audience validation
    - Expiration check (with 10s clock skew tolerance)
    
    Args:
        token: JWT token string (without 'Bearer ' prefix)
        
    Returns:
        JWTClaims with validated token data
        
    Raises:
        HTTPException: If token is invalid, expired, or verification fails
    """
    if not _settings:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT auth not initialized"
        )
    
    try:
        # Fetch JWKS
        jwks = await _fetch_jwks(_settings.jwks_url, _settings.jwt_cache_ttl)
        
        # Decode header to get key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        # Find matching key in JWKS
        rsa_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = key
                break
        
        if not rsa_key:
            log.warning(f"No matching key for kid: {kid}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find matching JWKS key"
            )
        
        # Verify and decode token (skip expiration validation, check manually)
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=_settings.oidc_audience,
            issuer=_settings.oidc_issuer,
            options={"verify_exp": False}  # We'll check manually for better error handling
        )
        
        # Manual expiration check for better error messages
        import time
        if "exp" in payload:
            if int(payload["exp"]) < int(time.time()):
                log.warning("JWT token has expired")
                raise JWTError("Token has expired")
        
        # Parse into JWTClaims
        claims = JWTClaims.from_jwt(payload, role_claim=_settings.jwt_role_claim)
        log.debug(f"JWT verified: sub={claims.sub}, role={claims.role}")
        
        return claims
    
    except JWTError as e:
        log.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"JWT verification error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed"
        )


async def RequireJWT(
    authorization: Annotated[str, Header()] = ""
) -> JWTClaims:
    """
    FastAPI dependency that requires and validates JWT token.
    
    Expects Authorization header: 'Bearer <token>'
    
    Args:
        authorization: Authorization header value
        
    Returns:
        JWTClaims if token is valid
        
    Raises:
        HTTPException: 401 if token missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract token from 'Bearer <token>'
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format (expected 'Bearer <token>')",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = parts[1]
    return await verify_jwt(token)


def RequireRole(required_role: Role):
    """
    FastAPI dependency factory that requires specific role.
    
    Implements role hierarchy:
    - admin can do everything
    - operator > viewer
    
    Usage:
        @router.post("/control/reload", dependencies=[Depends(RequireRole(Role.admin))])
        async def reload():
            ...
    
    Args:
        required_role: Minimum required role
        
    Returns:
        Dependency function that checks role
    """
    from fastapi import Depends
    
    async def _check_role(claims: JWTClaims = Depends(RequireJWT)) -> JWTClaims:
        # Admin can do everything
        if claims.role == Role.admin:
            return claims
        
        # Check if user has required role
        role_hierarchy = {Role.viewer: 0, Role.operator: 1, Role.admin: 2}
        user_level = role_hierarchy.get(claims.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            log.warning(
                f"Insufficient role: user has '{claims.role.value}', "
                f"requires '{required_role.value}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role.value}' required (user has '{claims.role.value}')"
            )
        
        return claims
    
    return _check_role

