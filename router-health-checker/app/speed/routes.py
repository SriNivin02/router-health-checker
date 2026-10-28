"""Speed test endpoints: download streaming, upload receiving, and micro-latency."""
import time
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.db.session import get_db
from app.security.auth import get_current_user_optional

router = APIRouter(prefix="/api/speed", tags=["speed"])

# 64KB dummy buffer for download streaming
CHUNK = b"0" * 65536

def generate_bytes(total_bytes: int):
    sent = 0
    while sent < total_bytes:
        size = min(len(CHUNK), total_bytes - sent)
        yield CHUNK[:size]
        sent += size

@router.get("/download")
async def download_speed(size_mb: int = 5):
    """Streams dummy binary data to measure Wi-Fi/local download bandwidth."""
    safe_size = max(1, min(size_mb, 20))
    total_bytes = safe_size * 1024 * 1024
    return StreamingResponse(
        generate_bytes(total_bytes),
        media_type="application/octet-stream",
        headers={
            "Content-Length": str(total_bytes),
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache"
        }
    )

@router.post("/upload")
async def upload_speed(request: Request):
    """Consumes client payload and measures incoming upload rate."""
    t0 = time.time()
    total_bytes = 0
    async for chunk in request.stream():
        total_bytes += len(chunk)
    elapsed = max(0.001, time.time() - t0)
    mbps = round((total_bytes * 8) / (elapsed * 1_000_000), 2)
    return {
        "status": "success",
        "bytes_received": total_bytes,
        "elapsed_seconds": round(elapsed, 3),
        "mbps": mbps
    }

@router.get("/ping")
async def ping_speed():
    """Micro round-trip latency endpoint."""
    return {"timestamp": time.time(), "status": "pong"}

@router.post("/save")
async def save_speed_result(request: Request):
    """Saves a speed run to the history database."""
    body = await request.json()
    user = await get_current_user_optional(request)
    user_id = int(user["sub"]) if user else 1
    
    download = float(body.get("download_mbps", 0))
    upload = float(body.get("upload_mbps", 0))
    ping = float(body.get("ping_ms", 0))
    jitter = float(body.get("jitter_ms", 0))
    verdict = body.get("verdict_code", "SPEED_VERDICT_GOOD")
    
    with get_db() as conn:
        conn.execute("""
        INSERT INTO speed_history (user_id, download_mbps, upload_mbps, ping_ms, jitter_ms, verdict_code)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, download, upload, ping, jitter, verdict))
        
    return {"status": "saved"}

@router.get("/history")
async def get_speed_history(request: Request):
    """Retrieves speed test history."""
    user = await get_current_user_optional(request)
    user_id = int(user["sub"]) if user else 1
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, timestamp, download_mbps, upload_mbps, ping_ms, jitter_ms, verdict_code
        FROM speed_history
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 10
        """, (user_id,))
        rows = cursor.fetchall()
        
    history = [dict(row) for row in rows]
    return {"history": history}
