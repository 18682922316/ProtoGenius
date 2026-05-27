# Insight Report — Enterprise #3: ByteDance TS Research (Timer-S1 + ChatTS)

> **coverage_note**: Two distinct contributions from ByteDance Research — largest TSFM (Timer-S1) and TS-native MLLM (ChatTS). Low uncertainty — both have public models and papers.

## Identification

| Field | Value |
|-------|-------|
| insight_id | `enterprise-03-bytedance` |
| insight_type | enterprise |
| title | ByteDance — Timer-S1 (8.3B TSFM) + ChatTS (TS Multimodal LLM) |
| company | ByteDance |
| source_type | Technical report + Open-source |
| date | VLDB 2025 (ChatTS) / Mar 2026 (Timer-S1) |
| uncertainty | low |

## Core Conclusions

1. **Timer-S1**: Largest published TSFM at 8.3B total params (0.75B activated per token via MoE). 11.5K context length. SOTA on GIFT-Eval (best MASE 0.693, CRPS 0.485).
2. **Serial-Token Prediction**: Novel training objective that avoids rolling inference — each token predicts the next time step directly, enabling efficient long-horizon forecasting.
3. **TimeBench**: Trained on 1 trillion time points — largest known TS training corpus.
4. **ChatTS (14B)**: TS-native MLLM for understanding/reasoning. Not for prediction, but for answering questions about temporal data with CoT reasoning.
5. **Complementary pair**: Timer-S1 (prediction) + ChatTS (reasoning) = complete agentic TS intelligence stack from one vendor.

## Adoption Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Technical maturity | ★★★★☆ | Published models on HuggingFace; no production API |
| Integration effort | ★★★☆☆ | Requires self-hosting 8.3B model (GPU infra) |
| Cost | ★★★☆☆ | GPU cost for inference; no cloud API available |
| Vendor lock-in risk | ★★★★☆ | Open weights; Apache-2.0 (ChatTS) |
| Community | ★★★☆☆ | Growing but smaller than TimesFM |

## Relevance to Platform

- **Scale advantage**: Timer-S1's MoE architecture (0.75B active) means only 2-3GB VRAM per inference — efficient for a model that rivals 200M dense models.
- **Reasoning + Prediction**: ChatTS + Timer-S1 together could form a two-agent system (one reasons, one predicts).
- **Risk**: No production API; requires self-hosting and inference infrastructure.

## Auditable Citation

```
Timer-S1: https://huggingface.co/bytedance-research/Timer-S1
ChatTS: https://github.com/NetManAIOps/ChatTS (Apache-2.0, VLDB 2025)
Accessed: 2026-05-27
```
