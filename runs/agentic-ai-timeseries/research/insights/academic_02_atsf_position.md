# Insight Report — Academic #2: ATSF Position Paper

> **coverage_note**: Position paper — no empirical results. Covers taxonomy and design-space formulation comprehensively.

## Identification

| Field | Value |
|-------|-------|
| insight_id | `academic-02-atsf-position` |
| insight_type | academic |
| title | Position: Beyond Model-Centric Prediction — Agentic Time Series Forecasting |
| authors | Cheng, Tao, Liu, Guo, Chen |
| affiliation | USTC (中国科学技术大学) |
| source_venue | arXiv preprint (v4) |
| date | 2026-02 |

## Core Conclusions

1. **Defines the ATSF formulation**: time-series forecasting reimagined as an agentic process with five capabilities — perception, planning, action, reflection, and memory.
2. **Three paradigms identified**: (a) workflow-based design (human-designed multi-step pipelines), (b) agentic RL (agent learns forecasting strategy through reward), (c) hybrid workflows (LLM reasoning + traditional models).
3. **Key insight**: The shift from "model-centric prediction" to "agent-centric process" unlocks iterative refinement, tool use, and self-correction — capabilities absent in traditional forecasting pipelines.
4. **Open challenges catalogued**: benchmark standardization, agent-specific evaluation metrics (beyond MAE/RMSE), computational cost of multi-turn reasoning, safety in autonomous deployment.

## Relevance to Platform

- **Taxonomy**: Directly usable as the conceptual framework for classifying internal forecasting capabilities.
- **Design-space map**: Guides architecture decisions (which paradigm to adopt for which use case).
- **Gap identification**: Points to where the platform should invest (evaluation, safety, cost management).

## Auditable Citation

```
@article{cheng2026atsf,
  title={Position: Beyond Model-Centric Prediction—Agentic Time Series Forecasting},
  author={Cheng, Mingyang and Tao, Xing and Liu, Qi and Guo, Zhicheng and Chen, Enhong},
  journal={arXiv preprint arXiv:2602.01776},
  year={2026},
  url={https://arxiv.org/abs/2602.01776}
}
```
