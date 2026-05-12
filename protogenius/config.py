"""Configuration loading & validation.

`load_config()` is the single entry point used by every other module. It reads
``config/default.yaml`` (plus ``config/quotas.yaml`` and friends), merges any
user-provided override file, and finally applies environment-variable
overrides whose names start with ``PROTOGENIUS_``.

The returned `ProtoGeniusConfig` is a Pydantic v2 model so that downstream
code can rely on validated types instead of dictionary access.
"""

from __future__ import annotations

import json
import os
import typing
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO_ROOT / "config" / "default.yaml"
QUOTAS_CONFIG = REPO_ROOT / "config" / "quotas.yaml"
MODELS_CONFIG = REPO_ROOT / "config" / "models.yaml"
SEARCH_CONFIG = REPO_ROOT / "config" / "search.yaml"


# ---------- Schema models -------------------------------------------------


class RuntimeConfig(BaseModel):
    run_name: str = ""
    workspace_root: str = "runs"
    random_seed: int = 20260101
    acceptance_platforms: list[str] = Field(default_factory=lambda: ["linux", "windows"])

    @field_validator("acceptance_platforms")
    @classmethod
    def _no_macos(cls, v: list[str]) -> list[str]:
        # macOS is explicitly NOT a v1 acceptance target.
        if "macos" in {p.lower() for p in v}:
            raise ValueError("macOS is not a v1 acceptance platform")
        return [p.lower() for p in v]


class LLMConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-5"
    api_key_env: str = "PROTOGENIUS_LLM_API_KEY"
    base_url_env: str = "PROTOGENIUS_LLM_BASE_URL"
    temperature: float = 0.2


class McpServerConfig(BaseModel):
    url_env: str | None = None
    url: str | None = None
    command: list[str] = Field(default_factory=list)
    token_env: str | None = None


class McpConfig(BaseModel):
    arxiv: McpServerConfig = Field(default_factory=McpServerConfig)
    github: McpServerConfig = Field(
        default_factory=lambda: McpServerConfig(url="https://api.githubcopilot.com/mcp/")
    )


class ClarificationConfig(BaseModel):
    max_rounds: int = 3
    abort_on_failure: bool = True

    @field_validator("max_rounds")
    @classmethod
    def _cap(cls, v: int) -> int:
        if v < 1 or v > 3:
            raise ValueError("clarification.max_rounds must be 1..3 (frozen v1 contract)")
        return v


class StackAnalysisConfig(BaseModel):
    max_options: int = 3
    require_architectural_diversity: bool = False

    @field_validator("max_options")
    @classmethod
    def _cap(cls, v: int) -> int:
        if v < 1 or v > 3:
            raise ValueError("stack_analysis.max_options must be 1..3 (frozen v1 contract)")
        return v


class AcademicDedupConfig(BaseModel):
    same_work_across_versions: bool = True


class InstitutionPrefConfig(BaseModel):
    mode: str = "agent_judged"
    record_rationale: bool = True


class AcademicConfig(BaseModel):
    arxiv_window_days: int = 90
    venue_window_days: int = 365
    venues: list[str] = Field(default_factory=list)
    extra_channels: list[str] = Field(default_factory=list)
    dedup: AcademicDedupConfig = Field(default_factory=AcademicDedupConfig)
    institution_preference: InstitutionPrefConfig = Field(default_factory=InstitutionPrefConfig)


class GitHubSortConfig(BaseModel):
    primary: str = "stars"
    secondary: str = "release_frequency"


class GitHubResearchConfig(BaseModel):
    sort: GitHubSortConfig = Field(default_factory=GitHubSortConfig)
    no_release_handling: str = "stars_only"
    target_top_n: int = 3
    tie_policy: str = "cutoff_include_all"

    @field_validator("tie_policy")
    @classmethod
    def _frozen(cls, v: str) -> str:
        if v not in {"cutoff_include_all", "strict_cap_3"}:
            raise ValueError("github.tie_policy must be cutoff_include_all or strict_cap_3")
        return v


class IndustryConfig(BaseModel):
    targets: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    allow_public_web_summary: bool = True
    multi_source_merge: bool = False


class ResearchConfig(BaseModel):
    academic: AcademicConfig = Field(default_factory=AcademicConfig)
    github: GitHubResearchConfig = Field(default_factory=GitHubResearchConfig)
    industry: IndustryConfig = Field(default_factory=IndustryConfig)


