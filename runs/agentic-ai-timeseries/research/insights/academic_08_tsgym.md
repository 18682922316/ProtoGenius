# Insight Report — Academic #8: TimeSeriesGym

> **coverage_note**: Peer-reviewed (NeurIPS 2025). Evaluation-focused — no new model, but critical infrastructure for benchmarking agentic TS systems.

## Identification

| Field | Value |
|-------|-------|
| insight_id | `academic-08-tsgym` |
| insight_type | academic |
| title | TimeSeriesGym: A Scalable Benchmark for (Time Series) ML Engineering Agents |
| authors | Cai, Li, Goswami, Wiliński, Welter, Dubrawski |
| affiliation | CMU |
| source_venue | NeurIPS 2025 |
| date | 2025-05 |

## Core Conclusions

1. **34 challenges across 8 TS problem types and 15 domains** for evaluating AI agents on realistic ML engineering tasks.
2. **Supports multiple agent scaffolds**: AIDE, ResearchAgent, OpenHands — enabling fair cross-framework comparison.
3. **Tasks include**: data labeling, model selection, hyperparameter tuning, code migration, pipeline debugging — full ML engineering lifecycle.
4. **Key finding**: Current agents solve <40% of challenges end-to-end, highlighting significant room for improvement.

## Relevance to Platform

- **Internal evaluation**: Adopt TimeSeriesGym (or a subset) as the internal benchmark for measuring agent capabilities.
- **Gap quantification**: <40% solve rate means production deployment requires careful guardrails and human oversight.
- **Task taxonomy**: The 8 problem types provide a checklist for internal capability planning.

## Auditable Citation

```
@article{cai2025tsgym,
  title={TimeSeriesGym: A Scalable Benchmark for (Time Series) ML Engineering Agents},
  author={Cai, Yifu and Li, Xinyu and Goswami, Mononito and Wili{\'n}ski, Micha{\l} and Welter, Gus and Dubrawski, Artur},
  journal={arXiv preprint arXiv:2505.13291},
  year={2025},
  url={https://arxiv.org/abs/2505.13291}
}
```
