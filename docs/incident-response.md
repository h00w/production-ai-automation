# Incident Response

AI automation incidents may involve incorrect actions, unsafe tool use, data exposure, service degradation, or model/policy regressions.

## Response sequence

1. Contain the affected automation or revoke risky permissions.
2. Preserve logs, configuration, artifact identifiers, and relevant inputs.
3. Assess user, security, operational, and data impact.
4. Roll back or switch to a safe fallback when appropriate.
5. Identify the control failure and add regression evidence.
6. Document corrective actions and conditions for re-enabling automation.

Post-incident changes should reduce recurrence, not only restore service.