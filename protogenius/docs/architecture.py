"""Render an architecture diagram for the TDD §component-view section.

Two outputs:

- A Mermaid ``flowchart LR`` showing components and their wiring.
- A paragraph of natural-language text that mirrors the diagram (per IEEE
  29148 §5.4.4, every diagram must have an explanatory prose companion).
"""

from __future__ import annotations

from collections.abc import Iterable

from ..utils.mermaid import FlowEdge, FlowNode, flowchart


def render_architecture_diagram(
    components: Iterable[tuple[str, str]],
    edges: Iterable[tuple[str, str, str]],
) -> tuple[str, str]:
    """Return ``(mermaid_block, prose_companion)``.

    ``components`` is an iterable of ``(id, label)``.
    ``edges`` is an iterable of ``(src_id, dst_id, label)``.
    """
    nodes = [FlowNode(id=cid, label=lbl) for cid, lbl in components]
    flow_edges = [FlowEdge(src=s, dst=d, label=lbl) for s, d, lbl in edges]
    diagram = flowchart(nodes, flow_edges, direction="LR")

    prose_lines = ["The diagram above renders the following components and connections:"]
    for node in nodes:
        prose_lines.append(f"- **{node.label}** (`{node.id}`)")
    if flow_edges:
        prose_lines.append("\nWiring:")
        for edge in flow_edges:
            arrow = f"{edge.src} → {edge.dst}"
            if edge.label:
                arrow = f"{edge.src} —[{edge.label}]→ {edge.dst}"
            prose_lines.append(f"- {arrow}")
    return f"```mermaid\n{diagram}\n```", "\n".join(prose_lines)
