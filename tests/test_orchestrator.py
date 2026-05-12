"""End-to-end orchestrator smoke test (dry-run, no network)."""

from __future__ import annotations

from pathlib import Path

from protogenius.config import load_config
from protogenius.context import ClarificationRound, ResearchItem, TechStackOption
from protogenius.docs import SrsGenerator, TddGenerator
from protogenius.orchestrator import Orchestrator, OrchestratorOptions
from protogenius.state_machine import Stage


def _make_handlers(orch: Orchestrator) -> None:
    """Wire deterministic stub handlers so the orchestrator can complete."""

    def understand(ctx, _o):
        ctx.structured_requirements = {
            "functions": ["search corpus", "render UI"],
            "users": "single power user",
            "functional": [{"id": "REQ-FN-001", "text": "Index corpus."}],
        }

    def clarify(ctx, _o):
        ctx.clarifications.append(ClarificationRound(question="?", answer="yes"))

    def stack(ctx, _o):
        ctx.stack_options = [
            TechStackOption(name="A", language="Python", runtime="FastAPI"),
        ]
        ctx.chosen_stack = ctx.stack_options[0]
        ctx.structured_requirements["stack_options"] = [
            {"name": "A", "language": "Python", "runtime": "FastAPI", "rationale": "fast"}
        ]

    def research_academic(ctx, _o):
        ctx.research.academic.append(
            ResearchItem(title="paper", source_type="arxiv", url="https://example.com/x")
        )

    def research_github(ctx, _o):
        ctx.research.github.append(
            ResearchItem(
                title="org/repo",
                source_type="github",
                url="https://github.com/org/repo",
                stars=100,
                release_frequency_per_year=2.0,
            )
        )

    def research_industry(ctx, _o):
        ctx.research.industry.append(
            ResearchItem(
                title="OpenAI blog",
                source_type="industry",
                url="https://openai.com/blog/x",
            )
        )
        # No algorithm task → return falsy so the next-stage selector picks
        # the non-optional edge (RESEARCH_INDUSTRY → CROSS_COMPARE).
        return False

    def cross_compare(ctx, _o):
        ctx.research.common_challenges = ["shared challenge"]

    def draft_docs(ctx, _o):
        srs = SrsGenerator().render(ctx)
        tdd = TddGenerator().render(ctx, srs_path=srs)
        from protogenius.context import DocumentArtifact

        ctx.documents.extend(
            [
                DocumentArtifact(name="srs", path=srs),
                DocumentArtifact(name="tdd", path=tdd),
            ]
        )

    def build_demo(ctx, _o):
        from protogenius.demo.scaffolds import scaffold
        from protogenius.demo.selector import DemoKind

        root = ctx.run_dir / "prototype"
        scaffold(DemoKind.SCRIPT, root)
        ctx.demo_root = root

    def gen_tests(ctx, _o):
        from protogenius.context import TestArtifact
        from protogenius.testing.ci_generator import render_github_actions_workflow
        from protogenius.testing.spec_layer import TestCase, TestSpec

        spec = TestSpec.from_iterable(
            [
                TestCase(
                    id="TC-001",
                    refs=["REQ-FN-001"],
                    kind="unit",
                    steps=["call thing"],
                    expected="returns ok",
                )
            ]
        )
        path = spec.save(ctx.run_dir / "tests" / "spec.yaml")
        ci_path = ctx.run_dir / "tests" / ".github" / "workflows" / "prototype-ci.yml"
        ci_path.parent.mkdir(parents=True, exist_ok=True)
        ci_path.write_text(render_github_actions_workflow(spec))
        ctx.tests.append(TestArtifact(spec_path=path, runner="pytest", ci_path=ci_path))

    def execute_tests(_ctx, _o):
        return None

    def alignment(ctx, _o):
        from protogenius.context import AlignmentReport

        ctx.alignment = AlignmentReport(
            confidence=0.6,
            reasoning_chain=["dry-run"],
            issues=[],
            improvements=[],
            satisfies_requirements=True,
        )

    orch.register(Stage.UNDERSTAND_REQUIREMENT, understand)
    orch.register(Stage.CLARIFY, clarify)
    orch.register(Stage.ANALYZE_STACK, stack)
    orch.register(Stage.RESEARCH_ACADEMIC, research_academic)
    orch.register(Stage.RESEARCH_GITHUB, research_github)
    orch.register(Stage.RESEARCH_INDUSTRY, research_industry)
    orch.register(Stage.CROSS_COMPARE, cross_compare)
    orch.register(Stage.DRAFT_DOCS, draft_docs)
    orch.register(Stage.BUILD_DEMO, build_demo)
    orch.register(Stage.GENERATE_TESTS_AND_CI, gen_tests)
    orch.register(Stage.EXECUTE_TESTS, execute_tests)
    orch.register(Stage.ALIGNMENT_REPORT, alignment)


def test_orchestrator_full_pipeline_dry_run(tmp_path: Path):
    config = load_config()
    orch = Orchestrator(
        config,
        options=OrchestratorOptions(dry_run=True, interactive=False, on_gate=lambda *_: True),
    )
    _make_handlers(orch)
    ctx = orch.run("test task", workspace=tmp_path)
    assert not ctx.aborted
    assert ctx.demo_root and ctx.demo_root.is_dir()
    assert ctx.alignment and ctx.alignment.satisfies_requirements
    assert (ctx.run_dir / "documents" / "srs.md").is_file()
    assert (ctx.run_dir / "documents" / "tdd.md").is_file()
    audit = (ctx.run_dir / config.audit.artifact_file).read_text()
    assert "GATE_RESEARCH_ADOPTION" in audit
    assert "GATE_DOC_SIGNOFF" in audit


def test_orchestrator_aborts_on_gate_refusal(tmp_path: Path):
    config = load_config()
    orch = Orchestrator(
        config,
        options=OrchestratorOptions(dry_run=True, interactive=False, on_gate=lambda *_: False),
    )
    _make_handlers(orch)
    ctx = orch.run("test task", workspace=tmp_path)
    assert ctx.aborted
    assert "gate" in ctx.abort_reason
