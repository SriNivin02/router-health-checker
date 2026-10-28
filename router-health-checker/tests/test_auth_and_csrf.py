"""Tests for authentication, hashing, sessions, and CSRF token mechanics."""
from app.security.auth import get_password_hash, verify_password, create_session_token, verify_signed_data
from app.security.csrf import generate_csrf_token
from app.config import settings

def test_password_hashing():
    pwd = "SecretPassphrase123!"
    h = get_password_hash(pwd)
    assert verify_password(pwd, h) is True
    assert verify_password("WrongPassword", h) is False

def test_session_token():
    token = create_session_token(user_id=42, username="testuser")
    data = verify_signed_data(token, settings.SECRET_KEY)
    assert data is not None
    assert data["sub"] == "42"
    assert data["username"] == "testuser"

def test_session_tampering_rejected():
    token = create_session_token(user_id=42, username="testuser")
    tampered = token[:-4] + "abcd"
    assert verify_signed_data(tampered, settings.SECRET_KEY) is None

def test_csrf_token():
    t1 = generate_csrf_token()
    t2 = generate_csrf_token()
    assert len(t1) == 64
    assert t1 != t2
