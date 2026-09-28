from __future__ import annotations

from .revops_models import (
    AutomationDecision,
    LeadInput,
    LeadQualification,
    PolicyDecision,
)

POLICY_VERSION = "revops-1.0.0"


def decide_lead_action(lead: LeadInput, qualification: LeadQualification) -> PolicyDecision:
    """Authorize the next action using deterministic rules.

    AI supplies the qualification evidence. This function decides whether the
    workflow may act automatically. Consequential actions never depend on the
    model response alone.
    """

    if not lead.consent_to_contact:
        return PolicyDecision(
            decision=AutomationDecision.HUMAN_REVIEW,
            reason="Lead has not provided consent for automated outreach.",
            requires_human_approval=True,
            can_contact=False,
            policy_version=POLICY_VERSION,
        )

    if qualification.risk_flags:
        return PolicyDecision(
            decision=AutomationDecision.HUMAN_REVIEW,
            reason="Qualification contains one or more risk flags.",
            requires_human_approval=True,
            can_contact=False,
            policy_version=POLICY_VERSION,
        )

    if qualification.confidence < 0.70:
        return PolicyDecision(
            decision=AutomationDecision.RESEARCH_MORE,
            reason="Confidence is below the minimum automation threshold.",
            requires_human_approval=False,
            can_contact=False,
            policy_version=POLICY_VERSION,
        )

    if qualification.score >= 80 and qualification.confidence >= 0.85:
        return PolicyDecision(
            decision=AutomationDecision.AUTO_ROUTE,
            reason="High score and high confidence satisfy auto-routing policy.",
            requires_human_approval=False,
            can_contact=True,
            policy_version=POLICY_VERSION,
        )

    if qualification.score >= 60:
        return PolicyDecision(
            decision=AutomationDecision.HUMAN_REVIEW,
            reason="Potentially qualified lead requires reviewer confirmation.",
            requires_human_approval=True,
            can_contact=False,
            policy_version=POLICY_VERSION,
        )

    return PolicyDecision(
        decision=AutomationDecision.NURTURE,
        reason="Lead is below the sales-routing threshold.",
        requires_human_approval=False,
        can_contact=True,
        policy_version=POLICY_VERSION,
    )
