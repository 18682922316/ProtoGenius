"""Build small Mermaid diagrams as plain strings.

Used by:
- the algorithm-task first-principles writer (for the **algorithm logic diagram**
  required when a task involves a core algorithm / model / optimization),
- the architecture renderer in `protogenius.docs.architecture`.

Mermaid output is intentionally text-only — rendering is left to the
consumer (Cursor, GitHub web UI, or `mermaid-cli`).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class FlowNode:
    id: str
    label: str
    shape: str = "rect"  # rect | round | stadium | diamond


@dataclass(frozen=True)
class FlowEdge:
    src: str
    dst: str
    label: str = ""


_SHAPE_TEMPLATES = {
    "rect": "{id}[{label}]",
    "round": "{id}({label})",
    "stadium": "{id}([{label}])",
    "diamond": "{id}{{{label}}}",
}


def flowchart(nodes: Iterable[FlowNode], edges: Iterable[FlowEdge], direction: str = "TD") -> str:
    """Render a Mermaid flowchart.

    Direction follows Mermaid conventions: TD (top-down), LR (left-right), …
    """
    lines = [f"flowchart {direction}"]
    for node in nodes:
        template = _SHAPE_TEMPLATES.get(node.shape, _SHAPE_TEMPLATES["rect"])
        safe_label = node.label.replace('"', "'")
        lines.append("    " + template.format(id=node.id, label=safe_label))
    for edge in edges:
        if edge.label:
            lines.append(f"    {edge.src} -- {edge.label} --> {edge.dst}")
        else:
            lines.append(f"    {edge.src} --> {edge.dst}")
    return "\n".join(lines)
