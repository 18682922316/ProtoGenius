"""Paper deduplication.

Per §2.4.2, "same work across multiple versions" must collapse into a single
entry. We use a two-step heuristic:

1. If two items share an arXiv canonical id (e.g. ``2406.12345`` ignoring the
   ``v1`` / ``v2`` suffix), they are duplicates.
2. Otherwise we fall back to a normalized-title + first-author match.

The function preserves the **first** occurrence — adapters should call it
once per result batch so that the highest-priority adapter (typically
``arxiv`` for very recent work) wins on ties.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable

from ..context import ResearchItem

_ARXIV_VERSION_RE = re.compile(r"^(?P<base>\d{4}\.\d{4,5})v\d+$")
_TITLE_PUNCT_RE = re.compile(r"[^\w\s]+", flags=re.UNICODE)


def _arxiv_canonical(item: ResearchItem) -> str:
    """Return an arXiv canonical id without the ``vN`` suffix, or ''."""
    candidate = item.extra.get("arxiv_id") if item.extra else ""
    if not candidate and "arxiv.org/abs/" in (item.url or ""):
        candidate = item.url.rsplit("/", 1)[-1]
    if not candidate:
        return ""
    match = _ARXIV_VERSION_RE.match(candidate)
    return match.group("base") if match else candidate


def _normalize_title(title: str) -> str:
    folded = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    folded = _TITLE_PUNCT_RE.sub(" ", folded.lower())
    return " ".join(folded.split())


def deduplicate_papers(items: Iterable[ResearchItem]) -> list[ResearchItem]:
    """Collapse arXiv version variants and title-equivalent duplicates."""
    seen_arxiv: set[str] = set()
    seen_titles: set[str] = set()
    out: list[ResearchItem] = []
    for item in items:
        arxiv_id = _arxiv_canonical(item)
        if arxiv_id:
            if arxiv_id in seen_arxiv:
                continue
            seen_arxiv.add(arxiv_id)
        else:
            key = _normalize_title(item.title)
            if not key:
                continue
            if key in seen_titles:
                continue
            seen_titles.add(key)
        out.append(item)
    return out
