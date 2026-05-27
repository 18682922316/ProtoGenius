"""Coverage-note helper — v2 §2.5.

Both insight reports (§2.4.A/B/C) and the four-layer technical documents
(§4.4.1-4.4.4) treat their field lists as a *recommended completeness set*,
not a strict mandatory schema. Whenever fields are dropped — because the
task type doesn't need them, evidence is insufficient, the user's
clarification narrowed the scope, or scoped research limited it — the
generator MUST emit a ``coverage_note`` at the top of the produced
artifact that:

1. Lists which fields from the template are present.
2. Lists which fields are absent.
3. Explains *why* each absent field was dropped (one short reason per
   missing field is enough).

This module gives a small dataclass + Markdown renderer plus a checker
that the document generators call before they hand off the artifact to
disk.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

# Reason strings used by the generators — keep them stable so audit log
# entries can be grep-able.
REASON_TASK_TYPE = "field not applicable to this task type"
REASON_EVIDENCE_MISSING = "no auditable evidence found in research streams"
REASON_USER_CLARIFICATION = "ruled out during clarification"
REASON_SCOPED_RESEARCH = "outside the scoped-research target"
REASON_KB_PROVIDED = "preferred existing knowledge-base document (kb_ref)"


@dataclass
class CoverageNote:
    """Record of which template fields were kept / dropped, plus reasons."""

    artifact_id: str
    template_id: str
    present: list[str] = field(default_factory=list)
    absent: list[tuple[str, str]] = field(default_factory=list)  # (field, reason)

    # Whether the doc meets the v2 §2.5 minimum-content baseline.
    meets_minimum: bool = True
    minimum_violations: list[str] = field(default_factory=list)

    def add_present(self, *fields: str) -> None:
        for f in fields:
            if f not in self.present:
                self.present.append(f)

    def add_absent(self, field_name: str, reason: str) -> None:
        # Reason is required.
        self.absent.append((field_name, reason.strip() or "(no reason provided)"))

    def render_markdown(self) -> str:
        lines = ["<!-- coverage_note v2 §2.5 -->", "## coverage_note", ""]
        lines.append(f"- **artifact_id**: `{self.artifact_id}`")
        lines.append(f"- **template_id**: `{self.template_id}`")
        if self.present:
            lines.append(f"- **fields present**: {', '.join(f'`{f}`' for f in self.present)}")
        if self.absent:
            lines.append("- **fields absent (with reason)**:")
            for fname, reason in self.absent:
                lines.append(f"  - `{fname}` — {reason}")
        if not self.meets_minimum:
            lines.append("- **WARN — minimum-content baseline violated**:")
            for v in self.minimum_violations:
                lines.append(f"  - {v}")
        return "\n".join(lines) + "\n"


# ----- Minimum-content baselines (v2 §2.5) --------------------------------


def check_insight_minimum(
    *,
    identification_present: bool,
    core_conclusions_present: bool,
    auditable_citation_present: bool,
) -> tuple[bool, list[str]]:
    """Return ``(ok, violations)`` for the v2 §2.5 insight minimum."""
    violations: list[str] = []
    if not identification_present:
        violations.append("missing identification block (insight_id / insight_type / title)")
    if not core_conclusions_present:
        violations.append("missing core conclusions section")
    if not auditable_citation_present:
        violations.append("missing auditable citation (need at least one of url/doi)")
    return (not violations, violations)


def check_layer_doc_minimum(
    *,
    frontmatter_present: bool,
    basic_info_present: bool,
    formalization_block_present: bool,
    references_present: bool,
) -> tuple[bool, list[str]]:
    """Return ``(ok, violations)`` for the v2 §2.5 layer-doc minimum."""
    violations: list[str] = []
    if not frontmatter_present:
        violations.append("missing YAML frontmatter")
    if not basic_info_present:
        violations.append("missing basic/core info section")
    if not formalization_block_present:
        violations.append("missing `## 形式化定义` block (v2 §4.4.5)")
    if not references_present:
        violations.append("missing references list")
    return (not violations, violations)


def render_coverage_block(note: CoverageNote) -> str:
    """Convenience wrapper used by document generators."""
    return note.render_markdown()


def fields_from(template_fields: Iterable[str], *, used: Iterable[str]) -> tuple[list[str], list[str]]:
    """Split ``template_fields`` into (used, dropped) preserving order."""
    used_set = set(used)
    used_list = [f for f in template_fields if f in used_set]
    dropped = [f for f in template_fields if f not in used_set]
    return used_list, dropped
