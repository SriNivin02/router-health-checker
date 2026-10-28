"""Authentication, password hashing, and session management."""
import time
import hmac
import hashlib
import json
import base64
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status, Depends
from app.config import settings

# Attempt to load argon2-cffi, fallback to secure PBKDF2 if absent
try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    _hasher = PasswordHasher()
    def get_password_hash(password: str) -> str:
        return _hasher.hash(password)
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return _hasher.verify(hashed_password, plain_password)
        except Exception:
            return False
except ImportError:
    def get_password_hash(password: str) -> str:
        salt = base64.b64encode(hashlib.sha256(str(time.time()).encode()).digest()[:16]).decode()
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return f"pbkdf2${salt}${base64.b64encode(key).decode()}"
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            parts = hashed_password.split("$")
            if len(parts) != 3 or parts[0] != "pbkdf2":
                return False
            salt, b64_expected = parts[1], parts[2]
            key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000)
            return hmac.compare_digest(base64.b64encode(key).decode(), b64_expected)
        except Exception:
            return False

hash_password = get_password_hash

def is_common_password(password: str) -> bool:
    weak = {"12345678", "password", "password123", "admin123", "qwerty123"}
    return password.lower() in weak

def decode_session_token(token: str) -> Optional[Dict[str, Any]]:
    return verify_signed_data(token, settings.SECRET_KEY)

def generate_recovery_code() -> str:
    import secrets
    return f"{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"

def sign_data(payload: Dict[str, Any], secret: str) -> str:
    payload_str = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload_str}.{sig}"

def verify_signed_data(token: str, secret: str) -> Optional[Dict[str, Any]]:
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_str, sig = parts[0], parts[1]
        expected_sig = hmac.new(secret.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        data = json.loads(base64.urlsafe_b64decode(payload_str.encode("utf-8")).decode("utf-8"))
        if data.get("exp", 0) < time.time():
            return None
        return data
    except Exception:
        return None

def create_session_token(user_id: int, username: str) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "iat": int(time.time()),
        "exp": int(time.time()) + (settings.SESSION_EXPIRE_MINUTES * 60)
    }
    return sign_data(payload, settings.SECRET_KEY)

async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    # 1. Check HttpOnly cookie
    token = request.cookies.get("rhc_session")
    # 2. Check Authorization header
    if not token and "Authorization" in request.headers:
        auth_hdr = request.headers["Authorization"]
        if auth_hdr.startswith("Bearer "):
            token = auth_hdr[7:].strip()
    if not token:
        return None
    return verify_signed_data(token, settings.SECRET_KEY)

async def get_current_user(request: Request) -> Dict[str, Any]:
    user = await get_current_user_optional(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_REQUIRED", "message": "Authentication required"}
        )
    return user