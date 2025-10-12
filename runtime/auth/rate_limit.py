# -*- coding: utf-8 -*-
"""
Simple rate limiting for OAuth endpoints.
Uses in-memory storage (suitable for single-server deployments).
"""

from functools import wraps
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """
    Simple in-memory rate limiter.
    Tracks requests by IP address and endpoint.
    """
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = Lock()
    
    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int) -> tuple[bool, int]:
        """
        Check if a key is rate limited.
        
        Args:
            key: Unique identifier (e.g., IP address + endpoint)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_limited, retry_after_seconds)
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=window_seconds)
        
        with self.lock:
            # Clean up old requests
            self.requests[key] = [
                timestamp for timestamp in self.requests[key]
                if timestamp > cutoff
            ]
            
            # Check if limit exceeded
            if len(self.requests[key]) >= max_requests:
                # Calculate retry_after
                oldest_request = min(self.requests[key])
                retry_after = int((oldest_request + timedelta(seconds=window_seconds) - now).total_seconds())
                return True, max(retry_after, 1)
            
            # Record this request
            self.requests[key].append(now)
            return False, 0
    
    def clear(self):
        """Clear all rate limit data."""
        with self.lock:
            self.requests.clear()


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(max_requests: int, window_seconds: int):
    """
    Decorator to add rate limiting to a route.
    
    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        
    Usage:
        @rate_limit(max_requests=10, window_seconds=60)
        async def my_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            from emmett import request, abort
            
            # Create a unique key based on IP and endpoint
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
            endpoint = request.path
            key = f"{ip_address}:{endpoint}"
            
            # Check rate limit
            is_limited, retry_after = _rate_limiter.is_rate_limited(
                key, max_requests, window_seconds
            )
            
            if is_limited:
                # Log rate limit event
                print(f"Rate limit exceeded for {ip_address} on {endpoint}")
                
                # Return 429 Too Many Requests
                abort(429, f"Rate limit exceeded. Try again in {retry_after} seconds.")
            
            return await f(*args, **kwargs)
        
        return wrapper
    return decorator


def get_rate_limiter():
    """Get the global rate limiter instance."""
    return _rate_limiter

