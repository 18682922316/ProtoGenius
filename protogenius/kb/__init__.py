"""v2 §2.8 — domain knowledge base connector.

The KB holds historical Markdown layer docs (foundation_theory /
atomic_algorithm / tech_topic / ai_application). It is **optional** —
when absent, ProtoGenius relies solely on external research.

Two sources are supported:

- ``local_path``  : a directory on the filesystem that holds layer docs.
- ``github_repo`` : ``owner/repo@ref:subdir`` cloned via ``git`` (shallow).

Both sources are normalized into a :class:`KnowledgeBaseSnapshot` that
indexes the docs by layer id and resolves them via :func:`resolve_kb_ref`.
"""

from .github import GitHubKb, parse_locator
from .indexer import (
    KbConflict,
    detect_conflicts,
    discover_layer_docs,
    resolve_kb_ref,
)
from .local import LocalKb

__all__ = [
    "GitHubKb",
    "KbConflict",
    "LocalKb",
    "detect_conflicts",
    "discover_layer_docs",
    "parse_locator",
    "resolve_kb_ref",
]
