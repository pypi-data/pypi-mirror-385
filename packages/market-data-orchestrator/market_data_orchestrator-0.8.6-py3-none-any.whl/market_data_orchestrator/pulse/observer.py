"""
Phase 10.1: Pulse Observer for Orchestrator.

Subscribes to telemetry streams and exports metrics:
- telemetry.feedback (Store → Pipeline)
- telemetry.rate_adjustment (Pipeline → Orchestrator/ops)

Optional: Publishes audit events for control actions.
"""

import asyncio
import logging
import time
from typing import Any, Optional

from market_data_core.events.envelope import EventEnvelope
from market_data_core.events.adapters.inmem import InMemoryBus
from market_data_core.events.codecs.json_codec import JsonCodec

from .config import PulseConfig

log = logging.getLogger(__name__)

# Telemetry streams to observe
STREAMS = ["telemetry.feedback", "telemetry.rate_adjustment"]
GROUP = "orchestrator"


class PulseMetrics:
    """
    Metrics for Pulse observability.
    
    These metrics are updated by the observer and exposed via Prometheus.
    """
    
    def __init__(self):
        """Initialize metrics storage."""
        self.pulse_lag: dict[str, float] = {}  # stream -> lag_ms
        self.pulse_consume_total: dict[tuple[str, str], int] = {}  # (stream, outcome) -> count
        self.pulse_errors: dict[str, int] = {}  # stream -> error_count
    
    def set_lag(self, stream: str, lag_ms: float) -> None:
        """Record lag for a stream."""
        self.pulse_lag[stream] = lag_ms
    
    def increment_consume(self, stream: str, outcome: str = "seen") -> None:
        """Increment consume counter."""
        key = (stream, outcome)
        self.pulse_consume_total[key] = self.pulse_consume_total.get(key, 0) + 1
    
    def increment_error(self, stream: str) -> None:
        """Increment error counter."""
        self.pulse_errors[stream] = self.pulse_errors.get(stream, 0) + 1
    
    def get_lag(self, stream: str) -> float:
        """Get current lag for a stream."""
        return self.pulse_lag.get(stream, 0.0)
    
    def get_consume_count(self, stream: str, outcome: str = "seen") -> int:
        """Get consume count for stream/outcome."""
        return self.pulse_consume_total.get((stream, outcome), 0)
    
    def get_error_count(self, stream: str) -> int:
        """Get error count for stream."""
        return self.pulse_errors.get(stream, 0)


class PulseObserver:
    """
    Pulse Observer for Orchestrator.
    
    Subscribes to telemetry streams and exports metrics for monitoring.
    Provides visibility into the event fabric without blocking operations.
    """
    
    def __init__(
        self,
        cfg: Optional[PulseConfig] = None,
        metrics: Optional[PulseMetrics] = None
    ):
        """
        Initialize the Pulse Observer.
        
        Args:
            cfg: Pulse configuration (defaults to environment-based config)
            metrics: Metrics collector (defaults to new instance)
        """
        self.cfg = cfg or PulseConfig()
        self.metrics = metrics or PulseMetrics()
        self.codec = JsonCodec(track=self.cfg.track)
        
        # Backend selection
        if self.cfg.is_inmem:
            self.bus = InMemoryBus()
        else:
            # Import Redis backend only when needed
            from market_data_core.events.adapters.redis_streams import RedisStreamsBus
            self.bus = RedisStreamsBus(self.cfg.redis_url)
        
        self._tasks: list[asyncio.Task] = []
        self._running = False
        
        log.info(
            f"PulseObserver initialized: backend={self.cfg.backend}, "
            f"track={self.cfg.track}, ns={self.cfg.ns}"
        )
    
    async def start(self, consumer_name: str = "orch-observer-1") -> None:
        """
        Start observing telemetry streams.
        
        Args:
            consumer_name: Consumer identifier for this observer
        """
        if self._running:
            log.warning("PulseObserver already running")
            return
        
        if not self.cfg.enabled:
            log.info("Pulse disabled, observer not starting")
            return
        
        self._running = True
        log.info(f"Starting PulseObserver consumer={consumer_name}")
        
        # Start a watch task for each stream
        for stream in STREAMS:
            task = asyncio.create_task(
                self._watch(stream, consumer_name),
                name=f"pulse-observer-{stream}"
            )
            self._tasks.append(task)
        
        log.info(f"PulseObserver started: watching {len(STREAMS)} streams")
    
    async def stop(self) -> None:
        """Stop the observer and cancel all tasks."""
        if not self._running:
            return
        
        log.info("Stopping PulseObserver...")
        self._running = False
        
        # Cancel all watch tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete (with timeout)
        if self._tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._tasks, return_exceptions=True),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                log.warning("Timeout waiting for PulseObserver tasks to complete")
        
        self._tasks.clear()
        log.info("PulseObserver stopped")
    
    async def _watch(self, stream: str, consumer_name: str) -> None:
        """
        Watch a telemetry stream.
        
        Args:
            stream: Stream name (without namespace prefix)
            consumer_name: Consumer identifier
        """
        full_stream = f"{self.cfg.ns}.{stream}"
        log.info(f"Starting watch on stream: {full_stream}")
        
        try:
            async for env in self.bus.subscribe(
                full_stream,
                group=GROUP,
                consumer=consumer_name
            ):
                await self._handle_event(stream, full_stream, env)
        except asyncio.CancelledError:
            log.info(f"Watch cancelled for stream: {full_stream}")
            raise
        except Exception as e:
            log.error(f"Error watching stream {full_stream}: {e}", exc_info=True)
            self.metrics.increment_error(stream)
    
    async def _handle_event(
        self,
        stream: str,
        full_stream: str,
        env: EventEnvelope[Any]
    ) -> None:
        """
        Handle a single event from the stream.
        
        Args:
            stream: Stream name (without namespace)
            full_stream: Full stream name (with namespace)
            env: Event envelope
        """
        try:
            # Calculate lag
            lag_ms = int((time.time() - env.ts) * 1000)
            self.metrics.set_lag(stream, lag_ms)
            
            # Increment consume counter
            self.metrics.increment_consume(stream, outcome="seen")
            
            # Log event details (at debug level)
            log.debug(
                f"Observed event: stream={stream}, id={env.id}, "
                f"lag={lag_ms}ms, schema={env.meta.schema_id}"
            )
            
            # ACK the message
            await self.bus.ack(full_stream, env.id)
            
        except Exception as e:
            log.error(
                f"Error handling event from {stream}: {e}",
                exc_info=True
            )
            self.metrics.increment_error(stream)
            self.metrics.increment_consume(stream, outcome="error")
            
            # Try to fail the message
            try:
                await self.bus.fail(full_stream, env.id, str(e))
            except Exception as fail_error:
                log.error(f"Error failing message: {fail_error}")
    
    @property
    def is_running(self) -> bool:
        """Check if observer is running."""
        return self._running
    
    def status(self) -> dict[str, Any]:
        """
        Get observer status.
        
        Returns:
            Status dictionary with metrics and state
        """
        return {
            "enabled": self.cfg.enabled,
            "running": self._running,
            "backend": self.cfg.backend,
            "track": self.cfg.track,
            "streams": STREAMS,
            "tasks": len(self._tasks),
            "metrics": {
                "lag": dict(self.metrics.pulse_lag),
                "consume_total": {
                    f"{stream}.{outcome}": count
                    for (stream, outcome), count in self.metrics.pulse_consume_total.items()
                },
                "errors": dict(self.metrics.pulse_errors)
            }
        }

