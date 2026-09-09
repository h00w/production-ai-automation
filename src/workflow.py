from __future__ import annotations
import re
from typing import Tuple

from .models import (
    RequestInput,
    Classification,
    Intent,
    RiskLevel,
    ToolResult,
    WorkflowResult,
)
from .adapters import MockBusinessTools


HIGH_RISK_REFUND_USD = 250.0


def classify_request(req: RequestInput) -> Classification:
    """Deterministic classifier used for reviewer-friendly execution.

    In a production implementation this function can be replaced with an LLM
    that returns the same validated Classification schema.
    """
    text = req.text.lower()

    if any(k in text for k in ["refund", "money back", "return"]):
        intent = Intent.REFUND
        confidence = 0.94
    elif any(k in text for k in ["where is my order", "not arrived", "delivery", "shipment", "tracking"]):
        intent = Intent.ORDER_STATUS
        confidence = 0.91
    elif any(k in text for k in ["error", "broken", "not working", "technical", "bug"]):
        intent = Intent.TECHNICAL_SUPPORT
        confidence = 0.89
    elif any(k in text for k in ["demo", "quote", "pricing", "sales", "buy", "purchase for my company"]):
        intent = Intent.SALES_LEAD
        confidence = 0.87
    elif any(k in text for k in ["invoice", "billing", "charged", "payment"]):
        intent = Intent.BILLING
        confidence = 0.90
    else:
        intent = Intent.GENERAL
        confidence = 0.72

    risk = RiskLevel.LOW
    if intent == Intent.REFUND:
        risk = RiskLevel.HIGH if (req.amount_usd or 0) >= HIGH_RISK_REFUND_USD else RiskLevel.MEDIUM
    elif intent in {Intent.BILLING, Intent.TECHNICAL_SUPPORT}:
        risk = RiskLevel.MEDIUM

    extracted = {}
    order_match = re.search(r"\b(?:order|#)\s*([A-Z0-9-]{4,})\b", req.text, flags=re.I)
    if order_match and not req.order_id:
        extracted["order_id"] = order_match.group(1)

    return Classification(
        intent=intent,
        confidence=confidence,
        risk=risk,
        extracted=extracted,
        rationale=f"Matched request to {intent.value}; risk set to {risk.value} using deterministic business rules.",
    )


def _resolve_order_id(req: RequestInput, cls: Classification) -> str | None:
    return req.order_id or cls.extracted.get("order_id")


