"""Semantic Scholar adapter — secondary academic channel.

Used in addition to arXiv MCP to cover *published* venue papers within the
1-year window. The optional API key reduces rate-limit pressure but is not
required for low-volume use; ``ProtoGenius`` always falls back to anonymous
calls.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..context import ResearchItem, RunContext
from .base import SearchAdapter, SearchQuery

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
DEFAULT_FIELDS = (
    "title,abstract,year,externalIds,url,authors.affiliations,venue,publicationVenue"
)


@dataclass
class SemanticScholarAdapter(SearchAdapter):
    name: str = "semantic_scholar"
    http_client: httpx.Client | None = None
    _client: httpx.Client = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._client = self.http_client or httpx.Client(timeout=60)

    def _headers(self) -> dict[str, str]:
        key = os.environ.get("PROTOGENIUS_SEMANTIC_SCHOLAR_API_KEY", "")
        return {"x-api-key": key} if key else {}

    def search(self, ctx: RunContext, query: SearchQuery) -> list[ResearchItem]:
        params: dict[str, Any] = {
            "query": query.text,
            "limit": min(query.max_results, 25),
            "fields": DEFAULT_FIELDS,
        }
        response = self._client.get(
            f"{SEMANTIC_SCHOLAR_API}/paper/search",
            params=params,
            headers=self._headers(),
        )
        response.raise_for_status()
        data = response.json()
        out: list[ResearchItem] = []
        for entry in data.get("data", []):
            ext = entry.get("externalIds") or {}
            doi = ext.get("DOI", "")
            arxiv_id = ext.get("ArXiv", "")
            venue_info = entry.get("publicationVenue") or {}
            url = entry.get("url") or (
                f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""
            )
            out.append(
                ResearchItem(
                    title=entry.get("title", "(untitled)"),
                    source_type="conference",
                    summary=entry.get("abstract", "") or "",
                    url=url,
                    doi=doi,
                    version=str(entry.get("year") or ""),
                    institutions=_collect_institutions(entry),
                    extra={
                        "arxiv_id": arxiv_id,
                        "venue": entry.get("venue", "") or venue_info.get("name", ""),
                    },
                )
            )
        return out


def _collect_institutions(paper: dict[str, Any]) -> list[str]:
    affiliations: set[str] = set()
    for author in paper.get("authors", []) or []:
        for aff in author.get("affiliations", []) or []:
            if isinstance(aff, str) and aff:
                affiliations.add(aff)
    return sorted(affiliations)
