# Insight Report — Enterprise #1: Google/DeepMind Complete TS Agent Stack

> **coverage_note**: Covers TimesFM 2.5 + BigQuery AI.FORECAST + Agent Skill (ADK/MCP). Three separate products forming a complete stack. Low uncertainty — all GA or well-documented.

## Identification

| Field | Value |
|-------|-------|
| insight_id | `enterprise-01-google-stack` |
| insight_type | enterprise |
| title | Google/DeepMind — TimesFM Agent Stack (Foundation Model + BigQuery + ADK/MCP) |
| company | Google / DeepMind |
| source_type | Product docs + Technical report + Official blog |
| date | Sep 2025 – Mar 2026 (GA) |
| uncertainty | low |

## Core Conclusions

1. **Only company with a complete agent-ready TS stack**: Foundation model (TimesFM 2.5) → SQL interface (BigQuery AI.FORECAST) → Agent integration (ADK/MCP Agent Skill).
2. **Production-deployed**: BigQuery AI.FORECAST is GA since Mar 2026. Used by enterprise customers. Zero ML expertise required — write SQL, get forecasts.
3. **Agent Skill pattern**: Structured interface with system preflight checks, hardware tier detection, model initialization. Accessible via Cursor, Claude Code, Gemini CLI.
4. **Performance**: TimesFM 2.5 achieves competitive/SOTA results on GIFT-Eval without any fine-tuning.
5. **Scale**: 16K context window (up to 15K data points in BigQuery), quantile forecasting, covariate support.

## Adoption Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Technical maturity | ★★★★★ | GA, 20K+ stars, 142K downloads |
| Integration effort | ★★★★☆ | Agent Skill simplifies; but JAX dependency for self-hosted |
| Cost | ★★★☆☆ | BigQuery pricing; self-hosted needs GPU/TPU |
| Vendor lock-in risk | ★★☆☆☆ | Apache-2.0 model; but BigQuery is Google-only |
| Community | ★★★★★ | Largest community in TS ML |

## Relevance to Platform

- **Blueprint**: The three-layer pattern (foundation model → SQL API → agent skill) is directly replicable.
- **MCP reference**: Google's Agent Skill + MCP Toolbox is the canonical example of making TSFMs agent-accessible.
- **Risk**: Google ecosystem coupling for the BigQuery path; self-hosted path requires JAX expertise.

## Auditable Citation

```
TimesFM: https://github.com/google-research/timesfm (Apache-2.0)
BigQuery AI.FORECAST: https://cloud.google.com/blog/products/data-analytics/timesfm-models-in-bigquery-and-alloydb
Agent Skill: https://deepwiki.com/google-research/timesfm/3.5-agent-skill-(timesfm-forecasting)
Accessed: 2026-05-27
```
