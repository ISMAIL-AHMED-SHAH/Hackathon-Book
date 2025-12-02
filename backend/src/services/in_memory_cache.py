"""
In-memory cache for rate limiting (Redis fallback).

Provides simple in-memory rate limiting when Redis is unavailable.
Used as fallback in Hugging Face Spaces and other environments without Redis.

Note: This is a simple implementation. In production with multiple workers,
consider using Redis or a shared cache like Memcached.
"""

import time
from collections import defaultdict
from typing import DefaultDict


class InMemoryRateLimiter:
    """
    Simple in-memory rate limiter using sliding window.

    Attributes:
        requests: Dict tracking requests per user per window
        window_seconds: Time window in seconds
        max_requests: Maximum requests allowed per window
    """

    def __init__(self, window_seconds: int = 60, max_requests: int = 10):
        """
        Initialize rate limiter.

        Args:
            window_seconds: Time window in seconds (default 60)
            max_requests: Max requests per window (default 10)
        """
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        # user_id -> list of timestamps
        self.requests: DefaultDict[str, list[float]] = defaultdict(list)

    async def is_rate_limited(self, user_id: str) -> bool:
        """
        Check if user is rate limited.

        Args:
            user_id: User identifier

        Returns:
            True if rate limited, False otherwise
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        # Remove old requests outside the time window
        self.requests[user_id] = [
            ts for ts in self.requests[user_id] if ts > cutoff_time
        ]

        # Check if user exceeded limit
        if len(self.requests[user_id]) >= self.max_requests:
            return True

        # Record this request
        self.requests[user_id].append(current_time)
        return False

    async def get_remaining_requests(self, user_id: str) -> int:
        """
        Get remaining requests for user in current window.

        Args:
            user_id: User identifier

        Returns:
            Number of remaining requests
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        # Clean old requests
        self.requests[user_id] = [
            ts for ts in self.requests[user_id] if ts > cutoff_time
        ]

        return max(0, self.max_requests - len(self.requests[user_id]))

    async def reset(self, user_id: str) -> None:
        """
        Reset rate limit for a user.

        Args:
            user_id: User identifier
        """
        if user_id in self.requests:
            del self.requests[user_id]

    async def ping(self) -> bool:
        """
        Health check method (for compatibility with Redis client).

        Returns:
            Always True
        """
        return True


# Global singleton instance
_in_memory_limiter: InMemoryRateLimiter | None = None


def get_in_memory_limiter(
    window_seconds: int = 60, max_requests: int = 10
) -> InMemoryRateLimiter:
    """
    Get or create in-memory rate limiter singleton.

    Args:
        window_seconds: Time window in seconds
        max_requests: Max requests per window

    Returns:
        InMemoryRateLimiter instance
    """
    global _in_memory_limiter
    if _in_memory_limiter is None:
        _in_memory_limiter = InMemoryRateLimiter(window_seconds, max_requests)
    return _in_memory_limiter
