---
name: semantic-scholar-search
description: Published-venue academic search via Semantic Scholar.
inputs: SearchQuery
outputs: list[ResearchItem]
code: protogenius.research.semantic_scholar.SemanticScholarAdapter
---

# semantic-scholar-search skill

Anonymous calls are supported but `PROTOGENIUS_SEMANTIC_SCHOLAR_API_KEY` is
recommended to avoid rate-limit pressure.
