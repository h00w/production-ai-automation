import json
import uuid
import streamlit as st

from src.models import RequestInput
from src.workflow import run_workflow

st.set_page_config(page_title="Production AI Automation", page_icon="⚙️", layout="wide")

st.title("Production AI Automation System")
st.caption("Proof-of-work demo: Context → Action → Verification")

with st.sidebar:
    st.header("Demo controls")
    st.write("This version uses deterministic local adapters so reviewers can run it without secrets.")
    st.markdown("**Human approval threshold:** $250 for refund requests")
    st.markdown("**Synthetic refund window:** 30 days")

left, right = st.columns([1, 1])

with left:
    st.subheader("1. Business request")
    examples = {
        "Late order": "My order has not arrived. Can you check where it is?",
        "Refund": "I want a refund because the product did not meet expectations.",
        "Technical support": "The device is not working after the latest update.",
        "Sales lead": "We are interested in a company-wide deployment. Can we get pricing and a demo?",
        "Billing": "We were charged twice on the latest invoice.",
    }
    example_name = st.selectbox("Example", list(examples))
    text = st.text_area("Request", value=examples[example_name], height=140)
    order_id = st.text_input("Order ID (used for order/refund flows)", value="ORD-1042")
    amount = st.number_input("Amount USD (used for refund risk)", min_value=0.0, value=99.0, step=10.0)

    run = st.button("Run automation", type="primary", use_container_width=True)

with right:
    st.subheader("2. Controlled outcome")
    if run:
        req = RequestInput(
            request_id=str(uuid.uuid4())[:8],
            text=text,
            order_id=order_id or None,
            amount_usd=amount,
        )
        result = run_workflow(req)

        c1, c2, c3 = st.columns(3)
        c1.metric("Intent", result.intent.value)
        c2.metric("Status", result.status)
        c3.metric("Automated", "Yes" if result.automated else "No")

        if result.requires_human_approval:
            st.warning("Human approval required")
        else:
            st.success("Workflow completed within configured controls")

        st.markdown("### Proposed action")
        st.write(result.proposed_action)

        st.markdown("### User-facing result")
        st.write(result.final_message)

        st.markdown("### Verification checks")
        for item in result.checks:
            st.write("✓", item)

        with st.expander("Audit trace", expanded=True):
            st.code("\n".join(result.trace))

        with st.expander("Structured output"):
            st.json(json.loads(result.model_dump_json()))
    else:
        st.info("Run an example to inspect the workflow, checks, and audit trace.")

st.divider()
st.markdown(
    """
### What this proof demonstrates
- workflow decomposition
- AI/classification boundary
- validated structured state
- tool/API abstraction
- risk-based human approval
- safe fallback paths
- auditability and regression-testable behavior

**Evidence integrity:** This is a portfolio demonstration using synthetic business data. It does not claim production customer metrics.
"""
)

st.divider()
st.markdown(
    """
<div style="text-align:center;color:#64748b;font-size:0.88rem;padding:0.5rem 0 1rem;">
  <strong>Hendarmawan, PhD Eng.</strong> &nbsp;·&nbsp;
  <a href="https://github.com/h00w/" target="_blank">GitHub</a> &nbsp;·&nbsp;
  <a href="https://www.linkedin.com/in/hender/" target="_blank">LinkedIn</a> &nbsp;·&nbsp;
  <a href="https://hendarmawan.se" target="_blank">hendarmawan.se</a>
</div>
""",
    unsafe_allow_html=True,
)
