"""v2 Appendix A — task input schema + profile derivation rules."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from protogenius.task_input import (
    KnowledgeBaseRef,
    ScopedInput,
    StructuredRequirementsSummary,
    TaskInput,
)


def test_unscoped_task_defaults_to_full_pipeline():
    ti = TaskInput(description="Build a knowledge base assistant")
    assert ti.resolve_profile() == "full_pipeline"
    assert ti.will_generate_demo() is True


def test_scoped_task_flips_to_research_and_docs_only():
    ti = TaskInput(
        description="Survey beam search variants",
        scoped_input=ScopedInput(type="algorithm", name="beam search"),
    )
    assert ti.resolve_profile() == "research_and_docs_only"
    assert ti.will_generate_demo() is False


def test_scoped_with_explicit_demo_opts_back_in():
    ti = TaskInput(
        description="Build a demo for beam search",
        scoped_input=ScopedInput(type="algorithm", name="beam search"),
        generate_prototype_demo=True,
    )
    assert ti.resolve_profile() == "full_pipeline"
    assert ti.will_generate_demo() is True


def test_scoped_input_requires_name_or_description():
    with pytest.raises(ValueError):
        ScopedInput(type="topic")


def test_kb_locator_validation():
    KnowledgeBaseRef(github_repo="acme/kb")
    KnowledgeBaseRef(github_repo="acme/kb@main")
    KnowledgeBaseRef(github_repo="acme/kb@main:docs/layers")
    with pytest.raises(ValidationError):
        KnowledgeBaseRef(github_repo="not a locator")


def test_structured_summary_completeness():
    summary = StructuredRequirementsSummary(
        core_objectives=["one"], challenges=["two"], constraints=["three"]
    )
    assert summary.is_complete is True
    assert StructuredRequirementsSummary().is_complete is False


def test_yaml_roundtrip(tmp_path: Path):
    yaml_payload = """\
task:
  description: "test task"
  profile: full_pipeline
  scoped_input:
    type: topic
    name: retrieval-augmented generation
  knowledge_base:
    github_repo: acme/kb@main:layers
  structured_requirements_summary:
    core_objectives: ["delivery on Linux+Windows"]
    challenges: ["dedup heuristics"]
    constraints: ["1M token budget"]
"""
    path = tmp_path / "task.yaml"
    path.write_text(yaml_payload, encoding="utf-8")
    ti = TaskInput.from_yaml(path)
    assert ti.scoped_input is not None
    assert ti.scoped_input.type == "topic"
    assert ti.knowledge_base is not None
    assert ti.knowledge_base.github_repo == "acme/kb@main:layers"
    assert ti.structured_requirements_summary.is_complete
    # Roundtrip back to YAML and re-parse.
    again = TaskInput.from_yaml(_write_yaml(tmp_path, ti))
    assert again.description == ti.description
    assert again.resolve_profile() == "research_and_docs_only"


def _write_yaml(tmp_path: Path, ti: TaskInput) -> Path:
    out = tmp_path / "roundtrip.yaml"
    out.write_text(ti.to_yaml(), encoding="utf-8")
    return out
