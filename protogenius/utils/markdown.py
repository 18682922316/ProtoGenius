"""Tiny Markdown helpers used by document and report renderers.

Avoiding a Markdown library keeps the dependency footprint small; ProtoGenius
only needs:

- escaping pipes for safe table cells,
- rendering simple tables that always have a header row,
- formatting citation footnotes that the audit layer can cross-reference.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence


def escape_cell(value: object) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    return text or "—"


def table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    """Render a Markdown table. Returns a string with a trailing newline."""
    header_line = "| " + " | ".join(escape_cell(h) for h in headers) + " |"
    divider_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_lines = ["| " + " | ".join(escape_cell(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header_line, divider_line, *body_lines]) + "\n"


def citation_footnote(index: int, *, url: str = "", doi: str = "", version: str = "") -> str:
    parts: list[str] = []
    if doi:
        parts.append(f"DOI: `{doi}`")
    if url:
        parts.append(f"<{url}>")
    if version:
        parts.append(f"version `{version}`")
    body = "; ".join(parts) if parts else "(no source recorded)"
    return f"[^{index}]: {body}"
