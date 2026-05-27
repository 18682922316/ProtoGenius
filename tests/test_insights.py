"""v2 §2.4.A/B/C — insight report generator."""

from __future__ import annotations

from pathlib import Path

import pytest

from protogenius.context import ResearchItem
from protogenius.docs import InsightGenerator, InsightMinimumContentError


def test_academic_insight_writes_to_disk(run_context):
    item = ResearchItem(
        title="Beam search variants",
        source_type="arxiv",
        summary="exhaustive review",
        url="https://arxiv.org/abs/2306.00001",
    )
    body = {
        "core_conclusions": "Adaptive beam width improves recall by 8%",
        "innovation": "ABC",
    }
    gen = InsightGenerator()
    report = gen.render_for_research_item(run_context, item, body=body)
    assert report.insight_type == "academic"
    assert report.path is not None
    assert report.path.is_file()
    text = report.path.read_text(encoding="utf-8")
    assert "insight_type: academic" in text
    assert "Adaptive beam width" in text
    assert "## coverage_note" in text


def test_oss_insight_uses_github_template(run_context):
    item = ResearchItem(
        title="example-org/cool-repo",
        source_type="github",
        url="https://github.com/example-org/cool-repo",
        stars=1200,
        release_frequency_per_year=4.0,
    )
    report = InsightGenerator().render_for_research_item(
        run_context,
        item,
        body={"core_conclusions": "great repo"},
    )
    assert report.insight_type == "oss"
    assert "insight_type: oss" in report.path.read_text(encoding="utf-8")


def test_enterprise_insight_carries_uncertainty(run_context):
    item = ResearchItem(
        title="OpenAI — Reasoning models",
        source_type="industry",
        url="https://openai.com/blog/reasoning",
        institutions=["OpenAI"],
        extra={"source_label": "blog", "uncertainty": "Inferred from public web; ..."},
    )
    report = InsightGenerator().render_for_research_item(
        run_context,
        item,
        body={"core_conclusions": "RM is interesting"},
    )
    text = report.path.read_text(encoding="utf-8")
    assert "insight_type: enterprise" in text
    assert "Inferred from public web" in text


def test_missing_minimum_content_raises_when_strict(run_context):
    item = ResearchItem(title="No URL", source_type="arxiv")
    with pytest.raises(InsightMinimumContentError):
        InsightGenerator().render_for_research_item(run_context, item, body={})


def test_minimum_content_can_be_relaxed(run_context):
    run_context.config.insights.enforce_minimum_content = False
    item = ResearchItem(title="No URL", source_type="arxiv")
    report = InsightGenerator().render_for_research_item(run_context, item, body={})
    assert isinstance(report.path, Path)


def test_render_all_iterates_each_stream(run_context):
    run_context.config.insights.enforce_minimum_content = False
    run_context.research.academic.append(
        ResearchItem(title="A", source_type="arxiv", url="https://example.com/a")
    )
    run_context.research.github.append(
        ResearchItem(title="org/r", source_type="github", url="https://github.com/org/r")
    )
    run_context.research.industry.append(
        ResearchItem(
            title="V — blog",
            source_type="industry",
            url="https://v.example.com/blog",
            institutions=["V"],
        )
    )
    reports = InsightGenerator().render_all(run_context)
    assert len(reports) == 3
    types = {r.insight_type for r in reports}
    assert {"academic", "oss", "enterprise"}.issubset(types)
