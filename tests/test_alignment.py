"""LLM alignment parser: lenient JSON extraction."""

from __future__ import annotations

from pathlib import Path

from protogenius.llm import RecordingLLMClient
from protogenius.testing.alignment import AlignmentRunner


def test_parser_extracts_fenced_json(run_context, tmp_path: Path):
    canned = (
        "Some reasoning prelude.\n"
        "```json\n"
        '{"satisfies_requirements": true, "confidence": 0.7, "reasoning_chain": ["a", "b"], "issues": [], "improvements": ["x"]}\n'
        "```\nTrailing text."
    )
    llm = RecordingLLMClient(canned=[canned])
    runner = AlignmentRunner(llm=llm)
    srs = tmp_path / "srs.md"
    tdd = tmp_path / "tdd.md"
    srs.write_text("# SRS\n")
    tdd.write_text("# TDD\n")
    report = runner.run(
        run_context,
        srs_path=srs,
        tdd_path=tdd,
        test_summary="all green",
        demo_summary="single FastAPI app",
    )
    assert report.satisfies_requirements is True
    assert report.confidence == 0.7
    assert report.reasoning_chain == ["a", "b"]
    assert report.improvements == ["x"]


def test_parser_falls_back_when_unparseable(run_context, tmp_path: Path):
    llm = RecordingLLMClient(canned=["not json"])
    runner = AlignmentRunner(llm=llm)
    report = runner.run(
        run_context,
        srs_path=tmp_path / "srs.md",
        tdd_path=tmp_path / "tdd.md",
        test_summary="",
        demo_summary="",
    )
    assert report.satisfies_requirements is False
    assert report.confidence == 0.0
    assert any("could not be parsed" in step for step in report.reasoning_chain)
