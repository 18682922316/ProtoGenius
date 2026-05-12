"""Paper deduplication: arXiv-family collapse + title-fallback."""

from __future__ import annotations

from protogenius.context import ResearchItem
from protogenius.research.dedup import deduplicate_papers


def _item(title: str = "", url: str = "", arxiv_id: str = "") -> ResearchItem:
    return ResearchItem(
        title=title,
        source_type="arxiv" if arxiv_id else "conference",
        url=url,
        extra={"arxiv_id": arxiv_id} if arxiv_id else {},
    )


def test_dedup_collapses_arxiv_versions():
    items = [
        _item(title="A", arxiv_id="2406.12345v1"),
        _item(title="A v2 also", arxiv_id="2406.12345v2"),
        _item(title="B", arxiv_id="2406.99999v1"),
    ]
    deduped = deduplicate_papers(items)
    titles = [item.title for item in deduped]
    assert titles == ["A", "B"]


def test_dedup_falls_back_to_title_match():
    items = [
        _item(title="Transformer-based Foo: A Study"),
        _item(title="Transformer-based foo: a study."),
        _item(title="Different Title"),
    ]
    deduped = deduplicate_papers(items)
    assert len(deduped) == 2


def test_dedup_first_occurrence_wins():
    items = [
        _item(title="A", arxiv_id="2400.00001v1", url="first"),
        _item(title="A duplicate", arxiv_id="2400.00001v3", url="second"),
    ]
    deduped = deduplicate_papers(items)
    assert deduped[0].url == "first"
