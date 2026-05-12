---
name: github-mcp-search
description: GitHub repository search via the Copilot-hosted MCP, with star + release-frequency ranking.
inputs: SearchQuery
outputs: list[ResearchItem]
code:
  - protogenius.research.github_mcp.GitHubMcpAdapter
  - protogenius.research.ranking.RepoRanking
---

# github-mcp-search skill

Endpoint frozen at `https://api.githubcopilot.com/mcp/`. Tools called:

- `github.search_repositories`
- `github.releases` (used to compute `release_frequency_per_year`)

Ranking happens after retrieval via `RepoRanking.rank` which honours
`tie_policy: cutoff_include_all`.
