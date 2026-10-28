"""CSRF Protection Middleware and Utilities."""
import secrets
import hmac
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

def generate_csrf_token() -> str:
    return secrets.token_hex(32)

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow safe read-only methods
        if request.method in SAFE_METHODS:
            return await call_next(request)
        
        # Exempt specific unauthenticated public auth routes (like login/register if CSRF token isn't seeded yet)
        path = request.url.path
        if path in {"/api/auth/login", "/api/auth/register", "/api/auth/forgot-password", "/api/speed/upload"}:
            return await call_next(request)
        
        # For state-changing APIs, verify double-submit cookie or custom header
        cookie_csrf = request.cookies.get("rhc_csrf")
        header_csrf = request.headers.get("X-CSRF-Token")
        
        if not cookie_csrf or not header_csrf or not hmac.compare_digest(cookie_csrf, header_csrf):
            # If session is active and token mismatched
            if request.cookies.get("rhc_session"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"code": "CSRF_TOKEN_INVALID", "message": "CSRF token missing or mismatched"}
                )
        
        return await call_next(request)
