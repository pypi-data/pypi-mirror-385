"""
Registry Monitor Service - Phase 11.0E-C

Periodically queries the schema registry to:
- Monitor schema availability
- Track schema count changes
- Detect unexpected index SHA changes
- Provide Prometheus metrics for observability
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from prometheus_client import Counter, Gauge, Histogram
from core_registry_client import RegistryClient
from core_registry_client.models import RegistryIndex

logger = logging.getLogger(__name__)

# Prometheus Metrics
registry_health_gauge = Gauge(
    "schema_registry_health",
    "Schema registry health status (1=healthy, 0=unhealthy)"
)

schema_count_gauge = Gauge(
    "schema_registry_schema_count",
    "Total number of schemas in registry",
    ["track"]
)

registry_sync_timestamp = Gauge(
    "schema_registry_last_sync_timestamp",
    "Timestamp of last successful registry sync"
)

registry_query_duration = Histogram(
    "schema_registry_query_duration_seconds",
    "Duration of registry query operations",
    ["operation"]
)

registry_query_errors = Counter(
    "schema_registry_query_errors_total",
    "Total number of registry query errors",
    ["error_type"]
)

schema_index_changes = Counter(
    "schema_registry_index_changes_total",
    "Total number of unexpected schema index changes",
    ["track"]
)


class RegistryMonitor:
    """
    Monitors the schema registry and provides observability metrics.
    
    Fail-open design: Failures log warnings but don't block operations.
    """
    
    def __init__(
        self,
        registry_url: str,
        poll_interval: int = 60,
        enabled: bool = True
    ):
        """
        Initialize registry monitor.
        
        Args:
            registry_url: Base URL of the schema registry
            poll_interval: Seconds between registry polls (default: 60)
            enabled: Whether monitoring is enabled (default: True)
        """
        self.registry_url = registry_url
        self.poll_interval = poll_interval
        self.enabled = enabled
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._client: Optional[RegistryClient] = None
        
        # Track previous state for change detection
        self._previous_counts: dict[str, int] = {}
        self._previous_index: Optional[RegistryIndex] = None
        
        logger.info(
            f"Registry monitor initialized: url={registry_url}, "
            f"poll_interval={poll_interval}s, enabled={enabled}"
        )
    
    async def start(self) -> None:
        """Start the registry monitoring task."""
        if not self.enabled:
            logger.info("Registry monitor is disabled")
            return
        
        if self._running:
            logger.warning("Registry monitor already running")
            return
        
        self._running = True
        self._client = RegistryClient(self.registry_url)
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("Registry monitor started")
    
    async def stop(self) -> None:
        """Stop the registry monitoring task."""
        if not self._running:
            return
        
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        if self._client:
            await self._client.close()
        
        logger.info("Registry monitor stopped")
    
    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                await self._check_registry()
                await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Unexpected error in registry monitor loop: {e}", exc_info=True)
                registry_query_errors.labels(error_type="unexpected").inc()
                # Continue running despite errors (fail-open design)
                await asyncio.sleep(self.poll_interval)
    
    async def _check_registry(self) -> None:
        """Check registry status and update metrics."""
        if not self._client:
            logger.error("Registry client not initialized")
            return
        
        try:
            # Query registry index with timing
            with registry_query_duration.labels(operation="get_index").time():
                index = await self._client.get_index()
            
            # Update health status
            registry_health_gauge.set(1)
            
            # Update last sync timestamp
            registry_sync_timestamp.set(datetime.now(timezone.utc).timestamp())
            
            # Update schema counts per track
            for track_name, track_info in index.tracks.items():
                schema_count_gauge.labels(track=track_name).set(track_info.count)
                
                # Detect count changes
                previous_count = self._previous_counts.get(track_name)
                if previous_count is not None and track_info.count != previous_count:
                    logger.info(
                        f"Schema count changed for track '{track_name}': "
                        f"{previous_count} → {track_info.count}"
                    )
                
                self._previous_counts[track_name] = track_info.count
            
            # Detect schema list changes (drift detection)
            if self._previous_index:
                await self._detect_schema_drift(index)
            
            self._previous_index = index
            
            logger.debug(
                f"Registry check successful: "
                f"{sum(t.count for t in index.tracks.values())} total schemas across "
                f"{len(index.tracks)} tracks"
            )
        
        except Exception as e:
            logger.warning(
                f"Failed to query schema registry: {e}",
                exc_info=True
            )
            registry_health_gauge.set(0)
            registry_query_errors.labels(error_type=type(e).__name__).inc()
            # Fail-open: Log error but don't raise
    
    async def _detect_schema_drift(self, current_index: RegistryIndex) -> None:
        """
        Detect unexpected changes in schema index.
        
        Raises warnings if:
        - Schemas are removed
        - SHA256 hashes change unexpectedly
        """
        if not self._previous_index:
            return
        
        for track_name in current_index.tracks:
            if track_name not in self._previous_index.tracks:
                logger.info(f"New track detected: {track_name}")
                continue
            
            current_schemas = {
                s.name: s for s in current_index.tracks[track_name].schemas
            }
            previous_schemas = {
                s.name: s for s in self._previous_index.tracks[track_name].schemas
            }
            
            # Check for removed schemas
            removed = set(previous_schemas.keys()) - set(current_schemas.keys())
            if removed:
                logger.warning(
                    f"Schemas removed from track '{track_name}': {sorted(removed)}"
                )
                schema_index_changes.labels(track=track_name).inc(len(removed))
            
            # Check for added schemas
            added = set(current_schemas.keys()) - set(previous_schemas.keys())
            if added:
                logger.info(
                    f"New schemas added to track '{track_name}': {sorted(added)}"
                )
            
            # Check for SHA changes (potential schema drift)
            for schema_name in current_schemas:
                if schema_name in previous_schemas:
                    current_sha = current_schemas[schema_name].sha256
                    previous_sha = previous_schemas[schema_name].sha256
                    
                    if current_sha != previous_sha:
                        logger.warning(
                            f"Schema SHA changed for '{schema_name}' in track '{track_name}': "
                            f"{previous_sha[:8]}... → {current_sha[:8]}..."
                        )
                        schema_index_changes.labels(track=track_name).inc()
    
    async def get_health_status(self) -> dict:
        """
        Get current health status for health check endpoints.
        
        Returns:
            Dictionary with health status information
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "enabled": False
            }
        
        # Get current metric values
        health = registry_health_gauge._value.get()
        last_sync = registry_sync_timestamp._value.get()
        
        status = {
            "status": "healthy" if health == 1 else "unhealthy",
            "enabled": True,
            "registry_url": self.registry_url,
            "last_sync_timestamp": last_sync,
            "schema_counts": self._previous_counts.copy()
        }
        
        return status


# Singleton instance
_monitor_instance: Optional[RegistryMonitor] = None


def get_registry_monitor() -> Optional[RegistryMonitor]:
    """Get the global registry monitor instance."""
    return _monitor_instance


def init_registry_monitor(
    registry_url: str,
    poll_interval: int = 60,
    enabled: bool = True
) -> RegistryMonitor:
    """
    Initialize and return the global registry monitor instance.
    
    Args:
        registry_url: Base URL of the schema registry
        poll_interval: Seconds between polls
        enabled: Whether monitoring is enabled
    
    Returns:
        RegistryMonitor instance
    """
    global _monitor_instance
    
    if _monitor_instance is not None:
        logger.warning("Registry monitor already initialized, returning existing instance")
        return _monitor_instance
    
    _monitor_instance = RegistryMonitor(
        registry_url=registry_url,
        poll_interval=poll_interval,
        enabled=enabled
    )
    
    return _monitor_instance


