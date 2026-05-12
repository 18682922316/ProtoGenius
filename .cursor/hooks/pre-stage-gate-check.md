---
name: pre-stage-gate-check
event: pre_stage_transition
code: protogenius.hooks.gate_check.gate_check_hook
---

# pre-stage gate check

Logs every stage transition and enforces invariants — e.g. refuses to enter
`DRAFT_DOCS` when the research bundle is empty, or `BUILD_DEMO` when no
documents are on record. The actual user-facing gating happens inside the
orchestrator (`Orchestrator._await_gate`); this hook is the diagnostic
counterpart.
