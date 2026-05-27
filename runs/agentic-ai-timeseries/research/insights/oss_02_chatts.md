# Insight Report — OSS #2: ChatTS

> **coverage_note**: ByteDance research output. VLDB 2025 peer-reviewed. Focuses on TS-native multimodal understanding rather than prediction.

## Identification

| Field | Value |
|-------|-------|
| insight_id | `oss-02-chatts` |
| insight_type | oss |
| title | ChatTS — Time Series Multimodal LLM |
| maintainer | NetManAIOps (ByteDance/Tsinghua) |
| license | Apache-2.0 |
| stars | 448 |
| last_release | No formal releases (active Apr 2026) |
| url | https://github.com/NetManAIOps/ChatTS |

## Core Conclusions

1. **First MLLM treating time series as a native modality** — like images in vision MLLMs. Encodes TS directly into the model's embedding space.
2. **46-76% gains on categorical tasks** and **80-113% on numerical alignment** vs. GPT-4o when reasoning over time series.
3. **Available in 8B and 14B variants** on HuggingFace — suitable for on-premise deployment.
4. **Focus on understanding/reasoning** rather than prediction — answers questions like "Is this series trending up?" or "When did the anomaly start?" with high accuracy.
5. **Chain-of-thought reasoning** over temporal patterns demonstrated — enables explanations alongside detections.

## Engineering Assessment

| Aspect | Rating | Notes |
|--------|--------|-------|
| Code quality | Good | Well-structured, reproducible training scripts |
| Documentation | Medium | Paper-focused; limited deployment docs |
| Dependency weight | Heavy | Requires GPU for inference (8B/14B models) |
| Production readiness | Medium | No formal releases; research codebase |
| Integration effort | Medium | Model loading + inference API needed |

## Relevance to Platform

- **Reasoning layer**: ChatTS could serve as the "understanding" agent in a multi-agent TS system — answering questions about data before/after forecasting.
- **Complementary to TSFMs**: TSFMs predict; ChatTS reasons. Combined = agentic forecasting with explanation.
- **GPU requirement**: 8B model needs ~16GB VRAM; 14B needs ~28GB. Plan for inference infrastructure.

## Auditable Citation

```
Repository: https://github.com/NetManAIOps/ChatTS
License: Apache-2.0
Paper: VLDB 2025
Accessed: 2026-05-27
Stars: 448 (as of access date)
```
