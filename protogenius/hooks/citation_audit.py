"""Citation audit hook — post-research gate.

Every research item that lands in the run context must carry an auditable
source identifier (URL or DOI). This hook walks the list of items returned by
an adapter and records each citation in the JSONL audit log.

When ``audit.fail_on_missing_citation`` is enabled (the default) the hook
raises a `MissingCitationError` so that the run aborts loudly rather than
producing an unattributable report.
"""

from __future__ import annotations

from ..audit import Citation
from ..context import ResearchItem, RunContext


class MissingCitationError(RuntimeError):
    """Raised when a research item lacks both URL and DOI."""


def citation_audit_hook(ctx: RunContext, items: list[ResearchItem]) -> None:
    if ctx.audit is None:  # pragma: no cover — defensive
        raise RuntimeError("RunContext.audit is unset; orchestrator must initialize it")
    fail_on_missing = ctx.config.audit.fail_on_missing_citation
    for item in items:
        citation = Citation(
            title=item.title,
            source_type=item.source_type,
            url=item.url,
            doi=item.doi,
            version=item.version,
            extra={
                k: v
                for k, v in {
                    "institutions": item.institutions,
                    "stars": item.stars,
                    "release_frequency_per_year": item.release_frequency_per_year,
                }.items()
                if v
            },
        )
        if not citation.is_complete():
            if fail_on_missing:
                raise MissingCitationError(
                    f"research item {item.title!r} has neither URL nor DOI"
                )
            ctx.audit.log_info("citation incomplete", title=item.title)
            continue
        ctx.audit.log_citation(citation, fail_on_missing=fail_on_missing)