class AlgoInstancesConfig(BaseModel):
    count: int = 3
    require_reproducibility: bool = True
    reproducibility_checklist: list[str] = Field(default_factory=list)

    @field_validator("count")
    @classmethod
    def _exactly_three(cls, v: int) -> int:
        if v != 3:
            raise ValueError("algo_task.instances.count must equal 3 (frozen v1 contract)")
        return v


class AlgoTaskConfig(BaseModel):
    trigger_keywords: list[str] = Field(default_factory=list)
    instances: AlgoInstancesConfig = Field(default_factory=AlgoInstancesConfig)


class DocumentsConfig(BaseModel):
    standard: str = "IEEE-29148-2018"
    generate: list[str] = Field(default_factory=list)


class DemoConfig(BaseModel):
    default_priority: list[str] = Field(default_factory=list)
    acceptance_platforms: list[str] = Field(default_factory=lambda: ["linux", "windows"])


class AlignmentConfig(BaseModel):
    backend: str = "llm"
    record_confidence: bool = True
    record_reasoning_chain: bool = True


class TestingConfig(BaseModel):
    spec_layer: str = "language_agnostic"
    must_include_e2e_when_applicable: bool = True
    ci_provider: str = "github_actions"
    alignment: AlignmentConfig = Field(default_factory=AlignmentConfig)


class QuotaCaps(BaseModel):
    """Per-task quota caps.

    Per §7.1 of the v1 contract, the **upper bounds** on these values are
    frozen at 50 / 100 / 1_000_000 / 21_600. Users may *lower* them (e.g.
    via ``PROTOGENIUS_MAX_TOKENS=200000`` for a cheap exploratory run) but
    not raise them — the model validator below rejects that.
    """

    max_turns: int = 50
    max_search_results: int = 100
    max_tokens: int = 1_000_000
    max_walltime_seconds: int = 21600

    # Frozen v1 upper bounds — must match the values quoted in §7.1.
    _FROZEN_UPPER_BOUNDS: typing.ClassVar[dict[str, int]] = {
        "max_turns": 50,
        "max_search_results": 100,
        "max_tokens": 1_000_000,
        "max_walltime_seconds": 21600,
    }

    @field_validator("max_turns", "max_search_results", "max_tokens", "max_walltime_seconds")
    @classmethod
    def _positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quota fields must be positive integers")
        return v

    @model_validator(mode="after")
    def _enforce_v1_upper_bounds(self) -> QuotaCaps:
        for field_name, frozen_max in self._FROZEN_UPPER_BOUNDS.items():
            value = getattr(self, field_name)
            if value > frozen_max:
                raise ValueError(
                    f"quotas.{field_name} = {value} exceeds the frozen v1 "
                    f"upper bound ({frozen_max}); v1 caps may only be lowered"
                )
        return self


class AuditConfig(BaseModel):
    citation_fields: list[str] = Field(default_factory=lambda: ["url", "doi", "version"])
    artifact_file: str = "audit.jsonl"
    fail_on_missing_citation: bool = True


class InternalRepoConfig(BaseModel):
    enabled: bool = False
    repositories: list[str] = Field(default_factory=list)
    credentials_env: str = ""


class ComplianceConfig(BaseModel):
    respect_oss_licenses: bool = True
    record_spdx_for_copied_code: bool = True
    collect_pii_by_default: bool = False
    internal_codebase_research: InternalRepoConfig = Field(default_factory=InternalRepoConfig)


class ProtoGeniusConfig(BaseModel):
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    mcp: McpConfig = Field(default_factory=McpConfig)
    clarification: ClarificationConfig = Field(default_factory=ClarificationConfig)
    stack_analysis: StackAnalysisConfig = Field(default_factory=StackAnalysisConfig)
    research: ResearchConfig = Field(default_factory=ResearchConfig)
    algo_task: AlgoTaskConfig = Field(default_factory=AlgoTaskConfig)
    documents: DocumentsConfig = Field(default_factory=DocumentsConfig)
    demo: DemoConfig = Field(default_factory=DemoConfig)
    testing: TestingConfig = Field(default_factory=TestingConfig)
    quotas: QuotaCaps = Field(default_factory=QuotaCaps)
    audit: AuditConfig = Field(default_factory=AuditConfig)
    compliance: ComplianceConfig = Field(default_factory=ComplianceConfig)


