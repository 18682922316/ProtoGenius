"""Gate-check hook — pre-stage-transition.

The orchestrator already pauses at every blocking gate (see
``Orchestrator._await_gate``). This hook is the diagnostic counterpart: it
logs the source / destination stage names to the audit trail so a reviewer
can reconstruct the exact pipeline path that was taken on a given run.

Hooks must not raise on legitimate transitions — any abort logic stays in
the orchestrator. The hook may, however, refuse to allow a transition by
raising ``GateCheckRefused`` if invariant checks fail (e.g. attempting to
enter ``BUILD_DEMO`` without a sign-off record for ``GATE_DOC_SIGNOFF``).
"""

from __future__ import annotations

from ..context import RunContext
from ..state_machine import Stage


class GateCheckRefused(RuntimeError):
    """Raised when a gate-check invariant is violated."""


def gate_check_hook(ctx: RunContext, src: Stage, dst: Stage) -> None:
    if ctx.audit is None:  # pragma: no cover — defensive
        raise RuntimeError("RunContext.audit is unset; orchestrator must initialize it")

    # Log every transition so the audit trail is a complete record.
    ctx.audit.log_info("transition", src=src.value, dst=dst.value)

    # Hard invariants — orchestrator must never have allowed these.
    if dst is Stage.DRAFT_DOCS and not ctx.research.academic and not ctx.research.github:
        raise GateCheckRefused(
            "cannot enter DRAFT_DOCS: research bundle is empty (invariant violation)"
        )
    if dst is Stage.BUILD_DEMO and not ctx.documents:
        raise GateCheckRefused(
            "cannot enter BUILD_DEMO: no documents on record (invariant violation)"
        )
