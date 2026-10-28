"""Tests for Rate Limiter and WAF firewall signatures."""
import re
from app.security.ratelimit import RateLimiter
from app.security.firewall import SUSPICIOUS_PATTERNS

def test_rate_limiter():
    limiter = RateLimiter()
    key = "127.0.0.1:test"
    # Allow 3 requests in window
    assert limiter.is_rate_limited(key, max_requests=3, window_seconds=60) is False
    assert limiter.is_rate_limited(key, max_requests=3, window_seconds=60) is False
    assert limiter.is_rate_limited(key, max_requests=3, window_seconds=60) is False
    # 4th request exceeds
    assert limiter.is_rate_limited(key, max_requests=3, window_seconds=60) is True

def test_waf_signatures():
    # Test path traversal
    payload1 = "../etc/passwd"
    assert any(p.search(payload1) for p in SUSPICIOUS_PATTERNS) is True

    # Test XSS
    payload2 = "<script>alert(1)</script>"
    assert any(p.search(payload2) for p in SUSPICIOUS_PATTERNS) is True

    # Test SQL injection signature
    payload3 = "admin' UNION SELECT 1, 2, 3--"
    assert any(p.search(payload3) for p in SUSPICIOUS_PATTERNS) is True

    # Safe legitimate payload
    safe_payload = "/api/scan/start"
    assert any(p.search(safe_payload) for p in SUSPICIOUS_PATTERNS) is False
