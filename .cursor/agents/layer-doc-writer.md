---
name: layer-doc-writer
description: Generate the four-layer technical-asset pack (L1 foundation_theory → L2 atomic_algorithm → L3 tech_topic → L4 ai_application).
stage: DRAFT_LAYER_DOCS
tools:
  - LLM only
---

# Four-layer Technical Doc Writer (v2 §4.4)

## Pipeline

1. Determine the layer set with `protogenius.research.select_layers(scoped)`.
2. For each selected layer, the sub-agent fills the `body` dict
   matching the layer's template (see `protogenius.docs.layer_docs.LAYER_SPECS`).
3. Hand the body off to
   `LayerDocsGenerator.render_layer(layer=..., name=..., body=..., references=...)`.
4. Append the resulting `LayerDoc` to `ctx.layer_docs`.

## Mandatory invariants

- Every produced doc must contain a `## 形式化定义` block populated with
  the layer-specific elements documented in v2 §4.4.5.
- Every produced doc must satisfy the v2 §2.5 minimum content baseline:
  frontmatter + basic info + formalization + references. The generator
  raises `LayerDocMinimumContentError` / `FormalizationBlockMissingError`
  if either invariant is violated.

## kb_ref / conflicts

- If `ctx.kb_snapshot` is populated, the writer must check whether a
  matching KB doc exists for the same name/layer. When yes:
  - Set `LayerDoc.kb_refs` to the resolved `kb://` URI.
  - If content disagrees, append a one-line summary to
    `LayerDoc.conflicts` (rendered as a `⚠ 与知识库冲突` block by the
    template) and log an audit `decision: kb_conflict` event.

## Sign-off

The four-layer pack is reviewed in the SAME sign-off gate as the SRS/TDD
(`GATE_DOC_SIGNOFF`) by default. Set `documents.merge_tdd_and_layer_signoff: false`
to split into two consecutive gates per v2 §3.
