"""
app/api/scanner.py – Router health scan endpoint
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.api.auth import _get_client_ip, _get_current_user
from app.config import get_settings
from app.db.models import ScanResult, User
from app.db.session import get_db
from app.scanner.admin_page import check_admin_page
from app.scanner.dns import check_dns
from app.scanner.gateway import detect_gateway, validate_target
from app.scanner.ports import scan_ports
from app.scanner.scoring import compute_score
from app.scanner.wifi import detect_wifi
from app.security.auth import audit
from app.security.csrf import require_csrf
from app.security.ratelimit import rate_limit_dependency

settings = get_settings()
router = APIRouter(prefix="/api/scan", tags=["scanner"])

# Per-user scan cooldown tracking (in-memory)
_last_scan_times: dict[str, float] = {}


class ScanRequest(BaseModel):
    gateway_ip: Optional[str] = Field(None, max_length=45)
    test_default_creds: bool = False
    wifi_security_manual: Optional[str] = Field(None, max_length=10)
    wps_manual: Optional[bool] = None

    @field_validator("gateway_ip")
    @classmethod
    def _validate_ip(cls, v):
        if v is not None:
            ok, err = validate_target(v)
            if not ok:
                raise ValueError(err)
        return v


@router.get("/gateway")
async def get_gateway(
    current_user: User = Depends(_get_current_user),
):
    """Auto-detect the default gateway IP."""
    gw = detect_gateway()
    return {"gateway_ip": gw, "detected": gw is not None}


@router.post(
    "/run",
    dependencies=[
        Depends(require_csrf),
        Depends(rate_limit_dependency("scan", "2/minute")),
    ],
)
async def run_scan(
    body: ScanRequest,
    request: Request,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    """Run the full router health scan."""

    # Enforce consent
    if not current_user.consent_given:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "CONSENT_REQUIRED"},
        )

    # Per-user scan cooldown
    last = _last_scan_times.get(current_user.id, 0)
    elapsed = time.monotonic() - last
    if elapsed < settings.scan_min_interval_seconds:
        wait = int(settings.scan_min_interval_seconds - elapsed)
        raise HTTPException(
            status_code=429,
            detail={"code": "SCAN_TOO_FREQUENT", "retry_after": wait},
        )

    # Determine gateway
    gateway = body.gateway_ip or detect_gateway()
    if not gateway:
        raise HTTPException(
            status_code=400,
            detail={"code": "GATEWAY_NOT_FOUND"},
        )

    ok, err = validate_target(gateway)
    if not ok:
        raise HTTPException(status_code=400, detail={"code": err})

    _last_scan_times[current_user.id] = time.monotonic()
    audit(db, "SCAN_STARTED", user_id=current_user.id,
          ip_address=_get_client_ip(request), details=gateway)

    # ── Run all checks concurrently ──────────────────────────────
    timeout = float(settings.scan_timeout_seconds)

    ports_task = asyncio.create_task(scan_ports(gateway, timeout=timeout))
    admin_task = asyncio.create_task(
        check_admin_page(gateway, timeout=timeout, test_default_creds=body.test_default_creds)
    )

    # Wi-Fi and DNS are sync – run in thread pool
    loop = asyncio.get_event_loop()
    wifi_task = loop.run_in_executor(None, detect_wifi)
    dns_task = loop.run_in_executor(None, check_dns, gateway)

    ports_result = await ports_task
    admin_result = await admin_task
    wifi_info = await wifi_task
    dns_result = await dns_task

    # ── Apply manual overrides ───────────────────────────────────
    wifi_security = wifi_info.security
    if body.wifi_security_manual and wifi_info.detection_method == "manual_needed":
        wifi_security = body.wifi_security_manual.upper()

    wps_detected = wifi_info.wps_detected
    if body.wps_manual is not None and wps_detected is None:
        wps_detected = body.wps_manual

    # ── Extract port flags ───────────────────────────────────────
    port_map = {p.service: p.is_open for p in ports_result}
    telnet_open = port_map.get("TELNET", False)
    upnp_open = port_map.get("UPNP", False)
    tr069_open = port_map.get("TR069", False)

    # ── Score ────────────────────────────────────────────────────
    score_result = compute_score(
        wifi_security=wifi_security,
        wps_detected=wps_detected,
        admin_http=admin_result.over_plain_http,
        admin_default_creds=admin_result.default_creds_found if admin_result.creds_tested else None,
        telnet_open=telnet_open,
        upnp_open=upnp_open,
        tr069_open=tr069_open,
        suspicious_dns=bool(dns_result.suspicious_servers),
    )

    # ── Persist ──────────────────────────────────────────────────
    checks_json = json.dumps([
        {"id": c.id, "status": c.status, "points_lost": c.points_lost,
         "message_code": c.message_code, "details": c.details}
        for c in score_result.checks
    ])

    scan_row = ScanResult(
        user_id=current_user.id,
        gateway_ip=gateway,
        score=score_result.score,
        wifi_security=wifi_security,
        wps_detected=wps_detected,
        admin_http=admin_result.over_plain_http,
        admin_default_creds=admin_result.default_creds_found if admin_result.creds_tested else None,
        telnet_open=telnet_open,
        upnp_open=upnp_open,
        tr069_open=tr069_open,
        dns_servers=",".join(dns_result.servers[:5]),
        checks_json=checks_json,
        fixes_json=json.dumps(score_result.top_fixes),
    )
    db.add(scan_row)
    db.commit()

    audit(db, "SCAN_COMPLETE", user_id=current_user.id,
          ip_address=_get_client_ip(request),
          details=f"score={score_result.score}")

    return {
        "ok": True,
        "scan_id": scan_row.id,
        "gateway_ip": gateway,
        "score": score_result.score,
        "label_code": score_result.label_code,
        "checks": checks_json,
        "top_fixes": score_result.top_fixes,
        "wifi": {
            "security": wifi_security,
            "ssid": wifi_info.ssid,
            "wps_detected": wps_detected,
            "detection_method": wifi_info.detection_method,
        },
        "ports": [
            {"port": p.port, "service": p.service, "is_open": p.is_open}
            for p in ports_result
        ],
        "admin": {
            "http_reachable": admin_result.http_reachable,
            "https_reachable": admin_result.https_reachable,
            "over_plain_http": admin_result.over_plain_http,
            "default_creds_found": admin_result.default_creds_found,
            "creds_tested": admin_result.creds_tested,
        },
        "dns": {
            "servers": dns_result.servers,
            "router_is_resolver": dns_result.router_is_resolver,
            "suspicious_servers": dns_result.suspicious_servers,
            "info_codes": dns_result.info_codes,
        },
    }


@router.get("/history")
async def scan_history(
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
):
    rows = (
        db.query(ScanResult)
        .filter(ScanResult.user_id == current_user.id)
        .order_by(ScanResult.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "ok": True,
        "history": [
            {
                "id": r.id,
                "created_at": r.created_at.isoformat(),
                "score": r.score,
                "gateway_ip": r.gateway_ip,
                "label_code": (
                    "EXCELLENT" if r.score >= 90 else
                    "GOOD" if r.score >= 75 else
                    "NEEDS_ATTENTION" if r.score >= 50 else
                    "RISKY"
                ),
            }
            for r in rows
        ],
    }


@router.get("/demo")
async def demo_scan():
    """Return simulated demo data so users can explore the UI without scanning."""
    return {
        "ok": True,
        "is_demo": True,
        "scan_id": "demo-001",
        "gateway_ip": "192.168.1.1",
        "score": 62,
        "label_code": "NEEDS_ATTENTION",
        "checks": json.dumps([
            {"id": "DEFAULT_CREDS", "status": "pass", "points_lost": 0, "message_code": "CHECK_DEFAULT_CREDS_PASS", "details": {}},
            {"id": "TELNET", "status": "fail", "points_lost": 20, "message_code": "CHECK_TELNET_FAIL", "details": {}},
            {"id": "WIFI_OPEN", "status": "pass", "points_lost": 0, "message_code": "CHECK_WIFI_OPEN_PASS", "details": {"security": "WPA2"}},
            {"id": "WIFI_WEP", "status": "pass", "points_lost": 0, "message_code": "CHECK_WIFI_WEP_PASS", "details": {"security": "WPA2"}},
            {"id": "WPS", "status": "fail", "points_lost": 10, "message_code": "CHECK_WPS_FAIL", "details": {}},
            {"id": "ADMIN_HTTP", "status": "fail", "points_lost": 10, "message_code": "CHECK_ADMIN_HTTP_FAIL", "details": {}},
            {"id": "UPNP", "status": "pass", "points_lost": 0, "message_code": "CHECK_UPNP_PASS", "details": {}},
            {"id": "TR069", "status": "pass", "points_lost": 0, "message_code": "CHECK_TR069_PASS", "details": {}},
            {"id": "DNS", "status": "pass", "points_lost": 0, "message_code": "CHECK_DNS_PASS", "details": {}},
        ]),
        "top_fixes": [
            {"check_id": "TELNET", "fix_code": "FIX_TELNET", "points_gain": 20},
            {"check_id": "WPS", "fix_code": "FIX_WPS", "points_gain": 10},
            {"check_id": "ADMIN_HTTP", "fix_code": "FIX_ADMIN_HTTP", "points_gain": 10},
        ],
        "wifi": {"security": "WPA2", "ssid": "HomeDemo_5G", "wps_detected": True, "detection_method": "demo"},
        "ports": [
            {"port": 21, "service": "FTP", "is_open": False},
            {"port": 22, "service": "SSH", "is_open": False},
            {"port": 23, "service": "TELNET", "is_open": True},
            {"port": 53, "service": "DNS", "is_open": True},
            {"port": 80, "service": "HTTP", "is_open": True},
            {"port": 443, "service": "HTTPS", "is_open": False},
            {"port": 8080, "service": "HTTP_ALT", "is_open": False},
            {"port": 7547, "service": "TR069", "is_open": False},
            {"port": 1900, "service": "UPNP", "is_open": False},
        ],
        "admin": {"http_reachable": True, "https_reachable": False, "over_plain_http": True, "default_creds_found": False, "creds_tested": False},
        "dns": {"servers": ["192.168.1.1"], "router_is_resolver": True, "suspicious_servers": [], "info_codes": ["DNS_ROUTER_IS_RESOLVER"]},
    }
