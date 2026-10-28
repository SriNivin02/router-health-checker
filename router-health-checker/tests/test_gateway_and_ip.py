"""Tests for RFC1918 private IP validation (anti-SSRF hard safety)."""
from app.scanner.gateway import is_private_ip

def test_private_ips_allowed():
    assert is_private_ip("192.168.1.1") is True
    assert is_private_ip("192.168.0.1") is True
    assert is_private_ip("10.0.0.1") is True
    assert is_private_ip("172.16.0.1") is True
    assert is_private_ip("169.254.1.1") is True

def test_public_and_invalid_ips_rejected():
    assert is_private_ip("127.0.0.1") is False
    assert is_private_ip("8.8.8.8") is False
    assert is_private_ip("1.1.1.1") is False
    assert is_private_ip("142.250.190.46") is False
    assert is_private_ip("example.com") is False
    assert is_private_ip("localhost") is False
    assert is_private_ip("http://192.168.1.1") is False
    assert is_private_ip("999.999.999.999") is False
