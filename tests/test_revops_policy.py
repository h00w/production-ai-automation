from src.revops_models import LeadInput, LeadQualification, LeadTemperature, AutomationDecision
from src.revops_policy import decide_lead_action
from pydantic import ValidationError
import pytest


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


@pytest.mark.parametrize("consent", ["true", "false", "yes", "on", 1, 0, None])
def test_contact_consent_requires_an_explicit_boolean(consent):
    with pytest.raises(ValidationError):
        lead(consent=consent)


def test_missing_contact_consent_defaults_to_refusal():
    payload = lead().model_dump()
    del payload["consent_to_contact"]
    result = decide_lead_action(LeadInput.model_validate(payload), qual())
    assert result.can_contact is False


@pytest.mark.parametrize("consent", ["true", "yes", 1])
def test_policy_refuses_mutated_consent_without_boolean_approval(consent):
    modified = lead().model_copy(update={"consent_to_contact": consent})
    assert decide_lead_action(modified, qual()).can_contact is False


def test_empty_evidence_blocks_automated_contact():
    for evidence in ([], ["  "]):
        qualification = qual()
        qualification.evidence = evidence
        result = decide_lead_action(lead(), qualification)
        assert result.decision == AutomationDecision.HUMAN_REVIEW
        assert result.can_contact is False


def test_low_score_nurtures():
    result = decide_lead_action(lead(), qual(score=45, confidence=0.91))
    assert result.decision == AutomationDecision.NURTURE
    assert result.can_contact is True


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_confidence_cannot_authorize_contact(invalid):
    with pytest.raises(ValidationError):
        qual(confidence=invalid)


@pytest.mark.parametrize("invalid", [True, False, "0.92"])
def test_coerced_confidence_cannot_authorize_contact(invalid):
    with pytest.raises(ValidationError):
        qual(confidence=invalid)


@pytest.mark.parametrize("field", ["icp_fit", "intent", "urgency", "technical_fit", "commercial_fit", "score"])
@pytest.mark.parametrize("invalid", [True, "90", 90.0])
def test_qualification_scores_require_integer_evidence(field, invalid):
    payload = qual().model_dump()
    payload[field] = invalid
    with pytest.raises(ValidationError):
        LeadQualification.model_validate(payload)
