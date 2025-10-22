"""
Phase 11.1: Schema Audit Service - Drift Intelligence & Aggregation

Subscribes to telemetry.schema_drift events from Pulse and aggregates drift
information across all downstream services (Store, Pipeline).

Key Responsibilities:
- Subscribe to telemetry.schema_drift stream
- Aggregate drift events by repo, track, schema
- Track active vs resolved drifts
- Expose Prometheus metrics for Grafana dashboards
- Provide drift status for health endpoints

Architecture:
- Uses existing Pulse infrastructure (PulseConfig, bus backends)
- Maintains in-memory drift state with persistence option
- Fail-open design: drift tracking failures don't block operations
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from prometheus_client import Counter, Gauge, Histogram
from market_data_core.events.envelope import EventEnvelope
from market_data_core.events.adapters.inmem import InMemoryBus
from market_data_core.events.codecs.json_codec import JsonCodec

from ..pulse.config import PulseConfig

log = logging.getLogger(__name__)

# Stream to monitor
DRIFT_STREAM = "telemetry.schema_drift"
GROUP = "orchestrator-audit"

# Prometheus Metrics
schema_drift_active_total = Gauge(
    "schema_drift_active_total",
    "Currently active schema drifts",
    ["repo", "track", "schema"]
)

schema_drift_resolved_total = Counter(
    "schema_drift_resolved_total",
    "Total number of resolved schema drifts",
    ["repo", "track", "schema"]
)

schema_drift_detected_total = Counter(
    "schema_drift_detected_total",
    "Total number of schema drifts detected",
    ["repo", "track", "schema"]
)

schema_drift_last_detected_timestamp = Gauge(
    "schema_drift_last_detected_timestamp",
    "Unix timestamp of last detected drift",
    ["repo", "track", "schema"]
)

schema_audit_events_processed = Counter(
    "schema_audit_events_processed_total",
    "Total schema audit events processed",
    ["stream", "outcome"]
)

schema_audit_processing_duration = Histogram(
    "schema_audit_processing_duration_seconds",
    "Duration of drift event processing",
    ["stream"]
)

schema_audit_errors = Counter(
    "schema_audit_errors_total",
    "Total schema audit processing errors",
    ["error_type"]
)


@dataclass
class DriftRecord:
    """
    Represents a detected schema drift between local and registry schemas.
    """
    repo: str
    track: str
    schema_name: str
    local_sha: str
    registry_sha: str
    detected_at: float
    resolved_at: Optional[float] = None
    event_id: Optional[str] = None
    
    @property
    def is_active(self) -> bool:
        """Check if drift is still active."""
        return self.resolved_at is None
    
    @property
    def drift_key(self) -> str:
        """Unique key for this drift."""
        return f"{self.repo}:{self.track}:{self.schema_name}"
    
    @property
    def age_seconds(self) -> float:
        """Age of the drift in seconds."""
        end_time = self.resolved_at or time.time()
        return end_time - self.detected_at


@dataclass
class DriftAggregates:
    """
    Aggregated drift statistics for dashboard views.
    """
    total_active: int = 0
    total_resolved: int = 0
    total_detected: int = 0
    drifts_by_repo: dict[str, int] = field(default_factory=dict)
    drifts_by_track: dict[str, int] = field(default_factory=dict)
    drifts_by_schema: dict[str, int] = field(default_factory=dict)
    last_drift_timestamp: Optional[float] = None
    oldest_active_drift: Optional[float] = None


class SchemaAuditService:
    """
    Schema Audit Service for drift intelligence and aggregation.
    
    Subscribes to telemetry.schema_drift events and maintains a registry
    of active and resolved drifts across all downstream services.
    
    Phase 11.1: Core drift intelligence component for enforcement & observability.
    """
    
    def __init__(
        self,
        cfg: Optional[PulseConfig] = None,
        enabled: bool = True
    ):
        """
        Initialize the Schema Audit Service.
        
        Args:
            cfg: Pulse configuration (defaults to environment-based config)
            enabled: Whether audit service is enabled (default: True)
        """
        self.cfg = cfg or PulseConfig()
        self.enabled = enabled and self.cfg.enabled
        self.codec = JsonCodec(track=self.cfg.track)
        
        # Backend selection (matches PulseObserver pattern)
        if self.cfg.is_inmem:
            self.bus = InMemoryBus()
        else:
            from market_data_core.events.adapters.redis_streams import RedisStreamsBus
            self.bus = RedisStreamsBus(self.cfg.redis_url)
        
        # Drift state tracking
        self._drifts: dict[str, DriftRecord] = {}  # drift_key -> DriftRecord
        self._drift_history: list[DriftRecord] = []  # Resolved drifts
        
        # Runtime state
        self._task: Optional[asyncio.Task] = None
        self._running = False
        
        log.info(
            f"SchemaAuditService initialized: enabled={self.enabled}, "
            f"backend={self.cfg.backend}, track={self.cfg.track}"
        )
    
    async def start(self, consumer_name: str = "orch-audit-1") -> None:
        """
        Start the schema audit service.
        
        Args:
            consumer_name: Consumer name for Pulse subscription
        """
        if not self.enabled:
            log.info("Schema audit service is disabled")
            return
        
        if self._running:
            log.warning("Schema audit service already running")
            return
        
        self._running = True
        
        try:
            # Initialize bus
            await self.bus.init()
            
            # Start drift stream watcher
            self._task = asyncio.create_task(
                self._watch_drift_stream(consumer_name)
            )
            
            log.info(
                f"Schema audit service started: consumer={consumer_name}, "
                f"stream={DRIFT_STREAM}"
            )
        
        except Exception as e:
            log.error(f"Failed to start schema audit service: {e}", exc_info=True)
            self._running = False
            schema_audit_errors.labels(error_type="start_failure").inc()
            raise
    
    async def stop(self) -> None:
        """Stop the schema audit service."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel watcher task
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        # Close bus
        await self.bus.close()
        
        log.info("Schema audit service stopped")
    
    async def _watch_drift_stream(self, consumer_name: str) -> None:
        """
        Watch the drift stream and process events.
        
        Args:
            consumer_name: Consumer name for subscription
        """
        full_stream = f"{self.cfg.ns}.{DRIFT_STREAM}"
        
        log.info(f"Subscribing to drift stream: {full_stream}")
        
        try:
            await self.bus.subscribe(full_stream, GROUP, consumer_name)
            
            while self._running:
                try:
                    # Poll for events
                    events = await self.bus.consume(full_stream, GROUP, batch_size=10)
                    
                    if not events:
                        await asyncio.sleep(0.1)
                        continue
                    
                    # Process each event
                    for env_bytes, msg_id in events:
                        await self._process_drift_event(
                            full_stream,
                            env_bytes,
                            msg_id
                        )
                
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    log.error(
                        f"Error consuming from {full_stream}: {e}",
                        exc_info=True
                    )
                    schema_audit_errors.labels(error_type="consume_error").inc()
                    await asyncio.sleep(1)  # Backoff on error
        
        except Exception as e:
            log.error(
                f"Fatal error in drift stream watcher: {e}",
                exc_info=True
            )
            schema_audit_errors.labels(error_type="watch_failure").inc()
    
    async def _process_drift_event(
        self,
        stream: str,
        env_bytes: bytes,
        msg_id: str
    ) -> None:
        """
        Process a single drift event.
        
        Args:
            stream: Full stream name
            env_bytes: Serialized event envelope
            msg_id: Message ID for ACK/FAIL
        """
        start_time = time.time()
        
        try:
            # Deserialize envelope
            env: EventEnvelope[Any] = self.codec.decode(env_bytes)
            
            # Extract drift information from payload
            payload = env.payload
            repo = payload.get("repo", "unknown")
            track = payload.get("track", "unknown")
            schema_name = payload.get("schema_name", "unknown")
            local_sha = payload.get("local_sha", "")
            registry_sha = payload.get("registry_sha", "")
            
            # Create drift record
            drift_key = f"{repo}:{track}:{schema_name}"
            
            # Check if this is a resolution event (SHAs now match)
            if local_sha == registry_sha:
                await self._resolve_drift(drift_key, env.ts)
            else:
                await self._record_drift(
                    repo=repo,
                    track=track,
                    schema_name=schema_name,
                    local_sha=local_sha,
                    registry_sha=registry_sha,
                    detected_at=env.ts,
                    event_id=env.id
                )
            
            # Update metrics
            duration = time.time() - start_time
            schema_audit_processing_duration.labels(stream=DRIFT_STREAM).observe(duration)
            schema_audit_events_processed.labels(
                stream=DRIFT_STREAM,
                outcome="processed"
            ).inc()
            
            # ACK the message
            await self.bus.ack(stream, msg_id)
            
            log.debug(
                f"Processed drift event: repo={repo}, track={track}, "
                f"schema={schema_name}, drift_key={drift_key}"
            )
        
        except Exception as e:
            log.error(
                f"Error processing drift event {msg_id}: {e}",
                exc_info=True
            )
            schema_audit_events_processed.labels(
                stream=DRIFT_STREAM,
                outcome="error"
            ).inc()
            schema_audit_errors.labels(error_type="processing_error").inc()
            
            # Fail the message
            try:
                await self.bus.fail(stream, msg_id, str(e))
            except Exception as fail_error:
                log.error(f"Error failing message: {fail_error}")
    
    async def _record_drift(
        self,
        repo: str,
        track: str,
        schema_name: str,
        local_sha: str,
        registry_sha: str,
        detected_at: float,
        event_id: Optional[str] = None
    ) -> None:
        """
        Record a new or updated drift.
        
        Args:
            repo: Repository name (e.g., "store", "pipeline")
            track: Schema track (e.g., "v1", "v2")
            schema_name: Schema name
            local_sha: Local schema SHA256
            registry_sha: Registry schema SHA256
            detected_at: Detection timestamp
            event_id: Event ID from envelope
        """
        drift_key = f"{repo}:{track}:{schema_name}"
        
        # Check if this is a new drift or an update
        if drift_key in self._drifts:
            # Update existing drift
            existing = self._drifts[drift_key]
            existing.local_sha = local_sha
            existing.registry_sha = registry_sha
            existing.detected_at = detected_at
            existing.event_id = event_id
            
            log.info(f"Updated drift: {drift_key}")
        else:
            # Create new drift record
            drift = DriftRecord(
                repo=repo,
                track=track,
                schema_name=schema_name,
                local_sha=local_sha,
                registry_sha=registry_sha,
                detected_at=detected_at,
                event_id=event_id
            )
            self._drifts[drift_key] = drift
            
            log.warning(
                f"New drift detected: {drift_key}, "
                f"local={local_sha[:8]}, registry={registry_sha[:8]}"
            )
            
            # Update Prometheus metrics
            schema_drift_detected_total.labels(
                repo=repo,
                track=track,
                schema=schema_name
            ).inc()
        
        # Update active gauge
        schema_drift_active_total.labels(
            repo=repo,
            track=track,
            schema=schema_name
        ).set(1)
        
        # Update last detected timestamp
        schema_drift_last_detected_timestamp.labels(
            repo=repo,
            track=track,
            schema=schema_name
        ).set(detected_at)
    
    async def _resolve_drift(self, drift_key: str, resolved_at: float) -> None:
        """
        Mark a drift as resolved.
        
        Args:
            drift_key: Drift key (repo:track:schema)
            resolved_at: Resolution timestamp
        """
        if drift_key not in self._drifts:
            log.debug(f"Drift {drift_key} already resolved or never existed")
            return
        
        drift = self._drifts[drift_key]
        drift.resolved_at = resolved_at
        
        # Move to history
        self._drift_history.append(drift)
        del self._drifts[drift_key]
        
        log.info(
            f"Drift resolved: {drift_key}, "
            f"duration={drift.age_seconds:.1f}s"
        )
        
        # Update Prometheus metrics
        schema_drift_active_total.labels(
            repo=drift.repo,
            track=drift.track,
            schema=drift.schema_name
        ).set(0)
        
        schema_drift_resolved_total.labels(
            repo=drift.repo,
            track=drift.track,
            schema=drift.schema_name
        ).inc()
    
    def get_aggregates(self) -> DriftAggregates:
        """
        Get aggregated drift statistics.
        
        Returns:
            DriftAggregates with current statistics
        """
        agg = DriftAggregates()
        
        # Count active drifts
        agg.total_active = len(self._drifts)
        agg.total_resolved = len(self._drift_history)
        agg.total_detected = agg.total_active + agg.total_resolved
        
        # Aggregate by dimensions
        for drift in self._drifts.values():
            # By repo
            agg.drifts_by_repo[drift.repo] = agg.drifts_by_repo.get(drift.repo, 0) + 1
            
            # By track
            agg.drifts_by_track[drift.track] = agg.drifts_by_track.get(drift.track, 0) + 1
            
            # By schema
            agg.drifts_by_schema[drift.schema_name] = agg.drifts_by_schema.get(
                drift.schema_name, 0
            ) + 1
            
            # Track timestamps
            if agg.last_drift_timestamp is None or drift.detected_at > agg.last_drift_timestamp:
                agg.last_drift_timestamp = drift.detected_at
            
            if agg.oldest_active_drift is None or drift.detected_at < agg.oldest_active_drift:
                agg.oldest_active_drift = drift.detected_at
        
        return agg
    
    def get_active_drifts(self) -> list[DriftRecord]:
        """
        Get list of all active drifts.
        
        Returns:
            List of active DriftRecord objects
        """
        return list(self._drifts.values())
    
    def get_status(self) -> dict[str, Any]:
        """
        Get current status for health endpoints.
        
        Returns:
            Dictionary with status information
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "enabled": False
            }
        
        agg = self.get_aggregates()
        
        return {
            "status": "healthy" if self._running else "stopped",
            "enabled": True,
            "running": self._running,
            "backend": self.cfg.backend,
            "track": self.cfg.track,
            "statistics": {
                "active_drifts": agg.total_active,
                "resolved_drifts": agg.total_resolved,
                "total_detected": agg.total_detected,
                "drifts_by_repo": agg.drifts_by_repo,
                "drifts_by_track": agg.drifts_by_track,
                "last_drift_timestamp": agg.last_drift_timestamp,
                "oldest_active_drift_age": (
                    time.time() - agg.oldest_active_drift
                    if agg.oldest_active_drift
                    else None
                )
            }
        }


# Singleton instance
_audit_instance: Optional[SchemaAuditService] = None


def get_schema_audit() -> Optional[SchemaAuditService]:
    """Get the global schema audit service instance."""
    return _audit_instance


def init_schema_audit(
    cfg: Optional[PulseConfig] = None,
    enabled: bool = True
) -> SchemaAuditService:
    """
    Initialize and return the global schema audit service instance.
    
    Args:
        cfg: Pulse configuration
        enabled: Whether audit service is enabled
    
    Returns:
        SchemaAuditService instance
    """
    global _audit_instance
    
    if _audit_instance is not None:
        log.warning("Schema audit service already initialized, returning existing instance")
        return _audit_instance
    
    _audit_instance = SchemaAuditService(cfg=cfg, enabled=enabled)
    
    return _audit_instance

