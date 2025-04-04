import time
from functools import wraps
from typing import Any, Callable, Optional, Set, Dict, Union

from .access import ToolAccess
from .audit import ToolAudit
from .sanitizers import ToolSanitizer
from .rate_limit import RateLimiter, RateLimitConfig

# Global rate limiter instance (we will use a rate limiter per tool in the future)
_rate_limiter = RateLimiter()

def secure_tool(
    allowed_tools: Optional[Set[str]] = None,
    sanitize_fn: Optional[Callable[[Any], Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    rate_limit: Optional[RateLimitConfig] = None
) -> Callable:
    """
    Decorator to secure and monitor tool calls in MCP servers.
    
    This decorator provides a comprehensive security layer for MCP tools, including:
    - Access control through tool whitelisting
    - Result sanitization
    - Rate limiting
    - Audit logging
    - Error handling
    
    Args:
        allowed_tools: Set of tool names that are allowed to be executed. If None, all tools are allowed.
        sanitize_fn: Function to sanitize the tool's result. If None, no sanitization is performed.
        user_id: Optional user identifier for audit logging and rate limiting.
        session_id: Optional session identifier for audit logging and rate limiting.
        rate_limit: Optional rate limit configuration. If None, no rate limiting is applied.
        
    Returns:
        Callable: The decorated function with security features applied.
        
    Example:
        @secure_tool(
            allowed_tools={"search", "read"},
            sanitize_fn=my_sanitizer,
            user_id="user123",
            rate_limit=RateLimitConfig(requests_per_minute=60)
        )
        def search(query: str) -> Dict[str, Any]:
            return {"results": [...]}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Union[Dict[str, Any], Any]:
            
            # Initialize components
            access = ToolAccess(allowed_tools)
            audit = ToolAudit()
            sanitizer = ToolSanitizer(sanitize_fn)
            
            # Get tool name (from function)
            tool_name = func.__name__
            
            # Validate access
            access.validateToolAccess(tool_name)
            
            # Check rate limit if configured 
            # (in a near future we will use a rate limiter per tool, you can experiment with it)
            if rate_limit:
                rate_limit_key = f"{user_id}:{session_id}:{tool_name}" if user_id and session_id else tool_name
                if not _rate_limiter.checkRateLimit(rate_limit_key, rate_limit):
                    error_msg = "Rate limit exceeded"
                    audit.logToolCallError(
                        tool_name=tool_name,
                        error=ValueError(error_msg),
                        duration_ms=0,
                        user_id=user_id,
                        session_id=session_id
                    )
                    return {
                        "isError": True,
                        "error": error_msg
                    }
            
            # Start timing
            start_time = time.time()
            
            try:
                # Log start
                audit.logToolCallStart(
                    tool_name=tool_name,
                    args=kwargs,
                    user_id=user_id,
                    session_id=session_id
                )
                
                # Execute tool
                result = func(*args, **kwargs)
                
                # Sanitize result
                sanitized_result = sanitizer.sanitize_result(result)
                
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Log success! You can keep track of session id and user id uwu
                audit.logToolCallEnd(
                    tool_name=tool_name,
                    result=sanitized_result,
                    duration_ms=duration_ms,
                    user_id=user_id,
                    session_id=session_id
                )
                
                return sanitized_result
                
            except Exception as e:
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Log error
                audit.logToolCallError(
                    tool_name=tool_name,
                    error=e,
                    duration_ms=duration_ms,
                    user_id=user_id,
                    session_id=session_id
                )
                
                # Return MCP error format
                return {
                    "isError": True,
                    "error": str(e)
                }
        
        return wrapper
    return decorator
