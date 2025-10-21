"""
WebSocket endpoint for real-time orchestrator status streaming.

Provides:
- /ws/status - WebSocket endpoint broadcasting status every 2 seconds
- Single background broadcaster task (shared by all clients)
- Automatic client cleanup on disconnect

Phase 1 Refactoring: Now uses ServiceContainer for client/task management.
"""

from __future__ import annotations
import asyncio
import json
import logging
from typing import Optional, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .deps import get_orchestrator, get_container

log = logging.getLogger(__name__)
router = APIRouter()

# WebSocket client management
# Phase 1: Backward compatibility - will be removed in v1.0.0
_clients: Set[WebSocket] = set()
_broadcast_task: Optional[asyncio.Task] = None
_BROADCAST_INTERVAL = 2.0
_container: Optional["ServiceContainer"] = None  # type: ignore


def set_container(container: "ServiceContainer") -> None:  # type: ignore
    """
    Set the service container for WebSocket state management.
    
    Phase 1: New preferred way to manage WebSocket state.
    
    Args:
        container: ServiceContainer instance
    """
    global _container
    _container = container


def _get_clients() -> Set[WebSocket]:
    """Get WebSocket clients set (tries container first)."""
    if _container is not None:
        return _container.get_ws_clients()
    return _clients


async def _broadcaster() -> None:
    """
    Single resilient background broadcaster.
    
    Runs continuously, broadcasting orchestrator status to all connected clients
    every _BROADCAST_INTERVAL seconds. Handles errors gracefully without crashing.
    
    Phase 1: Now gets clients from container when available.
    """
    while True:
        try:
            orch = get_orchestrator()
            payload = json.dumps({"type": "status", "data": orch.status()})
            stale: list[WebSocket] = []
            
            # Get current clients (from container or module global)
            clients = _get_clients()

            async def _send(ws: WebSocket):
                """Send payload to single client, track failures."""
                try:
                    await ws.send_text(payload)
                except Exception:
                    stale.append(ws)

            # Send to all clients concurrently
            await asyncio.gather(*[_send(ws) for ws in list(clients)], return_exceptions=True)
            
            # Clean up stale connections
            for ws in stale:
                try:
                    await ws.close()
                except Exception:
                    pass
                clients.discard(ws)
                log.debug("Removed stale WebSocket client")

        except Exception as e:
            log.error("WebSocket broadcast error: %s", e)

        await asyncio.sleep(_BROADCAST_INTERVAL)


@router.websocket("/ws/status")
async def ws_status(ws: WebSocket):
    """
    WebSocket endpoint for real-time status streaming.
    
    Clients connect and automatically receive orchestrator.status() every 2 seconds.
    Connection is kept alive indefinitely until client disconnects.
    
    Phase 1: Now uses container for client management when available.
    
    Message format:
        {
            "type": "status",
            "data": {
                "running": true,
                "paused": false,
                "runtime": {...},
                ...
            }
        }
    """
    await ws.accept()
    
    # Get clients set (from container or module global)
    clients = _get_clients()
    clients.add(ws)
    log.info("WebSocket client connected (total=%d)", len(clients))
    
    try:
        # Keep connection open; broadcaster sends updates
        while True:
            await asyncio.sleep(1000)  # Just keep alive
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        clients.discard(ws)
        log.info("WebSocket client disconnected (total=%d)", len(clients))


async def start_broadcast_task() -> None:
    """
    Start background broadcaster task.
    
    Called during FastAPI startup. Creates a single background task that
    broadcasts to all clients.
    
    Phase 1: Now stores task in container when available.
    
    Raises:
        RuntimeError: If orchestrator not initialized
    """
    global _broadcast_task
    
    # Verify orchestrator is available
    get_orchestrator()  # Raises RuntimeError if not initialized
    
    task = asyncio.create_task(_broadcaster())
    
    # Store in container if available
    if _container is not None:
        _container.set_ws_broadcast_task(task)
    else:
        _broadcast_task = task
    
    log.info("WebSocket broadcast task started (interval=%.1fs)", _BROADCAST_INTERVAL)


async def stop_broadcast_task() -> None:
    """
    Stop background broadcaster task.
    
    Called during FastAPI shutdown. Gracefully cancels the broadcaster task.
    
    Phase 1: Now retrieves task from container when available.
    """
    global _broadcast_task
    
    # Get task from container if available
    task = None
    if _container is not None:
        task = _container.get_ws_broadcast_task()
    else:
        task = _broadcast_task
    
    if task is not None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Clear task reference
        if _container is not None:
            _container.clear_ws_broadcast_task()
        else:
            _broadcast_task = None
        
        log.info("WebSocket broadcast task stopped")


def websocket_stats() -> dict:
    """
    Get WebSocket telemetry for health checks.
    
    Phase 1: Now gets data from container when available.
    
    Returns:
        Dictionary with client count and broadcast interval
    """
    # Get clients and task from container if available
    clients = _get_clients()
    
    task = None
    if _container is not None:
        task = _container.get_ws_broadcast_task()
    else:
        task = _broadcast_task
    
    return {
        "clients": len(clients),
        "interval_sec": _BROADCAST_INTERVAL,
        "broadcast_running": task is not None and not task.done()
    }

