"""IEEE 29148 SRS generator.

The generator combines the SRS template (``templates/srs_ieee29148.md``)
with structured run-context data, then optionally calls the LLM to fill in
the prose for each section. The intermediate Jinja layer keeps the output
deterministic up to the LLM step — useful for testing the structural
contract without spending tokens.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..config import REPO_ROOT
from ..context import RunContext

TEMPLATES_DIR = REPO_ROOT / "templates"


@dataclass
class SrsGenerator:
    """Renders an SRS Markdown file at ``<run>/documents/srs.md``."""

    template_name: str = "srs_ieee29148.md"
    env: Environment | None = None

    def __post_init__(self) -> None:
        if self.env is None:
            self.env = Environment(
                loader=FileSystemLoader(str(TEMPLATES_DIR)),
                undefined=StrictUndefined,
                keep_trailing_newline=True,
            )

    def render(self, ctx: RunContext, *, extra: dict[str, Any] | None = None) -> Path:
        assert self.env is not None
        template = self.env.get_template(self.template_name)
        rendered = template.render(
            task=ctx.task_description,
            run_id=ctx.run_id,
            chosen_stack=ctx.chosen_stack,
            structured_requirements=ctx.structured_requirements,
            research=ctx.research,
            clarifications=ctx.clarifications,
            extra=extra or {},
        )
        target = ctx.run_dir / "documents" / "srs.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        return target
