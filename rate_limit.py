import time
from typing import Dict, Optional, Final
from threading import Lock
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class RateLimitConfig:
    """
    Configuration for rate limiting in MCP tools.
    
    This class defines the rate limiting parameters for MCP tools,
    including the base rate and optional burst capacity.
    
    Attributes:
        requests_per_minute: Maximum number of requests allowed per minute
        burst_size: Optional maximum burst capacity. If None, defaults to requests_per_minute
    """
    requests_per_minute: int
    burst_size: Optional[int] = None

    def __post_init__(self):
        """Validate configuration parameters."""
        if self.requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be positive")
        if self.burst_size is not None and self.burst_size < self.requests_per_minute:
            raise ValueError("burst_size cannot be less than requests_per_minute")

class TokenBucket:
    """
    Token bucket algorithm implementation for rate limiting.
    
    This class implements the token bucket algorithm, which allows for
    rate limiting with burst capacity. Tokens are added at a constant rate,
    and requests consume tokens. If there are insufficient tokens, the request
    is rate limited.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the token bucket.
        
        Args:
            rate: Tokens added per second
            capacity: Maximum number of tokens the bucket can hold
        """
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")
            
        self.rate: Final[float] = rate
        self.capacity: Final[int] = capacity
        self.tokens: float = float(capacity)
        self.last_update: float = time.time()
        self.lock: Lock = Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume (default: 1)
            
        Returns:
            bool: True if tokens were consumed, False if rate limit exceeded
            
        Note:
            This method is thread-safe.
        """
        if tokens <= 0:
            raise ValueError("tokens must be positive")
            
        with self.lock:
            now = time.time()
            # Add new tokens based on time passed
            time_passed = now - self.last_update
            new_tokens = time_passed * self.rate
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_update = now

            if tokens <= self.tokens:
                self.tokens -= tokens
                return True
            return False

class RateLimiter:
    """
    Rate limiter implementation for MCP tools.
    
    This class manages multiple token buckets for different rate limit keys,
    allowing for per-key rate limiting with configurable rates and burst capacities.
    """
    
    def __init__(self):
        """Initialize the rate limiter."""
        self.limiters: Dict[str, TokenBucket] = {}
        self.lock: Lock = Lock()

    def getLimiter(self, key: str, config: RateLimitConfig) -> TokenBucket:
        """
        Get or create a rate limiter for the given key.
        
        Args:
            key: Unique identifier for the rate limit
            config: Rate limit configuration
            
        Returns:
            TokenBucket: The token bucket for the given key
            
        Note:
            This method is thread-safe.
        """
        with self.lock:
            if key not in self.limiters:
                # Convert requests per minute to tokens per second
                rate = config.requests_per_minute / 60.0
                capacity = config.burst_size or config.requests_per_minute
                self.limiters[key] = TokenBucket(rate=rate, capacity=capacity)
            return self.limiters[key]

    def checkRateLimit(
        self,
        key: str,
        config: RateLimitConfig,
        tokens: int = 1
    ) -> bool:
        """
        Check if the request should be rate limited.
        
        Args:
            key: Unique identifier for the rate limit
            config: Rate limit configuration
            tokens: Number of tokens to consume (default: 1)
            
        Returns:
            bool: True if the request should proceed, False if rate limited
            
        Note:
            This method is thread-safe.
        """
        limiter = self.getLimiter(key, config)
        return limiter.consume(tokens)

    def reset(self, key: Optional[str] = None) -> None:
        """
        Reset rate limiters for testing or manual intervention.
        
        Args:
            key: Optional specific key to reset. If None, resets all limiters.
            
        Note:
            This method is thread-safe.
        """
        with self.lock:
            if key:
                self.limiters.pop(key, None)
            else:
                self.limiters.clear()
