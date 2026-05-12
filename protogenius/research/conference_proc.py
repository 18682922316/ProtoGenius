"""Conference proceedings scraper — placeholder for venue-specific crawlers.

The v1 contract mentions "various conference proceedings scrapers" alongside
Semantic Scholar and OpenAlex. Each venue has its own website layout, so this
module exposes a thin registry of venue scrapers and a default null adapter
that returns no results when the corresponding crawler is unavailable.

Implementations can be plugged in by adding a callable to ``REGISTRY`` keyed
on the venue id (e.g. ``ACL``); each callable receives ``(query, since_date)``
and returns a list of `ResearchItem`s.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from ..context import ResearchItem, RunContext
from .base import SearchAdapter, SearchQuery

VenueScraper = Callable[[SearchQuery, date], list[ResearchItem]]

REGISTRY: dict[str, VenueScraper] = {}


def register(venue: str, scraper: VenueScraper) -> None:
    """Plug a venue-specific scraper into the registry."""
    REGISTRY[venue.upper()] = scraper


@dataclass
class ConferenceProceedingsAdapter(SearchAdapter):
    name: str = "conference_proceedings"
    venues: list[str] = field(default_factory=list)

    def search(self, ctx: RunContext, query: SearchQuery) -> list[ResearchItem]:
        window_days = query.window_days or ctx.config.research.academic.venue_window_days
        since = (datetime.now(UTC) - timedelta(days=window_days)).date()
        out: list[ResearchItem] = []
        for venue in self.venues or ctx.config.research.academic.venues:
            scraper = REGISTRY.get(venue.upper())
            if scraper is None:
                continue
            out.extend(scraper(query, since))
        return out
