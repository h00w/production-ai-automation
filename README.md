[![CI](https://github.com/h00w/production-ai-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/h00w/production-ai-automation/actions/workflows/ci.yml)

# Production AI Automation System

**Proof of Work — Hendarmawan, PhD Eng.**

A production-oriented AI automation portfolio project demonstrating how an ambiguous business request can be transformed into a controlled workflow with:

- AI-assisted intent classification
- structured outputs
- workflow routing
- tool/API execution
- business-rule validation
- human-in-the-loop escalation
- retry and failure handling
- audit logging
- measurable operational outcomes
- production-oriented documentation

The project is intentionally designed as a **small, inspectable system** rather than a toy chatbot.

## Why this project exists

Many AI demos optimize only for a fluent answer. Production automation must also control:

1. **Context** — what information enters the model
2. **Action** — what the system is allowed to do
3. **Verification** — how outputs and actions are checked

This repository applies that **CAV Loop: Context → Action → Verification** to a business-operations automation scenario.

## Demo workflow

A user submits a customer/operations request such as:

> "My order has not arrived and I want a refund."

The system:

1. validates the request
2. classifies intent
3. extracts structured fields
4. assigns a risk level
5. routes to the appropriate workflow
6. calls a tool adapter
7. validates the proposed outcome
8. either completes automatically or requests human approval
9. records an auditable trace

## Example architecture

```text
Business Request
      |
      v
Input Validation
      |
      v
AI / Intent Classification
      |
      v
Workflow Router
  +---+---------------------+
  |                         |
  v                         v
Automated Tool Action   Human Review
  |                         |
  v                         |
Business Rule Validation    |
  |                         |
  +-----------+-------------+
              |
              v
         Final Outcome
              |
              v
        Audit + Metrics
```

## Quick start

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate it

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run tests

```bash
pytest -q
```

### 5. Run the demo

```bash
streamlit run app.py
```

The default mode is **deterministic demo mode**, so no API key is required.

## Optional LLM mode

The architecture includes a provider boundary for adding an LLM-backed classifier. The demo remains functional without external credentials so reviewers can evaluate the workflow and controls immediately.

## Proof-of-work package

| Artifact | Purpose |
|---|---|
| `app.py` | Interactive demo |
| `src/workflow.py` | Core automation orchestration |
| `src/adapters.py` | Tool/API abstraction |
| `src/models.py` | Structured data contracts |
| `tests/` | Reliability and regression checks |
| `docs/architecture.md` | Architecture and design decisions |
| `docs/business_outcome.md` | Outcome measurement framework |
| `docs/walkthrough_script.md` | Recruiter demo script |
| `article/` | Production AI automation article |
| `proof_of_work_submission.md` | Copy-ready evidence descriptions |

## Production engineering principles demonstrated

- schema-first design
- explicit workflow states
- least-privilege tool boundary
- deterministic business rules around AI output
- no silent failure
- human approval for high-risk actions
- auditability
- testability
- idempotent-style action identifiers
- measurable outcome definitions

## Important evidence note

Any metrics shown in the demo are **demonstration measurements from synthetic test cases**, not claims about a real customer deployment. This keeps the proof-of-work verifiable and avoids overstating business outcomes.

## Author

**Hendarmawan, PhD Eng.**  
AI & Edge AI engineering leader focused on production AI systems, automation, secure AI infrastructure, embedded AI, and industrial R&D.
