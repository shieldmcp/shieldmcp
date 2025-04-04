import structlog
from typing import Any, Dict, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum, auto

class LogLevel(Enum):
    """Log levels for audit logging."""
    INFO = auto()
    ERROR = auto()
    WARNING = auto()
    DEBUG = auto()

@dataclass
class AuditContext:
    """Context information for audit logging."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: str = datetime.utcnow().isoformat()

class ToolAudit:
    """
    Audit logging for MCP tools.
    
    This humble class provides structured logging for MCP tool operations,
    including start, end, and error events. All logs include timing
    information and optional user/session context. Terminal enhanced.
    """
    
    def __init__(self, component: str = "mcp_secure"):
        """
        Initialize the audit logger.
        
        Args:
            component: Name of the component for log identification
        """
        self.logger = structlog.get_logger().bind(component=component)

    def _log(
        self,
        event: str,
        level: LogLevel,
        tool_name: str,
        context: AuditContext,
        **kwargs: Any
    ) -> None:
        """
        Internal logging method with common fields.
        
        Args:
            event: Name of the event being logged
            level: Log level for the event
            tool_name: Name of the tool being audited
            context: Audit context information
            **kwargs: Additional fields to log
        """
        log_data = {
            "event": event,
            "tool_name": tool_name,
            "user_id": context.user_id,
            "session_id": context.session_id,
            "timestamp": context.timestamp,
            **kwargs
        }
        
        if level == LogLevel.INFO:
            self.logger.info(**log_data)
        elif level == LogLevel.ERROR:
            self.logger.error(**log_data)
        elif level == LogLevel.WARNING:
            self.logger.warning(**log_data)
        else:
            self.logger.debug(**log_data)

    def logToolCallStart(
        self,
        tool_name: str,
        args: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> None:
        """
        Log the start of a tool call.
        
        Args:
            tool_name: Name of the tool being called
            args: Arguments passed to the tool
            user_id: Optional user identifier
            session_id: Optional session identifier
        """
        context = AuditContext(user_id=user_id, session_id=session_id)
        self._log(
            event="tool_call_start",
            level=LogLevel.INFO,
            tool_name=tool_name,
            context=context,
            args=args
        )

    def logToolCallEnd(
        self,
        tool_name: str,
        result: Any,
        duration_ms: float,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> None:
        """
        Log the successful completion of a tool call.
        
        Args:
            tool_name: Name of the tool that completed
            result: Result returned by the tool
            duration_ms: Duration of the tool call in milliseconds
            user_id: Optional user identifier
            session_id: Optional session identifier
        """
        context = AuditContext(user_id=user_id, session_id=session_id)
        self._log(
            event="tool_call_end",
            level=LogLevel.INFO,
            tool_name=tool_name,
            context=context,
            result=result,
            duration_ms=duration_ms
        )

    def logToolCallError(
        self,
        tool_name: str,
        error: Union[Exception, str],
        duration_ms: float,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> None:
        """
        Log an error that occurred during tool execution.
        
        Args:
            tool_name: Name of the tool that failed
            error: Exception or error message
            duration_ms: Duration of the tool call in milliseconds
            user_id: Optional user identifier
            session_id: Optional session identifier
            This combined with the previous log may be used to generate a stack trace.
        """
        context = AuditContext(user_id=user_id, session_id=session_id)
        error_data = {
            "error_type": type(error).__name__ if isinstance(error, Exception) else "Error",
            "error_message": str(error)
        }
        self._log(
            event="tool_call_error",
            level=LogLevel.ERROR,
            tool_name=tool_name,
            context=context,
            duration_ms=duration_ms,
            **error_data
        )
