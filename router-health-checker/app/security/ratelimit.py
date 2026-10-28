"""In-memory rate limiting with sliding window."""
import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, HTTPException, status

class RateLimiter:
    def __init__(self):
        # ip -> list of timestamps
        self.requests: Dict[str, List[float]] = defaultdict(list)
        # ip -> ban expiry timestamp
        self.banned: Dict[str, float] = {}

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        now = time.time()
        
        # Check temporary ban
        if key in self.banned:
            if now < self.banned[key]:
                return True
            else:
                del self.banned[key]
        
        timestamps = self.requests[key]
        # Filter timestamps within window
        valid_timestamps = [t for t in timestamps if now - t < window_seconds]
        valid_timestamps.append(now)
        self.requests[key] = valid_timestamps
        
        if len(valid_timestamps) > max_requests:
            # If exceeding twice the limit, ban for 5 minutes
            if len(valid_timestamps) > max_requests * 2:
                self.banned[key] = now + 300
            return True
        return False

limiter = RateLimiter()

def check_rate_limit(request: Request, limit_per_minute: int, endpoint_name: str = "general"):
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{endpoint_name}"
    if limiter.is_rate_limited(key, max_requests=limit_per_minute, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": "RATE_LIMIT_EXCEEDED", "message": f"Too many requests for {endpoint_name}. Please slow down."}
        )
