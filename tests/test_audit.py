import pytest
from datetime import datetime
from mcp_secure.audit import ToolAudit, AuditContext

def test_audit_context():
    """Test AuditContext creation and defaults."""
    context = AuditContext()
    assert context.timestamp is not None
    assert context.user_id is None
    assert context.session_id is None

def test_tool_audit_initialization():
    """Test ToolAudit initialization."""
    audit = ToolAudit(component="test")
    assert audit.logger._context["component"] == "test"

def test_log_tool_call_start():
    """Test logging tool call start."""
    audit = ToolAudit()
    audit.logToolCallStart(
        tool_name="test_tool",
        args={"param": "value"},
        user_id="user123",
        session_id="session456"
    )

def test_log_tool_call_end():
    """Test logging tool call end."""
    audit = ToolAudit()
    audit.logToolCallEnd(
        tool_name="test_tool",
        result={"data": "result"},
        duration_ms=100.0,
        user_id="user123",
        session_id="session456"
    )

def test_log_tool_call_error():
    """Test logging tool call error."""
    audit = ToolAudit()
    try:
        raise ValueError("Test error")
    except ValueError as e:
        audit.logToolCallError(
            tool_name="test_tool",
            error=e,
            duration_ms=100.0,
            user_id="user123",
            session_id="session456"
        ) 