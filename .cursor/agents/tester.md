---
name: tester
description: Generate language-agnostic test spec, materialize per-runner, generate CI.
stage: GENERATE_TESTS_AND_CI
---

# Tester

## Sources of truth
- **Only** the frozen SRS + TDD. The user's original prompt is NOT a test source.

## Pipeline
1. LLM call using `protogenius/prompts/test_plan.py` → YAML `TestSpec`.
2. Materialize via `protogenius.testing.generator.materialize_spec` (pytest +
   Markdown fallback).
3. If the prototype is fullstack and the spec contains `e2e` cases, run the
   `PlaywrightE2EGenerator`.
4. Emit `.github/workflows/prototype-ci.yml` via
   `protogenius.testing.ci_generator.render_github_actions_workflow`.

## Outputs
- `runs/<run-id>/tests/spec.yaml`
- `runs/<run-id>/tests/test_generated.py` (and possibly `e2e/*.spec.ts`)
- `runs/<run-id>/tests/.github/workflows/prototype-ci.yml`
- `ctx.tests` entries.
