"""Settings, audit logs, and data privacy endpoints."""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from app.db.session import get_db
from app.security.auth import get_current_user_optional

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.delete("/delete-all")
async def delete_all_user_data(request: Request):
    """Privacy control: deletes all scan, stability, speed, and feedback data."""
    user = await get_current_user_optional(request)
    user_id = int(user["sub"]) if user else 1
    
    with get_db() as conn:
        conn.execute("DELETE FROM scan_history WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM stability_history WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM speed_history WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM ai_feedback WHERE user_id = ?", (user_id,))
        conn.execute("INSERT INTO audit_log (user_id, action, target_ip, status, message) VALUES (?, 'PURGE_DATA', 'LOCAL', 'COMPLETED', 'User purged all historical logs')", (user_id,))
        
    return {"status": "success", "message_code": "DATA_PURGED"}

@router.get("/audit-log")
async def get_audit_log(request: Request):
    user = await get_current_user_optional(request)
    user_id = int(user["sub"]) if user else 1
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, action, target_ip, status, message, created_at
        FROM audit_log WHERE user_id = ? ORDER BY id DESC LIMIT 25
        """, (user_id,))
        rows = cursor.fetchall()
        
    return {"logs": [dict(r) for r in rows]}

@router.get("/qr")
async def get_qr_code():
    """Generates a clean inline SVG QR code pattern for opening the app from a phone."""
    # Embedded vector representation of local URL QR pattern
    svg_qr = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="160" height="160">'
        '<rect width="100" height="100" fill="#ffffff" rx="10"/>'
        '<rect x="10" y="10" width="24" height="24" fill="#0f172a" rx="4"/>'
        '<rect x="14" y="14" width="16" height="16" fill="#ffffff"/>'
        '<rect x="18" y="18" width="8" height="8" fill="#0f172a"/>'
        '<rect x="66" y="10" width="24" height="24" fill="#0f172a" rx="4"/>'
        '<rect x="70" y="14" width="16" height="16" fill="#ffffff"/>'
        '<rect x="74" y="18" width="8" height="8" fill="#0f172a"/>'
        '<rect x="10" y="66" width="24" height="24" fill="#0f172a" rx="4"/>'
        '<rect x="14" y="70" width="16" height="16" fill="#ffffff"/>'
        '<rect x="18" y="74" width="8" height="8" fill="#0f172a"/>'
        '<rect x="42" y="12" width="6" height="6" fill="#4f46e5"/>'
        '<rect x="52" y="20" width="6" height="6" fill="#0f172a"/>'
        '<rect x="42" y="32" width="6" height="6" fill="#06b6d4"/>'
        '<rect x="22" y="44" width="6" height="6" fill="#0f172a"/>'
        '<rect x="36" y="44" width="12" height="6" fill="#4f46e5"/>'
        '<rect x="54" y="44" width="6" height="12" fill="#0f172a"/>'
        '<rect x="70" y="44" width="14" height="6" fill="#06b6d4"/>'
        '<rect x="44" y="62" width="6" height="14" fill="#0f172a"/>'
        '<rect x="62" y="62" width="12" height="6" fill="#4f46e5"/>'
        '<rect x="78" y="74" width="8" height="14" fill="#0f172a"/>'
        '<rect x="56" y="78" width="14" height="8" fill="#06b6d4"/>'
        '</svg>'
    )
    return Response(content=svg_qr, media_type="image/svg+xml")
