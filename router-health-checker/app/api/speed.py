"""
app/api/speed.py – Speed test history persistence
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import _get_current_user
from app.db.models import SpeedResult, User
from app.db.session import get_db
from app.security.csrf import require_csrf

router = APIRouter(prefix="/api/speed-history", tags=["speed"])


class SpeedResultRequest(BaseModel):
    download_mbps: float = Field(ge=0, le=10000)
    upload_mbps: float = Field(ge=0, le=10000)
    ping_ms: float = Field(ge=0, le=10000)
    jitter_ms: float = Field(ge=0, le=10000)
    mode: str = Field(default="local", max_length=20)


@router.post(
    "/save",
    dependencies=[Depends(require_csrf)],
)
async def save_speed_result(
    body: SpeedResultRequest,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    row = SpeedResult(
        user_id=current_user.id,
        download_mbps=body.download_mbps,
        upload_mbps=body.upload_mbps,
        ping_ms=body.ping_ms,
        jitter_ms=body.jitter_ms,
        mode=body.mode,
    )
    db.add(row)
    db.commit()
    return {"ok": True, "id": row.id}


@router.get("/")
async def speed_history(
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 30,
):
    rows = (
        db.query(SpeedResult)
        .filter(SpeedResult.user_id == current_user.id)
        .order_by(SpeedResult.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "ok": True,
        "history": [
            {
                "id": r.id,
                "created_at": r.created_at.isoformat(),
                "download_mbps": r.download_mbps,
                "upload_mbps": r.upload_mbps,
                "ping_ms": r.ping_ms,
                "jitter_ms": r.jitter_ms,
                "mode": r.mode,
            }
            for r in rows
        ],
    }
