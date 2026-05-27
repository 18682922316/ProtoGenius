"""v2 §2.6 / §2.7 — profile-aware orchestrator behavior.

This test re-uses the orchestrator stub-handler harness from
``test_orchestrator.py`` and exercises the new branch where the run
profile is ``research_and_docs_only`` (e.g. via a scoped_input). In
that mode the orchestrator MUST skip BUILD_DEMO / GENERATE_TESTS_AND_CI
/ EXECUTE_TESTS but still produce the alignment report.
"""

from __future__ import annotations

from pathlib import Path

from protogenius.config import load_config
from protogenius.context import (
    AlignmentReport,
    ClarificationRound,
    DocumentArtifact,
    ResearchItem,
    TechStackOption,
)
from protogenius.docs import SrsGenerator, TddGenerator
from protogenius.orchestrator import Orchestrator, OrchestratorOptions
from protogenius.state_machine import Stage
from protogenius.task_input import ScopedInput, StructuredRequirementsSummary, TaskInput


def _stub_handlers(orch: Orchestrator) -> dict[str, list[Stage]]:
    """Register stub handlers and return a tracking dict for assertions."""
    visited: dict[str, list[Stage]] = {"stages": []}

    def track(stage: Stage):
        def _handler(_ctx, _o):
            visited["stages"].append(stage)
            return None

        return _handler

    def understand(ctx, _o):
        visited["stages"].append(Stage.UNDERSTAND_REQUIREMENT)
        ctx.structured_requirements = {
            "functions": ["analyze"], "users": "researcher", "functional": [],
        }

    def clarify(ctx, _o):
        visited["stages"].append(Stage.CLARIFY)
        ctx.clarifications.append(ClarificationRound(question="?", answer="yes"))

    def stack(ctx, _o):
        visited["stages"].append(Stage.ANALYZE_STACK)
        ctx.stack_options = [TechStackOption(name="A", language="Python", runtime="-")]
        ctx.chosen_stack = ctx.stack_options[0]

    def research_academic(ctx, _o):
        visited["stages"].append(Stage.RESEARCH_ACADEMIC)
        ctx.research.academic.append(
            ResearchItem(title="paper", source_type="arxiv", url="https://example.com/x")
        )

    def research_github(ctx, _o):
        visited["stages"].append(Stage.RESEARCH_GITHUB)
        ctx.research.github.append(
            ResearchItem(
                title="org/repo",
                source_type="github",
                url="https://github.com/org/repo",
                stars=10,
                release_frequency_per_year=2.0,
            )
        )

    def research_industry(ctx, _o):
        visited["stages"].append(Stage.RESEARCH_INDUSTRY)
        ctx.research.industry.append(
            ResearchItem(
                title="V — blog",
                source_type="industry",
                url="https://v.example.com",
                institutions=["V"],
            )
        )
        return False

    def cross_compare(ctx, _o):
        visited["stages"].append(Stage.CROSS_COMPARE)
        ctx.research.common_challenges = ["challenge"]

    def draft_docs(ctx, _o):
        visited["stages"].append(Stage.DRAFT_DOCS)
        srs = SrsGenerator().render(ctx)
        tdd = TddGenerator().render(ctx, srs_path=srs)
        ctx.documents.extend(
            [DocumentArtifact(name="srs", path=srs), DocumentArtifact(name="tdd", path=tdd)]
        )

    def alignment(ctx, _o):
        visited["stages"].append(Stage.ALIGNMENT_REPORT)
        ctx.alignment = AlignmentReport(
            confidence=0.5,
            reasoning_chain=["stub"],
            issues=[],
            improvements=[],
            satisfies_requirements=True,
        )

    orch.register(Stage.UNDERSTAND_REQUIREMENT, understand)
    orch.register(Stage.CLARIFY, clarify)
    orch.register(Stage.SELECT_PROFILE, track(Stage.SELECT_PROFILE))
    orch.register(Stage.INGEST_KB, track(Stage.INGEST_KB))
    orch.register(Stage.ANALYZE_STACK, stack)
    orch.register(Stage.RESEARCH_ACADEMIC, research_academic)
    orch.register(Stage.RESEARCH_GITHUB, research_github)
    orch.register(Stage.RESEARCH_INDUSTRY, research_industry)
    orch.register(Stage.CROSS_COMPARE, cross_compare)
    orch.register(Stage.GENERATE_INSIGHTS, track(Stage.GENERATE_INSIGHTS))
    orch.register(Stage.DRAFT_DOCS, draft_docs)
    orch.register(Stage.DRAFT_LAYER_DOCS, track(Stage.DRAFT_LAYER_DOCS))
    orch.register(Stage.BUILD_DEMO, track(Stage.BUILD_DEMO))
    orch.register(Stage.GENERATE_TESTS_AND_CI, track(Stage.GENERATE_TESTS_AND_CI))
    orch.register(Stage.EXECUTE_TESTS, track(Stage.EXECUTE_TESTS))
    orch.register(Stage.ALIGNMENT_REPORT, alignment)
    return visited


