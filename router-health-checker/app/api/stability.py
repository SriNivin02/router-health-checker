"""
app/api/stability.py – Network stability (device discovery + metrics) endpoints
"""
from __future__ import annotations

import asyncio
import csv
import io
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import _get_current_user
from app.config import get_settings
from app.db.models import KnownDevice, StabilityResult, User
from app.db.session import get_db
from app.scanner.gateway import detect_gateway, validate_target
from app.security.csrf import require_csrf
from app.security.ratelimit import rate_limit_dependency
from app.stability.discovery import discover_devices
from app.stability.metrics import measure_device

settings = get_settings()
router = APIRouter(prefix="/api/stability", tags=["stability"])


class NicknameRequest(BaseModel):
    ip: str = Field(max_length=45)
    mac: Optional[str] = Field(None, max_length=17)
    nickname: Optional[str] = Field(None, max_length=64)
    is_mine: Optional[bool] = None


@router.post(
    "/run",
    dependencies=[
        Depends(require_csrf),
        Depends(rate_limit_dependency("stability", "2/minute")),
    ],
)
async def run_stability(
    request: Request,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    """Discover devices and measure their stability."""
    gateway = detect_gateway()
    if not gateway:
        raise HTTPException(status_code=400, detail={"code": "GATEWAY_NOT_FOUND"})

    ok, err = validate_target(gateway)
    if not ok:
        raise HTTPException(status_code=400, detail={"code": err})

    devices = await discover_devices(gateway)
    if not devices:
        return {"ok": True, "devices": [], "network_score": 100}

    # Get known devices for this user
    known_macs = {
        kd.mac_address: kd
        for kd in db.query(KnownDevice).filter(KnownDevice.user_id == current_user.id).all()
    }

    results = []
    metric_tasks = [measure_device(d.ip, count=5) for d in devices if d.is_reachable]
    metrics_list = await asyncio.gather(*metric_tasks, return_exceptions=True)

    metrics_map: dict[str, object] = {}
    for m in metrics_list:
        if not isinstance(m, Exception):
            metrics_map[m.ip] = m

    for device in devices:
        metrics = metrics_map.get(device.ip)
        raw_mac = (device.mac or "").replace("XX:XX:XX", "")[:8].upper()
        known = known_macs.get(raw_mac)
        is_new = known is None and device.is_reachable

        row = StabilityResult(
            user_id=current_user.id,
            device_ip=device.ip,
            device_mac=device.mac,
            device_vendor=device.vendor,
            nickname=known.nickname if known else None,
            latency_ms=metrics.latency_ms if metrics else None,
            jitter_ms=metrics.jitter_ms if metrics else None,
            packet_loss_pct=metrics.packet_loss_pct if metrics else None,
            stability_score=metrics.stability_score if metrics else None,
            is_new=is_new,
        )
        db.add(row)

        results.append({
            "ip": device.ip,
            "mac": device.mac,
            "vendor": device.vendor,
            "nickname": known.nickname if known else None,
            "is_new": is_new,
            "is_mine": known.is_mine if known else None,
            "latency_ms": metrics.latency_ms if metrics else None,
            "jitter_ms": metrics.jitter_ms if metrics else None,
            "packet_loss_pct": metrics.packet_loss_pct if metrics else None,
            "stability_score": metrics.stability_score if metrics else None,
        })

    db.commit()

    scored = [r for r in results if r["stability_score"] is not None]
    network_score = int(sum(r["stability_score"] for r in scored) / len(scored)) if scored else 100

    return {
        "ok": True,
        "gateway_ip": gateway,
        "devices": results,
        "network_score": network_score,
    }


@router.get("/history")
async def stability_history(
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 100,
    device_ip: Optional[str] = None,
):
    query = db.query(StabilityResult).filter(StabilityResult.user_id == current_user.id)
    if device_ip:
        query = query.filter(StabilityResult.device_ip == device_ip)
    rows = query.order_by(StabilityResult.created_at.desc()).limit(limit).all()
    return {
        "ok": True,
        "history": [
            {
                "id": r.id,
                "created_at": r.created_at.isoformat(),
                "device_ip": r.device_ip,
                "device_mac": r.device_mac,
                "device_vendor": r.device_vendor,
                "nickname": r.nickname,
                "latency_ms": r.latency_ms,
                "jitter_ms": r.jitter_ms,
                "packet_loss_pct": r.packet_loss_pct,
                "stability_score": r.stability_score,
            }
            for r in rows
        ],
    }


@router.get("/export-csv")
async def export_csv(
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(StabilityResult)
        .filter(StabilityResult.user_id == current_user.id)
        .order_by(StabilityResult.created_at.desc())
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "IP", "MAC", "Vendor", "Nickname", "Latency(ms)", "Jitter(ms)", "Loss(%)", "Score"])
    for r in rows:
        writer.writerow([
            r.created_at.isoformat(), r.device_ip, r.device_mac, r.device_vendor,
            r.nickname, r.latency_ms, r.jitter_ms, r.packet_loss_pct, r.stability_score
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=stability_history.csv"},
    )


@router.post(
    "/nickname",
    dependencies=[Depends(require_csrf)],
)
async def set_nickname(
    body: NicknameRequest,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    mac_key = (body.mac or body.ip)[:17]
    existing = db.query(KnownDevice).filter(
        KnownDevice.user_id == current_user.id,
        KnownDevice.mac_address == mac_key,
    ).first()

    if existing:
        if body.nickname is not None:
            existing.nickname = body.nickname
        if body.is_mine is not None:
            existing.is_mine = body.is_mine
        existing.last_seen = datetime.utcnow()
    else:
        db.add(KnownDevice(
            user_id=current_user.id,
            mac_address=mac_key,
            nickname=body.nickname,
            is_mine=body.is_mine,
        ))
    db.commit()
    return {"ok": True, "code": "NICKNAME_SAVED"}
