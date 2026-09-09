from src.models import RequestInput
from src.workflow import run_workflow


def test_sales_lead_is_automated():
    req = RequestInput(
        request_id="t1",
        text="We want a demo and pricing for our company.",
    )
    result = run_workflow(req)
    assert result.status == "completed"
    assert result.automated is True
    assert result.requires_human_approval is False


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


def test_ambiguous_request_routes_safely():
    req = RequestInput(
        request_id="t4",
        text="Hello, I have a question.",
    )
    result = run_workflow(req)
    assert result.requires_human_approval is True
    assert result.automated is False
