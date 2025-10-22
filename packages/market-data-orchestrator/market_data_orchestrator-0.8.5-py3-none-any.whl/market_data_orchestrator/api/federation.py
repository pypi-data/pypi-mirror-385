"""
Federation API for multi-orchestrator deployments.

Allows one orchestrator instance to discover and forward control commands
to peer orchestrators in a federated setup.

Phase 6.3 Day 5: MVP implementation.
Phase 8.0 Day 2: Federation contract adoption from Core v1.1.0.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel
from prometheus_client import Counter

# Phase 8.0 Day 2: Import Core federation contracts
from market_data_core.federation import ClusterTopology
from market_data_core.protocols import FederationDirectory

from .auth_jwt import RequireRole
from .deps import get_settings
from ..models.security import Role
from ..settings import OrchestratorSettings
from ..services.federation_directory import StaticDirectory

log = logging.getLogger(__name__)

router = APIRouter(prefix="/federation", tags=["federation"])

# Prometheus metrics
federation_requests_total = Counter(
    "orchestrator_federation_requests_total",
    "Total federation requests to peer orchestrators",
    ["target", "action", "status"]
)


def _parse_peers(peers_str: str) -> List[str]:
    """
    Parse comma-separated peer list from settings.
    
    Args:
        peers_str: Comma-separated peer URLs
        
    Returns:
        List of peer URLs
    """
    return [p.strip() for p in peers_str.split(",") if p.strip()]


def get_federation_directory(
    settings: OrchestratorSettings = Depends(get_settings)
) -> FederationDirectory:
    """
    Get federation directory instance.
    
    Phase 8.0 Day 2: Dependency for FederationDirectory protocol.
    
    Returns:
        FederationDirectory implementation (StaticDirectory)
    """
    return StaticDirectory(settings)


class PeerListResponse(BaseModel):
    """Response model for /federation/list endpoint."""
    peers: List[str]


class ForwardRequest(BaseModel):
    """Request model for /federation/forward endpoint."""
    path: str = Body(..., description="Endpoint path on peer (e.g., /control/pause)")
    method: str = Body(default="POST", description="HTTP method (GET, POST, etc.)")
    payload: Optional[Dict[str, Any]] = Body(default=None, description="Request payload")


class ForwardResponse(BaseModel):
    """Response model for /federation/forward endpoint."""
    target: str
    status_code: int
    data: Optional[Dict[str, Any]] = None


@router.get("/topology", response_model=ClusterTopology)
async def get_topology(
    directory: FederationDirectory = Depends(get_federation_directory),
    _claims = Depends(RequireRole(Role.viewer))
) -> ClusterTopology:
    """
    Get cluster topology.
    
    Phase 8.0 Day 2: Returns Core v1.1.0 ClusterTopology contract.
    
    Provides rich topology information including:
    - Cluster ID
    - Node IDs, roles, regions
    - Node health status
    - Endpoint URLs
    
    Requires: viewer role or higher
    
    Returns:
        ClusterTopology with all nodes in the federation
    """
    topology = directory.topology()
    log.debug(f"Returning topology with {len(topology.nodes)} nodes")
    return topology


@router.get("/list", response_model=PeerListResponse)
async def list_peers(
    settings: OrchestratorSettings = Depends(get_settings),
    _claims = Depends(RequireRole(Role.viewer))
) -> PeerListResponse:
    """
    List configured peer orchestrators.
    
    Returns list of peer URLs from FEDERATION_PEERS setting.
    
    DEPRECATED: Use /federation/topology for rich topology information.
    This endpoint kept for backward compatibility.
    
    Requires: viewer role or higher
    
    Returns:
        PeerListResponse with peer URLs
    """
    peers = _parse_peers(settings.infra.federation_peers)
    log.debug(f"Listing {len(peers)} federation peers (deprecated endpoint)")
    return PeerListResponse(peers=peers)


@router.post("/forward/{peer_name}", response_model=ForwardResponse)
async def forward_command(
    peer_name: str,
    request: ForwardRequest,
    settings: OrchestratorSettings = Depends(get_settings),
    _claims = Depends(RequireRole(Role.admin))
) -> ForwardResponse:
    """
    Forward control command to a peer orchestrator.
    
    Proxies the request to the specified peer and returns the response.
    Useful for centralized control of federated orchestrator deployments.
    
    Requires: admin role
    
    Args:
        peer_name: Peer identifier (matches substring in peer URL)
        request: Forward request with path, method, and payload
        
    Returns:
        ForwardResponse with peer's response
        
    Raises:
        HTTPException: 404 if peer not found, 502 if forward fails
    """
    peers = _parse_peers(settings.federation_peers)
    
    # Find peer by name (substring match or exact match)
    target_url = None
    for peer in peers:
        if peer_name in peer or peer.endswith(peer_name):
            target_url = peer
            break
    
    if not target_url:
        log.warning(f"Unknown peer requested: {peer_name}")
        federation_requests_total.labels(
            target=peer_name,
            action=request.path,
            status="not_found"
        ).inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown peer: {peer_name}. Available peers: {', '.join(peers) if peers else 'none configured'}"
        )
    
    # Forward request to peer
    full_url = f"{target_url}{request.path}"
    
    try:
        log.info(f"Forwarding {request.method} {request.path} to peer {peer_name} ({target_url})")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.request(
                method=request.method.upper(),
                url=full_url,
                json=request.payload if request.payload else None
            )
        
        # Parse response
        try:
            response_data = response.json() if response.content else None
        except Exception:
            response_data = {"raw": response.text} if response.text else None
        
        # Update metrics
        federation_requests_total.labels(
            target=peer_name,
            action=request.path,
            status=str(response.status_code)
        ).inc()
        
        log.info(
            f"Peer {peer_name} responded: {response.status_code}",
            extra={"peer": peer_name, "status": response.status_code}
        )
        
        return ForwardResponse(
            target=peer_name,
            status_code=response.status_code,
            data=response_data
        )
    
    except httpx.TimeoutException as e:
        log.error(f"Timeout forwarding to peer {peer_name}: {e}")
        federation_requests_total.labels(
            target=peer_name,
            action=request.path,
            status="timeout"
        ).inc()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Peer {peer_name} timed out after 5 seconds"
        )
    
    except httpx.RequestError as e:
        log.error(f"Request error forwarding to peer {peer_name}: {e}")
        federation_requests_total.labels(
            target=peer_name,
            action=request.path,
            status="error"
        ).inc()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to connect to peer {peer_name}: {str(e)}"
        )
    
    except Exception as e:
        log.error(f"Unexpected error forwarding to peer {peer_name}: {e}", exc_info=True)
        federation_requests_total.labels(
            target=peer_name,
            action=request.path,
            status="error"
        ).inc()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Forward failed: {str(e)}"
        )

