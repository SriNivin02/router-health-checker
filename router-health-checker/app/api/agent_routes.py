"""AI agent conversational endpoints."""
from fastapi import APIRouter, Request, HTTPException
from app.db.models import ChatMessageRequest, FeedbackRequest
from app.db.session import get_db
from app.security.auth import get_current_user_optional
from app.security.ratelimit import check_rate_limit
from app.agent.llm import query_agent
from app.config import settings

router = APIRouter(prefix="/api/agent", tags=["agent"])

@router.post("/chat")
async def chat_with_agent(req: ChatMessageRequest, request: Request):
    check_rate_limit(request, 60, "agent_chat")
    
    user = await get_current_user_optional(request)
    user_id = int(user["sub"]) if user else 1
    
    # Enrich context with latest scan score if available
    context = req.client_context or {}
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT score FROM scan_history WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
        row = cursor.fetchone()
        if row:
            context["latest_score"] = row["score"]
            
    res = query_agent(
        message=req.message,
        language=req.language,
        client_context=context
    )
    return res

@router.post("/feedback")
async def record_feedback(req: FeedbackRequest, request: Request):
    user = await get_current_user_optional(request)
    user_id = int(user["sub"]) if user else 1
    
    with get_db() as conn:
        conn.execute("""
        INSERT INTO ai_feedback (user_id, question, answer, is_helpful, notes)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, req.question, req.answer, 1 if req.is_helpful else 0, req.notes))
        
    return {"status": "saved"}
