---
name: insight-writer
description: Render one structured insight report per accepted research source (v2 §2.4.A/B/C).
stage: GENERATE_INSIGHTS
tools:
  - LLM only (Cursor mode) or LLMClient (CLI mode)
---

# Insight Writer (v2 §2.4.A/B/C)

## Purpose

Convert every `ResearchItem` in `ctx.research.{academic, github, industry}`
into a structured insight Markdown report. One artifact per item,
written under `runs/<id>/research/insights/<INS-...>.md`.

## Template selection

| ResearchItem.source_type | insight_type | Template                                  |
|--------------------------|--------------|-------------------------------------------|
| arxiv, conference        | academic     | `templates/insight_academic.md`           |
| github                   | oss          | `templates/insight_oss.md`                |
| industry                 | enterprise   | `templates/insight_enterprise.md`         |

## Output discipline

- `insight_id` is deterministic (SHA1 of URL/DOI + slugified title).
- Every report ends with an auditable citation block (URL / DOI /
  version / accessed_at).
- Fields that were not filled (no evidence found, scoped out, KB
  preferred) are listed in the `coverage_note` block at the top.
- Minimum content (`identification` + `core_conclusions` + `citation`)
  is enforced by `protogenius.docs.insight_generator.check_insight_minimum`;
  the generator will refuse to write an artifact that violates the
  baseline unless `insights.enforce_minimum_content` is False.

## Code path

`protogenius.docs.insight_generator.InsightGenerator.render_all`
