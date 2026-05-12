"""Quota guard hook — pre-search gate.

Called by every research adapter before it issues a search query.

It performs three jobs:

1. Charge the projected number of results against the search quota dimension.
2. Re-check walltime, since long-running searches can silently consume the
   6-hour cap.
3. Emit a soft-cap warning to the audit log when the run crosses the
   ``soft_cap`` threshold (defined in ``config/quotas.yaml``).
"""

from __future__ import annotations

from ..context import RunContext


def quota_guard_hook(ctx: RunContext, projected_results: int) -> None:
    if ctx.ledger is None:  # pragma: no cover — defensive
        raise RuntimeError("RunContext.ledger is unset; orchestrator must initialize it")
    ctx.ledger.check_walltime()

    # Pre-charge speculative results so the next search short-circuits before
    # making a network call.
    soft_cap = int(ctx.ledger.caps.max_search_results * 0.8)
    pre_total = ctx.ledger.search_results + projected_results
    ctx.ledger.charge_search(projected_results)
    if (
        ctx.audit is not None
        and ctx.ledger.search_results >= soft_cap
        and pre_total < soft_cap + projected_results
    ):
        ctx.audit.log_quota_event(
            "search_results",
            ctx.ledger.search_results,
            ctx.ledger.caps.max_search_results,
            level="soft",
        )
