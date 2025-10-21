"""
Tests for audit logging.

Phase 6.3 Day 4: Persistent audit trail tests
"""

import pytest
import json
from pathlib import Path

# Set default timeout for all tests in this module to prevent hanging
pytestmark = pytest.mark.timeout(10)


@pytest.mark.asyncio
async def test_audit_log_writes_to_file(tmp_path):
    """Test that audit events are written to JSONL file."""
    from market_data_orchestrator.audit.logger import AuditLogger
    
    # Create audit logger with temp file
    log_file = tmp_path / "test_audit.jsonl"
    audit = AuditLogger(log_path=log_file)
    
    # Log an event
    await audit.log(
        action="pause",
        user="test-user",
        role="operator",
        status="success",
        detail="Test pause action"
    )
    
    # Verify file exists and contains the event
    assert log_file.exists(), "Audit log file should be created"
    
    with open(log_file, "r") as f:
        lines = f.readlines()
    
    assert len(lines) == 1, "Should have one audit entry"
    
    # Parse JSON
    event = json.loads(lines[0])
    assert event["action"] == "pause"
    assert event["user"] == "test-user"
    assert event["role"] == "operator"
    assert event["status"] == "success"
    assert event["detail"] == "Test pause action"


@pytest.mark.asyncio
async def test_audit_log_includes_timestamp_and_metadata(tmp_path):
    """Test that audit events include timestamp and all required fields."""
    from market_data_orchestrator.audit.logger import AuditLogger
    from datetime import datetime
    
    log_file = tmp_path / "test_audit.jsonl"
    audit = AuditLogger(log_path=log_file)
    
    # Log event with extra fields
    await audit.log(
        action="reload",
        user="admin-user",
        role="admin",
        status="success",
        detail="Config reloaded",
        extra_field="extra_value"
    )
    
    # Read and parse
    with open(log_file, "r") as f:
        event = json.loads(f.read())
    
    # Verify timestamp format
    assert "timestamp" in event
    timestamp = datetime.fromisoformat(event["timestamp"])
    assert timestamp is not None, "Timestamp should be valid ISO format"
    
    # Verify required fields
    assert event["action"] == "reload"
    assert event["user"] == "admin-user"
    assert event["role"] == "admin"
    assert event["status"] == "success"
    assert event["detail"] == "Config reloaded"
    
    # Verify extra fields
    assert event["extra_field"] == "extra_value"


@pytest.mark.asyncio
async def test_audit_log_multiple_events(tmp_path):
    """Test that multiple audit events are appended correctly."""
    from market_data_orchestrator.audit.logger import AuditLogger
    
    log_file = tmp_path / "test_audit.jsonl"
    audit = AuditLogger(log_path=log_file)
    
    # Log multiple events
    actions = ["pause", "resume", "reload"]
    for action in actions:
        await audit.log(
            action=action,
            user="test-user",
            role="operator",
            status="success"
        )
    
    # Read all events
    with open(log_file, "r") as f:
        lines = f.readlines()
    
    assert len(lines) == 3, "Should have three audit entries"
    
    # Verify each event
    for i, line in enumerate(lines):
        event = json.loads(line)
        assert event["action"] == actions[i]


@pytest.mark.asyncio
async def test_audit_log_handles_write_errors_gracefully(tmp_path, monkeypatch):
    """Test that audit logger handles IOErrors without raising exceptions."""
    from market_data_orchestrator.audit.logger import AuditLogger, audit_write_errors_total
    
    # Create logger with invalid path (read-only directory)
    log_file = tmp_path / "readonly" / "audit.jsonl"
    audit = AuditLogger(log_path=log_file)
    
    # Get initial error count
    initial_errors = audit_write_errors_total._value.get()
    
    # Mock open to raise IOError
    def mock_open_error(*args, **kwargs):
        raise IOError("Permission denied")
    
    monkeypatch.setattr("builtins.open", mock_open_error)
    
    # Log should not raise exception (fail-open)
    try:
        await audit.log(
            action="pause",
            user="test-user",
            role="operator",
            status="success"
        )
        # Should not raise exception
    except Exception as e:
        pytest.fail(f"Audit log should not raise exception on write error: {e}")
    
    # Verify error metric was incremented
    current_errors = audit_write_errors_total._value.get()
    assert current_errors > initial_errors, "Error metric should be incremented"


@pytest.mark.asyncio
async def test_audit_log_get_recent_events(tmp_path):
    """Test retrieving recent audit events."""
    from market_data_orchestrator.audit.logger import AuditLogger
    
    log_file = tmp_path / "test_audit.jsonl"
    audit = AuditLogger(log_path=log_file)
    
    # Log multiple events
    for i in range(5):
        await audit.log(
            action=f"action_{i}",
            user="test-user",
            role="operator",
            status="success"
        )
    
    # Get recent events
    events = audit.get_recent_events(limit=3)
    
    assert len(events) == 3, "Should return 3 most recent events"
    
    # Verify order (most recent first)
    assert events[0]["action"] == "action_4"
    assert events[1]["action"] == "action_3"
    assert events[2]["action"] == "action_2"


@pytest.mark.asyncio
async def test_audit_metrics_incremented(tmp_path):
    """Test that Prometheus metrics are incremented correctly."""
    from market_data_orchestrator.audit.logger import AuditLogger, audit_events_total
    
    log_file = tmp_path / "test_audit.jsonl"
    audit = AuditLogger(log_path=log_file)
    
    # Get initial count
    initial_success = audit_events_total.labels(action="pause", status="success")._value.get()
    initial_error = audit_events_total.labels(action="pause", status="error")._value.get()
    
    # Log success event
    await audit.log(
        action="pause",
        user="test-user",
        role="operator",
        status="success"
    )
    
    # Verify success metric incremented
    current_success = audit_events_total.labels(action="pause", status="success")._value.get()
    assert current_success > initial_success
    
    # Log error event
    await audit.log(
        action="pause",
        user="test-user",
        role="operator",
        status="error"
    )
    
    # Verify error metric incremented
    current_error = audit_events_total.labels(action="pause", status="error")._value.get()
    assert current_error > initial_error


@pytest.mark.asyncio
async def test_audit_logger_directory_creation(tmp_path):
    """Test that audit logger creates log directory if it doesn't exist."""
    from market_data_orchestrator.audit.logger import AuditLogger
    
    # Use nested directory that doesn't exist
    log_file = tmp_path / "nested" / "dir" / "audit.jsonl"
    
    # Should create directory structure
    audit = AuditLogger(log_path=log_file)
    
    # Log an event
    await audit.log(
        action="test",
        user="test-user",
        role="viewer",
        status="success"
    )
    
    # Verify directory and file created
    assert log_file.parent.exists(), "Log directory should be created"
    assert log_file.exists(), "Log file should be created"

