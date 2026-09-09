# 4-Minute Walkthrough Script

## Video title
**Production AI Automation: Request → AI → Tool → Verification → Action**

## 0:00–0:30 — Opening

“Hi, I’m Hendarmawan. This is a compact proof-of-work showing how I approach AI automation as a production engineering problem rather than only a chatbot demo.

The system takes an unstructured business request, classifies it, routes it into a workflow, uses a tool boundary, verifies the outcome, and either completes the task or escalates it to a human.”

## 0:30–1:05 — Architecture

“The design follows a framework I use for production AI: Context, Action, Verification.

Context controls what enters the system. Action defines what the AI-enabled workflow is allowed to do. Verification checks confidence, business rules, tool results, and whether human approval is required.”

Show `docs/architecture.md`.

## 1:05–2:00 — Normal automation

Run the **Sales lead** example.

Explain:

“The request is classified as a sales lead. The workflow creates a structured CRM-style lead through an adapter. The result is marked completed, and the trace shows the steps that were executed.”

Show:
- intent
- status
- automated = yes
- tool result
- verification checks
- audit trace

## 2:00–2:50 — High-risk path

Run a **Refund** example with an amount of `$500`.

If the selected order is outside the demo policy window, try another order ID until the system reaches `awaiting_approval`.

Explain:

“Here the system does not blindly automate a consequential action. It prepares a proposal, applies risk rules, and requires human approval before a refund could be committed.”

Show:
- requires human approval
- high-value gate
- trace

## 2:50–3:25 — Failure handling

Remove the order ID and run an order-status request.

Explain:

“Missing data is not guessed. The workflow explicitly asks for more information. This is important because production automation should fail visibly and safely.”

## 3:25–4:00 — Close

“The repository includes the workflow code, structured contracts, tool adapters, tests, architecture documentation, an outcome measurement plan, and this walkthrough.

The current demo uses synthetic data so it is reproducible and does not overstate production metrics. The same boundaries can be connected to systems such as HubSpot, Salesforce, Zendesk, Stripe, n8n, Make, or custom APIs.”

End with:
**GitHub | Live Demo | Architecture | Tests | Article**
