"""Decide which demo flavor to scaffold.

Rules (per §5):

1. If the task is unambiguously algorithmic (matched by configured trigger
   keywords) → ``algo``.
2. Otherwise, prefer ``fullstack`` when the task description references UI /
   user interaction / API surface.
3. Fall back to ``script`` when the task is best expressed as a CLI tool.
4. When the user's clarifications constrain resources (e.g. "single file
   demo", "no Node toolchain") the orchestrator can downgrade by supplying
   ``preferred_kind`` to override the default priority.
"""

from __future__ import annotations

from enum import StrEnum

from ..context import RunContext


class DemoKind(StrEnum):
    FULLSTACK = "fullstack"
    SCRIPT = "script"
    ALGO = "algo"


_FULLSTACK_HINTS = (
    "ui",
    "frontend",
    "web app",
    "dashboard",
    "rest",
    "api",
    "service",
    "chat",
    "browser",
    "前端",
    "网页",
    "界面",
    "服务",
)
_SCRIPT_HINTS = (
    "cli",
    "command-line",
    "command line",
    "shell script",
    "脚本",
    "命令行",
)


def _is_algo(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(kw.lower() in lowered for kw in keywords)


def choose_demo_kind(
    ctx: RunContext,
    *,
    preferred_kind: DemoKind | None = None,
) -> DemoKind:
    if preferred_kind is not None:
        return preferred_kind

    task = ctx.task_description.lower()
    if _is_algo(task, ctx.config.algo_task.trigger_keywords):
        return DemoKind.ALGO

    if any(hint in task for hint in _FULLSTACK_HINTS):
        return DemoKind.FULLSTACK
    if any(hint in task for hint in _SCRIPT_HINTS):
        return DemoKind.SCRIPT

    # Default priority per config.demo.default_priority.
    priority = ctx.config.demo.default_priority or ["fullstack", "script_or_cli", "algorithm_prototype"]
    mapping = {
        "fullstack": DemoKind.FULLSTACK,
        "script_or_cli": DemoKind.SCRIPT,
        "algorithm_prototype": DemoKind.ALGO,
    }
    return mapping.get(priority[0], DemoKind.FULLSTACK)
