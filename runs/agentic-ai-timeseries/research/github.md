# GitHub Research — Agentic AI × Time-Series Analytics

> **coverage_note**: Searched 6 query variants. Ranking: stars (primary) → release frequency (secondary). Tie policy: `cutoff_include_all`. No ties at TOP-3 boundary. Secondary table includes foundation-model infrastructure repos that agentic systems wrap.

## Primary — Directly Agentic TS Repos

| # | Repository | Stars | Last Release | URL | Relevance |
|---|---|---|---|---|---|
| 1 | **TimeCopilot/timecopilot** | 478 | v0.0.25 (2026-04-07), 23 releases | https://github.com/TimeCopilot/timecopilot | Agentic forecasting: LLM orchestrates 30+ TSFMs, NL interface, cross-validation, NeurIPS 2025. |
| 2 | **NetManAIOps/ChatTS** | 448 | No formal releases (active Apr 2026) | https://github.com/NetManAIOps/ChatTS | Multimodal LLM for native TS understanding/reasoning, VLDB 2025. Treats TS as first-class modality. |
| 3 | **Y-Research-SBU/TimeSeriesScientist** | 138 | No releases (Oct 2025) | https://github.com/Y-Research-SBU/TimeSeriesScientist | 4-agent architecture (Curator→Planner→Forecaster→Reporter) for general TS forecasting. |
| 4 | **ustc-time-series/CastClaw** | 35 | v1.2.1 (2026-04-30) | https://github.com/ustc-time-series/CastClaw | Multi-agent + reflection: session learning, parallel experiments, human-in-the-loop, 30+ models. |

## Secondary — Foundation Model Infrastructure

| # | Repository | Stars | Last Release | URL | Relevance |
|---|---|---|---|---|---|
| 1 | **google-research/timesfm** | 20,114 | v1.2.6 (2024-12-31) | https://github.com/google-research/timesfm | TimesFM 2.5 with explicit Agent Skill directory for ADK/MCP integration. |
| 2 | **amazon-science/chronos-forecasting** | 5,042 | v2.2.2 (2025-12-17) | https://github.com/amazon-science/chronos-forecasting | Chronos-2: T5-based tokenized forecasting, backbone for TimeCopilot & CastClaw. |
| 3 | **KimMeen/Time-LLM** | 2,601 | No releases | https://github.com/KimMeen/Time-LLM | ICLR 2024 — Reprogramming frozen LLMs for TS forecasting. Foundational concept for TS-MLLM. |

## Key Insight

The field was formally named **"Agentic Time Series Forecasting (ATSF)"** in a Feb 2026 position paper (arXiv:2602.01776). Three paradigms identified: workflow-based design, agentic RL, and hybrid workflows. Foundation models (TimesFM, Chronos) are rapidly adding agent-integration layers.
