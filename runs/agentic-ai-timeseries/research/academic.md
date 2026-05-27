# Academic Research — Agentic AI × Time-Series Analytics

> **coverage_note**: Covers arXiv preprints (Jan–May 2026, within 3-month window) and top-venue publications (NeurIPS 2025, ICML 2025, WWW 2026, VLDB 2025 — within 1-year window). Dedup applied: Augur v1/v2 → 1 entry; ATSF v1–v4 → 1 entry; TS-Agent v1/v2 → 1 entry. RAG/memory systems specifically for temporal TS data excluded (still emerging, no top-venue publication).

## Research Table

| # | Title | Authors | Venue/Source | Date | URL/DOI | Key Contribution |
|---|-------|---------|--------------|------|---------|------------------|
| 1 | **Nexus: An Agentic Framework for Time Series Forecasting** | Das et al. | arXiv (Google/Penn State) | May 2026 | https://arxiv.org/abs/2605.14389 | Multi-agent framework decomposing forecasting into macro/micro temporal fluctuation stages + contextual integration. |
| 2 | **Position: Beyond Model-Centric Prediction — Agentic Time Series Forecasting** | Cheng et al. | arXiv (USTC) | Feb 2026 | https://arxiv.org/abs/2602.01776 | Proposes the ATSF formulation — viewing forecasting as an agentic process with perception, planning, action, reflection, and memory. |
| 3 | **MAS4TS: Visual Reasoning over Time Series via Multi-Agent System** | Ruan & Liang | arXiv (HKUST-GZ) | Feb 2026 | https://arxiv.org/abs/2602.03026 | First tool-driven multi-agent system for general TS tasks using Analyzer–Reasoner–Executor paradigm with VLM-based visual anchoring. |
| 4 | **SAGE: Detecting Time Series Anomalies Like an Expert** | Multiple | arXiv | May 2026 | https://arxiv.org/abs/2605.05725 | Multi-agent LLM framework with four specialized Analyzers + Detector + Supervisor for structured anomaly diagnosis. |
| 5 | **TSAD-Agents: Can Multimodal LLMs Perform Time Series Anomaly Detection?** | Xu et al. | WWW 2026 | Apr 2026 | https://doi.org/10.1145/3774904.3792376 | First multi-agent system for multimodal TSAD with scanning, planning, detection, and checking agents. |
| 6 | **TimeART: Towards Agentic Time Series Reasoning via Tool-Augmentation** | Multiple | arXiv | Jan 2026 | https://arxiv.org/abs/2601.13653 | Integrates 21 analytical tools with a 100K-trajectory corpus (TimeToolBench) for training tool-use reasoning models. |
| 7 | **ChatAD: Reasoning-Enhanced TSAD with Multi-Turn Instruction Evolution** | Multiple | arXiv | Jan 2026 | https://arxiv.org/abs/2601.13546 | Multi-agent TSEvol generates 20K anomaly detection dialogues; introduces TKTO for cross-task generalization. |
| 8 | **ANOMSEER: TSAD via MLLM Post-Training** | Multiple | arXiv | Feb 2026 | https://arxiv.org/abs/2602.08868 | TimerPO, a temporal-aware RL algorithm grounding MLLM reasoning in classical TSAD techniques. |
| 9 | **Argos: Agentic TSAD with Autonomous Rule Generation** | Gu et al. | arXiv (Microsoft) | Jan 2025 | https://arxiv.org/abs/2501.14170 | Three-agent pipeline generating executable Python anomaly rules; +28.3% F1 on Microsoft internal dataset. |
| 10 | **TimeSeriesScientist: A General-Purpose AI Agent for TS Analysis** | Zhao et al. | arXiv | Oct 2025 | https://arxiv.org/abs/2510.01538 | End-to-end 4-agent framework (Curator, Planner, Forecaster, Reporter); reduces forecast error by 10.4%. |
| 11 | **TS-Agent: Understanding and Reasoning Over Raw TS via Iterative Insight** | Multiple | arXiv | Oct 2025 | https://arxiv.org/abs/2510.07432 | ReAct-style agentic framework keeping TS in native numeric form with tool execution and self-refinement. |
| 12 | **TimeCopilot** | Garza & Rosillo | NeurIPS 2025 (BERTs) | Sep 2025 | https://arxiv.org/abs/2509.00616 | First open-source agentic forecasting combining 30+ TSFMs with LLM reasoning; #1 on GIFT-Eval. |
| 13 | **TimeSeriesGym: A Scalable Benchmark for ML Engineering Agents** | Cai et al. | NeurIPS 2025 | May 2025 | https://arxiv.org/abs/2505.13291 | 34 challenges across 8 TS problem types for evaluating AI agents on realistic ML engineering tasks. |
| 14 | **LangTime: Language-Guided Unified Model for TS Forecasting with PPO** | Niu et al. | ICML 2025 | Jul 2025 | https://proceedings.mlr.press/v267/niu25e.html | Language-guided cross-domain forecasting using Temporal Comprehension Prompts + TimePPO (RL fine-tuning). |
| 15 | **Augur: A Teacher-Student LLM Framework for TS Forecasting** | Multiple | arXiv | Oct 2025 | https://arxiv.org/abs/2510.07858 | Fully LLM-driven forecasting using teacher-student architecture extracting directed causal associations. |

## Institution Rationale

- **Google DeepMind / Google Research** (Nexus): Top-tier — extensive time-series research (TimesFM, Chronos).
- **Microsoft Research** (Argos): Top-tier — cloud AI contributions, open-source.
- **HKUST Guangzhou** (MAS4TS): Strong in AI/ML, Yuxuan Liang is a prolific TS researcher.
- **CMU** (TimeSeriesGym): Top-tier in ML engineering and AI systems.
- **Nixtla / TimeCopilot**: Industry-leading open-source TS forecasting, NeurIPS workshop accepted.
