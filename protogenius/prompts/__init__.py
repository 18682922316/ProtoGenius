"""Reusable LLM prompt templates.

Every prompt module exports a pair of strings:

    SYSTEM : the system message — sets persona, contract, output schema.
    USER   : a Python ``str.format``-able template — feeds the run context.

Prompts are intentionally kept short and contractually strict (output a fenced
JSON block) so downstream parsing is deterministic.
"""

from . import (
    alignment,
    clarify,
    research_summary,
    srs,
    stack_analysis,
    tdd,
    test_plan,
)

__all__ = [
    "alignment",
    "clarify",
    "research_summary",
    "srs",
    "stack_analysis",
    "tdd",
    "test_plan",
]
