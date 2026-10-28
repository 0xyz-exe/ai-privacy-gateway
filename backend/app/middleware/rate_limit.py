import time
from collections import defaultdict
from fastapi import Request, HTTPException
from app.core.config import settings

from typing import Optional

class InMemoryRateLimiter:
    def __init__(self):
        # key_id -> list of timestamps
        self.requests = defaultdict(list)

    def is_allowed(self, identifier: str, limit: int = 60, window_seconds: int = 60) -> tuple[bool, int]:
        now = time.time()
        window_start = now - window_seconds
        
        # Purge expired
        self.requests[identifier] = [t for t in self.requests[identifier] if t > window_start]
        
        current_count = len(self.requests[identifier])
        if current_count >= limit:
            remaining = 0
            return False, remaining
            
        self.requests[identifier].append(now)
        remaining = limit - (current_count + 1)
        return True, remaining

limiter = InMemoryRateLimiter()

def check_rate_limit(request: Request, limit: Optional[int] = None, window_seconds: Optional[int] = None):
    if not settings.rate_limit_enabled:
        return
        
    limit = limit or settings.rate_limit_requests
    window_seconds = window_seconds or settings.rate_limit_window_seconds
    
    # Identify by API key prefix if authenticated, else client IP
    ident = getattr(request.state, "key_prefix", None) or (request.client.host if request.client else "unknown")
    
    allowed, remaining = limiter.is_allowed(ident, limit=limit, window_seconds=window_seconds)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {limit} requests per {window_seconds}s.",
            headers={"Retry-After": str(window_seconds)}
        )
