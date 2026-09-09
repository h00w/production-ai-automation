from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class Intent(str, Enum):
    REFUND = "refund"
    ORDER_STATUS = "order_status"
    TECHNICAL_SUPPORT = "technical_support"
    SALES_LEAD = "sales_lead"
    BILLING = "billing"
    GENERAL = "general"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RequestInput(BaseModel):
    request_id: str
    text: str = Field(min_length=3, max_length=4000)
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    amount_usd: Optional[float] = Field(default=None, ge=0)


class Classification(BaseModel):
    intent: Intent
    confidence: float = Field(ge=0, le=1)
    risk: RiskLevel
    extracted: Dict[str, Any] = Field(default_factory=dict)
    rationale: str


class ToolResult(BaseModel):
    tool: str
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class WorkflowResult(BaseModel):
    request_id: str
    intent: Intent
    status: str
    automated: bool
    requires_human_approval: bool
    proposed_action: str
    final_message: str
    tool_result: Optional[ToolResult] = None
    checks: List[str] = Field(default_factory=list)
    trace: List[str] = Field(default_factory=list)
