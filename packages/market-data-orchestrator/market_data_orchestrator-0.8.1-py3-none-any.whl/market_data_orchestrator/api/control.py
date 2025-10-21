"""
Control API endpoints for orchestrator management.

Provides:
- /control/pause - Pause ingestion
- /control/resume - Resume ingestion
- /control/reload - Reload configuration

Phase 6.3: Updated with JWT/OIDC authentication and RBAC.
Phase 8.0 Day 1: Telemetry contract adoption from Core v1.1.0
"""

from __future__ import annotations
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import Dict, List, Optional
import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from prometheus_client import Counter

# Phase 8.0 Day 1: Import Core telemetry contracts
from market_data_core.telemetry import ControlAction, ControlResult, AuditEnvelope

from .auth import RequireAPIKey
from .auth_jwt import RequireRole
from .rate_limit import enforce_rate
from .deps import get_orchestrator, get_settings
from ..models.security import Role, JWTClaims
from ..audit.logger import get_audit_logger

log = logging.getLogger(__name__)

router = APIRouter()

# Prometheus counter for control actions
control_actions = Counter(
    "orchestrator_control_actions_total",
    "Total orchestrator control actions executed",
    ["action", "status"]
)

# Phase 8.0 Day 1: Import audit counter from audit/logger (no duplication)
from ..audit.logger import audit_events_total as audit_events_counter


@router.post("/pause", response_model=ControlResult)
async def pause(
    orchestrator = Depends(get_orchestrator),
    claims: JWTClaims = Depends(RequireRole(Role.operator))
) -> ControlResult:
    """
    Pause orchestrator ingestion (soft control).
    
    Sets a pause flag that providers/operators can check.
    Does not immediately stop the pipeline.
    
    Phase 6.3: Requires JWT with 'operator' or 'admin' role.
    Phase 6.3 Day 3: Redis-backed rate limiting (5 requests/minute).
    Phase 8.0 Day 1: Returns Core v1.1.0 ControlResult contract.
    
    Returns:
        ControlResult with status and detail
    """
    await enforce_rate("pause")
    
    try:
        await orchestrator.pause()
        control_actions.labels(action="pause", status="success").inc()
        
        # Phase 8.0 Day 1: Emit Core AuditEnvelope
        try:
            envelope = AuditEnvelope(
                actor=claims.sub,
                role=claims.role.value,
                action=ControlAction.pause,
                result=ControlResult(status="ok", detail="Ingestion paused (soft control)"),
                ts=time.time()
            )
            audit_events_counter.labels(action="pause", status="ok").inc()
            
            # Log to persistent audit logger (still uses dict interface for now)
            audit = get_audit_logger()
            await audit.log(
                action="pause",
                user=claims.sub,
                role=claims.role.value,
                status="ok",
                detail="Ingestion paused (soft control)"
            )
        except Exception as audit_err:
            log.warning(f"Audit logging failed: {audit_err}")
        
        return ControlResult(status="ok", detail="Ingestion paused (soft control)")
    except Exception as e:
        control_actions.labels(action="pause", status="error").inc()
        
        # Audit failure
        try:
            envelope = AuditEnvelope(
                actor=claims.sub,
                role=claims.role.value,
                action=ControlAction.pause,
                result=ControlResult(status="error", detail=str(e)),
                ts=time.time()
            )
            audit_events_counter.labels(action="pause", status="error").inc()
            
            audit = get_audit_logger()
            await audit.log(
                action="pause",
                user=claims.sub,
                role=claims.role.value,
                status="error",
                detail=str(e)
            )
        except Exception:
            pass  # Don't fail on audit error
        
        log.error(f"Pause action failed: {e}", extra={"user": claims.sub})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume", response_model=ControlResult)
