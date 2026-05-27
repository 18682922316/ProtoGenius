# Insight Report — Academic #6: TimeSeriesScientist

> **coverage_note**: Full-paper analysis. 4-agent architecture is the most interpretable design in this space.

## Identification

| Field | Value |
|-------|-------|
| insight_id | `academic-06-tssci` |
| insight_type | academic |
| title | TimeSeriesScientist: A General-Purpose AI Agent for Time Series Analysis |
| authors | Zhao, Zhang, Wei, Xu, He, Sun, You |
| affiliation | Multiple (including Yale) |
| source_venue | arXiv preprint |
| date | 2025-10 |

## Core Conclusions

1. **First end-to-end LLM-driven 4-agent framework**: Curator (data prep), Planner (strategy), Forecaster (execution), Reporter (explanation).
2. **10.4% reduction in forecast error** over statistical baselines and **38.2% over LLM-only baselines** on 8 benchmarks.
3. **White-box interpretability**: Each agent's intermediate output is human-readable, enabling debugging and trust verification.
4. **General-purpose**: Handles forecasting, classification, and anomaly detection without architecture changes.

## Relevance to Platform

- **Agent role design**: 4-role decomposition (Curator/Planner/Forecaster/Reporter) is a clean reference for internal agent orchestration.
- **Interpretability**: Critical for enterprise adoption — every decision is traceable.
- **Limitation**: GitHub repo appears dormant (last push Nov 2025); may not scale to production workloads.

## Auditable Citation

```
@article{zhao2025tssci,
  title={TimeSeriesScientist: A General-Purpose AI Agent for Time Series Analysis},
  author={Zhao, Haokun and Zhang, Xiang and Wei, Jiaqi and Xu, Yiwei and He, Yuting and Sun, Siqi and You, Chenyu},
  journal={arXiv preprint arXiv:2510.01538},
  year={2025},
  url={https://arxiv.org/abs/2510.01538}
}
```
