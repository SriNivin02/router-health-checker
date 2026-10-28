"""Pydantic request/response models and schema definitions."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=8, max_length=128)
    security_question: Optional[str] = "What is your favorite router brand?"
    security_answer: Optional[str] = Field(None, min_length=2, max_length=128)

class UserLoginRequest(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    username: str
    security_answer: str
    new_password: str = Field(..., min_length=8)

class ConsentRequest(BaseModel):
    consent: bool

class DeviceItem(BaseModel):
    ip: str
    mac: str
    vendor: str
    device_type: str  # phone, laptop, tv, printer, unknown
    nickname: str
    is_online: bool = True
    latency_ms: float = 0.0
    jitter_ms: float = 0.0
    packet_loss_pct: float = 0.0
    stability_score: int = 100
    is_new: bool = False

class ScanStartRequest(BaseModel):
    target_ip: Optional[str] = None
    test_default_credentials: bool = False

class FixItem(BaseModel):
    id: str
    title_code: str
    desc_code: str
    gain: int
    estimated_time: str
    svg_icon: str
    steps_code: List[str]

class ScanResultResponse(BaseModel):
    id: Optional[int] = None
    gateway_ip: str
    score: int
    verdict: str  # excellent, good, fair, risky
    checks: Dict[str, Any]
    top_3_fixes: List[FixItem]
    all_fixes: List[FixItem]
    timestamp: str

class SpeedRecord(BaseModel):
    download_mbps: float
    upload_mbps: float
    ping_ms: float
    jitter_ms: float
    verdict: str
    timestamp: str

class ChatMessageRequest(BaseModel):
    message: str
    language: str = "en"
    client_context: Optional[Dict[str, Any]] = None

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    is_helpful: bool
    notes: Optional[str] = None
