# n8n Workflow Layer

This directory contains importable orchestration workflows for the production automation proof.

## Workflow contract

n8n is the orchestration layer, not the policy authority. Workflows may normalize input, invoke bounded services, route on validated outputs, record state, and trigger notifications. Consequential business authorization stays in deterministic policy code.

## Included workflow

`workflows/lead_intake.json`

Flow:

`Webhook -> Normalize -> Validate -> Build Event Envelope -> Respond`

The starter workflow intentionally has no embedded credentials and performs no irreversible action. It is safe to import and inspect before connecting external SaaS systems.

## Production extension pattern

1. Webhook verification / authentication
2. Normalize payload
3. Validate required fields
4. Compute idempotency key
5. Lookup existing event / lead
6. Enrich through bounded API adapters
7. Invoke qualification service
8. Validate structured result
9. Invoke deterministic policy
10. Route to CRM / review / nurture
11. Verify side effect
12. Write audit event
13. Emit metrics
14. Respond / acknowledge

## Required error workflow

A production deployment should define a dedicated n8n error workflow that records:

- workflow name and execution ID;
- correlation ID;
- failing node;
- HTTP status / provider error code;
- retry count;
- redacted input metadata;
- terminal disposition (`retry`, `dead_letter`, `human_review`).

## Credential policy

Do not commit exported credentials, OAuth tokens, API keys, sheet IDs containing sensitive context, phone-number IDs, or customer-specific webhook URLs. Use n8n credential objects and environment-specific configuration.

## Validation checklist

Before labeling a workflow capability-validated:

- import succeeds on a clean n8n instance;
- every branch has been executed;
- malformed payload path is tested;
- duplicate webhook path is tested;
- model failure path is tested;
- downstream 429 and 5xx behavior is tested;
- secrets are absent from exported JSON;
- audit trail contains a correlation ID;
- external side effects can be replayed safely.