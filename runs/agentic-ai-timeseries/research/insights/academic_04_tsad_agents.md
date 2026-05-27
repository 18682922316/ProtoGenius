# Insight Report — Academic #4: TSAD-Agents

> **coverage_note**: Peer-reviewed (WWW 2026). Includes VisualTimeAnomaly benchmark. Multimodal switching is the key novelty.

## Identification

| Field | Value |
|-------|-------|
| insight_id | `academic-04-tsad-agents` |
| insight_type | academic |
| title | TSAD-Agents: Can Multimodal LLMs Perform Time Series Anomaly Detection? |
| authors | Xu et al. |
| affiliation | Multiple |
| source_venue | ACM Web Conference (WWW) 2026 |
| date | 2026-04 |

## Core Conclusions

1. **First multi-agent system for multimodal TSAD** with four specialized agents: Scanning, Planning, Detection, and Checking.
2. **Dynamic modality switching**: Agents decide per-window whether to reason over textual (numeric) or visual (plot) representations based on anomaly complexity.
3. **VisualTimeAnomaly benchmark** introduced — first standardized benchmark for evaluating MLLM-based anomaly detection on time series.
4. Outperforms both pure-text LLM approaches and traditional TSAD methods on complex anomaly patterns (contextual anomalies, collective anomalies).

## Relevance to Platform

- **Anomaly detection pipeline**: Direct reference architecture for building agent-based monitoring.
- **Modality selection**: Important design decision — when to use visual vs. numeric representation.
- **Benchmark**: VisualTimeAnomaly can be adopted for internal evaluation.

## Auditable Citation

```
@inproceedings{xu2026tsadagents,
  title={TSAD-Agents: Can Multimodal LLMs Perform Time Series Anomaly Detection?},
  author={Xu et al.},
  booktitle={Proceedings of the ACM Web Conference 2026 (WWW'26)},
  year={2026},
  doi={10.1145/3774904.3792376},
  url={https://doi.org/10.1145/3774904.3792376}
}
```
