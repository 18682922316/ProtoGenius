"""OpenAlex adapter — third academic channel.

OpenAlex requires no authentication but the docs *strongly* recommend a
contact email via the ``mailto`` parameter for polite-pool routing. The
adapter reads it from ``PROTOGENIUS_OPENALEX_EMAIL``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..context import ResearchItem, RunContext
from .base import SearchAdapter, SearchQuery

OPENALEX_API = "https://api.openalex.org"


@dataclass
class OpenAlexAdapter(SearchAdapter):
    name: str = "openalex"
    http_client: httpx.Client | None = None
    _client: httpx.Client = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._client = self.http_client or httpx.Client(timeout=60)

    def search(self, ctx: RunContext, query: SearchQuery) -> list[ResearchItem]:
        params: dict[str, Any] = {
            "search": query.text,
            "per-page": min(query.max_results, 25),
        }
        email = os.environ.get("PROTOGENIUS_OPENALEX_EMAIL", "")
        if email:
            params["mailto"] = email
        response = self._client.get(f"{OPENALEX_API}/works", params=params)
        response.raise_for_status()
        data = response.json()
        out: list[ResearchItem] = []
        for entry in data.get("results", []):
            doi = entry.get("doi", "") or ""
            if doi.startswith("https://doi.org/"):
                doi = doi[len("https://doi.org/") :]
            out.append(
                ResearchItem(
                    title=entry.get("title", "(untitled)"),
                    source_type="conference",
                    summary=(entry.get("abstract_inverted_index") and "[inverted-index abstract]")
                    or entry.get("title", ""),
                    url=entry.get("id", ""),
                    doi=doi,
                    version=str(entry.get("publication_year") or ""),
                    institutions=_extract_institutions(entry),
                    extra={"openalex_id": entry.get("id", "")},
                )
            )
        return out


def _extract_institutions(entry: dict[str, Any]) -> list[str]:
    seen: set[str] = set()
    for authorship in entry.get("authorships", []) or []:
        for inst in authorship.get("institutions", []) or []:
            name = inst.get("display_name", "")
            if name:
                seen.add(name)
    return sorted(seen)
