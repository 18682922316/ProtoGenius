"""v2 §4.4 — four-layer technical doc pack (L1 → L2 → L3 → L4).

The four layers correspond to ``foundation_theory``, ``atomic_algorithm``,
``tech_topic``, ``ai_application`` (bottom-up dependency). Each layer has
its own template under ``templates/layer_l{1,2,3,4}_*.md`` and its own set
of mandatory ``形式化定义`` elements (v2 §4.4.5).

The generator:

1. Renders the requested layer doc with all known fields.
2. Inspects the rendered Markdown to confirm the ``## 形式化定义`` block
   is present (per §4.4.5).
3. Runs the v2 §2.5 minimum-content checker (frontmatter + basic info +
   formalization + references).
4. Persists the doc under ``<run>/documents/layers/<layer>/<slug>.md`` and
   returns a ``LayerDoc`` entry the orchestrator threads into
   ``RunContext.layer_docs``.

Sub-agents are expected to supply the prose ``body`` dict and the
``references`` / ``kb_refs`` / ``conflicts`` lists. Anything they don't
supply is recorded as "absent" in the ``coverage_note`` block (see
``protogenius.coverage``).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..config import REPO_ROOT
from ..context import LayerDoc, RunContext
from ..coverage import (
    REASON_EVIDENCE_MISSING,
    CoverageNote,
    check_layer_doc_minimum,
    render_coverage_block,
)
from ..utils.ids import slugify

TEMPLATES_DIR = REPO_ROOT / "templates"

# Mapping from layer id -> (template file, template-version tag, mandatory
# formalization elements, recommended body fields).
LAYER_SPECS: dict[str, dict[str, Any]] = {
    "foundation_theory": {
        "template": "layer_l1_foundation_theory.md",
        "version_tag": "v2-§4.4.4",
        "formal_elements": [
            "formal_symbols",
            "formal_axioms_theorems",
            "formal_derivation",
            "formal_domain",
        ],
        "body_fields": [
            "theory_name", "domain", "background", "canonical_source",
            "applicability_scope", "constraints",
            "terminology", "axioms", "theorems", "derivations", "corollaries",
            "core_idea", "mechanism", "internal_logic", "preconditions", "limitations",
            "prerequisites", "peers", "derivatives",
            "pitfalls",
            "formal_symbols", "formal_axioms_theorems",
            "formal_derivation", "formal_domain",
        ],
    },
    "atomic_algorithm": {
        "template": "layer_l2_atomic_algorithm.md",
        "version_tag": "v2-§4.4.3",
        "formal_elements": [
            "formal_io_space",
            "formal_objective",
            "formal_time_complexity",
            "formal_space_complexity",
            "formal_correctness",
        ],
        "body_fields": [
            "algorithm_name", "algorithm_en", "algorithm_category",
            "depends_on_theories", "applicable_scenarios", "forbidden_scenarios",
            "input_spec", "output_format", "core_logic", "steps",
            "hyperparameters", "convergence", "complexity",
            "accuracy", "efficiency", "resource_usage", "best_vs_typical",
            "bottlenecks", "improvements",
            "repo_url", "runtime_env", "dependencies", "entry_script",
            "tests", "launch_cmd", "api_usage", "deployment",
            "formal_io_space", "formal_objective",
            "formal_time_complexity", "formal_space_complexity", "formal_correctness",
        ],
    },
    "tech_topic": {
        "template": "layer_l3_tech_topic.md",
        "version_tag": "v2-§4.4.2",
        "formal_elements": [
            "formal_problem",
            "formal_solution_family",
            "formal_selection_conditions",
            "formal_eval_vector",
        ],
        "body_fields": [
            "topic_name", "tech_definition", "problem_statement",
            "development_goal", "tech_domain",
            "history", "schools", "evolution",
            "solutions_md",
            "depends_on_algorithms", "pre_post_processing",
            "feature_engineering", "objective_design",
            "evaluation_metrics", "benchmark_datasets", "comparison_methods",
            "bottlenecks", "frontier_improvements",
            "integration_repo", "per_solution_repos", "batch_test_script",
            "env_setup_doc", "one_click_run", "result_compare_tool",
            "formal_problem", "formal_solution_family",
            "formal_selection_conditions", "formal_eval_vector",
        ],
    },
    "ai_application": {
        "template": "layer_l4_ai_application.md",
        "version_tag": "v2-§4.4.1",
        "formal_elements": [
            "formal_user_objective",
            "formal_state_machine",
            "formal_sla_security",
        ],
        "body_fields": [
            "app_name", "positioning", "target_users", "pain_points", "business_value",
            "core_features", "business_flow", "user_flow", "usage_patterns",
            "architecture_overview_md",
            "frontend_stack", "frontend_pages", "frontend_interaction", "frontend_deploy",
            "midplatform_scheduler", "midplatform_orchestration",
            "midplatform_authz", "midplatform_workflow",
            "backend_language", "backend_services", "backend_interfaces",
            "backend_middleware", "backend_database",
            "ai_depends_topics", "ai_depends_algorithms",
            "ai_model_chain", "ai_kb_logic",
            "deploy_cluster", "deploy_compute", "deploy_scaling",
            "data_formats", "data_flow", "data_storage", "data_security",
            "input_rules", "output_paradigm", "multiturn_logic", "intent_matching",
            "challenges", "improvements",
            "repo_url", "project_tree", "config_files", "docker_deploy",
            "demo_link", "kb_integration_code", "prod_deploy_flow",
            "formal_user_objective", "formal_state_machine", "formal_sla_security",
        ],
    },
}


_FORMALIZATION_HEADING_RE = re.compile(r"^##\s*形式化定义\s*$", re.MULTILINE)


class LayerDocMinimumContentError(RuntimeError):
    """Raised when a layer doc would violate the v2 §2.5 baseline."""


class FormalizationBlockMissingError(RuntimeError):
    """Raised when a generated layer doc lacks the required formalization block."""


@dataclass
class LayerDocsGenerator:
    env: Environment | None = None

    def __post_init__(self) -> None:
        if self.env is None:
            self.env = Environment(
                loader=FileSystemLoader(str(TEMPLATES_DIR)),
                undefined=StrictUndefined,
                keep_trailing_newline=True,
            )

    # ---- public API ----------------------------------------------------

    def render_layer(
        self,
        ctx: RunContext,
        *,
        layer: str,
        name: str,
        description: str,
        body: Mapping[str, Any] | None = None,
        references: Iterable[str] | None = None,
        kb_refs: Iterable[str] | None = None,
        conflicts: Iterable[str] | None = None,
        absent_reasons: Mapping[str, str] | None = None,
        version: str = "v1.0.0",
        version_type: str = "create",
        related_versions: Iterable[str] | None = None,
        change_summary: str = "",
    ) -> LayerDoc:
        if layer not in LAYER_SPECS:
            raise ValueError(
                f"unknown layer {layer!r}; expected one of {list(LAYER_SPECS)}"
            )
        spec = LAYER_SPECS[layer]
        body_dict = self._merge_default_body(layer, body or {})
        references_list = list(references or [])
        kb_refs_list = list(kb_refs or [])
        conflicts_list = list(conflicts or [])
        related_versions_list = list(related_versions or [])

        coverage = self._build_coverage_note(
            artifact_id=f"LD-{slugify(name)}",
            layer=layer,
            body=body_dict,
            references=references_list,
            absent_reasons=absent_reasons or {},
        )

        rendered = self._render_template(
            spec["template"],
            name=name,
            description=description,
            version=version,
            version_type=version_type,
            related_versions=", ".join(related_versions_list),
            change_summary=change_summary,
            body=body_dict,
            references_md=_render_references_md(references_list),
            kb_refs=kb_refs_list,
            conflicts=conflicts_list,
            coverage_block=render_coverage_block(coverage),
            run_id=ctx.run_id,
        )

        # v2 §4.4.5 enforcement.
        formal_present = bool(_FORMALIZATION_HEADING_RE.search(rendered))
        if (
            ctx.config.layer_docs.require_formalization_block
            and not formal_present
        ):
            raise FormalizationBlockMissingError(
                f"layer doc {name!r} ({layer}) is missing the `## 形式化定义` block"
            )

        # v2 §2.5 minimum-content enforcement.
        coverage.meets_minimum, coverage.minimum_violations = check_layer_doc_minimum(
            frontmatter_present=rendered.lstrip().startswith("---"),
            basic_info_present="## 1. " in rendered,
            formalization_block_present=formal_present,
            references_present=bool(references_list),
        )
        if (
            ctx.config.layer_docs.enforce_minimum_content
            and not coverage.meets_minimum
        ):
            raise LayerDocMinimumContentError(
                f"layer doc {name!r} ({layer}) fails v2 §2.5 minimum content: "
                f"{coverage.minimum_violations}"
            )

        # Re-render coverage block with the minimum-content verdict baked in
        # so the on-disk doc carries the final coverage note.
        rendered = self._render_template(
            spec["template"],
            name=name,
            description=description,
            version=version,
            version_type=version_type,
            related_versions=", ".join(related_versions_list),
            change_summary=change_summary,
            body=body_dict,
            references_md=_render_references_md(references_list),
            kb_refs=kb_refs_list,
            conflicts=conflicts_list,
            coverage_block=render_coverage_block(coverage),
            run_id=ctx.run_id,
        )

        target = (
            ctx.run_dir
            / "documents"
            / "layers"
            / layer
            / f"{slugify(name)}.md"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")

        doc = LayerDoc(
            layer=layer,
            name=name,
            description=description,
            path=target,
            version=version,
            version_type=version_type,
            related_versions=related_versions_list,
            change_summary=change_summary,
            formalization_block_present=formal_present,
            references=references_list,
            kb_refs=kb_refs_list,
            conflicts=conflicts_list,
        )
        return doc

    # ---- helpers -------------------------------------------------------

    def _render_template(self, template_name: str, **kwargs: Any) -> str:
        assert self.env is not None
        template = self.env.get_template(template_name)
        return template.render(**kwargs)

    def _merge_default_body(
        self, layer: str, body: Mapping[str, Any]
    ) -> dict[str, Any]:
        merged: dict[str, Any] = {
            field_name: "" for field_name in LAYER_SPECS[layer]["body_fields"]
        }
        merged.update(body)
        return merged

    def _build_coverage_note(
        self,
        *,
        artifact_id: str,
        layer: str,
        body: Mapping[str, Any],
        references: list[str],
        absent_reasons: Mapping[str, str],
    ) -> CoverageNote:
        spec = LAYER_SPECS[layer]
        template_id = f"layer_{layer}"
        note = CoverageNote(artifact_id=artifact_id, template_id=template_id)
        for field_name in spec["body_fields"]:
            value = body.get(field_name, "")
            if value:
                note.add_present(field_name)
            else:
                reason = absent_reasons.get(field_name, REASON_EVIDENCE_MISSING)
                note.add_absent(field_name, reason)
        if references:
            note.add_present("references")
        else:
            note.add_absent(
                "references",
                absent_reasons.get(
                    "references", "no upstream insights / docs referenced"
                ),
            )
        return note


def _render_references_md(references: list[str]) -> str:
    if not references:
        return "_无引用_"
    return "\n".join(f"- {ref}" for ref in references) + "\n"
