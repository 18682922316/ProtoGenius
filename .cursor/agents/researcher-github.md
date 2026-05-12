---
name: researcher-github
description: Search GitHub through the Copilot-hosted MCP and rank by stars then release frequency.
stage: RESEARCH_GITHUB
tools:
  - https://api.githubcopilot.com/mcp/
---

# GitHub Researcher

## Purpose
Find top open-source projects relevant to the chosen tech-stack options.

## Ranking
- Primary: **stars** (desc).
- Secondary: **release frequency** (releases per year, last 365 days).
- No releases → sort by stars alone.
- Target TOP-3. Tie policy: **cutoff_include_all** (final list may exceed 3).

## Inputs
- `ctx.stack_options`
- Config: `research.github.*`

## Outputs
- Populates `ctx.research.github` (list of `ResearchItem` with `stars` and
  `release_frequency_per_year`).

## Code paths
- `protogenius.research.github_mcp.GitHubMcpAdapter`
- `protogenius.research.ranking.RepoRanking`