def run_workflow(req: RequestInput, tools: MockBusinessTools | None = None) -> WorkflowResult:
    tools = tools or MockBusinessTools()
    trace = ["input_validated"]

    cls = classify_request(req)
    trace.append(f"classified:{cls.intent.value}:{cls.confidence:.2f}")
    checks = ["request_schema_valid", "classification_schema_valid"]

    if cls.confidence < 0.75:
        trace.append("low_confidence_escalation")
        return WorkflowResult(
            request_id=req.request_id,
            intent=cls.intent,
            status="needs_human_review",
            automated=False,
            requires_human_approval=True,
            proposed_action="Ask a human operator to classify and resolve the request.",
            final_message="The request is ambiguous and has been routed for human review.",
            checks=checks + ["confidence_below_threshold"],
            trace=trace,
        )

    if cls.intent in {Intent.ORDER_STATUS, Intent.REFUND}:
        order_id = _resolve_order_id(req, cls)
        order = tools.lookup_order(order_id)
        trace.append("tool:lookup_order")
        tool_result = ToolResult(tool="lookup_order", success=order.get("found", False), data=order)

        if not order.get("found"):
            trace.append("missing_order_escalation")
            return WorkflowResult(
                request_id=req.request_id,
                intent=cls.intent,
                status="needs_more_information",
                automated=False,
                requires_human_approval=False,
                proposed_action="Request a valid order ID.",
                final_message="Please provide the order ID so the request can be processed.",
                tool_result=tool_result,
                checks=checks + ["order_lookup_failed"],
                trace=trace,
            )

        checks.append("order_exists")

        if cls.intent == Intent.ORDER_STATUS:
            return WorkflowResult(
                request_id=req.request_id,
                intent=cls.intent,
                status="completed",
                automated=True,
                requires_human_approval=False,
                proposed_action="Return current order status.",
                final_message=f"Order {order_id} is currently {order['status']}.",
                tool_result=tool_result,
                checks=checks + ["read_only_action"],
                trace=trace + ["completed"],
            )

        # Refund workflow
        if order["days_since_purchase"] > 30:
            trace.append("refund_policy_block")
            return WorkflowResult(
                request_id=req.request_id,
                intent=cls.intent,
                status="policy_blocked",
                automated=False,
                requires_human_approval=True,
                proposed_action="Escalate because the synthetic demo refund window is 30 days.",
                final_message="The refund request requires human review because it falls outside the configured policy window.",
                tool_result=tool_result,
                checks=checks + ["refund_window_check_failed"],
                trace=trace,
            )

        proposal = tools.propose_refund(order_id, req.amount_usd)
        trace.append("tool:propose_refund")
        tool_result = ToolResult(tool="propose_refund", success=True, data=proposal)

        requires_approval = cls.risk == RiskLevel.HIGH
        if requires_approval:
            trace.append("high_value_human_approval")
            return WorkflowResult(
                request_id=req.request_id,
                intent=cls.intent,
                status="awaiting_approval",
                automated=False,
                requires_human_approval=True,
                proposed_action="Refund proposal created; human approval required before commit.",
                final_message="A refund proposal was prepared and routed for approval.",
                tool_result=tool_result,
                checks=checks + ["refund_window_valid", "high_value_approval_gate"],
                trace=trace,
            )

        return WorkflowResult(
            request_id=req.request_id,
            intent=cls.intent,
            status="completed",
            automated=True,
            requires_human_approval=False,
            proposed_action="Low-risk refund proposal accepted by demo policy.",
            final_message="The refund request passed the configured demo checks.",
            tool_result=tool_result,
            checks=checks + ["refund_window_valid", "amount_below_approval_threshold"],
            trace=trace + ["completed"],
        )

    if cls.intent == Intent.SALES_LEAD:
        lead = tools.create_sales_lead(req.text)
        trace.append("tool:create_sales_lead")
        return WorkflowResult(
            request_id=req.request_id,
            intent=cls.intent,
            status="completed",
            automated=True,
            requires_human_approval=False,
            proposed_action="Create a qualified lead record.",
            final_message=f"Lead {lead['lead_id']} created for sales follow-up.",
            tool_result=ToolResult(tool="create_sales_lead", success=True, data=lead),
            checks=checks + ["crm_payload_valid"],
            trace=trace + ["completed"],
        )

    if cls.intent in {Intent.TECHNICAL_SUPPORT, Intent.BILLING}:
        ticket = tools.create_support_ticket(cls.intent.value, req.text[:240])
        trace.append("tool:create_support_ticket")
        return WorkflowResult(
            request_id=req.request_id,
            intent=cls.intent,
            status="completed",
            automated=True,
            requires_human_approval=False,
            proposed_action="Create a routed support ticket.",
            final_message=f"Support ticket {ticket['ticket_id']} created.",
            tool_result=ToolResult(tool="create_support_ticket", success=True, data=ticket),
            checks=checks + ["ticket_payload_valid"],
            trace=trace + ["completed"],
        )

    trace.append("general_human_route")
    return WorkflowResult(
        request_id=req.request_id,
        intent=cls.intent,
        status="needs_human_review",
        automated=False,
        requires_human_approval=True,
        proposed_action="Route general/ambiguous request to a human operator.",
        final_message="The request has been routed for human review.",
        checks=checks + ["safe_default_route"],
        trace=trace,
    )
