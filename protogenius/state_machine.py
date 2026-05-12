"""Pipeline state machine — the spine of every ProtoGenius run.

A `Transition` represents one stage transition. A `StateMachine` is a fixed,
declarative pipeline whose stages mirror §2-§6 of the v1 requirements:

    UNDERSTAND_REQUIREMENT
      → CLARIFY (up to 3 rounds; failure → ABORTED)
      → ANALYZE_STACK (≤ 3 mutually exclusive options)
      → RESEARCH_ACADEMIC / RESEARCH_GITHUB / RESEARCH_INDUSTRY
      → (if algorithm task) FIRST_PRINCIPLES
      → CROSS_COMPARE
      → GATE_RESEARCH_ADOPTION   ← blocking, requires user confirmation
      → DRAFT_DOCS               (SRS / TDD / interfaces / arch)
      → GATE_DOC_SIGNOFF          ← blocking, requires user confirmation
      → BUILD_DEMO
      → GENERATE_TESTS_AND_CI
      → EXECUTE_TESTS
      → ALIGNMENT_REPORT
      → DONE

The machine itself is intentionally inert: ``Orchestrator.run`` is the active
party that walks transitions and calls each registered sub-agent. The
gate-check hook intercepts ``GATE_*`` transitions to pause for human input.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum


class Stage(StrEnum):
    INIT = "INIT"
    UNDERSTAND_REQUIREMENT = "UNDERSTAND_REQUIREMENT"
    CLARIFY = "CLARIFY"
    ANALYZE_STACK = "ANALYZE_STACK"
    RESEARCH_ACADEMIC = "RESEARCH_ACADEMIC"
    RESEARCH_GITHUB = "RESEARCH_GITHUB"
    RESEARCH_INDUSTRY = "RESEARCH_INDUSTRY"
    FIRST_PRINCIPLES = "FIRST_PRINCIPLES"
    CROSS_COMPARE = "CROSS_COMPARE"
    GATE_RESEARCH_ADOPTION = "GATE_RESEARCH_ADOPTION"
    DRAFT_DOCS = "DRAFT_DOCS"
    GATE_DOC_SIGNOFF = "GATE_DOC_SIGNOFF"
    BUILD_DEMO = "BUILD_DEMO"
    GENERATE_TESTS_AND_CI = "GENERATE_TESTS_AND_CI"
    EXECUTE_TESTS = "EXECUTE_TESTS"
    ALIGNMENT_REPORT = "ALIGNMENT_REPORT"
    DONE = "DONE"
    ABORTED = "ABORTED"


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
    Transition(Stage.CLARIFY, Stage.ANALYZE_STACK, "Clarification succeeded"),
    Transition(Stage.ANALYZE_STACK, Stage.RESEARCH_ACADEMIC, "Begin academic research"),
    Transition(Stage.RESEARCH_ACADEMIC, Stage.RESEARCH_GITHUB, "Begin GitHub research"),
    Transition(Stage.RESEARCH_GITHUB, Stage.RESEARCH_INDUSTRY, "Begin industry research"),
    Transition(Stage.RESEARCH_INDUSTRY, Stage.FIRST_PRINCIPLES, "If algorithm task", optional=True),
    Transition(Stage.FIRST_PRINCIPLES, Stage.CROSS_COMPARE, "Compare research outputs"),
    Transition(Stage.RESEARCH_INDUSTRY, Stage.CROSS_COMPARE, "Skip first principles (non-algorithm)"),
    Transition(
        Stage.CROSS_COMPARE,
        Stage.GATE_RESEARCH_ADOPTION,
        "Await user adoption of research",
        blocking_gate=True,
    ),
    Transition(Stage.GATE_RESEARCH_ADOPTION, Stage.DRAFT_DOCS, "Research adopted → draft SRS/TDD"),
    Transition(
        Stage.DRAFT_DOCS,
        Stage.GATE_DOC_SIGNOFF,
        "Await user document sign-off",
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
