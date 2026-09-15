# Production AI Automation — Deliverable Proof Schema

This document is the reviewer-facing map from job requirement to runnable evidence.

## 1. System boundary

```text
Inbound business event
        |
        v
Webhook/API gateway
        |
        v
Normalize + validate + authenticate
        |
        v
Idempotency / identity resolution
        |
        +-----------------------+
        |                       |
        v                       v
Enrichment adapters         Existing record
        |                       |
        +-----------+-----------+
                    v
            AI qualification
                    |
                    v
        Structured-output validator
                    |
                    v
          Deterministic policy
          /        |        \
         v         v         v
   auto-route   review   research-more
         |         |         |
         +---------+---------+
                   v
          Bounded SaaS adapters
      CRM / email / Slack / calendar
                   |
                   v
             Side-effect verify
                   |
                   v
        Audit + metrics + tracing
                   |
                   v
         retry / complete / DLQ
```

## 2. Capability matrix

| Capability | Repository evidence | Acceptance proof |
|---|---|---|
| Workflow decomposition | `docs/architecture.md`, n8n workflow | reviewer can trace each state |
| API/webhook handling | `n8n/workflows/lead_intake.json` | valid request -> HTTP 202; invalid -> HTTP 400 |
| Typed contracts | `src/revops_models.py` | invalid email/score/confidence rejected |
| AI agents | qualification/enrichment boundary | model output cannot bypass validation |
| Prompt logic | version/model metadata in qualification contract | eval result can be linked to prompt version |
| Deterministic policy | `src/revops_policy.py` | confidence, risk, consent branches tested |
| Human-in-the-loop | `HUMAN_REVIEW` policy state | medium-risk or consent-blocked cases stop |
| CRM automation | adapter-ready architecture | no CRM-specific business logic in policy |
| Reliability | production readiness gates | retries/DLQ/idempotency required for release |
| Debuggability | event envelope + correlation ID | workflow instance is reconstructable |
| Replay | stable idempotency key | duplicate processing can be detected safely |
| Documentation | docs + proof schema + runbook path | reviewer can operate without oral explanation |
| Business outcomes | `docs/business_outcome.md` | measured vs target claims clearly separated |
| CI | GitHub Actions + pytest | release regression is machine-checkable |

## 3. Event schema

All production workflow events use an envelope with:

- `event_id`: unique immutable event identity;
- `event_type`: semantic event name, e.g. `lead.created`;
- `schema_version`: event contract version;
- `workflow_version`: automation implementation version;
- `correlation_id`: connects all work for one business transaction;
- `idempotency_key`: stable duplicate-detection key;
- `occurred_at`: UTC timestamp;
- `payload`: validated business data;
- `metadata`: non-business execution context.

## 4. Lead qualification schema

The model may propose these dimensions:

- ICP fit: 0–100
- intent: 0–100
- urgency: 0–100
- technical fit: 0–100
- commercial fit: 0–100
- aggregate score: 0–100
- confidence: 0.0–1.0
- temperature: hot / warm / cold
- evidence list
- risk flags
- recommended action
- model provider/name
- prompt version

The policy engine—not the model—decides authorization.

## 5. Current deterministic policy

| Condition | Decision | Automatic contact? |
|---|---|---:|
| no contact consent | human review | no |
| any risk flag | human review | no |
| confidence < 0.70 | research more | no |
| score >= 80 and confidence >= 0.85 | auto route | yes |
| score >= 60 | human review | no |
| otherwise | nurture | yes, subject to channel policy |

Thresholds are versioned policy, not hidden prompt behavior.

## 6. Production failure contract

Every external connector must classify errors into:

- `validation_error` — terminal, do not retry;
- `authentication_error` — terminal until credentials repaired;
- `rate_limited` — retry using provider guidance/backoff;
- `timeout` — bounded retry;
- `provider_5xx` — bounded retry + circuit-breaker candidate;
- `conflict_duplicate` — reconcile idempotently;
- `policy_block` — no side effect; review if appropriate;
- `unknown_error` — fail closed and escalate.

After retry exhaustion the workflow must record enough state for dead-letter inspection and replay.

## 7. Proof scenarios

### A. Happy path

Valid, consented lead -> structured qualification -> high confidence -> `AUTO_ROUTE` -> bounded CRM action -> verification -> audit.

### B. Human review

Valid lead -> medium score -> `HUMAN_REVIEW` -> no outbound side effect until approved.

### C. Low-confidence AI

Valid lead -> confidence below threshold -> `RESEARCH_MORE` -> no customer contact.

### D. Safety/risk flag

Valid lead -> qualification includes risk flag -> `HUMAN_REVIEW` regardless of score.

### E. Malformed inbound request

Missing required field / invalid email -> rejected before model or CRM call.

### F. Duplicate request

Same stable business identity -> same idempotency strategy -> no duplicate side effect.

### G. Provider failure

429/5xx/timeout -> bounded retries -> terminal DLQ/review state when exhausted.

## 8. Adopted portfolio use cases

The architecture can host the strongest use cases represented in the reviewed public automation portfolios without duplicating their workflows:

- CRM lead capture, scoring, enrichment, and nurture;
- cold outreach with approval boundaries;
- appointment request triage and scheduling;
- support ticket classification;
- proposal generation;
- RAG knowledge support with low-confidence escalation;
- WhatsApp/customer-channel routing;
- invoice/document processing;
- hiring-signal lead enrichment;
- social-media/content pipeline automation.

Each use case plugs into shared validation, policy, adapter, audit, failure, and observability layers instead of becoming an isolated demo.

## 9. Reviewer run path

```bash
git clone https://github.com/h00w/production-ai-automation.git
cd production-ai-automation
python -m venv .venv
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

For workflow inspection, import `n8n/workflows/lead_intake.json` into n8n. No credentials are embedded.

## 10. Definition of done

This branch is a stronger production proof when all of the following are true:

- typed contracts and deterministic policy tests pass;
- importable n8n workflow exists;
- invalid input fails before external calls;
- side-effect authorization is separated from AI output;
- production-readiness gates are documented;
- provenance/reference adoption is explicit;
- CI passes;
- no secrets are committed;
- claims distinguish targets, synthetic evidence, capability validation, and real production evidence.

The next implementation layer after this schema is connector hardening: HubSpot/Salesforce adapters, provider retries, webhook signature verification, dead-letter persistence, evaluation datasets, and the operations dashboard.