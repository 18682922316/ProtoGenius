"""LLM-based semantic alignment runner.

Per §6.2, the alignment step compares the executed prototype against the
frozen SRS / TDD using an LLM. The verdict (along with confidence and the
reasoning chain) is rendered into the test report.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from ..context import AlignmentReport, RunContext
from ..llm import LLMClient
from ..prompts import alignment as alignment_prompts


@dataclass
class AlignmentRunner:
    llm: LLMClient

    def run(
        self,
        ctx: RunContext,
        *,
        srs_path: Path,
        tdd_path: Path,
        test_summary: str,
        demo_summary: str,
    ) -> AlignmentReport:
        srs_md = _safe_read(srs_path)
        tdd_md = _safe_read(tdd_path)
        user_prompt = alignment_prompts.USER.format(
            srs_md=srs_md,
            tdd_md=tdd_md,
            test_summary=test_summary,
            demo_summary=demo_summary,
        )
        response = self.llm.complete(
            system=alignment_prompts.SYSTEM,
            user=user_prompt,
        )
        if ctx.ledger is not None:
            ctx.ledger.charge_tokens(
                prompt=response.prompt_tokens, completion=response.completion_tokens
            )
        report = _parse(response.text)
        ctx.alignment = report
        return report


_FENCED_JSON_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


def _safe_read(path: Path) -> str:
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return ""


def _parse(text: str) -> AlignmentReport:
    match = _FENCED_JSON_RE.search(text)
    payload_text = match.group(1) if match else text
    try:
        data = json.loads(payload_text)
    except json.JSONDecodeError:
        # Conservative fallback so the report is always populated.
        return AlignmentReport(
            confidence=0.0,
            reasoning_chain=["alignment response could not be parsed as JSON"],
            issues=["alignment_response_unparseable"],
            improvements=[],
            satisfies_requirements=False,
        )
    return AlignmentReport(
        satisfies_requirements=bool(data.get("satisfies_requirements", False)),
        confidence=float(data.get("confidence", 0.0)),
        reasoning_chain=list(data.get("reasoning_chain", []) or []),
        issues=list(data.get("issues", []) or []),
        improvements=list(data.get("improvements", []) or []),
    )
