"""Pipeline state machine — the spine of every ProtoGenius run.

v2 ordering (mirrors §2-§6 of the v2 requirements; differences vs. v1 are
marked with **[v2]**):

    UNDERSTAND_REQUIREMENT
      → CLARIFY (up to 3 rounds; failure → ABORTED)
      → SELECT_PROFILE                                                **[v2]**
      → INGEST_KB (no-op when no knowledge base configured)           **[v2]**
      → ANALYZE_STACK (≤ 3 mutually exclusive options)
      → RESEARCH_ACADEMIC / RESEARCH_GITHUB / RESEARCH_INDUSTRY
      → (if algorithm task) FIRST_PRINCIPLES
      → CROSS_COMPARE
      → GENERATE_INSIGHTS (one per accepted source, §2.4.A/B/C)       **[v2]**
      → GATE_RESEARCH_ADOPTION   ← blocking, requires user confirmation
      → DRAFT_DOCS               (SRS / TDD / interfaces / arch)
      → DRAFT_LAYER_DOCS         (four-layer pack §4.4)               **[v2]**
      → GATE_DOC_SIGNOFF         ← blocking
                                    by default covers BOTH SRS/TDD and the
                                    four-layer pack (§3); split into two
                                    gates by setting
                                    documents.merge_tdd_and_layer_signoff=false
      → BUILD_DEMO               (skipped when profile = research_and_docs_only)
      → GENERATE_TESTS_AND_CI    (skipped + degraded when no demo)    **[v2]**
      → EXECUTE_TESTS            (skipped when no demo)
      → ALIGNMENT_REPORT
      → DONE

The machine itself is intentionally inert: ``Orchestrator.run`` is the
active party that walks transitions and calls each registered sub-agent.
The orchestrator short-circuits to DONE after the doc sign-off gate when
``RunContext.will_generate_demo`` is false (per §2.7 / §5).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum


class Stage(StrEnum):
    INIT = "INIT"
    UNDERSTAND_REQUIREMENT = "UNDERSTAND_REQUIREMENT"
    CLARIFY = "CLARIFY"
    SELECT_PROFILE = "SELECT_PROFILE"          # v2 §2.6 / §2.7
    INGEST_KB = "INGEST_KB"                     # v2 §2.8
    ANALYZE_STACK = "ANALYZE_STACK"
    RESEARCH_ACADEMIC = "RESEARCH_ACADEMIC"
    RESEARCH_GITHUB = "RESEARCH_GITHUB"
    RESEARCH_INDUSTRY = "RESEARCH_INDUSTRY"
    FIRST_PRINCIPLES = "FIRST_PRINCIPLES"
    CROSS_COMPARE = "CROSS_COMPARE"
    GENERATE_INSIGHTS = "GENERATE_INSIGHTS"     # v2 §2.4.A/B/C
    GATE_RESEARCH_ADOPTION = "GATE_RESEARCH_ADOPTION"
    DRAFT_DOCS = "DRAFT_DOCS"
    DRAFT_LAYER_DOCS = "DRAFT_LAYER_DOCS"       # v2 §4.4
    GATE_DOC_SIGNOFF = "GATE_DOC_SIGNOFF"
    BUILD_DEMO = "BUILD_DEMO"
    GENERATE_TESTS_AND_CI = "GENERATE_TESTS_AND_CI"
    EXECUTE_TESTS = "EXECUTE_TESTS"
    ALIGNMENT_REPORT = "ALIGNMENT_REPORT"
    DONE = "DONE"
    ABORTED = "ABORTED"


# Stages that do not generate user-visible prototype artifacts. The
# orchestrator may skip them when running in ``research_and_docs_only``
# profile (v2 §2.6 / §2.7 / §5).
DEMO_ONLY_STAGES: frozenset[Stage] = frozenset(
    {
        Stage.BUILD_DEMO,
        Stage.GENERATE_TESTS_AND_CI,
        Stage.EXECUTE_TESTS,
    }
)


@dataclass(frozen=True)
class Transition:
    src: Stage
    dst: Stage
    description: str
    blocking_gate: bool = False
    optional: bool = False


_PIPELINE: tuple[Transition, ...] = (
    Transition(Stage.INIT, Stage.UNDERSTAND_REQUIREMENT, "Parse natural-language task"),
    Transition(Stage.UNDERSTAND_REQUIREMENT, Stage.CLARIFY, "Detect ambiguity / missing constraints"),
    Transition(Stage.CLARIFY, Stage.SELECT_PROFILE, "Pick run profile (§2.6)"),
    Transition(Stage.SELECT_PROFILE, Stage.INGEST_KB, "Ingest optional KB (§2.8)"),
    Transition(Stage.INGEST_KB, Stage.ANALYZE_STACK, "Continue to tech-stack analysis"),
    Transition(Stage.ANALYZE_STACK, Stage.RESEARCH_ACADEMIC, "Begin academic research"),
    Transition(Stage.RESEARCH_ACADEMIC, Stage.RESEARCH_GITHUB, "Begin GitHub research"),
    Transition(Stage.RESEARCH_GITHUB, Stage.RESEARCH_INDUSTRY, "Begin industry research"),
    Transition(Stage.RESEARCH_INDUSTRY, Stage.FIRST_PRINCIPLES, "If algorithm task", optional=True),
    Transition(Stage.FIRST_PRINCIPLES, Stage.CROSS_COMPARE, "Compare research outputs"),
    Transition(Stage.RESEARCH_INDUSTRY, Stage.CROSS_COMPARE, "Skip first principles (non-algorithm)"),
    Transition(Stage.CROSS_COMPARE, Stage.GENERATE_INSIGHTS, "Render per-source insight reports (§2.4.A/B/C)"),
    Transition(
        Stage.GENERATE_INSIGHTS,
        Stage.GATE_RESEARCH_ADOPTION,
        "Await user adoption of research",
        blocking_gate=True,
    ),
    Transition(Stage.GATE_RESEARCH_ADOPTION, Stage.DRAFT_DOCS, "Research adopted → draft SRS/TDD"),
    Transition(Stage.DRAFT_DOCS, Stage.DRAFT_LAYER_DOCS, "Draft four-layer technical pack (§4.4)"),
    Transition(
        Stage.DRAFT_LAYER_DOCS,
        Stage.GATE_DOC_SIGNOFF,
        "Await user sign-off (merged SRS/TDD + layer pack)",
        blocking_gate=True,
    ),
    Transition(Stage.GATE_DOC_SIGNOFF, Stage.BUILD_DEMO, "Documents signed off → build demo"),
    Transition(Stage.BUILD_DEMO, Stage.GENERATE_TESTS_AND_CI, "Generate test spec + CI"),
    Transition(Stage.GENERATE_TESTS_AND_CI, Stage.EXECUTE_TESTS, "Execute generated tests"),
    Transition(Stage.EXECUTE_TESTS, Stage.ALIGNMENT_REPORT, "LLM semantic alignment vs SRS/TDD"),
    Transition(Stage.ALIGNMENT_REPORT, Stage.DONE, "Run complete"),
)


HandlerFn = Callable[..., None]


class StateMachine:
    """Declarative pipeline."""

    def __init__(self) -> None:
        self._transitions = list(_PIPELINE)
        self._handlers: dict[Stage, HandlerFn] = {}

    # ---- iteration ----------------------------------------------------

    @property
    def transitions(self) -> list[Transition]:
        return list(self._transitions)

    def next_stage(self, current: Stage, *, took_optional_branch: bool = False) -> Stage:
        """Return the stage that immediately follows ``current``.

        ``took_optional_branch`` lets the caller pick the variant transition
        from a multi-edge source (e.g. RESEARCH_INDUSTRY → FIRST_PRINCIPLES
        when the task is algorithmic, else RESEARCH_INDUSTRY → CROSS_COMPARE).
        """
        candidates = [t for t in self._transitions if t.src == current]
        if not candidates:
            return Stage.DONE
        if len(candidates) == 1:
            return candidates[0].dst
        for transition in candidates:
            if transition.optional == took_optional_branch:
                return transition.dst
        return candidates[0].dst

    # ---- registration --------------------------------------------------

    def register(self, stage: Stage, handler: HandlerFn) -> None:
        """Attach a handler that will execute when the orchestrator enters ``stage``."""
        self._handlers[stage] = handler

    def handler(self, stage: Stage) -> HandlerFn | None:
        return self._handlers.get(stage)

    def blocking_gates(self) -> list[Stage]:
        return [t.dst for t in self._transitions if t.blocking_gate]
