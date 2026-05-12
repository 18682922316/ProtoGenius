"""Runtime context object passed through every orchestrator stage.

`RunContext` is the single mutable artifact that a single ProtoGenius run
threads through its state machine. Sub-agents read from / write to it; the
audit log lives next to it on disk.

Design goals:

- **Serializable.** A `RunContext.to_jsonable()` method makes it trivial to
  snapshot the run between stages, which is what the gate-check hook does to
  produce the human review payload.
- **Minimal coupling.** The context does *not* hold a reference to the
  orchestrator or to the live LLM client; sub-agents receive those
  separately. This keeps test doubles simple.
- **Crystal-clear ownership.** Each top-level attribute corresponds to one
  bounded responsibility (clarification, stack analysis, research…). When a
  new sub-agent is added, allocate a new attribute rather than reusing an
  existing dictionary.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .audit import AuditLog
from .config import ProtoGeniusConfig
from .quotas import QuotaLedger
from .utils.ids import new_run_id


@dataclass
class ClarificationRound:
    question: str
    answer: str | None = None


@dataclass
class TechStackOption:
    """One mutually exclusive option produced by the stack analyzer."""

    name: str
    language: str
    runtime: str
    rationale: str = ""
    risks: list[str] = field(default_factory=list)


@dataclass
class ResearchItem:
    """Single research hit (one of: arxiv paper, conference paper, GitHub repo, industry doc)."""

    title: str
    source_type: str
    summary: str = ""
    url: str = ""
    doi: str = ""
    version: str = ""
    stars: int | None = None
    release_frequency_per_year: float | None = None
    institutions: list[str] = field(default_factory=list)
    pros: list[str] = field(default_factory=list)
    challenges: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchBundle:
    academic: list[ResearchItem] = field(default_factory=list)
    github: list[ResearchItem] = field(default_factory=list)
    industry: list[ResearchItem] = field(default_factory=list)
    common_challenges: list[str] = field(default_factory=list)
    algo_first_principles: str = ""
    algo_diagram_mermaid: str = ""
    algo_instances: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DocumentArtifact:
    name: str
    path: Path
    standard: str = "IEEE-29148-2018"


@dataclass
class TestArtifact:
    spec_path: Path
    runner: str  # pytest | playwright | shell | custom
    ci_path: Path | None = None


@dataclass
class AlignmentReport:
    confidence: float
    reasoning_chain: list[str]
    issues: list[str]
    improvements: list[str]
    satisfies_requirements: bool


@dataclass
class RunContext:
    """The state object threaded through every orchestration stage."""

    config: ProtoGeniusConfig
    task_description: str
    run_id: str = field(default_factory=new_run_id)
    workspace: Path = field(default_factory=lambda: Path("runs"))
    ledger: QuotaLedger | None = None
    audit: AuditLog | None = None

    # Stage outputs (filled in as the run progresses).
    structured_requirements: dict[str, Any] = field(default_factory=dict)
    clarifications: list[ClarificationRound] = field(default_factory=list)
    stack_options: list[TechStackOption] = field(default_factory=list)
    chosen_stack: TechStackOption | None = None
    research: ResearchBundle = field(default_factory=ResearchBundle)
    documents: list[DocumentArtifact] = field(default_factory=list)
    demo_root: Path | None = None
    tests: list[TestArtifact] = field(default_factory=list)
    alignment: AlignmentReport | None = None
    aborted: bool = False
    abort_reason: str = ""

    # ---- helpers -------------------------------------------------------

    @property
    def run_dir(self) -> Path:
        return self.workspace / self.run_id

    def ensure_dirs(self) -> None:
        for sub in ("research", "documents", "prototype", "tests", "reports"):
            (self.run_dir / sub).mkdir(parents=True, exist_ok=True)

    def to_jsonable(self) -> dict[str, Any]:
        """Return a JSON-safe snapshot suitable for review payloads."""
        return {
            "run_id": self.run_id,
            "task": self.task_description,
            "structured_requirements": self.structured_requirements,
            "clarifications": [asdict(c) for c in self.clarifications],
            "stack_options": [asdict(o) for o in self.stack_options],
            "chosen_stack": asdict(self.chosen_stack) if self.chosen_stack else None,
            "research": {
                "academic": [asdict(x) for x in self.research.academic],
                "github": [asdict(x) for x in self.research.github],
                "industry": [asdict(x) for x in self.research.industry],
                "common_challenges": self.research.common_challenges,
                "algo_first_principles": self.research.algo_first_principles,
                "algo_diagram_mermaid": self.research.algo_diagram_mermaid,
                "algo_instances": self.research.algo_instances,
            },
            "documents": [
                {"name": d.name, "path": str(d.path), "standard": d.standard}
                for d in self.documents
            ],
            "demo_root": str(self.demo_root) if self.demo_root else None,
            "tests": [
                {"spec_path": str(t.spec_path), "runner": t.runner, "ci_path": str(t.ci_path) if t.ci_path else None}
                for t in self.tests
            ],
            "alignment": asdict(self.alignment) if self.alignment else None,
            "aborted": self.aborted,
            "abort_reason": self.abort_reason,
            "quotas": self.ledger.snapshot() if self.ledger else None,
        }
