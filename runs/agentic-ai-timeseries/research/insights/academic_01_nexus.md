# Insight Report — Academic #1: Nexus

> **coverage_note**: Full-paper analysis. Fields `methodology_detail` and `ablation_results` partially covered (paper is preprint, appendix not yet peer-reviewed).

## Identification

| Field | Value |
|-------|-------|
| insight_id | `academic-01-nexus` |
| insight_type | academic |
| title | Nexus: An Agentic Framework for Time Series Forecasting |
| authors | Das, Goyal, Parmar, Peng, Tirumalashetty, Li, Zhang, Yoon, Pfister |
| affiliation | Google Research, Penn State University |
| source_venue | arXiv preprint |
| date | 2026-05-20 |

## Core Conclusions

1. **LLMs possess stronger intrinsic forecasting ability than previously recognized** when numerical and contextual reasoning are properly decomposed and organized via multi-agent collaboration.
2. **Macro/micro temporal decomposition** (separating trend-level fluctuations from fine-grained patterns) outperforms monolithic forecasting approaches by allowing each agent to specialize.
3. **Contextual integration stage** enables the system to incorporate domain knowledge and external signals that purely numerical models miss.
4. Multi-agent architecture achieves SOTA on multiple benchmarks while maintaining interpretability through explicit intermediate outputs at each stage.

## Relevance to Platform

- **Architecture pattern**: Direct blueprint for building multi-agent forecasting pipelines on the internal platform.
- **Interface design**: Each agent exposes a clear input/output contract → maps to MCP tool definitions.
- **Limitation**: Google-internal infrastructure assumptions; needs adaptation for platform-specific data connectors.

## Auditable Citation

```
@article{das2026nexus,
  title={Nexus: An Agentic Framework for Time Series Forecasting},
  author={Das, Sarkar Snigdha Sarathi and Goyal, Palash and Parmar, Mihir and Peng, Nanyun and Tirumalashetty, Vishy and Li, Chun-Liang and Zhang, Rui and Yoon, Jinsung and Pfister, Tomas},
  journal={arXiv preprint arXiv:2605.14389},
  year={2026},
  url={https://arxiv.org/abs/2605.14389}
}
```
