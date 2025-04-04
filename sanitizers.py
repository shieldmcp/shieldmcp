from typing import Any, Callable, Optional, List, Pattern
import re
import html

class Sanitizer:
    """Base class providing static sanitization methods."""
    
    @staticmethod
    def htmlEscape(text: str) -> str:
        """
        Escape HTML special characters in text.
        
        Args:
            text: The input text to escape
            
        Returns:
            str: Text with HTML special characters escaped
        """
        return html.escape(text)

    @staticmethod
    def removeSensitiveData(text: str, patterns: List[Pattern[str]]) -> str:
        """
        Remove sensitive data based on regex patterns.
        
        Args:
            text: The input text to sanitize
            patterns: List of compiled regex patterns to match sensitive data
            
        Returns:
            str: Text with sensitive data replaced by [cleansed...]
        """
        result = text
        for pattern in patterns:
            result = re.sub(pattern, "[cleansed...]", result)
        return result

    @staticmethod
    def truncateText(text: str, max_length: int = 1000) -> str:
        """
        Truncate text to a maximum length, adding ellipsis if truncated.
        
        Args:
            text: The input text to truncate
            max_length: Maximum allowed length (default: 1000)
            
        Returns:
            str: Truncated text if longer than max_length, original text otherwise
        """
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

class ToolSanitizer:
    """
    Sanitizer for MCP tool results.
    
    This class provides sanitization capabilities for tool outputs,
    including HTML escaping, sensitive data removal, and text truncation.
    """
    
    def __init__(self, sanitize_fn: Optional[Callable[[Any], Any]] = None):
        """
        Initialize the sanitizer with an optional custom sanitization function.
        
        Args:
            sanitize_fn: Optional custom sanitization function. If None, 
                        a pass-through function is used.
        """
        self.sanitize_fn = sanitize_fn or (lambda x: x)

    def sanitizeResult(self, result: Any) -> Any:
        """
        Apply sanitization to the tool result.
        
        Args:
            result: The tool result to sanitize
            
        Returns:
            Any: The sanitized result
        """
        return self.sanitize_fn(result)

    @staticmethod
    def createTextSanitizer(
        max_length: int = 1000,
        sensitive_patterns: Optional[List[str]] = None
    ) -> Callable[[str], str]:
        """
        Create a text sanitizer function with specified parameters.
        
        Args:
            max_length: Maximum length for text truncation (default: 1000)
            sensitive_patterns: Optional list of regex patterns for sensitive data
            
        Returns:
            Callable[[str], str]: A function that sanitizes text input
            
        Example:
            sanitizer = ToolSanitizer.createTextSanitizer(
                max_length=500,
                sensitive_patterns=[r"\b\d{16}\b"]  # Credit card numbers
            )
            clean_text = sanitizer("Your text with sensitive data")
        """
        def sanitizeText(text: str) -> str:
            if not isinstance(text, str):
                return text
            
            # Compile patterns once for better performance
            compiled_patterns = [re.compile(pattern) for pattern in (sensitive_patterns or [])]
            
            text = Sanitizer.htmlEscape(text)
            if compiled_patterns:
                text = Sanitizer.removeSensitiveData(text, compiled_patterns)
            return Sanitizer.truncateText(text, max_length)
        
        return sanitizeText
