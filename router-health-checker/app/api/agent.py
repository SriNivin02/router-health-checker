"""
app/api/agent.py – AI Agent chat endpoint with streaming
"""
from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import _get_current_user
from app.agent.llm import stream_llm_response
from app.agent.prompts import get_refusal, is_harmful_query
from app.db.models import ChatMessage, ScanResult, User
from app.db.session import get_db
from app.security.csrf import require_csrf
from app.security.ratelimit import rate_limit_dependency

router = APIRouter(prefix="/api/agent", tags=["agent"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="en", max_length=10)
    history: list[dict] = Field(default_factory=list, max_length=20)


@router.post(
    "/chat",
    dependencies=[
        Depends(require_csrf),
        Depends(rate_limit_dependency("ai", "20/minute")),
    ],
)
async def chat(
    body: ChatRequest,
    request: Request,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    """Stream an AI chat response."""

    # Safety check
    if is_harmful_query(body.message):
        refusal = get_refusal(body.language)
        async def _refusal_gen():
            yield f"data: {json.dumps({'chunk': refusal})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(_refusal_gen(), media_type="text/event-stream")

    # Get latest scan context for personalisation
    latest_scan = (
        db.query(ScanResult)
        .filter(ScanResult.user_id == current_user.id)
        .order_by(ScanResult.created_at.desc())
        .first()
    )
    scan_context = ""
    if latest_scan:
        label = (
            "Excellent" if latest_scan.score >= 90 else
            "Good" if latest_scan.score >= 75 else
            "Needs attention" if latest_scan.score >= 50 else
            "Risky"
        )
        scan_context = (
            f"User's latest scan: score={latest_scan.score}/100 ({label}), "
            f"wifi_security={latest_scan.wifi_security}, "
            f"telnet_open={latest_scan.telnet_open}, "
            f"wps_detected={latest_scan.wps_detected}."
        )

    # Build message history (limit to last 10)
    history = body.history[-10:] if body.history else []
    messages = history + [{"role": "user", "content": body.message}]

    # Save user message
    db.add(ChatMessage(
        user_id=current_user.id,
        role="user",
        content=body.message,
        language=body.language,
    ))
    db.commit()

    full_response: list[str] = []

    async def _stream():
        async for chunk in stream_llm_response(messages, lang=body.language, scan_context=scan_context):
            full_response.append(chunk)
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: [DONE]\n\n"

        # Save assistant message after streaming
        db.add(ChatMessage(
            user_id=current_user.id,
            role="assistant",
            content="".join(full_response),
            language=body.language,
        ))
        db.commit()

    return StreamingResponse(_stream(), media_type="text/event-stream")


@router.get("/history")
async def chat_history(
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )
    return {
        "ok": True,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
                "thumbs_up": m.thumbs_up,
            }
            for m in rows
        ],
    }


@router.delete(
    "/history",
    dependencies=[Depends(require_csrf)],
)
async def clear_chat_history(
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id).delete()
    db.commit()
    return {"ok": True, "code": "CHAT_CLEARED"}


class FeedbackRequest(BaseModel):
    message_id: str = Field(max_length=36)
    thumbs_up: bool


@router.post(
    "/feedback",
    dependencies=[Depends(require_csrf)],
)
async def feedback(
    body: FeedbackRequest,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    msg = db.query(ChatMessage).filter(
        ChatMessage.id == body.message_id,
        ChatMessage.user_id == current_user.id,
    ).first()
    if msg:
        msg.thumbs_up = body.thumbs_up
        db.commit()
    return {"ok": True}
