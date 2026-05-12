"""Interface definition helpers used inside the TDD section.

`InterfaceSpec` is the lingua franca: any kind of inter-component contract
(REST endpoint, RPC method, CLI flag set, library entry point) can be
expressed in the same dataclass. The TDD generator renders it as a Markdown
sub-section.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from ..utils.markdown import table

InterfaceKind = Literal["rest", "rpc", "cli", "library", "queue"]


@dataclass
class InterfaceField:
    name: str
    type: str
    required: bool = True
    description: str = ""


@dataclass
class InterfaceSpec:
    name: str
    kind: InterfaceKind
    path_or_method: str
    summary: str = ""
    inputs: list[InterfaceField] = field(default_factory=list)
    outputs: list[InterfaceField] = field(default_factory=list)
    error_modes: list[str] = field(default_factory=list)


def render_interfaces_section(interfaces: list[InterfaceSpec]) -> str:
    if not interfaces:
        return "_No external interfaces defined for this prototype._\n"
    parts: list[str] = []
    for spec in interfaces:
        parts.append(f"### {spec.name} (`{spec.kind}`)\n")
        parts.append(f"- **Path / method**: `{spec.path_or_method}`")
        if spec.summary:
            parts.append(f"- **Summary**: {spec.summary}")
        parts.append("\n**Inputs**\n")
        parts.append(_render_fields(spec.inputs))
        parts.append("\n**Outputs**\n")
        parts.append(_render_fields(spec.outputs))
        if spec.error_modes:
            parts.append("\n**Error modes**\n")
            parts.extend(f"- {mode}" for mode in spec.error_modes)
        parts.append("")
    return "\n".join(parts) + "\n"


def _render_fields(fields: list[InterfaceField]) -> str:
    if not fields:
        return "_None._"
    rows = [(f.name, f.type, "yes" if f.required else "no", f.description) for f in fields]
    return table(("name", "type", "required", "description"), rows)
