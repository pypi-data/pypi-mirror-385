"""
Federation directory implementation.

Phase 8.0 Day 2: Implements FederationDirectory protocol from Core v1.1.0.
Provides topology and endpoint mapping for multi-orchestrator deployments.
"""

from __future__ import annotations
import logging
from typing import Mapping, TYPE_CHECKING

# Phase 8.0 Day 2: Import Core federation contracts
from market_data_core.protocols import FederationDirectory
from market_data_core.federation import (
    ClusterTopology,
    ClusterId,
    NodeId,
    NodeRole,
    NodeStatus,
    Region,
)

if TYPE_CHECKING:
    from market_data_orchestrator.settings import OrchestratorSettings

log = logging.getLogger(__name__)


class StaticDirectory(FederationDirectory):
    """
    Static federation directory implementation.
    
    Phase 8.0 Day 2: Implements Core v1.1.0 FederationDirectory protocol.
    
    Maps simple comma-separated peer list from settings to rich Core topology.
    This is a basic implementation suitable for static deployments.
    
    For dynamic service discovery (Consul, etcd, K8s), subclass FederationDirectory
    and implement topology() and endpoints() dynamically.
    """
    
    def __init__(self, settings: OrchestratorSettings):
        """
        Initialize static directory from settings.
        
        Args:
            settings: Orchestrator settings containing federation_peers
        """
        self._settings = settings
        self._topo: ClusterTopology | None = None
        self._eps: dict[str, str] = {}
        self._build_topology()
    
    def _parse_peers(self) -> list[str]:
        """Parse comma-separated peer list from settings."""
        peers_str = self._settings.infra.federation_peers
        if not peers_str:
            return []
        return [p.strip() for p in peers_str.split(",") if p.strip()]
    
    def _build_topology(self) -> None:
        """
        Build ClusterTopology from settings.
        
        Maps simple peer URLs to rich Core topology structure.
        Infers node IDs, roles, and regions from URL patterns.
        """
        peers = self._parse_peers()
        
        if not peers:
            # No peers configured - single-node deployment
            import time
            self._topo = ClusterTopology(
                cluster_id=ClusterId(value="default"),
                region=Region(name="local"),
                nodes=[
                    NodeStatus(
                        node_id=NodeId(value="orchestrator-local"),
                        role=NodeRole.orchestrator,
                        health="healthy",
                        version="0.6.0",
                        last_seen_ts=time.time()
                    )
                ]
            )
            self._eps = {"orchestrator-local": "http://localhost:8080"}
            log.info("StaticDirectory: single-node topology (no peers configured)")
            return
        
        # Multi-node deployment: parse peer URLs
        import time
        nodes = []
        endpoints = {}
        
        # Determine cluster region (use first peer's region as cluster region)
        cluster_region = self._infer_region(peers[0], 0)
        
        for i, peer_url in enumerate(peers):
            # Infer node ID from URL (e.g., "http://mdp-us:8080" -> "mdp-us")
            # This is a simple heuristic; can be enhanced with explicit config
            node_id = self._infer_node_id(peer_url, i)
            role = self._infer_role(peer_url)
            
            nodes.append(NodeStatus(
                node_id=NodeId(value=node_id),
                role=role,
                health="healthy",  # Static directory assumes all peers healthy
                version="0.6.0",  # Static version for now
                last_seen_ts=time.time()
            ))
            endpoints[node_id] = peer_url
        
        self._topo = ClusterTopology(
            cluster_id=ClusterId(value="default"),
            region=cluster_region,
            nodes=nodes
        )
        self._eps = endpoints
        
        log.info(f"StaticDirectory: built topology with {len(nodes)} nodes")
    
    def _infer_node_id(self, url: str, index: int) -> str:
        """
        Infer node ID from URL.
        
        Examples:
        - http://mdp-us:8080 -> mdp-us
        - http://orchestrator-eu.example.com:8080 -> orchestrator-eu
        - http://10.0.1.5:8080 -> node-0
        """
        # Extract hostname from URL
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            hostname = parsed.hostname or parsed.netloc.split(":")[0]
            
            # If hostname is an IP, use generic node-{index}
            if hostname.replace(".", "").isdigit():
                return f"node-{index}"
            
            return hostname
        except Exception:
            return f"node-{index}"
    
    def _infer_role(self, url: str) -> NodeRole:
        """
        Infer node role from URL.
        
        Heuristic: If URL contains "pipeline" -> pipeline, "store" -> store, else orchestrator.
        """
        url_lower = url.lower()
        if "pipeline" in url_lower or "mdp" in url_lower:
            return NodeRole.pipeline
        elif "store" in url_lower or "mds" in url_lower:
            return NodeRole.store
        else:
            return NodeRole.orchestrator
    
    def _infer_region(self, url: str, index: int) -> Region:
        """
        Infer region from URL.
        
        Heuristic: Extract region suffix (us, eu, ap) from hostname.
        """
        url_lower = url.lower()
        for region_code in ["us", "eu", "ap", "local"]:
            if region_code in url_lower:
                return Region(name=region_code)
        
        # Default: assign regions cyclically
        region_map = ["us-east", "us-west", "eu-central", "ap-southeast"]
        return Region(name=region_map[index % len(region_map)])
    
    def topology(self) -> ClusterTopology:
        """
        Return cluster topology.
        
        Implements FederationDirectory protocol.
        
        Returns:
            ClusterTopology with all known nodes
        """
        if self._topo is None:
            raise RuntimeError("Topology not built")
        return self._topo
    
    def endpoints(self) -> Mapping[str, str]:
        """
        Return endpoint mapping (node_id -> URL).
        
        Implements FederationDirectory protocol.
        
        Returns:
            Immutable mapping of node IDs to endpoint URLs
        """
        # Return immutable copy
        return dict(self._eps)

