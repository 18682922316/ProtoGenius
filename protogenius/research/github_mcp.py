"""GitHub adapter — via the **Copilot-hosted MCP** (§2.4.3).

The hosted MCP endpoint is fixed by contract:

    https://api.githubcopilot.com/mcp/

The adapter speaks MCP ``tools/call`` and expects two tools:

- ``github.search_repositories`` — returns repos with at least stars / pushed_at.
- ``github.releases``           — returns recent releases for a repo.

Per the v1 ranking contract, this adapter does **not** itself enforce the
ranking — it returns raw repos, and `protogenius.research.ranking.RepoRanking`
applies the cutoff_include_all policy downstream.
"""

from __future__ import annotations

import datetime as _dt
import os
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..context import ResearchItem, RunContext
from .base import SearchAdapter, SearchQuery


@dataclass
class GitHubMcpAdapter(SearchAdapter):
    name: str = "github"
    search_tool: str = "github.search_repositories"
    releases_tool: str = "github.releases"
    http_client: httpx.Client | None = None
    _client: httpx.Client = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._client = self.http_client or httpx.Client(timeout=60)

    def _endpoint(self, ctx: RunContext) -> str:
        url = ctx.config.mcp.github.url or "https://api.githubcopilot.com/mcp/"
        return url.rstrip("/") + "/tools/call"

    def _headers(self, ctx: RunContext) -> dict[str, str]:
        token = os.environ.get(ctx.config.mcp.github.token_env or "", "") or os.environ.get(
            "PROTOGENIUS_GITHUB_TOKEN", ""
        )
        return {"Authorization": f"Bearer {token}"} if token else {}

    def search(self, ctx: RunContext, query: SearchQuery) -> list[ResearchItem]:
        payload: dict[str, Any] = {
            "name": self.search_tool,
            "arguments": {
                "query": query.text,
                "sort": "stars",
                "order": "desc",
                "per_page": min(query.max_results, 25),
            },
        }
        response = self._client.post(
            self._endpoint(ctx), json=payload, headers=self._headers(ctx)
        )
        response.raise_for_status()
        raw = response.json()
        repos = raw.get("content") or raw.get("items") or []

        results: list[ResearchItem] = []
        for repo in repos:
            full_name = repo.get("full_name") or repo.get("name", "")
            html_url = repo.get("html_url") or f"https://github.com/{full_name}"
            stars = int(repo.get("stargazers_count") or repo.get("stars") or 0)
            release_freq = self._release_frequency(ctx, full_name)
            results.append(
                ResearchItem(
                    title=full_name,
                    source_type="github",
                    summary=repo.get("description", "") or "",
                    url=html_url,
                    stars=stars,
                    release_frequency_per_year=release_freq,
                    extra={"default_branch": repo.get("default_branch", "")},
                )
            )
        return results

    # ---- helpers -------------------------------------------------------

    def _release_frequency(self, ctx: RunContext, full_name: str) -> float | None:
        """Releases per year over the last 365 days. Returns None when unknown."""
        if not full_name:
            return None
        try:
            response = self._client.post(
                self._endpoint(ctx),
                json={
                    "name": self.releases_tool,
                    "arguments": {"repo": full_name, "limit": 30},
                },
                headers=self._headers(ctx),
            )
            response.raise_for_status()
        except httpx.HTTPError:
            return None
        releases = (response.json().get("content") or response.json().get("releases") or [])
        if not releases:
            return None
        cutoff = _dt.datetime.now(_dt.UTC) - _dt.timedelta(days=365)
        recent = 0
        for release in releases:
            published = release.get("published_at") or release.get("created_at")
            if not published:
                continue
            try:
                when = _dt.datetime.fromisoformat(published.replace("Z", "+00:00"))
            except ValueError:
                continue
            if when >= cutoff:
                recent += 1
        return float(recent)


@dataclass
class RecordingGitHubAdapter(SearchAdapter):
    """Deterministic stub. Returns a fixed list regardless of query."""

    name: str = "github"
    canned: list[ResearchItem] = field(default_factory=list)

    def search(self, ctx: RunContext, query: SearchQuery) -> list[ResearchItem]:  # noqa: ARG002
        return list(self.canned)
