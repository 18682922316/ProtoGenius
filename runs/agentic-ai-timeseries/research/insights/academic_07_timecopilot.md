# Insight Report — Academic #7: TimeCopilot

> **coverage_note**: Peer-reviewed (NeurIPS 2025 BERTs Workshop). Also the top-starred directly-agentic TS GitHub repo. Dual academic+OSS analysis.

## Identification

| Field | Value |
|-------|-------|
| insight_id | `academic-07-timecopilot` |
| insight_type | academic |
| title | TimeCopilot |
| authors | Garza, Rosillo |
| affiliation | Nixtla |
| source_venue | NeurIPS 2025 (BERTs Workshop) |
| date | 2025-09 |

## Core Conclusions

1. **First open-source agentic forecasting framework** combining 30+ time-series foundation models with LLM reasoning via a unified API.
2. **#1 on GIFT-Eval benchmark** — the most comprehensive public evaluation of forecasting systems.
3. **Automated pipeline**: Feature analysis → model selection → cross-validation → natural-language explanations. User provides data + NL question, system handles everything.
4. **23 releases in <1 year** — highest release velocity in the agentic TS space, indicating production maturity.

## Relevance to Platform

- **Production reference**: Most mature open-source implementation of the agentic forecasting pattern.
- **Model aggregation**: Pattern of wrapping multiple TSFMs behind a single agent is directly adoptable.
- **NL interface**: Demonstrates that natural-language interaction with forecasting is viable and accurate.
- **Integration path**: Apache 2.0 licensed; could be wrapped as an MCP tool.

## Auditable Citation

```
@article{garza2025timecopilot,
  title={TimeCopilot},
  author={Garza, Azul and Rosillo, Ren{\'e}e},
  journal={arXiv preprint arXiv:2509.00616},
  year={2025},
  url={https://arxiv.org/abs/2509.00616}
}
```
