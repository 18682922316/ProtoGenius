"""Common types and pipeline harness for research adapters."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol

from ..context import ResearchItem, RunContext


@dataclass(frozen=True)
class SearchQuery:
    """Generic search query.

    Adapters extend the meaning of these fields as appropriate (e.g. the
    arXiv adapter respects ``window_days`` while the GitHub adapter ignores
    it and uses ``sort`` instead).
    """

    text: str
    max_results: int = 20
    window_days: int | None = None
    sort: str = ""
    extras: dict[str, str] = field(default_factory=dict)


class SearchAdapter(Protocol):
    """Minimum interface that the orchestrator depends on."""

    name: str

    def search(self, ctx: RunContext, query: SearchQuery) -> list[ResearchItem]:  # pragma: no cover
        ...


@dataclass
class ResearchPipeline:
    """Aggregates adapters and runs them with hook integration."""

    adapters: list[SearchAdapter] = field(default_factory=list)

    def register(self, adapter: SearchAdapter) -> None:
        self.adapters.append(adapter)

    def run(
        self,
        ctx: RunContext,
        queries: Sequence[SearchQuery],
        *,
        registry,
    ) -> list[ResearchItem]:
        """Execute every adapter against every query, invoking hooks."""
        collected: list[ResearchItem] = []
        for adapter in self.adapters:
            for query in queries:
                for hook in registry.pre_search:
                    hook(ctx, query.max_results)
                items = adapter.search(ctx, query)
                for hook in registry.post_research:
                    hook(ctx, items)
                collected.extend(items)
        return collected
