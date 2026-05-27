---
name: insight-reports
description: Render structured insight reports (academic / oss / enterprise) per accepted research source.
inputs:
  - RunContext.research.{academic, github, industry}
  - body dictionaries (LLM-filled prose)
outputs: runs/<id>/research/insights/INS-*.md + InsightReport entries
code: protogenius.docs.insight_generator.InsightGenerator
templates:
  - templates/insight_academic.md
  - templates/insight_oss.md
  - templates/insight_enterprise.md
---

# insight-reports skill (v2 §2.4.A/B/C)

Every accepted source generates exactly one structured Markdown report.
The skill takes care of:

- deterministic `insight_id` derivation (SHA1 of URL/DOI + slugified
  title);
- coverage_note block at the top listing which fields are present /
  absent and why (v2 §2.5);
- minimum-content baseline enforcement (identification + core
  conclusions + auditable citation), raising
  `InsightMinimumContentError` on violations.
