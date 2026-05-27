"""Task input schema — v2 Appendix A.

The v2 spec defines a structured task-input envelope that wraps the user's
natural-language description, an optional run profile, an optional scoped
input, an optional knowledge-base reference, and a structured-requirements
summary (the latter is filled in by the clarifier sub-agent).

This module gives Pydantic models for the schema so it can be loaded from
YAML / JSON files or constructed programmatically by the CLI / Cursor
surface. The validation rules mirror v2 §2.6 / §2.7 / §2.8:

- ``profile`` is one of ``full_pipeline`` / ``research_and_docs_only``.
- When ``scoped_input`` is present the *effective* profile silently flips
  to ``research_and_docs_only`` unless the user explicitly sets
  ``profile: full_pipeline`` AND ``generate_prototype_demo: true`` (or
  passes one of those at clarification time).
- ``structured_requirements_summary`` carries the three mandatory v2 fields
  ``core_objectives`` / ``challenges`` / ``constraints``.
- ``knowledge_base`` is optional; if both ``local_path`` and ``github_repo``
  are set the loader prefers the local path (and records the override in
  the audit log).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

ProfileName = Literal["full_pipeline", "research_and_docs_only"]
ScopedType = Literal["topic", "algorithm", "theory", "product"]


# --------------------------------------------------------------------- §2.1.1


class StructuredRequirementsSummary(BaseModel):
    """v2 §2.1.1 — three mandatory fields.

    The clarifier sub-agent fills these in *during* the CLARIFY stage. They
    are the authoritative input for all downstream stages (SRS, TDD,
    research queries, layer docs). The clarifier MUST NOT silently
    populate them from defaults — empty lists indicate the field is
    still pending clarification, and a final pass with any empty list
    aborts the task per §2.2.
    """

    core_objectives: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    # Free-form extension paragraph allowed by §2.1 to carry "sub-targets,
    # business scope, non-goals" without polluting the three core fields.
    extended_notes: str = ""

    @property
    def is_complete(self) -> bool:
        return bool(self.core_objectives) and bool(self.challenges) and bool(self.constraints)


# --------------------------------------------------------------------- §2.7


_GITHUB_LOCATOR_RE = re.compile(
    r"^(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)(?:@(?P<ref>[\w./-]+))?(?::(?P<subdir>[^\s]+))?$"
)


class ScopedInput(BaseModel):
    """v2 §2.7 — narrow research / doc generation to one scope.

    ``type`` selects the doc-layer focus; the orchestrator uses it to
    decide which combination of L1-L4 docs to produce by default. The
    user can still override via ``generate_prototype_demo`` (§5 / §8).
    """

    type: ScopedType
    name: str = ""
    description: str = ""

    @model_validator(mode="after")
    def _name_or_description_present(self) -> ScopedInput:
        if not (self.name.strip() or self.description.strip()):
            raise ValueError(
                "scoped_input requires at least one of `name` or `description`"
            )
        return self


# --------------------------------------------------------------------- §2.8


class KnowledgeBaseRef(BaseModel):
    """v2 §2.8 — pointer to an optional domain knowledge base.

    Either ``local_path`` or ``github_repo`` must resolve to a readable
    directory of Markdown layer docs (foundation_theory / atomic_algorithm /
    tech_topic / ai_application). When both are present, ``local_path``
    wins and the override is recorded in the audit log.
    """

    local_path: str | None = None
    github_repo: str | None = None

    @field_validator("github_repo")
    @classmethod
    def _well_formed_locator(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not _GITHUB_LOCATOR_RE.match(v):
            raise ValueError(
                f"github_repo {v!r} does not match owner/repo[@ref][:subdir]"
            )
        return v

    @property
    def is_empty(self) -> bool:
        return not self.local_path and not self.github_repo


# --------------------------------------------------------------------- §A


class TaskInput(BaseModel):
    """v2 Appendix A — the structured task envelope."""

    description: str
    profile: ProfileName = "full_pipeline"
    generate_prototype_demo: bool = False
    scoped_input: ScopedInput | None = None
    knowledge_base: KnowledgeBaseRef | None = None
    structured_requirements_summary: StructuredRequirementsSummary = Field(
        default_factory=StructuredRequirementsSummary
    )

    # ---- v2 derived behaviors ------------------------------------------

    def resolve_profile(self) -> ProfileName:
        """Return the *effective* run profile (after §2.6 / §2.7 rules)."""
        if self.scoped_input is not None and not self.generate_prototype_demo:
            return "research_and_docs_only"
        return self.profile

    def will_generate_demo(self) -> bool:
        """Return True iff §5 will produce a runnable prototype.

        The rule, lifted verbatim from §2.7 / §5:
        - scoped_input present AND generate_prototype_demo=False → no demo.
        - profile == research_and_docs_only → no demo.
        - otherwise → demo (§5 / §6 normal path).
        """
        return self.resolve_profile() != "research_and_docs_only"

    # ---- IO ------------------------------------------------------------

    @classmethod
    def from_yaml(cls, path: Path | str) -> TaskInput:
        with Path(path).open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        if "task" in data:
            data = data["task"]
        return cls.model_validate(data)

    def to_yaml(self) -> str:
        return yaml.safe_dump(
            {"task": self.model_dump(exclude_none=True)}, sort_keys=False, allow_unicode=True
        )
