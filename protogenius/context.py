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
from .task_input import (
    KnowledgeBaseRef,
    ProfileName,
    ScopedInput,
    StructuredRequirementsSummary,
    TaskInput,
)
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


# ----- v2 §2.4.A/B/C — insight reports per accepted source ----------------


@dataclass
class InsightReport:
    """One structured insight report produced from a single research item.

    The fields below are the cross-type identifiers; per-type body content
    is rendered by ``protogenius.docs.insight_generator`` against the
    matching template under ``templates/insight_<type>.md``.
    """

    insight_id: str
    insight_type: str   # academic | oss | enterprise
    title: str
    source_url: str = ""
    source_doi: str = ""
    source_version: str = ""
    accessed_at: str = ""
    path: Path | None = None
    coverage_note_path: Path | None = None
    # Free-form body kept on the dataclass for downstream linking; the
    # path above is the authoritative on-disk artifact.
    summary: str = ""
    kb_ref: str = ""           # set when the insight reuses a KB entry


# ----- v2 §4.4 — four-layer technical doc pack ---------------------------


@dataclass
class LayerDoc:
    """One technical-asset document at layer L1 / L2 / L3 / L4."""

    layer: str                  # foundation_theory | atomic_algorithm | tech_topic | ai_application
    name: str
    description: str
    path: Path
    version: str = "v1.0.0"
    version_type: str = "create"  # create | feature | fix | optimize | deprecate
    related_versions: list[str] = field(default_factory=list)
    change_summary: str = ""
    formalization_block_present: bool = False
    references: list[str] = field(default_factory=list)
    kb_refs: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)


# ----- v2 §2.8 — KB binding -----------------------------------------------


@dataclass
class KnowledgeBaseSnapshot:
    """Materialized view of the KB after ingest."""

    ref: KnowledgeBaseRef
    root: Path                  # local directory holding the (possibly cloned) KB
    layer_index: dict[str, list[Path]] = field(default_factory=dict)
    doc_versions: dict[str, str] = field(default_factory=dict)  # path -> commit / version


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

    # v2 — task envelope. When constructed from a TaskInput it carries
    # the profile / scoped_input / KB ref / structured-requirements
    # summary. When constructed from a bare description it is created
    # with defaults that match the v1 behavior.
    task_input: TaskInput | None = None

    # Stage outputs (filled in as the run progresses).
    structured_requirements: dict[str, Any] = field(default_factory=dict)
    structured_requirements_summary: StructuredRequirementsSummary = field(
        default_factory=StructuredRequirementsSummary
    )
    clarifications: list[ClarificationRound] = field(default_factory=list)
    stack_options: list[TechStackOption] = field(default_factory=list)
    chosen_stack: TechStackOption | None = None
    research: ResearchBundle = field(default_factory=ResearchBundle)
    insights: list[InsightReport] = field(default_factory=list)
    documents: list[DocumentArtifact] = field(default_factory=list)
    layer_docs: list[LayerDoc] = field(default_factory=list)
    kb_snapshot: KnowledgeBaseSnapshot | None = None
    demo_root: Path | None = None
    tests: list[TestArtifact] = field(default_factory=list)
    alignment: AlignmentReport | None = None
    aborted: bool = False
    abort_reason: str = ""

    # ---- v2 profile / scope helpers ------------------------------------

    @property
    def effective_profile(self) -> ProfileName:
        """The *effective* profile after applying §2.6 / §2.7 rules."""
        if self.task_input is not None:
            return self.task_input.resolve_profile()
        return self.config.runtime.default_profile  # type: ignore[return-value]

    @property
    def will_generate_demo(self) -> bool:
        """True iff §5 should produce a runnable prototype on this run."""
        if self.task_input is not None:
            return self.task_input.will_generate_demo()
        return self.config.runtime.default_profile == "full_pipeline"

    @property
    def scoped_input(self) -> ScopedInput | None:
        return self.task_input.scoped_input if self.task_input else None

    @property
    def kb_ref(self) -> KnowledgeBaseRef | None:
        if self.task_input and self.task_input.knowledge_base:
            return self.task_input.knowledge_base
        return None

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
            "profile": self.effective_profile,
            "will_generate_demo": self.will_generate_demo,
            "scoped_input": self.scoped_input.model_dump() if self.scoped_input else None,
            "knowledge_base": self.kb_ref.model_dump() if self.kb_ref else None,
            "structured_requirements_summary": self.structured_requirements_summary.model_dump(),
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
            "insights": [
                {
                    "insight_id": i.insight_id,
                    "insight_type": i.insight_type,
                    "title": i.title,
                    "path": str(i.path) if i.path else None,
                    "source_url": i.source_url,
                    "source_doi": i.source_doi,
                    "kb_ref": i.kb_ref,
                }
                for i in self.insights
            ],
            "documents": [
                {"name": d.name, "path": str(d.path), "standard": d.standard}
                for d in self.documents
            ],
            "layer_docs": [
                {
                    "layer": d.layer,
                    "name": d.name,
                    "path": str(d.path),
                    "version": d.version,
                    "formalization_block_present": d.formalization_block_present,
                    "references": d.references,
                    "kb_refs": d.kb_refs,
                    "conflicts": d.conflicts,
                }
                for d in self.layer_docs
            ],
            "kb_snapshot": (
                {
                    "ref": self.kb_snapshot.ref.model_dump(),
                    "root": str(self.kb_snapshot.root),
                    "layer_counts": {
                        layer: len(paths)
                        for layer, paths in self.kb_snapshot.layer_index.items()
                    },
                }
                if self.kb_snapshot
                else None
            ),
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
