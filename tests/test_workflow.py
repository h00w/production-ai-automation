from src.models import RequestInput
from src.workflow import run_workflow
from src.adapters import MockBusinessTools
from pydantic import ValidationError
import pytest


@pytest.mark.parametrize("age", [float("nan"), float("inf"), -1, True, "2", None])
def test_invalid_purchase_age_never_creates_refund(age):
    class InvalidAgeTools(MockBusinessTools):
        def lookup_order(self, order_id):
            return {"found": True, "order_id": order_id, "days_since_purchase": age}

        def propose_refund(self, order_id, amount_usd):
            raise AssertionError("invalid purchase age must never reach refund proposal")

    req = RequestInput(request_id="invalid-age", text="Refund my order", order_id="ORD-1000", amount_usd=10)
    result = run_workflow(req, tools=InvalidAgeTools())
    assert result.status == "needs_human_review"
    assert result.requires_human_approval
    assert "refund_age_invalid" in result.checks


def test_sales_lead_is_automated():
    req = RequestInput(
        request_id="t1",
        text="We want a demo and pricing for our company.",
    )
    result = run_workflow(req)
    assert result.status == "completed"
    assert result.automated is True
    assert result.requires_human_approval is False


@pytest.mark.parametrize("overrides", [
    {"order_id": "OTHER"}, {"amount_usd": 11}, {"amount_usd": True},
    {"amount_usd": "10"}, {"amount_usd": None}, {"amount_usd": float("nan")},
    {"state": "committed"}, {"state": None},
])
@pytest.mark.parametrize("amount", [10, 500])
def test_mismatched_refund_proposal_requires_review(overrides, amount):
    class InvalidProposalTools(MockBusinessTools):
        def lookup_order(self, order_id):
            return {"found": True, "order_id": order_id, "days_since_purchase": 1}

        def propose_refund(self, order_id, amount_usd):
            return {**super().propose_refund(order_id, amount_usd), **overrides}

    req = RequestInput(request_id="proposal", text="Refund my order", order_id="ORD-1000", amount_usd=amount)
    result = run_workflow(req, InvalidProposalTools())
    assert result.status == "needs_human_review"
    assert result.automated is False
    assert result.requires_human_approval is True
    assert result.tool_result.success is False
    assert "refund_proposal_mismatch" in result.checks


def test_high_value_refund_requires_approval_when_policy_allows():
    # We search a small set of deterministic IDs until one is within the demo window.
    candidate = None
    for i in range(1000, 1100):
        req = RequestInput(
            request_id="t2",
            text="I want a refund",
            order_id=f"ORD-{i}",
            amount_usd=500,
        )
        result = run_workflow(req)
        if result.status == "awaiting_approval":
            candidate = result
            break
    assert candidate is not None
    assert candidate.requires_human_approval is True
    assert candidate.automated is False


def test_missing_order_id_requests_more_information():
    req = RequestInput(
        request_id="t3",
        text="Where is my order?",
    )
    result = run_workflow(req)
    assert result.status == "needs_more_information"
    assert result.automated is False


def test_mismatched_order_lookup_requires_review_before_refund():
    class WrongOrderTools(MockBusinessTools):
        def lookup_order(self, order_id):
            return {"found": True, "order_id": "ORD-DIFFERENT", "status": "delivered", "days_since_purchase": 1}

        def propose_refund(self, order_id, amount_usd):
            raise AssertionError("mismatched order must never reach refund proposal")

    req = RequestInput(request_id="mismatch", text="Refund my order", order_id="ORD-1000", amount_usd=10)
    result = run_workflow(req, tools=WrongOrderTools())
    assert result.status == "needs_human_review"
    assert result.requires_human_approval
    assert "order_identity_mismatch" in result.checks


def test_refund_without_amount_never_creates_proposal():
    req = RequestInput(request_id="t-missing-amount", text="Refund my order", order_id="ORD-1000")
    result = run_workflow(req)
    assert result.status == "needs_more_information"
    assert result.automated is False
    assert result.tool_result is not None
    assert result.tool_result.tool == "lookup_order"
    assert "refund_amount_missing" in result.checks


def test_zero_refund_never_creates_proposal():
    req = RequestInput(request_id="t-zero", text="Refund my order", order_id="ORD-1000", amount_usd=0)
    result = run_workflow(req)
    assert result.status == "needs_more_information"
    assert result.tool_result.tool == "lookup_order"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_refund_amount_is_rejected(value):
    with pytest.raises(ValidationError):
        RequestInput(request_id="t-invalid", text="Refund my order", amount_usd=value)


def test_ambiguous_request_routes_safely():
    req = RequestInput(
        request_id="t4",
        text="Hello, I have a question.",
    )
    result = run_workflow(req)
    assert result.requires_human_approval is True
    assert result.automated is False
