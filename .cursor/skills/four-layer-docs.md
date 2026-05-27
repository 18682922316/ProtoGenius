---
name: four-layer-docs
description: Generate the four-layer technical-asset documentation pack with the v2 §4.4.5 formalization block.
inputs: RunContext + body dictionaries per layer
outputs: runs/<id>/documents/layers/<layer>/<slug>.md + LayerDoc entries
code: protogenius.docs.layer_docs.LayerDocsGenerator
templates:
  - templates/layer_l1_foundation_theory.md
  - templates/layer_l2_atomic_algorithm.md
  - templates/layer_l3_tech_topic.md
  - templates/layer_l4_ai_application.md
---

# four-layer-docs skill (v2 §4.4)

Produces one technical-asset document per selected layer with:

- the IEEE-style YAML frontmatter (name / description / layer / version),
- a coverage_note block (kept vs. dropped fields with reasons),
- a `## 形式化定义` block populated with layer-specific elements
  (v2 §4.4.5),
- a references list + optional `kb_ref` block + optional
  `⚠ 与知识库冲突` block.

Two strict invariants are enforced before the doc is written to disk:

1. `FormalizationBlockMissingError` if the `## 形式化定义` heading is
   absent.
2. `LayerDocMinimumContentError` if the doc fails the v2 §2.5 minimum
   (frontmatter + basic info + formalization + references).
