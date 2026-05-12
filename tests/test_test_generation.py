"""Test spec materialization + CI workflow generation."""

from __future__ import annotations

from pathlib import Path

from protogenius.testing import (
    materialize_spec,
    render_github_actions_workflow,
)
from protogenius.testing.spec_layer import TestCase, TestSpec


def _spec_with_e2e() -> TestSpec:
    return TestSpec.from_iterable(
        [
            TestCase(id="TC-1", refs=["REQ-FN-1"], kind="unit", steps=["x"], expected="y"),
            TestCase(
                id="TC-2",
                refs=["REQ-FN-2"],
                kind="e2e",
                steps=["click"],
                expected="title visible",
                runner_hint="playwright",
            ),
        ]
    )


def test_pytest_materialization(tmp_path: Path):
    spec = TestSpec.from_iterable(
        [TestCase(id="TC-1", refs=["REQ-FN-1"], kind="unit", steps=["x"], expected="y")]
    )
    paths = materialize_spec(spec, tmp_path)
    assert any(p.name == "test_generated.py" for p in paths)
    content = (tmp_path / "test_generated.py").read_text()
    assert "def test_tc_1" in content


def test_unsupported_runner_writes_markdown(tmp_path: Path):
    spec = TestSpec.from_iterable(
        [
            TestCase(
                id="TC-X",
                refs=["REQ-FN-3"],
                kind="integration",
                steps=["go"],
                expected="done",
                runner_hint="exotic",
            )
        ]
    )
    paths = materialize_spec(spec, tmp_path)
    assert any(p.name.startswith("_unsupported_") for p in paths)


def test_ci_workflow_adds_e2e_job_only_when_needed():
    yaml_text = render_github_actions_workflow(_spec_with_e2e())
    assert "ubuntu-latest, windows-latest" in yaml_text
    assert "e2e:" in yaml_text
    plain = render_github_actions_workflow(
        TestSpec.from_iterable(
            [TestCase(id="TC-1", refs=[], kind="unit", steps=[], expected="x")]
        )
    )
    assert "e2e:" not in plain
