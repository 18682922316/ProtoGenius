"""Research adapters (academic, GitHub, industry).

All adapters implement the `SearchAdapter` protocol in ``base.py`` and are
registered into a `ResearchPipeline` that the orchestrator uses to run them
in sequence.

Provider-specific quirks (rate-limits, pagination, auth) belong inside each
adapter — the pipeline only sees normalised `ResearchItem` instances.
"""

from .base import ResearchPipeline, SearchAdapter, SearchQuery
from .dedup import deduplicate_papers
from .ranking import RepoRanking
from .scope import narrow_queries, select_layers

__all__ = [
    "RepoRanking",
    "ResearchPipeline",
    "SearchAdapter",
    "SearchQuery",
    "deduplicate_papers",
    "narrow_queries",
    "select_layers",
]