def test_scoped_input_skips_demo_stages(tmp_path: Path):
    config = load_config()
    orch = Orchestrator(
        config,
        options=OrchestratorOptions(dry_run=True, interactive=False, on_gate=lambda *_: True),
    )
    visited = _stub_handlers(orch)
    task = TaskInput(
        description="Survey beam-search variants",
        scoped_input=ScopedInput(type="algorithm", name="beam search"),
        structured_requirements_summary=StructuredRequirementsSummary(
            core_objectives=["produce insights"],
            challenges=["dedup"],
            constraints=["≤ 100 results"],
        ),
    )
    ctx = orch.run(task, workspace=tmp_path)
    assert not ctx.aborted
    assert ctx.effective_profile == "research_and_docs_only"
    # The demo stages MUST NOT have produced any handler invocations.
    assert Stage.BUILD_DEMO not in visited["stages"]
    assert Stage.GENERATE_TESTS_AND_CI not in visited["stages"]
    assert Stage.EXECUTE_TESTS not in visited["stages"]
    # Alignment still runs so the audit trail has a coverage verdict.
    assert Stage.ALIGNMENT_REPORT in visited["stages"]
    # Audit log records the profile and the skip events.
    audit = (ctx.run_dir / config.audit.artifact_file).read_text()
    assert '"profile": "research_and_docs_only"' in audit
    assert "stage skipped" in audit


def test_full_pipeline_runs_demo_stages(tmp_path: Path):
    config = load_config()
    orch = Orchestrator(
        config,
        options=OrchestratorOptions(dry_run=True, interactive=False, on_gate=lambda *_: True),
    )
    visited = _stub_handlers(orch)
    task = TaskInput(
        description="Build a tool",
        structured_requirements_summary=StructuredRequirementsSummary(
            core_objectives=["x"], challenges=["y"], constraints=["z"]
        ),
    )
    ctx = orch.run(task, workspace=tmp_path)
    assert ctx.effective_profile == "full_pipeline"
    assert Stage.BUILD_DEMO in visited["stages"]
    assert Stage.GENERATE_TESTS_AND_CI in visited["stages"]
    assert Stage.EXECUTE_TESTS in visited["stages"]


def test_split_signoff_runs_gate_twice(tmp_path: Path):
    config = load_config()
    # Opt out of the merge default — two consecutive gate confirmations.
    config = config.model_copy(
        update={
            "documents": config.documents.model_copy(
                update={"merge_tdd_and_layer_signoff": False}
            )
        }
    )
    confirms: list[Stage] = []

    def on_gate(stage: Stage, _snapshot: dict) -> bool:
        confirms.append(stage)
        return True

    orch = Orchestrator(
        config,
        options=OrchestratorOptions(dry_run=True, interactive=False, on_gate=on_gate),
    )
    _stub_handlers(orch)
    task = TaskInput(
        description="Anything",
        structured_requirements_summary=StructuredRequirementsSummary(
            core_objectives=["x"], challenges=["y"], constraints=["z"]
        ),
    )
    orch.run(task, workspace=tmp_path)
    # Expected gates: research_adoption + doc_signoff + doc_signoff (layer pack).
    doc_signoff_count = sum(1 for s in confirms if s == Stage.GATE_DOC_SIGNOFF)
    assert doc_signoff_count == 2
