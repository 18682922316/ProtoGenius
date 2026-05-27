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

from .audit import AuditLog  # noqa: F401  (re-export surface for downstream)
from .config import ProtoGeniusConfig
from .context import RunContext
from .hooks.registry import HookRegistry, default_registry
from .llm import LLMClient, build_client
from .quotas import QuotaExceededError, QuotaLedger  # noqa: F401
from .state_machine import DEMO_ONLY_STAGES, Stage, StateMachine
from .task_input import TaskInput

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

    def run(
        self,
        task: str | TaskInput,
        *,
        workspace: Path | str = "runs",
    ) -> RunContext:
        """Execute one full pipeline pass against ``task``.

        ``task`` accepts either a plain natural-language string (v1-style)
        or a :class:`TaskInput` envelope (v2). When a ``TaskInput`` is
        supplied, its ``profile`` / ``scoped_input`` / ``knowledge_base``
        / ``structured_requirements_summary`` fields are loaded onto the
        ``RunContext``.
        """
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

                # v2 §2.6 / §2.7 / §5 — skip demo-only stages when the
                # effective profile is research_and_docs_only.
                if next_stage in DEMO_ONLY_STAGES and not ctx.will_generate_demo:
                    ctx.audit.log_info(
                        "stage skipped — research_and_docs_only profile",
                        stage=next_stage.value,
                    )
                    current = next_stage
                    took_optional = False
                    continue

                # Blocking gates: pause for confirmation.
                if next_stage in self.state_machine.blocking_gates():
                    if not self._await_gate(ctx, next_stage):
                        return self._abort(ctx, stage=next_stage, reason="gate not confirmed")
                    # v2 §3 — split sign-off: run the doc-signoff gate
                    # twice (once for SRS/TDD, once for the four-layer
                    # pack) when the user opted out of the merge default.
                    if (
                        next_stage is Stage.GATE_DOC_SIGNOFF
                        and not ctx.config.documents.merge_tdd_and_layer_signoff
                        and not self._await_gate(
                            ctx, Stage.GATE_DOC_SIGNOFF, label="layer_pack"
                        )
                    ):
                        return self._abort(
                            ctx,
                            stage=next_stage,
                            reason="layer-pack sign-off gate not confirmed",
                        )

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

    def _build_context(self, *, task: str | TaskInput, workspace: Path) -> RunContext:
        if isinstance(task, TaskInput):
            task_input = task
            description = task.description
        else:
            task_input = None
            description = task
        ctx = RunContext(
            config=self.config,
            task_description=description,
            workspace=workspace,
            task_input=task_input,
        )
        if task_input is not None:
            # Mirror the structured summary onto the context so
            # downstream sub-agents see it without having to chase the
            # TaskInput pointer.
            ctx.structured_requirements_summary = task_input.structured_requirements_summary
        ctx.ensure_dirs()
        ctx.ledger = QuotaLedger(caps=self.config.quotas)
        ctx.audit = AuditLog(path=ctx.run_dir / self.config.audit.artifact_file)
        ctx.audit.log_info(
            "run started",
            run_id=ctx.run_id,
            task=description,
            profile=ctx.effective_profile,
            will_generate_demo=ctx.will_generate_demo,
            scoped_input=ctx.scoped_input.type if ctx.scoped_input else None,
            kb_present=bool(ctx.kb_ref and not ctx.kb_ref.is_empty),
        )
        return ctx

    def _before_transition(self, ctx: RunContext, src: Stage, dst: Stage) -> None:
        for hook in self.hooks.pre_stage_transition:
            hook(ctx, src, dst)

    def _await_gate(
        self,
        ctx: RunContext,
        gate: Stage,
        *,
        label: str = "",
    ) -> bool:
        """Pause until a confirmation callback returns True.

        ``label`` distinguishes between split sign-off iterations (v2 §3
        with ``documents.merge_tdd_and_layer_signoff: false``). It is
        recorded in the audit-log gate entry so the trail clearly shows
        whether a confirmation referred to the SRS/TDD bundle, the
        four-layer pack, or the merged review.
        """
        snapshot = ctx.to_jsonable()
        assert ctx.audit is not None
        gate_label = f"{gate.value}:{label}" if label else gate.value
        ctx.audit.log_gate(gate=gate_label, decision="pending")
        confirmed = self.options.on_gate(gate, snapshot)
        ctx.audit.log_gate(
            gate=gate_label,
            decision="approved" if confirmed else "rejected",
        )
        return bool(confirmed)

    def _abort(self, ctx: RunContext, *, stage: Stage, reason: str) -> RunContext:
        assert ctx.audit is not None
        ctx.aborted = True
        ctx.abort_reason = reason
        ctx.audit.log_abort(reason=reason, stage=stage.value)
        return ctx
