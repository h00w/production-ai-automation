# Production Readiness Gates

A workflow is not described as production-ready merely because it runs end-to-end. It must satisfy explicit release gates.

## Gate model

| Gate | Blocking criterion | Evidence |
|---|---|---|
| Contract | Input/output schemas validate | unit + contract tests |
| Safety | No consequential action bypasses policy | policy tests + trace |
| Idempotency | Duplicate events create no duplicate side effects | replay test |
| Reliability | Retryable failures recover within retry budget | integration test |
| Failure containment | Exhausted failures enter DLQ / review state | failure injection test |
| AI quality | Structured-output validity >= 99% on eval set | evaluation report |
| Business quality | Qualification accuracy meets declared threshold | labeled benchmark |
| Observability | Each run has correlation ID, state, latency, outcome | trace / dashboard |
| Security | Secrets excluded; webhook auth and least privilege documented | security review |
| Operability | Runbook covers rollback, replay, escalation, ownership | runbook |
| Cost | Cost-per-run is measured and bounded | benchmark |
| Documentation | Architecture, setup, limitations, and evidence are current | docs review |

## Maturity labels

### Concept
Architecture or screenshots exist, but the workflow is not importable and repeatably testable.

### Runnable
A workflow or service can be started from the repository and executes its documented happy path.

### Portfolio-tested
Happy path, expected negative paths, and representative edge cases have automated or recorded evidence.

### Capability-validated
A third-party integration has been exercised end-to-end against a real account using non-sensitive test data.

### Production-candidate
All blocking gates above pass in a staging-like environment. This still does not imply a customer deployment.

### Production-validated
Operational evidence from a real deployment demonstrates reliability, monitoring, security controls, recovery procedures, and measured business outcomes.

## Required failure injection

The proof suite must cover at least:

- duplicate inbound webhook;
- malformed payload;
- invalid LLM JSON;
- low-confidence AI result;
- model/API timeout;
- HTTP 429 with Retry-After;
- downstream HTTP 500;
- expired/invalid token;
- partial CRM failure;
- notification failure;
- replay after recovery.

## Release decision

A release candidate is accepted only when:

1. all blocking tests pass;
2. no known P0/P1 defect remains open;
3. evaluation thresholds pass;
4. rollback/replay procedures are documented;
5. all environment-specific configuration is externalized;
6. business metrics are clearly labeled as measured, simulated, or target values.

This distinction is intentionally strict: **runnable is evidence of implementation; production readiness is evidence of controlled operation.**