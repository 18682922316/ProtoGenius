"""arXiv search via the user-configured MCP server (§2.4.2).

This adapter speaks **MCP**, not the raw arXiv API. The MCP server URL or
stdio command is configured under ``mcp.arxiv`` in ``config/default.yaml``
(or the env override ``PROTOGENIUS_ARXIV_MCP_URL``).

The class is provider-agnostic: it sends an MCP ``tools/call`` request named
``arxiv.search`` and expects a normalized list of papers back. If your MCP
server exposes a different tool name, supply it via ``tool_name``.

For offline / unit-test use, pass ``http_client=httpx.Client(transport=…)``
or use the `RecordingArxivAdapter` for a deterministic stub.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from ..context import ResearchItem, RunContext
from .base import SearchAdapter, SearchQuery


@dataclass
class ArxivMcpAdapter(SearchAdapter):
    name: str = "arxiv"
    tool_name: str = "arxiv.search"
    http_client: httpx.Client | None = None
    _client: httpx.Client = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._client = self.http_client or httpx.Client(timeout=60)

    def _endpoint(self, ctx: RunContext) -> str:
        url = os.environ.get(ctx.config.mcp.arxiv.url_env or "", "") or (
            ctx.config.mcp.arxiv.url or ""
        )
        if not url:
            raise RuntimeError(
                "arXiv MCP URL is not configured (mcp.arxiv.url_env / mcp.arxiv.url)"
            )
        return url.rstrip("/") + "/tools/call"

    def search(self, ctx: RunContext, query: SearchQuery) -> list[ResearchItem]:
        window_days = query.window_days or ctx.config.research.academic.arxiv_window_days
        since = (datetime.now(UTC) - timedelta(days=window_days)).date().isoformat()
        payload: dict[str, Any] = {
            "name": self.tool_name,
            "arguments": {
                "query": query.text,
                "limit": query.max_results,
                "since": since,
                "categories": ["cs.AI", "cs.CL", "cs.LG", "cs.SE"],
            },
        }
        response = self._client.post(self._endpoint(ctx), json=payload)
        response.raise_for_status()
        data = response.json()
        results: list[ResearchItem] = []
        for entry in (data.get("content") or data.get("results") or []):
            results.append(
                ResearchItem(
                    title=entry.get("title", "(untitled)"),
                    source_type="arxiv",
                    summary=entry.get("abstract", "") or entry.get("summary", ""),
                    url=entry.get("url", ""),
                    doi=entry.get("doi", ""),
                    version=entry.get("version", ""),
                    institutions=list(entry.get("affiliations", []) or []),
                    extra={"arxiv_id": entry.get("id", "")},
                )
            )
        return results


@dataclass
class RecordingArxivAdapter(SearchAdapter):
    """Deterministic stub useful in tests / dry-runs."""

    name: str = "arxiv"
    canned: list[ResearchItem] = field(default_factory=list)
    last_query: SearchQuery | None = field(default=None, repr=False)

    def search(self, ctx: RunContext, query: SearchQuery) -> list[ResearchItem]:
        self.last_query = query
        return list(self.canned)
