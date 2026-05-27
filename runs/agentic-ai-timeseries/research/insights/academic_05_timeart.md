# Insight Report — Academic #5: TimeART

> **coverage_note**: Full analysis. TimeToolBench (100K trajectories) is the most comprehensive tool-use training corpus for TS agents to date.

## Identification

| Field | Value |
|-------|-------|
| insight_id | `academic-05-timeart` |
| insight_type | academic |
| title | TimeART: Towards Agentic Time Series Reasoning via Tool-Augmentation |
| authors | Multiple |
| affiliation | Multiple |
| source_venue | arXiv preprint |
| date | 2026-01 |

## Core Conclusions

1. **21 analytical tools** integrated into a unified agent interface spanning statistical methods (ACF, STL decomposition), ML models (XGBoost, ARIMA), and lightweight time-series foundation models.
2. **TimeToolBench**: 100K-trajectory training corpus for teaching LLMs to select and chain TS analysis tools — largest of its kind.
3. **8B fine-tuned TSRM** (Time Series Reasoning Model) achieves SOTA on multiple benchmarks by learning when and how to invoke each tool.
4. **Key insight**: Tool selection matters more than model size — an 8B model with proper tool training outperforms much larger models without tool access.

## Relevance to Platform

- **Tool registry design**: The 21-tool taxonomy provides a blueprint for what tools an agentic TS platform should expose.
- **Training data**: TimeToolBench pattern (synthetic tool-use trajectories) is replicable for internal fine-tuning.
- **Cost efficiency**: 8B model + tools beats 70B+ models — important for production cost control.

## Auditable Citation

```
@article{timeart2026,
  title={TimeART: Towards Agentic Time Series Reasoning via Tool-Augmentation},
  journal={arXiv preprint arXiv:2601.13653},
  year={2026},
  url={https://arxiv.org/abs/2601.13653}
}
```
