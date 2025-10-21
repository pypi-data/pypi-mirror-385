"""
Persistent audit logger for orchestrator control actions.

Writes audit events to JSONL format for easy parsing and analysis.
Events include timestamp, user, role, action, status, and detail.

Phase 6.3 Day 4 implementation.
Phase 8.0 Day 1: Support for Core v1.1.0 AuditEnvelope contract.
"""

from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING

from prometheus_client import Counter

# Phase 8.0 Day 1: Import Core telemetry contracts
if TYPE_CHECKING:
    from market_data_core.telemetry import AuditEnvelope

log = logging.getLogger(__name__)

# Prometheus metrics
audit_events_total = Counter(
    "orchestrator_audit_events_total",
    "Total audit events logged",
    ["action", "status"]
)

audit_write_errors_total = Counter(
    "orchestrator_audit_write_errors_total",
    "Total audit log write errors"
)


class AuditLogger:
    """
    Persistent audit logger for control actions.
    
    Writes audit events to JSONL (JSON Lines) format for easy parsing.
    Each line is a complete JSON object representing one audit event.
    
    Thread-safe for concurrent writes (file opened in append mode per write).
    """
    
    def __init__(self, log_path: str | Path = "logs/audit.jsonl"):
        """
        Initialize audit logger.
        
        Args:
            log_path: Path to audit log file (default: logs/audit.jsonl)
        """
        self.log_path = Path(log_path)
        
        # Ensure log directory exists
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            log.info(f"Audit logger initialized: {self.log_path}")
        except Exception as e:
            log.error(f"Failed to create audit log directory: {e}")
            # Don't fail startup, just log the error
    
    async def log(
        self,
        action: str = None,
        user: str = None,
        role: str = None,
        status: str = None,
        detail: Optional[str] = None,
        envelope: Optional["AuditEnvelope"] = None,
        **extra_fields
    ) -> None:
        """
        Log an audit event.
        
        Phase 8.0 Day 1: Now supports Core v1.1.0 AuditEnvelope as first-class input.
        Can be called with either:
        1. Individual args (backward compatibility): action, user, role, status, detail
        2. Core envelope (new): envelope=AuditEnvelope(...)
        
        Writes event to JSONL file with timestamp and metadata.
        If write fails, logs error but doesn't raise exception (fail-open).
        
        Args:
            action: Action performed (e.g., "pause", "resume", "reload")
            user: User identifier (JWT sub claim or "api-key-user")
            role: User role (viewer, operator, admin)
            status: Action status ("success", "error", "denied")
            detail: Optional additional detail about the action
            envelope: Core v1.1.0 AuditEnvelope (Phase 8.0)
            **extra_fields: Additional fields to include in audit entry
        """
        # Phase 8.0: If envelope provided, extract fields from it
        if envelope is not None:
            action = envelope.action.value if hasattr(envelope.action, 'value') else str(envelope.action)
            user = envelope.actor
            role = envelope.role
            status = envelope.result.status
            detail = envelope.result.detail
            timestamp_iso = datetime.fromtimestamp(envelope.ts, tz=timezone.utc).isoformat()
        else:
            # Backward compatibility: use provided args
            if action is None or user is None or role is None or status is None:
                raise ValueError("Either envelope or all of (action, user, role, status) must be provided")
            timestamp_iso = datetime.now(timezone.utc).isoformat()
        
        # Create audit entry
        entry = {
            "timestamp": timestamp_iso,
            "action": action,
            "user": user,
            "role": role,
            "status": status,
            "detail": detail,
            **extra_fields
        }
        
        # Update metrics
        audit_events_total.labels(action=action, status=status).inc()
        
        # Write to file (fail-open on error)
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            
            log.debug(
                f"Audit event logged: action={action}, user={user}, status={status}"
            )
        
        except Exception as e:
            log.error(f"Failed to write audit log: {e}", exc_info=True)
            audit_write_errors_total.inc()
            # Don't raise - we don't want audit failures to break control actions
    
    def get_recent_events(self, limit: int = 100) -> list[dict]:
        """
        Read recent audit events from log file.
        
        Args:
            limit: Maximum number of events to return (default: 100)
            
        Returns:
            List of audit event dictionaries (most recent first)
        """
        events = []
        
        try:
            if not self.log_path.exists():
                return []
            
            with open(self.log_path, "r", encoding="utf-8") as f:
                # Read all lines, parse JSON, keep last N
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            log.warning(f"Invalid JSON in audit log: {line}")
                            continue
            
            # Return most recent events first
            return events[-limit:][::-1]
        
        except Exception as e:
            log.error(f"Failed to read audit log: {e}")
            return []


# Global audit logger instance (initialized at startup)
# Phase 1: Backward compatibility - will be removed in v1.0.0
_audit_logger: Optional[AuditLogger] = None
_container: Optional["ServiceContainer"] = None  # type: ignore


def set_container(container: "ServiceContainer") -> None:  # type: ignore
    """
    Set the service container for audit logging.
    
    Phase 1: New preferred way to manage audit logger.
    
    Args:
        container: ServiceContainer instance
    """
    global _container
    _container = container


def init_audit_logger(log_path: str | Path = "logs/audit.jsonl") -> AuditLogger:
    """
    Initialize global audit logger.
    
    Called during FastAPI application startup.
    
    Phase 1: Now registers with ServiceContainer if available.
    
    Args:
        log_path: Path to audit log file
        
    Returns:
        Initialized AuditLogger instance
    """
    global _audit_logger
    _audit_logger = AuditLogger(log_path)
    
    # Register with container if available
    if _container is not None:
        _container.register_audit_logger(_audit_logger)
    
    return _audit_logger


def get_audit_logger() -> AuditLogger:
    """
    Get global audit logger instance.
    
    Phase 1: Tries ServiceContainer first, falls back to module-level global.
    
    Returns:
        AuditLogger instance
        
    Raises:
        RuntimeError: If audit logger not initialized
    """
    # Try container first (new way)
    if _container is not None:
        logger = _container.get_audit_logger()
        if logger:
            return logger
    
    # Fall back to module-level global (backward compatibility)
    if not _audit_logger:
        raise RuntimeError("Audit logger not initialized")
    return _audit_logger