# ---------- Loading helpers ----------------------------------------------


def _deep_merge(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge ``overlay`` into ``base``; dicts merge, scalars replace."""
    result: dict[str, Any] = dict(base)
    for key, value in overlay.items():
        if key in result and isinstance(result[key], Mapping) and isinstance(value, Mapping):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not parse to a mapping")
    return data


_QUOTA_ENV_TO_FIELD: dict[str, str] = {
    "PROTOGENIUS_MAX_TURNS": "max_turns",
    "PROTOGENIUS_MAX_SEARCH_RESULTS": "max_search_results",
    "PROTOGENIUS_MAX_TOKENS": "max_tokens",
    "PROTOGENIUS_MAX_WALLTIME_SECS": "max_walltime_seconds",
}


def _apply_env_overrides(data: dict[str, Any]) -> dict[str, Any]:
    """Apply environment-variable overrides on top of the merged config.

    Two override styles are supported:

    1. **Section overrides** — ``PROTOGENIUS_<TOP_LEVEL_KEY>`` is interpreted
       as JSON when present, replacing the entire section. Useful for
       overriding nested config in a single shot, e.g.::

           PROTOGENIUS_LLM='{"provider":"openai","model":"gpt-5"}'

    2. **Scalar shortcuts** — a small set of single-field shortcuts that map
       to specific schema fields. Currently:

       =========================================  ==========================
       Variable                                    Mapped field
       =========================================  ==========================
       ``PROTOGENIUS_MAX_TURNS``                   ``quotas.max_turns``
       ``PROTOGENIUS_MAX_SEARCH_RESULTS``          ``quotas.max_search_results``
       ``PROTOGENIUS_MAX_TOKENS``                  ``quotas.max_tokens``
       ``PROTOGENIUS_MAX_WALLTIME_SECS``           ``quotas.max_walltime_seconds``
       =========================================  ==========================

    Variables that don't match either style are ignored — that keeps a
    user's broader environment from leaking into the config inadvertently.

    Note: secret / endpoint variables such as ``PROTOGENIUS_LLM_API_KEY``,
    ``PROTOGENIUS_GITHUB_TOKEN`` and ``PROTOGENIUS_ARXIV_MCP_URL`` are NOT
    consumed here — they are read directly by the relevant adapters
    (`protogenius.llm`, `protogenius.research.github_mcp`, etc.) at the
    point of use so that secrets never enter the validated config object.
    """
    prefix = "PROTOGENIUS_"

    # Style 1 — section overrides.
    for env_name, raw in os.environ.items():
        if not env_name.startswith(prefix):
            continue
        key = env_name[len(prefix) :].lower()
        if key not in data:
            continue
        try:
            data[key] = json.loads(raw)
        except json.JSONDecodeError:
            data[key] = raw

    # Style 2 — scalar quota shortcuts.
    for env_name, field_name in _QUOTA_ENV_TO_FIELD.items():
        raw = os.environ.get(env_name, "").strip()
        if not raw:
            continue
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError(
                f"{env_name} must be an integer; got {raw!r}"
            ) from exc
        data.setdefault("quotas", {})[field_name] = value

    return data


def load_config(override_path: Path | str | None = None) -> ProtoGeniusConfig:
    """Load configuration, applying override-file and environment-variable layers.

    Order of precedence (lowest → highest):

        config/default.yaml < <override_path> < environment variables
    """
    base = _load_yaml(DEFAULT_CONFIG)
    quotas = _load_yaml(QUOTAS_CONFIG)
    if quotas:
        # Mirror quotas.yaml hard caps into the QuotaCaps section.
        base.setdefault("quotas", {})
        base["quotas"].update(
            {
                "max_turns": quotas["turns"]["hard_cap"],
                "max_search_results": quotas["search_results"]["hard_cap"],
                "max_tokens": quotas["tokens"]["hard_cap"],
                "max_walltime_seconds": quotas["walltime_seconds"]["hard_cap"],
            }
        )

    if override_path is not None:
        overlay = _load_yaml(Path(override_path))
        base = _deep_merge(base, overlay)

    base = _apply_env_overrides(base)
    return ProtoGeniusConfig.model_validate(base)
