# Industry Research — Agentic AI × Time-Series Analytics

> **coverage_note**: Surveyed all 7 target companies (Anthropic, OpenAI, DeepMind, ByteDance, Alibaba, Tencent, Meituan). Tencent had no relevant direct findings. Multiple sources per capability kept separate per v2 rules. All items carry `uncertainty` field.

## Findings

| # | Company | Product/Feature | Source | Date | URL | Summary | Uncertainty |
|---|---------|----------------|--------|------|-----|---------|-------------|
| 1 | Anthropic | Claude Financial Services Agents | Blog/Docs | May 2026 | https://www.anthropic.com/news/finance-agents | 10 agent templates for finance: 13-week cash flow forecasting, revenue modeling, scenario planning. | medium |
| 2 | Anthropic | Claude for Financial Services | Blog/Docs | Apr 2026 | https://www.anthropic.com/news/claude-for-financial-services | Monte Carlo simulations, risk modeling, TS-based portfolio monitoring. | medium |
| 3 | Anthropic | Model Context Protocol (MCP) | Docs/Report | Nov 2024+ | https://modelcontextprotocol.io/ | Open protocol for agent-to-data connectivity; supports TimescaleDB, GreptimeDB, IoTDB, Prometheus. | low |
| 4 | OpenAI | In-House Data Agent | Blog | 2026 | https://openai.com/index/inside-our-in-house-data-agent/ | Internal data agent with RAG over metadata, live queries to data warehouse. | high |
| 5 | OpenAI | Agents SDK | Docs/GitHub | Mar 2025+ | https://github.com/openai/openai-agents-python | Multi-agent framework (26.7k stars): tool calling, sandbox agents, tracing. | medium |
| 6 | OpenAI | o3/o4-mini Tool Use | Report/Docs | Apr 2025 | https://cdn.openai.com/pdf/2221c875-02dc-4789-800b-e7758f3722c1/o3-and-o4-mini-system-card.pdf | Reasoning models with Python interpreter for TS forecasting via code execution. | medium |
| 7 | DeepMind/Google | TimesFM 2.5 | Report/Docs | Sep 2025+ | https://github.com/google-research/timesfm | 200M-param decoder-only TSFM, 16K context, zero-shot forecasting. 20K+ stars. | low |
| 8 | DeepMind/Google | TimesFM in BigQuery (AI.FORECAST) | Blog/Docs | Mar 2026 GA | https://cloud.google.com/blog/products/data-analytics/timesfm-models-in-bigquery-and-alloydb | SQL-based forecasting via AI.FORECAST, AI.EVALUATE, AI.DETECT_ANOMALIES. | low |
| 9 | DeepMind/Google | TimesFM Agent Skill (ADK/MCP) | Docs/GitHub | 2026 | https://deepwiki.com/google-research/timesfm/3.5-agent-skill-(timesfm-forecasting) | First-party Agent Skill for agentic invocation via ADK, MCP Toolbox. | low |
| 10 | ByteDance | ChatTS (TS-MLLM) | Report | VLDB 2025 | https://github.com/NetManAIOps/ChatTS | Multimodal LLM for native TS understanding/reasoning. 8B/14B models. | low |
| 11 | ByteDance | Timer-S1 (8.3B TSFM) | Report | Mar 2026 | https://huggingface.co/bytedance-research/Timer-S1 | Largest TSFM: 8.3B params (0.75B activated), SOTA on GIFT-Eval. | low |
| 12 | Alibaba | Time-MoE (2.4B TSFM) | Report | ICLR 2025 | https://github.com/Time-MoE/Time-MoE | First MoE-based TSFM, 2.4B params (1.1B active), trained on Time-300B. | low |
| 13 | Alibaba | Qwen-Agent Framework | Docs | 2025-2026 | https://github.com/QwenLM/Qwen-Agent | Agent framework with MCP support for orchestrating TS workflows. | medium |
| 14 | Alibaba | Qwen3.7-Max | Blog | May 2026 | https://www.media-outreach.com/news/singapore/2026/05/26/466902/ | Frontier agentic model: 35-hour sustained operation without context drift. | high |
| 15 | Tencent | — | — | — | — | No relevant findings. | — |
| 16 | Meituan | PGHS (Hybrid Simulation) | Report | Apr 2026 | https://arxiv.org/abs/2604.15190 | Dual-process LLM+ML framework for simulating group-level temporal behavior. | medium |
| 17 | Meituan | Xiaotuan AI Agent (LongCat) | Blog | 2025-2026 | https://www.houdao.com/d/6690 | AI decision engine with real-time demand forecasting for local services. | high |

## Summary by Company

| Company | Position | Key Offerings |
|---------|----------|---------------|
| **DeepMind/Google** | Leader (complete stack) | TimesFM 2.5 + BigQuery GA + Agent Skill (ADK/MCP) |
| **ByteDance** | Strong research | ChatTS (reasoning) + Timer-S1 (largest TSFM) |
| **Alibaba** | Strong research + infra | Time-MoE (ICLR) + Qwen-Agent (MCP) |
| **Anthropic** | Connectivity leader | MCP standard + financial agents |
| **OpenAI** | General infra | Agents SDK + reasoning models with tool use |
| **Meituan** | Tangential | Hybrid simulation, demand forecasting |
| **Tencent** | No relevant findings | — |
