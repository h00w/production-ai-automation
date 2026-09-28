from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field


class LeadTemperature(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class AutomationDecision(str, Enum):
    AUTO_ROUTE = "auto_route"
    HUMAN_REVIEW = "human_review"
    RESEARCH_MORE = "research_more"
    NURTURE = "nurture"
    REJECT = "reject"


class LeadInput(BaseModel):
    lead_id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    company: str = Field(min_length=1, max_length=300)
    role: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=50)
    message: str = Field(default="", max_length=4000)
    source: str = Field(default="unknown", max_length=100)
    consent_to_contact: bool = False


class LeadQualification(BaseModel):
    icp_fit: int = Field(ge=0, le=100)
    intent: int = Field(ge=0, le=100)
    urgency: int = Field(ge=0, le=100)
    technical_fit: int = Field(ge=0, le=100)
    commercial_fit: int = Field(ge=0, le=100)
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    temperature: LeadTemperature
    evidence: List[str] = Field(default_factory=list, max_length=20)
    risk_flags: List[str] = Field(default_factory=list, max_length=20)
    recommended_action: str = Field(min_length=1, max_length=200)
    model_provider: str = "unknown"
    model_name: str = "unknown"
    prompt_version: str = "unknown"


class PolicyDecision(BaseModel):
    decision: AutomationDecision
    reason: str
    requires_human_approval: bool
    can_contact: bool
    policy_version: str


class EventEnvelope(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid4().hex}")
    event_type: str
    schema_version: str = "1.0"
    workflow_version: str = "1.0.0"
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid4().hex}")
    idempotency_key: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowAuditRecord(BaseModel):
    correlation_id: str
    event_id: str
    state: str
    outcome: str
    automated: bool
    policy_version: str
    latency_ms: Optional[int] = Field(default=None, ge=0)
    provider_cost_usd: Optional[float] = Field(default=None, ge=0)
    retry_count: int = Field(default=0, ge=0)
    error_code: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
