"""LLM proxy module with offline fallback."""
import requests
from typing import Dict, Any, Optional
from app.config import settings
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.kb import kb

def query_agent(
    message: str,
    language: str = "en",
    client_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Two-layer architecture:
    1. Online LLM proxy (if enabled in .env and API key present)
    2. Instant offline knowledge base fallback
    """
    # Check if online LLM is enabled and configured
    if settings.LLM_ENABLED and settings.LLM_API_KEY:
        try:
            sys_prompt = SYSTEM_PROMPT.format(language=language)
            if client_context and "latest_score" in client_context:
                sys_prompt += f"\nUser's latest router score: {client_context['latest_score']}/100."

            headers = {
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "Content-Type": "application/json"
            }
            body = {
                "model": settings.LLM_MODEL,
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.4,
                "max_tokens": 400
            }
            resp = requests.post(
                f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions",
                headers=headers,
                json=body,
                timeout=5.0
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return {
                    "source": "online_llm",
                    "answer": content,
                    "language": language
                }
        except Exception:
            pass  # Seamlessly fall back to offline knowledge base

    # Fallback to local offline knowledge base
    kb_result = kb.search(message, lang=language)
    return {
        "source": "offline_kb",
        "answer": kb_result["answer"],
        "id": kb_result.get("id"),
        "confidence": kb_result.get("confidence", 1.0),
        "language": language
    }
