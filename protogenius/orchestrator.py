"""Pipeline driver.

The orchestrator walks the `StateMachine` and dispatches each stage to its
registered handler. It also:

- charges quotas on each stage entry,
- runs hooks (`pre_search`, `post_research`, `pre_stage_transition`),
- pauses on blocking gates until a confirmation callback returns truthy,
- records every decision in the audit log.

This module is deliberately small. All heavy lifting belongs in
``protogenius.research``, ``protogenius.docs``, ``protogenius.demo`` and
``protogenius.testing`` — the orchestrator only orchestrates.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .audit import AuditLog
from .config import ProtoGeniusConfig
from .context import RunContext
from .hooks.registry import HookRegistry, default_registry
from .llm import LLMClient, build_client
from .quotas import QuotaExceededError, QuotaLedger
from .state_machine import Stage, StateMachine

# A gate-confirmation callback receives the run context snapshot (JSON-able)
# and returns True if the user confirms, False otherwise. The default
# implementation aborts the run with a "no confirmation" reason — the CLI
# replaces it with an interactive prompt; Cursor commands provide their own.
GateCallback = Callable[[Stage, dict[str, Any]], bool]


def _abort_on_unconfirmed(stage: Stage, snapshot: dict[str, Any]) -> bool:  # noqa: ARG001
    return False


@dataclass
class OrchestratorOptions:
    dry_run: bool = False
    interactive: bool = True
    on_gate: GateCallback = field(default=_abort_on_unconfirmed)


class Orchestrator:
    """Walks the state machine, dispatches handlers, enforces gates and quotas."""

    def __init__(
        self,
        config: ProtoGeniusConfig,
        *,
        state_machine: StateMachine | None = None,
        hooks: HookRegistry | None = None,
        llm: LLMClient | None = None,
        options: OrchestratorOptions | None = None,
    ) -> None:
        self.config = config
        self.state_machine = state_machine or StateMachine()
        self.hooks = hooks or default_registry()
        self.options = options or OrchestratorOptions()
        self.llm: LLMClient = llm or build_client(config.llm, dry_run=self.options.dry_run)

    # ---- public entry --------------------------------------------------

    def run(self, task: str, *, workspace: Path | str = "runs") -> RunContext:
        """Execute one full pipeline pass against ``task``."""
        ctx = self._build_context(task=task, workspace=Path(workspace))
        assert ctx.ledger is not None and ctx.audit is not None

        current = Stage.INIT
        took_optional = False
        try:
            while current != Stage.DONE:
                next_stage = self.state_machine.next_stage(
                    current, took_optional_branch=took_optional
                )
                self._before_transition(ctx, current, next_stage)
                if next_stage == Stage.DONE:
                    break

                # Blocking gates: pause for confirmation.
                if next_stage in self.state_machine.blocking_gates() and not self._await_gate(
                    ctx, next_stage
                ):
                    return self._abort(ctx, stage=next_stage, reason="gate not confirmed")

                # Charge one turn for entering a stage.
                ctx.ledger.charge_turn()
                ctx.ledger.check_walltime()

                handler = self.state_machine.handler(next_stage)
                took_optional = bool(handler(ctx, self) or False) if handler is not None else False

                current = next_stage
        except QuotaExceededError as exc:
            ctx.audit.log_quota_event(exc.dimension, exc.current, exc.cap, level="hard")
            return self._abort(ctx, stage=current, reason=f"quota exceeded: {exc.dimension}")

        ctx.audit.log_info("run complete", run_id=ctx.run_id)
        return ctx

    # ---- registration helpers -----------------------------------------

    def register(self, stage: Stage, handler: Any) -> None:
        self.state_machine.register(stage, handler)

    # ---- internals -----------------------------------------------------

    def _build_context(self, *, task: str, workspace: Path) -> RunContext:
        ctx = RunContext(
            config=self.config,
            task_description=task,
            workspace=workspace,
        )
        ctx.ensure_dirs()
        ctx.ledger = QuotaLedger(caps=self.config.quotas)
        ctx.audit = AuditLog(path=ctx.run_dir / self.config.audit.artifact_file)
        ctx.audit.log_info("run started", run_id=ctx.run_id, task=task)
        return ctx

    def _before_transition(self, ctx: RunContext, src: Stage, dst: Stage) -> None:
        for hook in self.hooks.pre_stage_transition:
            hook(ctx, src, dst)

    def _await_gate(self, ctx: RunContext, gate: Stage) -> bool:
        snapshot = ctx.to_jsonable()
        assert ctx.audit is not None
        ctx.audit.log_gate(gate=gate.value, decision="pending")
        confirmed = self.options.on_gate(gate, snapshot)
        ctx.audit.log_gate(
            gate=gate.value,
            decision="approved" if confirmed else "rejected",
        )
        return bool(confirmed)

    def _abort(self, ctx: RunContext, *, stage: Stage, reason: str) -> RunContext:
        assert ctx.audit is not None
        ctx.aborted = True
        ctx.abort_reason = reason
        ctx.audit.log_abort(reason=reason, stage=stage.value)
        return ctx
