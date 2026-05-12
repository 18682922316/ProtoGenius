---
document: Test Plan
generated_by: ProtoGenius
run_id: {{ run_id }}
---

# Test Plan

## 1. Sources of truth

- Frozen SRS — `{{ srs_path }}`
- Frozen TDD — `{{ tdd_path }}`

Per §6.2 of the v1 product contract, **the user's original natural-language
input is not an authoritative source** for test cases. Any requirement that
only appears in the original prompt must first be folded into the SRS via a
clarification round before it can drive a test.

## 2. Coverage strategy

- **Unit tests** — exercise pure logic in isolation.
- **Integration tests** — exercise the contract surface between components,
  matching the interface definitions in the TDD.
- **E2E tests** — exercised by Playwright when the prototype exposes a UI.

## 3. Acceptance platforms

The CI matrix mirrors the v1 acceptance set:

- `ubuntu-latest`
- `windows-latest`

## 4. Spec layer

The full test specification lives at `tests/spec.yaml` in language-agnostic
form (see `protogenius.testing.spec_layer.TestSpec`). The pytest adapter is
the default materializer; Playwright is added for the E2E subset.

## 5. Reporting

- Pytest output → console + JUnit XML (`reports/unit.junit.xml`).
- Playwright output → JUnit XML (`reports/e2e.junit.xml`).
- LLM alignment report → `reports/alignment.md`, with confidence + reasoning
  chain attached.
