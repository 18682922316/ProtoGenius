"""v2 §2.4.A/B/C — insight reports per accepted research source.

The generator wraps each ``ResearchItem`` adopted by the user into a
structured insight report. Three templates are supported, one per
``insight_type``:

- ``academic``    — ``templates/insight_academic.md``
- ``oss``         — ``templates/insight_oss.md``
- ``enterprise``  — ``templates/insight_enterprise.md``

Each report carries:

- An ``insight_id`` (deterministic from the source URL/DOI).
- A ``coverage_note`` (v2 §2.5) listing kept vs. dropped fields.
- An auditable citation block (URL / DOI / version / accessed_at).

The generator does NOT call the LLM directly — sub-agents do that, then
hand the structured ``body`` dictionary back here for rendering. Keeping
the LLM call out of this module makes the generator deterministic in
tests and lets us reuse it from the Cursor surface (where the agent is
the LLM).
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..config import REPO_ROOT
from ..context import InsightReport, ResearchItem, RunContext
from ..coverage import (
    CoverageNote,
    check_insight_minimum,
    render_coverage_block,
)
from ..utils.ids import slugify

TEMPLATES_DIR = REPO_ROOT / "templates"

# v2 §2.4.A/B/C — recommended (not strictly mandatory) field set per type.
# These power the coverage_note generator: anything not in ``used`` here is
# recorded as "absent" with the supplied reason.
_TEMPLATE_FIELDS: dict[str, list[str]] = {
    "academic": [
        "title", "authors", "institutions", "published_at", "keywords",
        "bottleneck", "new_perspective",
        "innovation", "formula", "pipeline", "pipeline_mermaid",
        "benchmarks", "metrics", "ablation",
        "engineering_feasibility", "transferable", "limitations",
        "core_conclusions",
    ],
    "oss": [
        "repo_name", "star_activity", "license",
        "capabilities", "differentiators",
        "architecture", "core_algorithms",
        "performance", "security", "transferable", "limitations",
        "core_conclusions",
    ],
    "enterprise": [
        "vendor", "tech_name", "tech_category",
        "business_driven", "evolution",
        "architecture", "core_algorithms",
        "direct_reuse", "transferable",
        "core_conclusions", "uncertainty", "source_label",
    ],
}

# Map ``ResearchItem.source_type`` to ``insight_type``.
_SOURCE_TO_INSIGHT_TYPE = {
    "arxiv": "academic",
    "conference": "academic",
    "github": "oss",
    "industry": "enterprise",
}


@dataclass
class InsightGenerator:
    env: Environment | None = None

    def __post_init__(self) -> None:
        if self.env is None:
            self.env = Environment(
                loader=FileSystemLoader(str(TEMPLATES_DIR)),
                undefined=StrictUndefined,
                keep_trailing_newline=True,
            )

    # ---- public API ----------------------------------------------------

    def render_for_research_item(
        self,
        ctx: RunContext,
        item: ResearchItem,
        body: Mapping[str, Any] | None = None,
        *,
        kb_ref: str = "",
        absent_reasons: Mapping[str, str] | None = None,
    ) -> InsightReport:
        """Render a single insight report for one accepted research source.

        ``body`` carries the LLM-filled prose. If a sub-agent has not
        produced anything for a field, leave that key out of ``body`` and
        supply ``absent_reasons[field] = "<why>"``; the coverage_note
        section will record the omission.
        """
        insight_type = _SOURCE_TO_INSIGHT_TYPE.get(item.source_type, "academic")
        insight_id = self._make_id(insight_type, item)
        body_dict = self._merge_default_body(insight_type, item, body or {})
        coverage = self._build_coverage_note(insight_id, insight_type, body_dict, absent_reasons)
        identification_ok = bool(item.title) and bool(insight_id)
        citation_ok = bool(item.url) or bool(item.doi)
        conclusions_ok = bool(body_dict.get("core_conclusions"))
        coverage.meets_minimum, coverage.minimum_violations = check_insight_minimum(
            identification_present=identification_ok,
            core_conclusions_present=conclusions_ok,
            auditable_citation_present=citation_ok,
        )

        if ctx.config.insights.enforce_minimum_content and not coverage.meets_minimum:
            raise InsightMinimumContentError(
                f"insight {insight_id!r} fails v2 §2.5 minimum content: "
                f"{coverage.minimum_violations}"
            )

        rendered = self._render(insight_type, insight_id, item, body_dict, coverage, kb_ref)
        target = ctx.run_dir / "research" / "insights" / f"{insight_id}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")

        report = InsightReport(
            insight_id=insight_id,
            insight_type=insight_type,
            title=item.title,
            source_url=item.url,
            source_doi=item.doi,
            source_version=item.version,
            accessed_at=_now_iso(),
            path=target,
            summary=str(body_dict.get("core_conclusions", "") or ""),
            kb_ref=kb_ref,
        )
        return report

    def render_all(
        self,
        ctx: RunContext,
        bodies: Mapping[str, Mapping[str, Any]] | None = None,
        *,
        kb_refs: Mapping[str, str] | None = None,
    ) -> list[InsightReport]:
        """Render one insight per accepted research item across all streams.

        ``bodies`` maps ``insight_id`` -> ``body`` (so tests / sub-agents
        can pre-stage prose). Items without a matching body are still
        emitted but their ``coverage_note`` records the absence.
        """
        bodies = bodies or {}
        kb_refs = kb_refs or {}
        reports: list[InsightReport] = []
        items: list[ResearchItem] = []
        items.extend(ctx.research.academic)
        items.extend(ctx.research.github)
        items.extend(ctx.research.industry)
        for item in items:
            insight_type = _SOURCE_TO_INSIGHT_TYPE.get(item.source_type, "academic")
            preview_id = self._make_id(insight_type, item)
            report = self.render_for_research_item(
                ctx,
                item,
                body=bodies.get(preview_id, {}),
                kb_ref=kb_refs.get(preview_id, ""),
            )
            reports.append(report)
        ctx.insights.extend(reports)
        return reports

    # ---- helpers -------------------------------------------------------

    def _render(
        self,
        insight_type: str,
        insight_id: str,
        item: ResearchItem,
        body: Mapping[str, Any],
        coverage: CoverageNote,
        kb_ref: str,
    ) -> str:
        assert self.env is not None
        template = self.env.get_template(f"insight_{insight_type}.md")
        return template.render(
            insight_id=insight_id,
            title=item.title,
            source_url=item.url,
            source_doi=item.doi,
            source_version=item.version,
            accessed_at=_now_iso(),
            run_id="run",
            coverage_block=render_coverage_block(coverage),
            body=body,
            kb_ref=kb_ref,
        )

    def _make_id(self, insight_type: str, item: ResearchItem) -> str:
        seed = (item.url or item.doi or item.title or "").strip()
        digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8]
        title_slug = slugify(item.title)[:32] or "untitled"
        return f"INS-{insight_type[:3].upper()}-{title_slug}-{digest}"

    def _merge_default_body(
        self,
        insight_type: str,
        item: ResearchItem,
        body: Mapping[str, Any],
    ) -> dict[str, Any]:
        merged: dict[str, Any] = {field_name: "" for field_name in _TEMPLATE_FIELDS[insight_type]}
        # Pre-fill what we already know from the ResearchItem.
        if insight_type == "academic":
            merged.update(
                {
                    "title": item.title,
                    "authors": item.extra.get("authors", "") if item.extra else "",
                    "institutions": ", ".join(item.institutions),
                    "published_at": item.version or (item.extra.get("year", "") if item.extra else ""),
                }
            )
        elif insight_type == "oss":
            merged.update(
                {
                    "repo_name": item.title,
                    "star_activity": (
                        f"Stars: {item.stars}, releases/yr: {item.release_frequency_per_year}"
                        if item.stars is not None
                        else ""
                    ),
                    "license": item.extra.get("license", "") if item.extra else "",
                }
            )
        elif insight_type == "enterprise":
            vendor = (item.institutions or [""])[0]
            merged.update(
                {
                    "vendor": vendor,
                    "tech_name": item.title,
                    "source_label": item.extra.get("source_label", "") if item.extra else "",
                    "uncertainty": item.extra.get(
                        "uncertainty",
                        "Inferred from public web; may be incomplete or stale.",
                    ) if item.extra else "",
                }
            )
        merged.update(body)
        return merged

    def _build_coverage_note(
        self,
        insight_id: str,
        insight_type: str,
        body: Mapping[str, Any],
        absent_reasons: Mapping[str, str] | None,
    ) -> CoverageNote:
        note = CoverageNote(artifact_id=insight_id, template_id=f"insight_{insight_type}")
        absent_reasons = absent_reasons or {}
        for field_name in _TEMPLATE_FIELDS[insight_type]:
            value = body.get(field_name, "")
            if value:
                note.add_present(field_name)
            else:
                reason = absent_reasons.get(field_name, "field not populated (no prose supplied)")
                note.add_absent(field_name, reason)
        return note


class InsightMinimumContentError(RuntimeError):
    """Raised when an insight artifact would violate v2 §2.5 minimum content."""


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---- module-level convenience for callers -------------------------------


def render_insights(
    ctx: RunContext,
    bodies: Mapping[str, Mapping[str, Any]] | None = None,
    *,
    kb_refs: Mapping[str, str] | None = None,
) -> Iterable[InsightReport]:
    """Functional alias around :class:`InsightGenerator`."""
    return InsightGenerator().render_all(ctx, bodies, kb_refs=kb_refs)
