"""Application-level WAF firewall middleware."""
import re
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Max body size (5 Megabytes)
MAX_BODY_SIZE = 5 * 1024 * 1024

SUSPICIOUS_PATTERNS = [
    re.compile(r"(\.\./|\.\.\\)", re.IGNORECASE),                         # Path Traversal
    re.compile(r"(<script|javascript:|onerror=|onload=)", re.IGNORECASE), # XSS
    re.compile(r"(union\s+select|insert\s+into|drop\s+table)", re.IGNORECASE), # SQLi signatures
    re.compile(r"(/etc/passwd|/windows/win\.ini)", re.IGNORECASE),        # OS Path Traversal
]

class FirewallMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. URL Path Inspection
        path_str = request.url.path
        for pattern in SUSPICIOUS_PATTERNS:
            if pattern.search(path_str):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"code": "FIREWALL_BLOCKED", "detail": "Malicious path pattern detected."}
                )
        
        # 2. Query String Inspection
        query_str = str(request.url.query)
        for pattern in SUSPICIOUS_PATTERNS:
            if pattern.search(query_str):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"code": "FIREWALL_BLOCKED", "detail": "Malicious query pattern detected."}
                )
        
        # 3. Payload size check via Content-Length header
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > MAX_BODY_SIZE:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"code": "PAYLOAD_TOO_LARGE", "detail": "Request body exceeds safe limit."}
                    )
            except ValueError:
                pass
        
        return await call_next(request)
