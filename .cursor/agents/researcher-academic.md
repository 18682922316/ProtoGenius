---
name: researcher-academic
description: Search arXiv (MCP) + Semantic Scholar + OpenAlex + venue proceedings, with dedup and institution-preference handling.
stage: RESEARCH_ACADEMIC
tools:
  - arxiv MCP
  - https://api.semanticscholar.org
  - https://api.openalex.org
  - venue scrapers (optional)
---

# Academic Researcher

## Purpose
Produce the academic stream of the research bundle. Honours:

- arXiv window: last **3 months**.
- Top-tier venues window: **1 year** since conference date.
- Same work across multiple versions → **one** entry (`dedup.deduplicate_papers`).
- Institution preference is **agent-judged** at runtime; the rationale is
  recorded in the research summary.

## Inputs
- `ctx.stack_options` (used to build search queries)
- Config: `research.academic.*`

## Outputs
- Populates `ctx.research.academic` (list of `ResearchItem`).
- Each item carries URL or DOI (or both); citations land in `audit.jsonl`.

## Code paths
- `protogenius.research.arxiv_mcp.ArxivMcpAdapter`
- `protogenius.research.semantic_scholar.SemanticScholarAdapter`
- `protogenius.research.openalex.OpenAlexAdapter`
- `protogenius.research.conference_proc.ConferenceProceedingsAdapter`
- `protogenius.research.dedup.deduplicate_papers`
