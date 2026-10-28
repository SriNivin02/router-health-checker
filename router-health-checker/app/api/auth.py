"""
app/api/auth.py – Authentication routes: register, login, logout, profile, consent
"""
from __future__ import annotations

import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import User
from app.db.session import get_db
from app.security.auth import (
    COMMON_PASSWORDS,
    audit,
    create_session_token,
    decode_session_token,
    generate_recovery_code,
    hash_password,
    is_common_password,
    is_locked_out,
    lockout_seconds_remaining,
    needs_rehash,
    record_failed_login,
    reset_failed_logins,
    verify_password,
)
from app.security.csrf import CSRF_COOKIE_NAME, generate_csrf_token, require_csrf
from app.security.ratelimit import rate_limit_dependency

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["auth"])

# ── Pydantic models ──────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=10, max_length=128)
    security_question: Optional[str] = Field(None, max_length=200)
    security_answer: Optional[str] = Field(None, max_length=200)

    @field_validator("password")
    @classmethod
    def _strong_password(cls, v: str) -> str:
        if is_common_password(v):
            raise ValueError("PASSWORD_TOO_COMMON")
        return v


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)
    remember_me: bool = False


class ConsentRequest(BaseModel):
    consent_given: bool


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=10, max_length=128)


class UpdateProfileRequest(BaseModel):
    language: Optional[str] = Field(None, max_length=10)
    theme: Optional[str] = Field(None, max_length=20)
    text_size: Optional[str] = Field(None, max_length=10)
    profile_type: Optional[str] = Field(None, max_length=20)


# ── Helpers ──────────────────────────────────────────────────────

def _get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "NOT_AUTHENTICATED"})
    user_id = decode_session_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "SESSION_EXPIRED"})
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "USER_NOT_FOUND"})
    return user


def _set_session_cookie(response: Response, token: str, max_age: int | None = None) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        samesite="strict",
        secure=False,  # Set True in production with HTTPS
        max_age=max_age or settings.session_max_age_seconds,
        path="/",
    )


def _set_csrf_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        httponly=False,  # JS needs to read this
        samesite="strict",
        secure=False,
        max_age=settings.session_max_age_seconds,
        path="/",
    )


# ── Routes ───────────────────────────────────────────────────────

@router.post(
    "/register",
    dependencies=[Depends(rate_limit_dependency("login", "5/minute"))],
)
async def register(
    body: RegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    ip = _get_client_ip(request)

    # Check username uniqueness
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=400, detail={"code": "USERNAME_TAKEN"})

    pw_hash = hash_password(body.password)
    sec_answer_hash = hash_password(body.security_answer) if body.security_answer else None
    recovery_plain, recovery_hash = generate_recovery_code()

    user = User(
        username=body.username,
        password_hash=pw_hash,
        security_question=body.security_question,
        security_answer_hash=sec_answer_hash,
        recovery_code_hash=recovery_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    audit(db, "REGISTER", user_id=user.id, ip_address=ip)

    token = create_session_token(user.id)
    csrf_token = generate_csrf_token(token)
    _set_session_cookie(response, token)
    _set_csrf_cookie(response, csrf_token)

    return {
        "ok": True,
        "code": "REGISTERED",
        "recovery_code": recovery_plain,  # Show once to user
        "user": {"id": user.id, "username": user.username},
    }


@router.post(
    "/login",
    dependencies=[Depends(rate_limit_dependency("login", "5/minute"))],
)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    ip = _get_client_ip(request)

    # Generic error message to prevent user enumeration
    auth_fail = HTTPException(status_code=401, detail={"code": "INVALID_CREDENTIALS"})

    user = db.query(User).filter(User.username == body.username).first()
    if not user:
        raise auth_fail

    if is_locked_out(user):
        secs = lockout_seconds_remaining(user)
        raise HTTPException(
            status_code=429,
            detail={"code": "ACCOUNT_LOCKED", "retry_after": secs},
        )

    if not verify_password(body.password, user.password_hash):
        record_failed_login(user, db)
        audit(db, "LOGIN_FAILED", user_id=user.id, ip_address=ip)
        raise auth_fail

    # Success
    reset_failed_logins(user, db)
    audit(db, "LOGIN", user_id=user.id, ip_address=ip)

    # Rehash if needed
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(body.password)
        db.commit()

    max_age = 86400 * 7 if body.remember_me else settings.session_max_age_seconds
    token = create_session_token(user.id)
    csrf_token = generate_csrf_token(token)
    _set_session_cookie(response, token, max_age=max_age)
    _set_csrf_cookie(response, csrf_token)

    return {
        "ok": True,
        "code": "LOGGED_IN",
        "user": {
            "id": user.id,
            "username": user.username,
            "language": user.language,
            "theme": user.theme,
            "text_size": user.text_size,
            "profile_type": user.profile_type,
            "consent_given": user.consent_given,
        },
    }


@router.post(
    "/logout",
    dependencies=[Depends(require_csrf)],
)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    audit(db, "LOGOUT", user_id=current_user.id, ip_address=_get_client_ip(request))
    response.delete_cookie(settings.session_cookie_name)
    response.delete_cookie(CSRF_COOKIE_NAME)
    return {"ok": True, "code": "LOGGED_OUT"}


@router.post(
    "/consent",
    dependencies=[Depends(require_csrf)],
)
async def give_consent(
    body: ConsentRequest,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    if body.consent_given:
        current_user.consent_given = True
        current_user.consent_at = datetime.datetime.utcnow()
        db.commit()
    return {"ok": True, "consent_given": current_user.consent_given}


@router.get("/me")
async def get_me(current_user: User = Depends(_get_current_user)):
    return {
        "ok": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "language": current_user.language,
            "theme": current_user.theme,
            "text_size": current_user.text_size,
            "profile_type": current_user.profile_type,
            "consent_given": current_user.consent_given,
        },
    }


@router.put(
    "/profile",
    dependencies=[Depends(require_csrf)],
)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    if body.language is not None:
        current_user.language = body.language
    if body.theme is not None:
        current_user.theme = body.theme
    if body.text_size is not None:
        current_user.text_size = body.text_size
    if body.profile_type is not None:
        current_user.profile_type = body.profile_type
    db.commit()
    return {"ok": True, "code": "PROFILE_UPDATED"}


@router.post(
    "/change-password",
    dependencies=[Depends(require_csrf)],
)
async def change_password(
    body: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail={"code": "INVALID_CURRENT_PASSWORD"})
    if is_common_password(body.new_password):
        raise HTTPException(status_code=400, detail={"code": "PASSWORD_TOO_COMMON"})
    current_user.password_hash = hash_password(body.new_password)
    db.commit()
    audit(db, "PASSWORD_CHANGED", user_id=current_user.id, ip_address=_get_client_ip(request))
    return {"ok": True, "code": "PASSWORD_CHANGED"}


@router.delete(
    "/data",
    dependencies=[Depends(require_csrf)],
)
async def delete_all_data(
    request: Request,
    response: Response,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    """Delete all user data (GDPR-style)."""
    audit(db, "DELETE_ALL_DATA", user_id=current_user.id, ip_address=_get_client_ip(request))
    db.delete(current_user)
    db.commit()
    response.delete_cookie(settings.session_cookie_name)
    response.delete_cookie(CSRF_COOKIE_NAME)
    return {"ok": True, "code": "DATA_DELETED"}
