# Cross-Comparison Synthesis — Agentic AI × Time-Series Analytics

> **coverage_note**: Synthesizes academic (15 papers), GitHub (4+3 repos), and industry (17 findings from 7 companies). Focus areas: paradigm classification, common challenges, evaluation gaps, and adoption paths.

---

## 1. Paradigm Taxonomy

Based on cross-stream analysis, the "Agentic AI × Time-Series" space decomposes into **four paradigms**:

| Paradigm | Description | Academic | GitHub | Industry |
|----------|-------------|----------|--------|----------|
| **P1: Multi-Agent Decomposition** | Multiple specialized agents collaborate on TS tasks (planning, analysis, execution, critique) | Nexus, MAS4TS, SAGE, TSAD-Agents, TimeSeriesScientist, Argos | TimeSeriesScientist, CastClaw | — |
| **P2: Tool-Augmented LLM Reasoning** | Single LLM agent with access to statistical/ML tools for TS analysis | TimeART, TS-Agent, ChatAD | TimeCopilot | OpenAI o3/o4-mini, Codex |
| **P3: Foundation Model + Agent Interface** | Large pre-trained TS models wrapped with agentic interfaces (NL, MCP, ADK) | LangTime, Augur, TimeCopilot | TimesFM, Chronos, ChatTS | Google TimesFM Agent Skill, ByteDance Timer-S1 |
| **P4: MLLM-Native TS Reasoning** | Multimodal LLMs treating time series as a first-class modality | ANOMSEER, MAS4TS (VLM branch) | ChatTS | ByteDance ChatTS |

### Cross-Paradigm Observations

1. **P1 and P2 are converging**: Multi-agent systems increasingly give each agent tool access (CastClaw = P1+P2).
2. **P3 is the industry favorite**: Google's TimesFM + Agent Skill + BigQuery is the only production-complete stack.
3. **P4 is nascent but high-potential**: ChatTS shows 46-76% gains over GPT-4o when TS is treated as a native modality rather than text.

---

## 2. Common Challenges (Cross-Stream)

| Challenge | Academic | OSS | Industry |
|-----------|----------|-----|----------|
| **Evaluation heterogeneity** | TimeSeriesGym (NeurIPS 2025) attempts to standardize; but most papers use incomparable benchmarks | No unified eval harness across repos | Google uses GIFT-Eval; ByteDance uses same; no cross-company standard |
| **Context length vs. TS horizon** | LangTime uses PPO to mitigate error accumulation; Nexus decomposes macro/micro | TimesFM offers 16K context; Chronos up to 2K | Google BigQuery: 15K points dynamic window |
| **Hallucination in numeric reasoning** | TS-Agent adds self-refinement critic; ChatAD uses TKTO optimization | — | GPT-4o shows 46-76% worse numeric alignment than ChatTS on TS tasks |
| **Dedup across versions** | Multiple v1→v4 preprints for same work (ATSF had 4 versions) | Code duplication across forks | Same models appear under different product names |
| **Reproducibility** | Only TimeSeriesGym and TimeART provide standardized benchmarks | CastClaw + TimeCopilot have test suites | Only Google TimesFM has pinned model weights + reproducible eval |

---

## 3. Maturity Assessment

```
                 Research ─────────────── Production
                    │                         │
Academic Papers     ████████████░░░░░░░░░     (strong; 15 papers in 6 months)
OSS Repos           ████████░░░░░░░░░░░░░     (emerging; most <1yr old)
Industry Products   ██████████████████░░░     (Google leading; others catching up)
Evaluation/Bench    ██████░░░░░░░░░░░░░░░     (fragmented; TimeSeriesGym is a start)
Agent Protocols     ████████████░░░░░░░░░     (MCP gaining adoption; ADK is Google-specific)
```

---

## 4. Key Findings for Platform Adoption

### 4.1 Architecture Patterns Worth Adopting

1. **Tool-Augmented Agent (P2)** — Lowest barrier to entry. Use LLM as reasoner + existing statistical/ML tools. (TimeCopilot pattern)
2. **Foundation Model + MCP/ADK Interface (P3)** — Best production path. Wrap TimesFM/Chronos with MCP server. (Google pattern)
3. **Multi-Agent with Specialized Roles (P1)** — Best for complex workflows. Assign forecasting, anomaly detection, reporting to separate agents. (CastClaw pattern)

### 4.2 Infrastructure Requirements

| Component | Options | Maturity |
|-----------|---------|----------|
| TS Foundation Model | TimesFM 2.5, Chronos-2, Timer-S1, Time-MoE | Production-ready |
| Agent Framework | OpenAI Agents SDK, Qwen-Agent, LangGraph | Production-ready |
| Agent-to-Model Protocol | MCP (Anthropic), ADK (Google) | Emerging standard |
| Evaluation | TimeSeriesGym, GIFT-Eval | Research-grade |
| TS-Native LLM | ChatTS (14B) | Research-grade |

### 4.3 Gaps Identified

1. **No unified agent-TS benchmark** that tests both forecasting accuracy AND agent task success simultaneously.
2. **No production-grade multi-agent TS system** — all multi-agent implementations are research prototypes.
3. **No standard for TS observability in agent pipelines** — token cost, latency, forecast confidence intervals are ad-hoc.
4. **Safety/guardrails for agentic forecasting** — only Argos (Microsoft) addresses autonomous rule deployment risks.

---

## 5. Recommended Sources for Insight Reports

Based on cross-comparison, the following sources are recommended for individual insight reports:

### Academic (9 accepted)
1. Nexus (Google, May 2026) — Multi-agent forecasting architecture
2. ATSF Position Paper (USTC, Feb 2026) — Taxonomy & formulation
3. MAS4TS (HKUST-GZ, Feb 2026) — VLM-based multi-agent TS
4. TSAD-Agents (WWW 2026) — Multimodal anomaly detection agents
5. TimeART (Jan 2026) — Tool-augmented reasoning with 21 tools
6. TimeSeriesScientist (Oct 2025) — 4-agent general TS framework
7. TimeCopilot (NeurIPS 2025) — Agentic forecasting with TSFMs
8. TimeSeriesGym (NeurIPS 2025) — Agent evaluation benchmark
9. LangTime (ICML 2025) — Language-guided TS with RL

### OSS (3 accepted)
1. TimeCopilot — Production-closest agentic TS system
2. ChatTS — TS-native multimodal LLM
3. TimesFM — Foundation model with agent skill integration

### Enterprise (4 accepted)
1. Google TimesFM Agent Skill + BigQuery — Complete production stack
2. Anthropic MCP — Connectivity standard for agent-to-TS-data
3. ByteDance Timer-S1 + ChatTS — Largest TSFM + native reasoning
4. Alibaba Time-MoE + Qwen-Agent — MoE architecture + agent framework
