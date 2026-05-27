# Insight Report — OSS #3: TimesFM (with Agent Skill)

> **coverage_note**: Google Research. 20K+ stars. The addition of an Agent Skill directory in 2026 makes this the first foundation model with first-party agentic integration.

## Identification

| Field | Value |
|-------|-------|
| insight_id | `oss-03-timesfm` |
| insight_type | oss |
| title | TimesFM 2.5 — Time Series Foundation Model with Agent Skill |
| maintainer | Google Research |
| license | Apache-2.0 |
| stars | 20,114 |
| last_release | v1.2.6 (2024-12-31); active commits May 2026 |
| url | https://github.com/google-research/timesfm |

## Core Conclusions

1. **200M-parameter decoder-only TSFM**: Zero-shot forecasting across any domain. 16K context length.
2. **Quantile forecasting**: Produces prediction intervals (not just point forecasts) — critical for risk-aware decision-making.
3. **Agent Skill directory** (`timesfm-forecasting/`): First-party structured interface for integration into AI agent environments (Cursor, Claude Code, OpenCode).
4. **ADK/MCP integration**: Accessible via Google's Agent Development Kit and MCP Toolbox for Databases.
5. **BigQuery GA**: `AI.FORECAST`, `AI.EVALUATE`, `AI.DETECT_ANOMALIES` SQL functions — production-deployed.

## Engineering Assessment

| Aspect | Rating | Notes |
|--------|--------|-------|
| Code quality | Excellent | Google research quality, comprehensive tests |
| Documentation | Excellent | Tutorials, colab notebooks, API docs |
| Dependency weight | Medium | JAX-based; requires TPU/GPU for training, CPU for inference |
| Production readiness | High | BigQuery GA, HuggingFace (142K downloads) |
| Integration effort | Low | pip install + Agent Skill provides structured interface |

## Relevance to Platform

- **Primary forecasting backbone**: Most production-ready TSFM with agent integration.
- **MCP pattern**: Agent Skill + MCP Toolbox is the reference implementation for exposing TSFMs to agents.
- **Ecosystem**: BigQuery integration means SQL-based access for non-ML teams.

## Auditable Citation

```
Repository: https://github.com/google-research/timesfm
License: Apache-2.0
Accessed: 2026-05-27
Stars: 20,114 (as of access date)
Agent Skill: https://deepwiki.com/google-research/timesfm/3.5-agent-skill-(timesfm-forecasting)
```