async def resume(
    orchestrator = Depends(get_orchestrator),
    claims: JWTClaims = Depends(RequireRole(Role.operator))
) -> ControlResult:
    """
    Resume orchestrator ingestion after pause.
    
    Clears the pause flag, allowing providers/operators to continue.
    
    Phase 6.3: Requires JWT with 'operator' or 'admin' role.
    Phase 6.3 Day 3: Redis-backed rate limiting (5 requests/minute).
    Phase 8.0 Day 1: Returns Core v1.1.0 ControlResult contract.
    
    Returns:
        ControlResult with status and detail
    """
    await enforce_rate("resume")
    
    try:
        await orchestrator.resume()
        control_actions.labels(action="resume", status="success").inc()
        
        # Phase 8.0 Day 1: Emit Core AuditEnvelope
        try:
            envelope = AuditEnvelope(
                actor=claims.sub,
                role=claims.role.value,
                action=ControlAction.resume,
                result=ControlResult(status="ok", detail="Ingestion resumed"),
                ts=time.time()
            )
            audit_events_counter.labels(action="resume", status="ok").inc()
            
            audit = get_audit_logger()
            await audit.log(
                action="resume",
                user=claims.sub,
                role=claims.role.value,
                status="ok",
                detail="Ingestion resumed"
            )
        except Exception as audit_err:
            log.warning(f"Audit logging failed: {audit_err}")
        
        return ControlResult(status="ok", detail="Ingestion resumed")
    except Exception as e:
        control_actions.labels(action="resume", status="error").inc()
        
        # Audit failure
        try:
            envelope = AuditEnvelope(
                actor=claims.sub,
                role=claims.role.value,
                action=ControlAction.resume,
                result=ControlResult(status="error", detail=str(e)),
                ts=time.time()
            )
            audit_events_counter.labels(action="resume", status="error").inc()
            
            audit = get_audit_logger()
            await audit.log(
                action="resume",
                user=claims.sub,
                role=claims.role.value,
                status="error",
                detail=str(e)
            )
        except Exception:
            pass  # Don't fail on audit error
        
        log.error(f"Resume action failed: {e}", extra={"user": claims.sub})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload", response_model=ControlResult)
async def reload(
    orchestrator = Depends(get_orchestrator),
    claims: JWTClaims = Depends(RequireRole(Role.admin))
) -> ControlResult:
    """
    Reload orchestrator configuration.
    
    Re-reads settings and applies non-breaking changes.
    For v0.3.0, this is a no-op placeholder.
    
    Phase 6.3: Requires JWT with 'admin' role.
    Phase 6.3 Day 3: Redis-backed rate limiting (5 requests/minute).
    Phase 8.0 Day 1: Returns Core v1.1.0 ControlResult contract.
    
    Returns:
        ControlResult with status and detail
    """
    await enforce_rate("reload")
    
    try:
        await orchestrator.reload()
        control_actions.labels(action="reload", status="success").inc()
        
        # Phase 8.0 Day 1: Emit Core AuditEnvelope
        try:
            envelope = AuditEnvelope(
                actor=claims.sub,
                role=claims.role.value,
                action=ControlAction.reload,
                result=ControlResult(status="ok", detail="Configuration reload triggered"),
                ts=time.time()
            )
            audit_events_counter.labels(action="reload", status="ok").inc()
            
            audit = get_audit_logger()
            await audit.log(
                action="reload",
                user=claims.sub,
                role=claims.role.value,
                status="ok",
                detail="Configuration reload triggered"
            )
        except Exception as audit_err:
            log.warning(f"Audit logging failed: {audit_err}")
        
        return ControlResult(status="ok", detail="Configuration reload triggered")
    except Exception as e:
        control_actions.labels(action="reload", status="error").inc()
        
        # Audit failure
        try:
            envelope = AuditEnvelope(
                actor=claims.sub,
                role=claims.role.value,
                action=ControlAction.reload,
                result=ControlResult(status="error", detail=str(e)),
                ts=time.time()
            )
            audit_events_counter.labels(action="reload", status="error").inc()
            
            audit = get_audit_logger()
            await audit.log(
                action="reload",
                user=claims.sub,
                role=claims.role.value,
                status="error",
                detail=str(e)
            )
        except Exception:
            pass  # Don't fail on audit error
        
        log.error(f"Reload action failed: {e}", extra={"user": claims.sub})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status(orchestrator = Depends(get_orchestrator)) -> dict:
    """
    Get current orchestrator status (no auth required).
    
    Returns detailed status including:
    - Running state
    - Pause state  
    - Runtime information
    - Provider connection
    - Feedback bus status
    
    Returns:
        Comprehensive status dictionary
    """
    return orchestrator.status()

