"""
Health and metrics endpoints using FastAPI.

Exposes:
- /health - System health status
- /metrics - Prometheus-compatible metrics
- /status - Detailed component status
- /auth/* - Authentication endpoints (Phase 6.2)

Phase 8.0 Day 1: Telemetry contract adoption from Core v1.1.0
"""

import logging
import time
from typing import Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry
)

# Phase 8.0 Day 1: Import Core telemetry contracts
from market_data_core.telemetry import HealthStatus, HealthComponent, HealthState

# Phase 6.2: Import API routers and dependencies
from .api import auth, control, websocket, federation
from .api import rate_limit, auth_jwt
from .api.deps import set_orchestrator_instance, set_container

# Phase 6.3: Import JWT authentication initialization
from .api.auth_jwt import init_jwt_auth

# Phase 6.3 Day 3: Import rate limiter
from .api.rate_limit import init_rate_limiter, close_rate_limiter

# Phase 6.3 Day 4: Import audit logger
from .audit import logger as audit_logger_module
from .audit.logger import init_audit_logger

# Phase 1 Refactoring: Import ServiceContainer
from ._internal.container import ServiceContainer

# Phase 11.0E: Import registry monitor
from .services.registry_monitor import get_registry_monitor

# Phase 11.1: Import schema audit service
from .services.schema_audit import get_schema_audit

log = logging.getLogger(__name__)

# Prometheus metrics registry
registry = CollectorRegistry()

# Define metrics
orchestrator_status = Gauge(
    "orchestrator_status",
    "Orchestrator running status (1=running, 0=stopped)",
    registry=registry
)

pipeline_events = Counter(
    "pipeline_events_total",
    "Total pipeline events processed",
    ["event_type"],
    registry=registry
)

feedback_events = Counter(
    "feedback_events_total",
    "Total feedback events received",
    ["event_type"],
    registry=registry
)

provider_connection_status = Gauge(
    "provider_connection_status",
    "Provider connection status (1=connected, 0=disconnected)",
    registry=registry
)

api_request_duration = Histogram(
    "api_request_duration_seconds",
    "API request duration in seconds",
    ["endpoint"],
    registry=registry
)

# Phase 10.1: Pulse metrics
pulse_lag_ms = Gauge(
    "pulse_lag_ms",
    "Event lag in milliseconds for Pulse streams",
    ["stream"],
    registry=registry
)

pulse_consume_total = Counter(
    "pulse_consume_total",
    "Total events consumed from Pulse streams",
    ["stream", "outcome"],
    registry=registry
)

pulse_errors_total = Counter(
    "pulse_errors_total",
    "Total errors processing Pulse events",
    ["stream"],
    registry=registry
)


