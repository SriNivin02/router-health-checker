"""Offline knowledge base fuzzy search engine."""
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import settings
from app.agent.prompts import SAFE_REFUSAL_TEMPLATES

# Project root = the folder that contains "app/" (this file is app/agent/kb.py).
# Use settings.BASE_DIR when it exists, otherwise derive it from this file's location.
_BASE_DIR = Path(getattr(settings, "BASE_DIR", Path(__file__).resolve().parents[2]))


def _find_kb_path() -> Path:
    """Return the first location where knowledge/qa.json exists."""
    candidates = [
        _BASE_DIR / "knowledge" / "qa.json",
        _BASE_DIR / "app" / "knowledge" / "qa.json",
    ]
    data_dir = getattr(settings, "DATA_DIR", None)
    if data_dir:
        candidates.append(Path(data_dir) / "knowledge" / "qa.json")
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


KB_PATH = _find_kb_path()

class KnowledgeBase:
    def __init__(self):
        self.entries = []
        self.load_data()

    def load_data(self):
        if KB_PATH.exists():
            try:
                with open(KB_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.entries = data.get("entries", [])
            except Exception:
                self.entries = []

    def check_harmful_intent(self, query: str) -> bool:
        """Detect illegal hacking requests (cracking neighbour's Wi-Fi, bypassing)."""
        ql = query.lower()
        patterns = [
            r"\b(crack|hack|break|steal)\b.*\b(neighbor|neighbour|someone|other|external)\b",
            r"\b(bypass|exploit|attack)\b.*\b(router|login|password)\b",
            r"\b(how to hack|crack wifi password)\b"
        ]
        return any(re.search(p, ql) for p in patterns)

    def search(self, query: str, lang: str = "en") -> Dict[str, Any]:
        """Fuzzy match user query against offline Q&A database."""
        # 1. Harmful intent filter
        if self.check_harmful_intent(query):
            refusal = SAFE_REFUSAL_TEMPLATES.get(lang, SAFE_REFUSAL_TEMPLATES["en"])
            return {
                "matched": True,
                "confidence": 1.0,
                "answer": refusal,
                "id": "SAFE_REFUSAL"
            }

        if not self.entries:
            self.load_data()

        clean_words = set(re.findall(r"\w+", query.lower()))
        best_entry = None
        best_score = 0

        for entry in self.entries:
            score = 0
            # Keyword weight
            for kw in entry.get("keywords", []):
                kw_clean = kw.lower()
                if kw_clean in query.lower():
                    score += 5
                for w in kw_clean.split():
                    if w in clean_words:
                        score += 2

            # Question words weight
            q_words = set(re.findall(r"\w+", entry.get("question", "").lower()))
            common = clean_words.intersection(q_words)
            score += len(common) * 1.5

            if score > best_score:
                best_score = score
                best_entry = entry

        if best_entry and best_score >= 3:
            return {
                "matched": True,
                "confidence": min(1.0, best_score / 15.0),
                "question": best_entry["question"],
                "answer": best_entry["answer"],
                "id": best_entry.get("id")
            }

        # Fallback friendly response
        default_reply = (
            "🛡️ That is a great question about Wi-Fi security! You can run the Router Check "
            "to inspect open ports, WPS, and your admin password. "
            "Try asking me: 'What is WPS?', 'How to change admin password?', or 'Why is Wi-Fi slow?' 🔑"
        )
        return {
            "matched": False,
            "confidence": 0.0,
            "answer": default_reply,
            "id": "KB_FALLBACK"
        }

kb = KnowledgeBase()