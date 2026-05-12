"""Industry / head-vendor research adapter (§2.4.4).

Scope (frozen for v1):

    Anthropic, OpenAI, DeepMind, ByteDance, Alibaba, Tencent, Meituan

Allowed sources:

    Official blog, product docs, technical reports.

Because most vendors do not expose a structured search API, this adapter
performs a permissive page fetch + a tagged "inferred from public web"
disclaimer. The disclaimer is recorded on every item so the human reviewer
sees the uncertainty before adopting research.

Multiple sources covering the same capability are kept **as separate items**
(``multi_source_merge: false`` in config).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import httpx

from ..context import ResearchItem, RunContext
from .base import SearchAdapter, SearchQuery

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_META_DESC_RE = re.compile(
    r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']',
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class IndustryAdapter(SearchAdapter):
    """Lightweight HTTP fetcher with a tiny title/description extractor.

    Production deployments are expected to swap this for an integrated search
    backend (e.g. a Brave / Tavily MCP). The contract this class enforces is
    the **scope filter** and the **uncertainty label**.
    """

    name: str = "industry"
    http_client: httpx.Client | None = None
    _client: httpx.Client = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._client = self.http_client or httpx.Client(timeout=30, follow_redirects=True)

    def search(self, ctx: RunContext, query: SearchQuery) -> list[ResearchItem]:  # noqa: ARG002
        from ..config import SEARCH_CONFIG
        from ..config import _load_yaml as load_yaml

        catalog = load_yaml(SEARCH_CONFIG).get("industry", {})
        targets = ctx.config.research.industry.targets
        uncertainty = catalog.get(
            "uncertainty_label", "Inferred from public web; may be incomplete or stale."
        )
        endpoints = catalog.get("targets", {})

        out: list[ResearchItem] = []
        for vendor in targets:
            urls = endpoints.get(vendor, {})
            for source_label, url in urls.items():
                title, summary = _peek(self._client, url)
                out.append(
                    ResearchItem(
                        title=f"{vendor} — {source_label}: {title}",
                        source_type="industry",
                        summary=summary,
                        url=url,
                        institutions=[vendor],
                        extra={"uncertainty": uncertainty, "source_label": source_label},
                    )
                )
        return out


def _peek(client: httpx.Client, url: str) -> tuple[str, str]:
    """Best-effort title + meta description extraction; never raises."""
    try:
        response = client.get(url)
        response.raise_for_status()
    except httpx.HTTPError:
        return ("(unreachable)", "(public web fetch failed)")
    text = response.text[:200_000]
    title_match = _TITLE_RE.search(text)
    desc_match = _META_DESC_RE.search(text)
    title = (title_match.group(1) if title_match else "").strip() or url
    summary = (desc_match.group(1) if desc_match else "").strip()
    return (title, summary or "(no meta description)")
