"""v2 §2.5 — coverage_note helper."""

from __future__ import annotations

from protogenius.coverage import (
    REASON_EVIDENCE_MISSING,
    CoverageNote,
    check_insight_minimum,
    check_layer_doc_minimum,
)


def test_coverage_note_render_includes_present_and_absent():
    note = CoverageNote(artifact_id="A1", template_id="t")
    note.add_present("title")
    note.add_absent("conclusions", "missing evidence")
    rendered = note.render_markdown()
    assert "## coverage_note" in rendered
    assert "`title`" in rendered
    assert "`conclusions` — missing evidence" in rendered


def test_check_insight_minimum_violations():
    ok, violations = check_insight_minimum(
        identification_present=True,
        core_conclusions_present=False,
        auditable_citation_present=False,
    )
    assert not ok
    assert "core conclusions" in " ".join(violations)
    assert "citation" in " ".join(violations)


def test_check_layer_doc_minimum_passes_when_all_present():
    ok, violations = check_layer_doc_minimum(
        frontmatter_present=True,
        basic_info_present=True,
        formalization_block_present=True,
        references_present=True,
    )
    assert ok
    assert violations == []


def test_check_layer_doc_minimum_lists_each_missing():
    ok, violations = check_layer_doc_minimum(
        frontmatter_present=False,
        basic_info_present=False,
        formalization_block_present=False,
        references_present=False,
    )
    assert not ok
    assert len(violations) == 4


def test_reason_constants_exposed():
    assert REASON_EVIDENCE_MISSING
