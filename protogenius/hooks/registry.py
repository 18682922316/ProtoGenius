"""Hook registry — wires the three hook points used by the orchestrator.

Hook points:

- ``pre_search``        : called by every research adapter immediately before
                          issuing a search; responsible for charging the
                          search quota and refusing if a hard cap would trip.
- ``post_research``     : called once a research adapter has produced a list
                          of `ResearchItem`s; responsible for citation audit.
- ``pre_stage_transition`` : called by the orchestrator before moving from
                          one stage to the next; the default implementation
                          performs the gate check and logs the transition.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from ..context import RunContext
from ..state_machine import Stage

PreSearchHook = Callable[[RunContext, int], None]
PostResearchHook = Callable[[RunContext, list], None]
PreStageHook = Callable[[RunContext, Stage, Stage], None]


@dataclass
class HookRegistry:
    pre_search: list[PreSearchHook] = field(default_factory=list)
    post_research: list[PostResearchHook] = field(default_factory=list)
    pre_stage_transition: list[PreStageHook] = field(default_factory=list)


def default_registry() -> HookRegistry:
    """Return the registry with the three first-party hooks pre-wired."""
    from .citation_audit import citation_audit_hook
    from .gate_check import gate_check_hook
    from .quota_guard import quota_guard_hook

    return HookRegistry(
        pre_search=[quota_guard_hook],
        post_research=[citation_audit_hook],
        pre_stage_transition=[gate_check_hook],
    )
