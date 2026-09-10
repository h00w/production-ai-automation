# Reproducibility

Production AI automation should be repeatable, inspectable, and versioned. Record the exact configuration, model or service version, input assumptions, dependency versions, and evaluation evidence used for each meaningful run.

## Minimum evidence

- Configuration and environment version
- Input dataset or fixture version
- Model/service identifier
- Dependency lockfile or equivalent
- Test and evaluation results
- Known limitations and rollback notes

Prefer deterministic fixtures for regression tests and retain enough metadata to explain why two runs differ.