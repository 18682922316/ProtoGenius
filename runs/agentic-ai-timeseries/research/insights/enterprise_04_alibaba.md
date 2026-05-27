# Insight Report — Enterprise #4: Alibaba (Time-MoE + Qwen-Agent)

> **coverage_note**: Covers ICLR 2025 Spotlight paper (Time-MoE) and Qwen-Agent framework (MCP support). Low uncertainty for Time-MoE (peer-reviewed); medium for Qwen-Agent (evolving product).

## Identification

| Field | Value |
|-------|-------|
| insight_id | `enterprise-04-alibaba` |
| insight_type | enterprise |
| title | Alibaba — Time-MoE (2.4B TSFM) + Qwen-Agent (MCP Framework) |
| company | Alibaba (DAMO Academy + Qwen Team) |
| source_type | Technical report (ICLR 2025) + Product docs |
| date | ICLR 2025 (Time-MoE) / 2025-2026 (Qwen-Agent) |
| uncertainty | low (Time-MoE) / medium (Qwen-Agent) |

## Core Conclusions

1. **Time-MoE**: First MoE-based TSFM. 2.4B total params, 1.1B activated at inference (<8GB VRAM). Multi-resolution forecasting head supports arbitrary horizons.
2. **Time-300B**: Pre-trained on 300B+ time points across 9 domains — demonstrates domain-diverse foundation model scaling.
3. **>20% MSE reduction** over baselines on standard benchmarks (ICLR 2025 Spotlight).
4. **Qwen-Agent**: General-purpose agent framework with MCP integration, tool calling, planning, and memory. Qwen3 excels at tool-calling — relevant for orchestrating TS workflows.
5. **Qwen3.7-Max**: Frontier model supporting 35-hour sustained operation — applicable to continuous monitoring/forecasting scenarios.

## Adoption Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Technical maturity | ★★★★☆ | ICLR Spotlight; open weights on HuggingFace |
| Integration effort | ★★★☆☆ | Self-hosting required for Time-MoE; Qwen-Agent is pip-installable |
| Cost | ★★★★☆ | MoE efficiency: <8GB VRAM for 2.4B model |
| Vendor lock-in risk | ★★★★☆ | Open weights; Qwen-Agent is open-source |
| Community | ★★★☆☆ | Chinese-language community dominant; English docs available |

## Relevance to Platform

- **Efficient TSFM**: Time-MoE's <8GB footprint makes it deployable on consumer GPUs — lowest infrastructure requirement.
- **Agent framework**: Qwen-Agent + MCP provides a ready-made orchestration layer for TS agents.
- **Combination**: Time-MoE (prediction) + Qwen-Agent (orchestration) = low-cost agentic TS pipeline.

## Auditable Citation

```
Time-MoE: https://github.com/Time-MoE/Time-MoE (ICLR 2025 Spotlight)
Qwen-Agent: https://github.com/QwenLM/Qwen-Agent
Accessed: 2026-05-27
```
