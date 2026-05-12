"""Technical Design Document generator.

The TDD references the frozen SRS — it does **not** re-derive requirements.
Section ordering follows the v1 contract: traceability matrix → component
view → interface definitions → data structures → deployment topology →
risk register.
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
class TddGenerator:
    template_name: str = "tdd_ieee29148.md"
    env: Environment | None = None

    def __post_init__(self) -> None:
        if self.env is None:
            self.env = Environment(
                loader=FileSystemLoader(str(TEMPLATES_DIR)),
                undefined=StrictUndefined,
                keep_trailing_newline=True,
            )

    def render(
        self,
        ctx: RunContext,
        *,
        srs_path: Path,
        extra: dict[str, Any] | None = None,
    ) -> Path:
        assert self.env is not None
        template = self.env.get_template(self.template_name)
        rendered = template.render(
            task=ctx.task_description,
            run_id=ctx.run_id,
            chosen_stack=ctx.chosen_stack,
            srs_path=srs_path.relative_to(ctx.run_dir),
            research=ctx.research,
            extra=extra or {},
        )
        target = ctx.run_dir / "documents" / "tdd.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        return target
