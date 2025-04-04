from typing import List, Optional, Set, Callable, Any, Dict, Union
from functools import wraps
import time

class ToolAccess:
    """
    Access control manager for MCP tools.
    
    This class provides functionality to manage and validate access to MCP tools
    through a whitelist-based approach.
    """
    
    def __init__(self, allowed_tools: Optional[Set[str]] = None):
        """
        Initialize the access control manager.
        
        Args:
            allowed_tools: Optional set of allowed tool names. If None, an empty set is used.
        """
        self.allowed_tools = allowed_tools or set()

    def isToolAllowed(self, tool_name: str) -> bool:
        """
        Check if a tool is allowed to be executed.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            bool: True if the tool is allowed, False otherwise
        """
        return tool_name in self.allowed_tools

    def validateToolAccess(self, tool_name: str) -> None:
        """
        Validate if a tool is allowed to be executed.
        
        Args:
            tool_name: Name of the tool to validate
            
        Raises:
            ValueError: If the tool is not in the allowed set
        """
        if not self.isToolAllowed(tool_name):
            raise ValueError(f"Tool '{tool_name}' is not allowed")

    def addAllowedTool(self, tool_name: str) -> None:
        """
        Add a tool to the allowed tools set.
        
        Args:
            tool_name: Name of the tool to add
        """
        self.allowed_tools.add(tool_name)

    def removeAllowedTool(self, tool_name: str) -> None:
        """
        Remove a tool from the allowed tools set.
        
        Args:
            tool_name: Name of the tool to remove
        """
        self.allowed_tools.discard(tool_name)

    def getAllowedTools(self) -> Set[str]:
        """
        Get a copy of the set of allowed tools.
        
        Returns:
            Set[str]: Copy of the allowed tools set
        """
        return self.allowed_tools.copy()

def secure_tool(
    allowed_tools: Optional[Set[str]] = None,
    sanitize_fn: Optional[Callable[[Any], Any]] = None,
    rate_limit: Optional[RateLimitConfig] = None,
    input_schema: Optional[Dict[str, Any]] = None,
    sensitive_operation: bool = False,
    timeout: Optional[int] = None,
    require_preview: bool = False
) -> Callable:
    """
    Decorator that implements all MUST and SHOULD requirements of MCP.
    See to end of: https://modelcontextprotocol.io/docs/concepts/architecture
    
    Args:
        allowed_tools: Set of allowed tool names
        sanitize_fn: Optional function to sanitize tool results
        rate_limit: Optional rate limit configuration
        input_schema: Optional JSON schema for input validation
        sensitive_operation: Whether the operation requires confirmation
        timeout: Optional timeout in seconds
        require_preview: Whether to require input preview
        
    Returns:
        Callable: The decorated function with security features applied
        
    Example:
        @secure_tool(
            allowed_tools={"search", "read"},
            input_schema={"query": {"type": "string"}},
            sensitive_operation=True
        )
        def search(query: str) -> Dict[str, Any]:
            return {"results": [...]}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Union[Dict[str, Any], Any]:
            # 1. First validate inputs
            if input_schema:
                InputValidator(input_schema).validate(kwargs)

            # 2. Preview (is this necesary already? you can just call the function and see the output)
            if require_preview:
                InputPreview().preview_inputs(func.__name__, kwargs)

            # 3. Confirm
            if sensitive_operation:
                if not UserConfirmation().requires_confirmation(func.__name__):
                    return {
                        "isError": True,
                        "error": "User confirmation required"
                    }

            # 4. Access control
            access = ToolAccess(allowed_tools)
            try:
                access.validateToolAccess(func.__name__)
            except ValueError as e:
                return {
                    "isError": True,
                    "error": str(e)
                }

            # 5. Rate limiting
            if rate_limit:
                if not _rate_limiter.checkRateLimit(...):
                    return {
                        "isError": True,
                        "error": "Rate limit exceeded"
                    }

            # 6. Timeout handling
            start_time = time.time()
            try:
                if timeout:
                    with TimeoutManager(timeout).with_timeout(func):
                        result = func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
            except TimeoutError:
                return {
                    "isError": True,
                    "error": f"Operation timed out after {timeout} seconds"
                }

            # 7. Result (sanitization)
            sanitized_result = ToolSanitizer(sanitize_fn).sanitizeResult(result)

            # 8. Result (validation)
            if not ResultValidator().validate_result(sanitized_result):
                return {
                    "isError": True,
                    "error": "Invalid result format"
                }

            # 9. Audit logging
            duration_ms = (time.time() - start_time) * 1000
            audit = ToolAudit()
            audit.logToolCallEnd(
                tool_name=func.__name__,
                result=sanitized_result,
                duration_ms=duration_ms
            )

            return sanitized_result

        return wrapper
    return decorator
