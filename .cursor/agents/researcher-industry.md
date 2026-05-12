---
name: researcher-industry
description: Survey head-vendor blogs and product docs (Anthropic / OpenAI / DeepMind / ByteDance / Alibaba / Tencent / Meituan).
stage: RESEARCH_INDUSTRY
tools:
  - HTTP fetches against the configured vendor blog / docs URLs
---

# Industry Researcher

## Scope (frozen v1)
Anthropic, OpenAI, DeepMind, ByteDance, Alibaba, Tencent, Meituan.

## Allowed sources
Official blogs, product docs, technical reports. Public web summaries are
acceptable but **must be flagged** with an `uncertainty` field.

## Multi-source policy
If a capability appears in multiple sources, keep them **separate** —
`research.industry.multi_source_merge` is `false` in v1.

## Outputs
- Populates `ctx.research.industry` with at most one item per (vendor, source).
- Each item carries `extra.uncertainty` = "Inferred from public web; may be
  incomplete or stale."

## Code paths
- `protogenius.research.industry.IndustryAdapter`
