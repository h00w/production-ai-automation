from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import hashlib


@dataclass
class MockBusinessTools:
    """Deterministic stand-in for CRM/order/billing APIs.

    The interface is deliberately separated from workflow logic so a live API,
    webhook, CRM, or SaaS connector can be substituted without rewriting the
    orchestration layer.
    """

    def lookup_order(self, order_id: str | None) -> Dict[str, Any]:
        if not order_id:
            return {"found": False, "reason": "missing_order_id"}

        digest = int(hashlib.sha256(order_id.encode()).hexdigest()[:4], 16)
        delivered = digest % 3 == 0
        days_since_purchase = 5 + (digest % 55)
        return {
            "found": True,
            "order_id": order_id,
            "delivered": delivered,
            "days_since_purchase": days_since_purchase,
            "status": "delivered" if delivered else "in_transit",
        }

    def create_support_ticket(self, category: str, summary: str) -> Dict[str, Any]:
        ticket_id = "T-" + hashlib.sha256((category + summary).encode()).hexdigest()[:8].upper()
        return {"ticket_id": ticket_id, "category": category, "created": True}

    def create_sales_lead(self, summary: str) -> Dict[str, Any]:
        lead_id = "L-" + hashlib.sha256(summary.encode()).hexdigest()[:8].upper()
        return {"lead_id": lead_id, "created": True}

    def propose_refund(self, order_id: str, amount_usd: float | None) -> Dict[str, Any]:
        return {
            "order_id": order_id,
            "amount_usd": amount_usd,
            "state": "proposed_not_committed",
        }
