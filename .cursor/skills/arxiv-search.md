---
name: arxiv-search
description: Search arXiv via the configured MCP server, with the 3-month window and dedup.
inputs: SearchQuery
outputs: list[ResearchItem]
code: protogenius.research.arxiv_mcp.ArxivMcpAdapter
---

# arxiv-search skill

Uses the user-configured arXiv MCP (`mcp.arxiv.url_env` or stdio command).
Defaults: 90-day window, categories `cs.AI / cs.CL / cs.LG / cs.SE`.

Calls into this skill are intercepted by the `pre_search` hook, which charges
the search-results quota and aborts on hard-cap overflow.
