from src.revops_models import LeadInput, LeadQualification, LeadTemperature, AutomationDecision
from src.revops_policy import decide_lead_action


def lead(consent=True):
    return LeadInput(
        lead_id="lead-1",
        name="Jane Doe",
        email="jane@example.com",
        company="Example AB",
        role="VP Engineering",
        message="We need workflow automation for our sales team",
        source="website",
        consent_to_contact=consent,
    )


def qual(score=90, confidence=0.92, risk_flags=None):
    return LeadQualification(
        icp_fit=90,
        intent=85,
        urgency=75,
        technical_fit=90,
        commercial_fit=88,
        score=score,
        confidence=confidence,
        temperature=LeadTemperature.HOT if score >= 80 else LeadTemperature.WARM,
        evidence=["Target segment", "Active buying signal"],
        risk_flags=risk_flags or [],
        recommended_action="assign_account_executive",
        model_provider="mock",
        model_name="deterministic-fixture",
        prompt_version="test-v1",
    )


def test_high_confidence_high_score_auto_routes():
    result = decide_lead_action(lead(), qual())
    assert result.decision == AutomationDecision.AUTO_ROUTE
    assert result.can_contact is True
    assert result.requires_human_approval is False


def test_medium_score_requires_review():
    result = decide_lead_action(lead(), qual(score=72, confidence=0.88))
    assert result.decision == AutomationDecision.HUMAN_REVIEW
    assert result.requires_human_approval is True


def test_low_confidence_requests_more_research():
    result = decide_lead_action(lead(), qual(score=92, confidence=0.61))
    assert result.decision == AutomationDecision.RESEARCH_MORE
    assert result.can_contact is False


def test_risk_flag_blocks_automatic_action():
    result = decide_lead_action(lead(), qual(risk_flags=["possible_duplicate_identity"]))
    assert result.decision == AutomationDecision.HUMAN_REVIEW
    assert result.can_contact is False


def test_missing_contact_consent_blocks_outreach():
    result = decide_lead_action(lead(consent=False), qual())
    assert result.decision == AutomationDecision.HUMAN_REVIEW
    assert result.can_contact is False


def test_low_score_nurtures():
    result = decide_lead_action(lead(), qual(score=45, confidence=0.91))
    assert result.decision == AutomationDecision.NURTURE
    assert result.can_contact is True