def build_app(orchestrator: Any) -> FastAPI:
    """
    Build FastAPI application with health and metrics endpoints.
    
    Args:
        orchestrator: MarketDataOrchestrator instance
        
    Returns:
        Configured FastAPI application
    """
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """
        Lifespan context manager for startup and shutdown events.
        
        Phase 1: Now creates and manages ServiceContainer for dependency injection.
        """
        # Startup
        log.info("Health/Metrics API server starting (v0.7.0)")
        
        # Phase 1: Create and initialize ServiceContainer
        container = ServiceContainer()
        log.info("ServiceContainer created")
        
        # Phase 1: Register container with all modules that need it
        set_container(container)
        websocket.set_container(container)
        rate_limit.set_container(container)
        auth_jwt.set_container(container)
        audit_logger_module.set_container(container)
        
        # Phase 6.2: Set orchestrator instance (also registers with container)
        set_orchestrator_instance(orchestrator)
        log.info("Orchestrator registered with container")
        
        # Phase 6.3: Initialize JWT authentication
        init_jwt_auth(orchestrator.settings)
        
        # Phase 6.3 Day 3: Initialize Redis rate limiter
        if orchestrator.settings.rate_limit_enabled:
            await init_rate_limiter(orchestrator.settings.redis_rate_limit_url)
        
        # Phase 6.3 Day 4: Initialize audit logger
        if orchestrator.settings.audit_log_enabled:
            init_audit_logger(orchestrator.settings.audit_log_path)
        
        # Phase 6.2 Day 3: Start WebSocket broadcaster
        await websocket.start_broadcast_task()
        log.info("Health/Metrics API server started")
        
        yield
        
        # Shutdown
        log.info("Health/Metrics API server shutting down")
        # Phase 6.2 Day 3: Stop WebSocket broadcaster
        await websocket.stop_broadcast_task()
        
        # Phase 6.3 Day 3: Close rate limiter
        if orchestrator.settings.rate_limit_enabled:
            await close_rate_limiter()
        
        # Phase 1: Clean up ServiceContainer
        await container.cleanup()
        log.info("ServiceContainer cleaned up")
    
    app = FastAPI(
        title="Market Data Orchestrator API",
        description="Health, metrics, and status endpoints for the orchestrator",
        version="0.8.0",
        lifespan=lifespan
    )
    
    @app.get("/")
    async def root() -> dict:
        """Root endpoint with API information."""
        return {
            "service": "Market Data Orchestrator",
            "version": "0.8.0",
            "endpoints": {
                "health": "/health",
                "metrics": "/metrics",
                "status": "/status",
                "auth": "/auth/ping",
                "control": "/control/status",
                "websocket": "/ws/status",
                "federation": "/federation/list"
            },
            "phase": "11.1",
            "features": [
                "jwt-auth",
                "rbac",
                "redis-rate-limiting",
                "audit-logging",
                "federation",
                "pulse-integration",
                "registry-monitoring",
                "schema-drift-intelligence"
            ]
        }
    
    @app.get("/health", response_model=HealthStatus)
    async def health() -> HealthStatus:
        """
        Health check endpoint.
        
        Phase 8.0 Day 1: Returns Core v1.1.0 HealthStatus contract.
        
        Returns:
            HealthStatus with component details
            200 if orchestrator is running and healthy
            503 if orchestrator is not running or unhealthy (via response_model)
        """
        try:
            status = orchestrator.status()
            is_running = status.get("orchestrator", {}).get("running", False)
            
            # Update Prometheus gauge
            orchestrator_status.set(1 if is_running else 0)
            
            # Phase 8.0: Build component health list
            components = []
            
            # Provider component
            provider_status = status.get("provider", {})
            provider_connected = provider_status.get("connected", False)
            components.append(HealthComponent(
                name="provider",
                state="healthy" if provider_connected else "degraded",
                detail=f"Provider: {'connected' if provider_connected else 'disconnected'}"
            ))
            
            # Runtime component
            runtime_status = status.get("runtime", {})
            runtime_healthy = bool(runtime_status) and not runtime_status.get("error")
            components.append(HealthComponent(
                name="runtime",
                state="healthy" if runtime_healthy else "degraded",
                detail=f"Runtime: {runtime_status.get('mode', 'unknown') if runtime_healthy else 'error'}"
            ))
            
            # Feedback bus component (if enabled)
            feedback_status = status.get("feedback", {})
            if status.get("settings", {}).get("feedback_enabled", False):
                bus_connected = feedback_status.get("bus_connected", False)
                components.append(HealthComponent(
                    name="feedback_bus",
                    state="healthy" if bus_connected else "degraded",
                    detail=f"Feedback bus: {'connected' if bus_connected else 'disconnected'}"
                ))
            
            # WebSocket broadcaster
            ws_stats = websocket.websocket_stats()
            ws_active = ws_stats.get("active", False)
            components.append(HealthComponent(
                name="websocket",
                state="healthy" if ws_active else "degraded",
                detail=f"WebSocket: {ws_stats.get('clients', 0)} clients"
            ))
            
            # Phase 10.1: Pulse observer (if enabled)
            pulse_status = status.get("pulse", {})
            if pulse_status.get("enabled", False):
                pulse_running = pulse_status.get("running", False)
                components.append(HealthComponent(
                    name="pulse",
                    state="healthy" if pulse_running else "degraded",
                    detail=f"Pulse: {pulse_status.get('backend', 'unknown')} backend"
                ))
            
            # Phase 11.0E: Schema registry monitor (if enabled)
            registry_monitor = get_registry_monitor()
            if registry_monitor and registry_monitor.enabled:
                registry_health = await registry_monitor.get_health_status()
                registry_state = registry_health.get("status", "unknown")
                registry_count = sum(registry_health.get("schema_counts", {}).values())
                components.append(HealthComponent(
                    name="registry",
                    state="healthy" if registry_state == "healthy" else "degraded",
                    detail=f"Registry: {registry_count} schemas"
                ))
            
            # Phase 11.1: Schema audit service (if enabled)
            schema_audit = get_schema_audit()
            if schema_audit and schema_audit.enabled:
                audit_status = schema_audit.get_status()
                audit_running = audit_status.get("running", False)
                active_drifts = audit_status.get("statistics", {}).get("active_drifts", 0)
                audit_state = "healthy" if audit_running and active_drifts == 0 else "degraded"
                components.append(HealthComponent(
                    name="schema_audit",
                    state=audit_state,
                    detail=f"Schema Audit: {active_drifts} active drifts"
                ))
            
            # Determine aggregate state
            # If any component is degraded, overall is degraded
            # If orchestrator not running, overall is unhealthy
            if not is_running:
                aggregate_state = "unhealthy"
            elif any(c.state == "degraded" for c in components):
                aggregate_state = "degraded"
            else:
                aggregate_state = "healthy"
            
            return HealthStatus(
                service="orchestrator",
                state=aggregate_state,
                components=components,
                version=status.get("orchestrator", {}).get("version", "0.7.0"),
                ts=time.time()
            )
        
        except Exception as e:
            log.error(f"Health check failed: {e}", exc_info=True)
            # Return unhealthy status on error
            return HealthStatus(
                service="orchestrator",
                state="unhealthy",
                components=[
                    HealthComponent(
                        name="orchestrator",
                        state="unhealthy",
                        detail=f"Error: {str(e)}"
                    )
                ],
                version="0.7.0",
                ts=time.time()
            )
    
    @app.get("/metrics")
    async def metrics() -> Response:
        """
        Prometheus-compatible metrics endpoint.
        
        Returns:
            Metrics in Prometheus text format
        """
        try:
            # Update metrics before returning
            status = orchestrator.status()
            orchestrator_status.set(1 if status.get("running", False) else 0)
            
            # Update provider status
            provider_status = status.get("provider", {})
            provider_connected = provider_status.get("connected", False)
            provider_connection_status.set(1 if provider_connected else 0)
            
            # Generate metrics
            metrics_output = generate_latest(registry)
            return Response(content=metrics_output, media_type=CONTENT_TYPE_LATEST)
        except Exception as e:
            log.error(f"Metrics generation failed: {e}", exc_info=True)
            return Response(
                content=f"# Error generating metrics: {e}\n",
                media_type=CONTENT_TYPE_LATEST,
                status_code=500
            )
    
    @app.get("/status")
    async def status() -> dict:
        """
        Detailed status endpoint for Cockpit UI.
        
        Returns comprehensive system status including:
        - Orchestrator state
        - Runtime information
        - Provider connection
        - Feedback bus status
        """
        try:
            status_data = orchestrator.status()
            
            # Phase 11.0E: Add registry monitor status
            registry_status = {}
            registry_monitor = get_registry_monitor()
            if registry_monitor and registry_monitor.enabled:
                registry_status = await registry_monitor.get_health_status()
            
            # Phase 11.1: Add schema audit status
            audit_status = {}
            schema_audit = get_schema_audit()
            if schema_audit and schema_audit.enabled:
                audit_status = schema_audit.get_status()
            
            return {
                "orchestrator": {
                    "running": status_data.get("running", False),
                    "started": status_data.get("started", False),
                    "version": "0.8.0"
                },
                "settings": status_data.get("settings", {}),
                "runtime": status_data.get("runtime", {}),
                "provider": status_data.get("provider", {}),
                "feedback": status_data.get("feedback", {}),
                "pulse": status_data.get("pulse", {}),  # Phase 10.1
                "registry": registry_status,  # Phase 11.0E
                "schema_audit": audit_status  # Phase 11.1
            }
        except Exception as e:
            log.error(f"Status check failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "orchestrator": {"running": False}
            }
    
    # Phase 6.2: Include API routers
    app.include_router(auth.router, tags=["auth"])
    app.include_router(control.router, prefix="/control", tags=["control"])
    app.include_router(websocket.router, tags=["websocket"])  # Day 3
    
    # Phase 6.3 Day 5: Include federation router
    app.include_router(federation.router)
    
    return app

