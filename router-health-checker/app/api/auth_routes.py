"""Authentication and session management routes."""
import time
from fastapi import APIRouter, Request, Response, HTTPException, status
from app.db.models import UserRegisterRequest, UserLoginRequest, ForgotPasswordRequest, ConsentRequest
from app.db.session import get_db
from app.security.auth import (
    get_password_hash,
    verify_password,
    create_session_token,
    get_current_user,
    get_current_user_optional
)
from app.security.csrf import generate_csrf_token
from app.security.ratelimit import check_rate_limit
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

COMMON_WEAK_PASSWORDS = {"12345678", "password", "password123", "admin123", "qwerty123"}

@router.get("/csrf")
async def get_csrf_token(response: Response):
    """Generate CSRF token and set cookie."""
    token = generate_csrf_token()
    response.set_cookie(
        key="rhc_csrf",
        value=token,
        httponly=False,
        samesite="strict",
        secure=False  # Set True when on HTTPS
    )
    return {"csrf_token": token}

@router.post("/register")
async def register(req: UserRegisterRequest, request: Request):
    check_rate_limit(request, settings.RATE_LIMIT_LOGIN_PER_MIN, "auth_register")
    
    # Check minimum password strength
    if req.password.lower() in COMMON_WEAK_PASSWORDS or len(req.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "PASSWORD_TOO_WEAK", "message": "Password must be at least 8 characters and not a common phrase."}
        )
        
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (req.username.strip().lower(),))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "USERNAME_EXISTS", "message": "Username is already registered."}
            )
            
        pwd_hash = get_password_hash(req.password)
        ans_hash = get_password_hash(req.security_answer.lower()) if req.security_answer else None
        
        cursor.execute("""
        INSERT INTO users (username, password_hash, security_question, security_answer_hash)
        VALUES (?, ?, ?, ?)
        """, (req.username.strip().lower(), pwd_hash, req.security_question, ans_hash))
        user_id = cursor.lastrowid
        
    return {"status": "success", "user_id": user_id, "message_code": "REGISTRATION_SUCCESS"}

@router.post("/login")
async def login(req: UserLoginRequest, request: Request, response: Response):
    check_rate_limit(request, settings.RATE_LIMIT_LOGIN_PER_MIN, "auth_login")
    
    username_clean = req.username.strip().lower()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, username, password_hash, consent_given, failed_attempts, lockout_until
        FROM users WHERE username = ?
        """, (username_clean,))
        user_row = cursor.fetchone()
        
        if not user_row:
            # Constant time delay to prevent user enumeration
            time.sleep(0.3)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Invalid username or password."}
            )
            
        # Check lockout
        if user_row["lockout_until"]:
            try:
                lockout_ts = float(user_row["lockout_until"])
                if time.time() < lockout_ts:
                    remaining = int(lockout_ts - time.time())
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail={"code": "ACCOUNT_LOCKED", "message": f"Account temporarily locked. Try again in {remaining} seconds."}
                    )
            except ValueError:
                pass
                
        # Verify password
        if not verify_password(req.password, user_row["password_hash"]):
            failed = user_row["failed_attempts"] + 1
            lockout_time = None
            if failed >= 5:
                # Exponential backoff lock for 5 minutes
                lockout_time = str(time.time() + 300)
            cursor.execute("UPDATE users SET failed_attempts = ?, lockout_until = ? WHERE id = ?", (failed, lockout_time, user_row["id"]))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Invalid username or password."}
            )
            
        # Reset failed attempts on success
        cursor.execute("UPDATE users SET failed_attempts = 0, lockout_until = NULL, last_login = datetime('now') WHERE id = ?", (user_row["id"],))
        
    token = create_session_token(user_row["id"], user_row["username"])
    csrf_token = generate_csrf_token()
    
    response.set_cookie(
        key="rhc_session",
        value=token,
        httponly=True,
        samesite="strict",
        max_age=settings.SESSION_EXPIRE_MINUTES * 60,
        secure=False
    )
    response.set_cookie(
        key="rhc_csrf",
        value=csrf_token,
        httponly=False,
        samesite="strict",
        secure=False
    )
    
    return {
        "status": "success",
        "username": user_row["username"],
        "consent_given": bool(user_row["consent_given"]),
        "csrf_token": csrf_token
    }

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("rhc_session")
    response.delete_cookie("rhc_csrf")
    return {"status": "logged_out"}

@router.get("/me")
async def get_me(request: Request):
    user = await get_current_user_optional(request)
    if not user:
        return {"authenticated": False}
        
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, consent_given, consent_timestamp, last_login FROM users WHERE id = ?", (int(user["sub"]),))
        row = cursor.fetchone()
        
    if not row:
        return {"authenticated": False}
        
    return {
        "authenticated": True,
        "id": row["id"],
        "username": row["username"],
        "consent_given": bool(row["consent_given"]),
        "consent_timestamp": row["consent_timestamp"]
    }

@router.post("/consent")
async def give_consent(req: ConsentRequest, request: Request):
    user = await get_current_user(request)
    user_id = int(user["sub"])
    
    with get_db() as conn:
        conn.execute("""
        UPDATE users SET consent_given = ?, consent_timestamp = datetime('now')
        WHERE id = ?
        """, (1 if req.consent else 0, user_id))
        
    return {"status": "success", "consent_given": req.consent}

@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, request: Request):
    check_rate_limit(request, settings.RATE_LIMIT_LOGIN_PER_MIN, "auth_forgot")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, security_answer_hash FROM users WHERE username = ?", (req.username.strip().lower(),))
        row = cursor.fetchone()
        if not row or not row["security_answer_hash"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "RECOVERY_FAILED", "message": "Security verification failed."}
            )
        if not verify_password(req.security_answer.lower(), row["security_answer_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "RECOVERY_FAILED", "message": "Incorrect answer to security question."}
            )
            
        new_pwd_hash = get_password_hash(req.new_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_pwd_hash, row["id"]))
        
    return {"status": "success", "message_code": "PASSWORD_RESET_SUCCESS"}
