"""Router scan endpoints."""
import json
import time
from fastapi import APIRouter, Request, HTTPException, status
from app.db.models import ScanStartRequest
from app.db.session import get_db
from app.security.auth import get_current_user_optional
from app.security.ratelimit import check_rate_limit
from app.scanner.gateway import get_default_gateway, is_private_ip
from app.scanner.ports import scan_ports
from app.scanner.admin_page import check_admin_page
from app.scanner.wifi import get_wifi_security_info
from app.scanner.dns import get_dns_resolvers
from app.scanner.scoring import calculate_router_score
from app.scanner.fixes import generate_remediation_fixes
from app.config import settings

router = APIRouter(prefix="/api/scan", tags=["scan"])

@router.post("/start")
async def start_router_scan(req: ScanStartRequest, request: Request):
    # Rate limit check (max 2 scans per minute)
    check_rate_limit(request, settings.RATE_LIMIT_SCAN_PER_MIN, "scan_start")
    
    user = await get_current_user_optional(request)
    user_id = int(user["sub"]) if user else 1
    
    # Verify user consent
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT consent_given FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row or not row["consent_given"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "CONSENT_REQUIRED", "message": "You must accept the ethical use consent before scanning."}
            )
            
    # Resolve target gateway
    target = req.target_ip.strip() if req.target_ip else get_default_gateway()
    
    # HARD SAFETY RULE: Only private IPs permitted!
    if not is_private_ip(target):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "TARGET_NOT_PRIVATE", "message": "Scanning is strictly restricted to local RFC1918 private subnets."}
        )
        
    # Execute non-intrusive diagnostic probes
    # 1. Wi-Fi Security
    wifi_info = get_wifi_security_info()
    
    # 2. Ports Check
    port_results = scan_ports(target)
    
    # 3. Admin Page Check
    admin_info = check_admin_page(target, test_defaults=req.test_default_credentials)
    
    # 4. DNS Check
    dns_info = get_dns_resolvers(target)
    
    # 5. Score Calculation
    score, verdict, deductions = calculate_router_score(
        wifi_grade=wifi_info["grade"],
        admin_info=admin_info,
        open_ports=port_results,
        dns_info=dns_info,
        wps_enabled=wifi_info["wps_enabled_hint"]
    )
    
    # 6. Generate Top 3 & All Fixes
    top_3, all_fixes = generate_remediation_fixes(deductions)
    
    checks_summary = {
        "wifi": "pass" if wifi_info["grade"] in ["wpa2", "wpa3"] else "fail",
        "admin": "fail" if admin_info["default_login_detected"] else ("warn" if admin_info["is_plain_http_only"] else "pass"),
        "ports": "fail" if any(p["port"] == 23 and p["is_open"] for p in port_results) else ("warn" if any(p["is_open"] for p in port_results) else "pass"),
        "wps": "fail" if wifi_info["wps_enabled_hint"] else "pass",
        "dns": "warn" if dns_info["has_suspicious_dns"] else "pass",
        "fw": "pass"
    }
    
    open_port_names = [f"{p['port']}/{p['service']}" for p in port_results if p["is_open"]]
    dns_ips = [d["ip"] for d in dns_info["resolvers"]]
    fixes_json = json.dumps([f.model_dump() for f in top_3])
    details_json = json.dumps({
        "checks": checks_summary,
        "wifi": wifi_info,
        "ports": port_results,
        "admin": admin_info,
        "dns": dns_info,
        "deductions": deductions
    })
    
    # Save to scan history & audit log
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO scan_history (user_id, gateway_ip, score, status_verdict, wifi_type, admin_status, open_ports_json, dns_servers_json, fixes_json, details_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, target, score, verdict, wifi_info["auth_type"],
            "default_detected" if admin_info["default_login_detected"] else "custom",
            json.dumps(open_port_names), json.dumps(dns_ips), fixes_json, details_json
        ))
        scan_id = cursor.lastrowid
        
        cursor.execute("""
        INSERT INTO audit_log (user_id, action, target_ip, status, message)
        VALUES (?, 'ROUTER_SCAN', ?, 'COMPLETED', ?)
        """, (user_id, target, f"Score: {score}/100, Verdict: {verdict}"))
        
    return {
        "id": scan_id,
        "gateway_ip": target,
        "score": score,
        "verdict": verdict,
        "checks": checks_summary,
        "top_3_fixes": [f.model_dump() for f in top_3],
        "all_fixes": [f.model_dump() for f in all_fixes],
        "details": {
            "wifi": wifi_info,
            "admin": admin_info,
            "open_ports": open_port_names,
            "dns": dns_info
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@router.get("/latest")
async def get_latest_scan(request: Request):
    user = await get_current_user_optional(request)
    user_id = int(user["sub"]) if user else 1
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM scan_history WHERE user_id = ? ORDER BY id DESC LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        
    if not row:
        return {"has_scan": False}
        
    fixes = json.loads(row["fixes_json"]) if row["fixes_json"] else []
    details = json.loads(row["details_json"]) if row["details_json"] else {}
    
    return {
        "has_scan": True,
        "id": row["id"],
        "gateway_ip": row["gateway_ip"],
        "score": row["score"],
        "verdict": row["status_verdict"],
        "checks": details.get("checks", {}),
        "top_3_fixes": fixes,
        "timestamp": row["timestamp"]
    }

@router.get("/history")
async def get_scan_history(request: Request):
    user = await get_current_user_optional(request)
    user_id = int(user["sub"]) if user else 1
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, timestamp, gateway_ip, score, status_verdict, wifi_type
        FROM scan_history WHERE user_id = ? ORDER BY id DESC LIMIT 20
        """, (user_id,))
        rows = cursor.fetchall()
        
    return {"history": [dict(r) for r in rows]}
