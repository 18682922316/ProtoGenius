"""Layer-doc indexing + ``kb_ref`` resolution + conflict detection.

A KB root that follows the recommended layout::

    kb_root/
    ├── foundation_theory/
    │   ├── information_theory.md
    │   └── ...
    ├── atomic_algorithm/
    │   ├── beam_search.md
    │   └── ...
    ├── tech_topic/
    │   └── ...
    └── ai_application/
        └── ...

is the easiest case: :func:`discover_layer_docs` will just walk it. If
the KB uses a flat layout, the indexer falls back to reading each
file's YAML frontmatter ``layer:`` key.

``kb_ref`` strings have the form ``kb://<layer>/<relative-path>@<rev>``.
The ``<rev>`` segment is whatever the source supplied (commit hash for
GitHub-backed KB, file mtime for local-backed KB).
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from ..context import LayerDoc

_FRONTMATTER_RE = re.compile(r"^---\s*\n(?P<body>.*?)\n---\s*\n", re.DOTALL)
_LAYER_LINE_RE = re.compile(r"^\s*layer\s*:\s*(?P<layer>[a-z_]+)\s*$", re.MULTILINE)

KNOWN_LAYERS = {"foundation_theory", "atomic_algorithm", "tech_topic", "ai_application"}


@dataclass(frozen=True)
class KbConflict:
    """A disagreement between a freshly-generated doc and a KB doc."""

    layer: str
    kb_ref: str
    summary: str


def discover_layer_docs(root: Path) -> dict[str, list[Path]]:
    """Walk ``root`` and return ``{layer_id: [paths]}``.

    The function prefers a hierarchical layout (one directory per layer)
    and falls back to scanning every ``.md`` file's frontmatter for the
    ``layer:`` key.
    """
    index: dict[str, list[Path]] = {layer: [] for layer in KNOWN_LAYERS}
    if not root.is_dir():
        return index

    for child in root.iterdir():
        if child.is_dir() and child.name in KNOWN_LAYERS:
            for md in sorted(child.rglob("*.md")):
                index[child.name].append(md)

    # Fallback: scan any stray .md files at the root for frontmatter.
    for md in sorted(root.rglob("*.md")):
        if any(md in paths for paths in index.values()):
            continue
        layer = _layer_from_frontmatter(md)
        if layer in KNOWN_LAYERS:
            index[layer].append(md)
    return index


def resolve_kb_ref(
    *,
    root: Path,
    file_path: Path,
    revision: str,
) -> str:
    """Build a stable ``kb_ref`` URI for ``file_path`` inside the KB."""
    layer = _layer_from_path(root, file_path) or _layer_from_frontmatter(file_path) or "unknown"
    relative = file_path.relative_to(root)
    rev = revision or "head"
    return f"kb://{layer}/{relative.as_posix()}@{rev}"


def detect_conflicts(
    *,
    generated_layer: LayerDoc,
    kb_doc_paths: Iterable[Path],
    same_topic_keywords: Iterable[str] | None = None,
) -> list[KbConflict]:
    """Surface obvious-looking conflicts between a generated doc and KB docs.

    The detector is intentionally **lightweight**: it does not attempt to
    parse semantics. It flags pairs where the KB doc and the freshly
    generated doc share a topic keyword AND the KB doc's frontmatter
    ``name:`` field differs from the generated doc's name (a heuristic
    that mostly catches version drift). The sub-agent in charge of the
    review can then decide how to surface the conflict to the user.
    """
    keywords = {k.strip().lower() for k in (same_topic_keywords or []) if k.strip()}
    conflicts: list[KbConflict] = []
    for kb_path in kb_doc_paths:
        text = _safe_read(kb_path)
        if not text:
            continue
        kb_name = _frontmatter_value(text, "name") or kb_path.stem
        kb_layer = _frontmatter_value(text, "layer") or generated_layer.layer
        if kb_layer != generated_layer.layer:
            continue
        if kb_name.strip().lower() == generated_layer.name.strip().lower():
            continue
        text_lower = text.lower()
        if keywords and not any(kw in text_lower for kw in keywords):
            continue
        conflicts.append(
            KbConflict(
                layer=generated_layer.layer,
                kb_ref=f"kb://{kb_layer}/{kb_path.name}@head",
                summary=(
                    f"KB doc {kb_name!r} appears related but differs from "
                    f"generated {generated_layer.name!r}"
                ),
            )
        )
    return conflicts


# ---- helpers -------------------------------------------------------------


def _layer_from_path(root: Path, file_path: Path) -> str | None:
    try:
        rel = file_path.relative_to(root)
    except ValueError:
        return None
    parts = rel.parts
    if parts and parts[0] in KNOWN_LAYERS:
        return parts[0]
    return None


def _layer_from_frontmatter(path: Path) -> str | None:
    text = _safe_read(path)
    if not text:
        return None
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None
    body = match.group("body")
    layer_match = _LAYER_LINE_RE.search(body)
    if not layer_match:
        return None
    layer = layer_match.group("layer").strip()
    return layer if layer in KNOWN_LAYERS else None


def _frontmatter_value(text: str, key: str) -> str:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return ""
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(?P<value>.+?)\s*$", re.MULTILINE)
    value_match = pattern.search(match.group("body"))
    return value_match.group("value").strip() if value_match else ""


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""
