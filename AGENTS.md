# AGENTS.md — top-level instructions for agents working in this repo

This file is consumed by Cursor / Claude / OpenAI Codex-style agents that
operate **on the ProtoGenius repository itself**, and is also the entry point
that the ProtoGenius runtime uses to orient sub-agents.

> If you are a user reading this file: this is *not* end-user documentation.
> See [`README.md`](README.md) and [`docs/`](docs/) instead.

---

## 1. Mission

ProtoGenius is an **end-to-end autonomous task validation agent**. The product
contract is frozen at requirements **v2** (with v1 retained read-only for
traceability). Your job, as an agent operating on this repo, is to keep the
system faithful to the v2 contract.

## 2. Non-negotiable rules (lifted from v2 requirements)

1. **Two blocking human gates** must remain in the pipeline:
   - *Research adoption* — between research output and SRS/TDD drafting.
   - *Document sign-off* — between SRS/TDD + **four-layer pack** finalization
     and demo build. By default this gate covers BOTH artifacts (v2 §3 —
     *merged sign-off*); the user can opt into two consecutive gates by
     setting `documents.merge_tdd_and_layer_signoff: false`.
   Removing or auto-bypassing these gates is a regression.
2. **Clarification is capped at 3 rounds.** On failure the system **aborts**;
   it must not silently invent default requirements. Clarification rounds
   prioritize filling `core_objectives` / `challenges` / `constraints` per
   v2 §2.1.1.
3. **Tech-stack analysis emits ≤ 3 mutually-exclusive options.** Differences
   may be limited to language / runtime — do not require architecture-style
   diversity.
4. **Quotas are hard caps**: 50 turns, 100 search results, 1M tokens, < 6h
   wall time per task. The quota guard hook must be honored. Scoped runs may
   *lower* the per-run caps via `scoped_input.quota_scale_factor` but **must
   never** raise them above §7.1.
5. **Acceptance platforms are Windows + Linux.** macOS is explicitly out of
   v2 scope for acceptance — do not add it as a required CI matrix entry.
6. **Algorithm tasks trigger** first-principles writeup + Mermaid algo
   diagram + **exactly 3 reproducible instances** (fixed seed, pinned data).
7. **GitHub ranking**: Stars then Release-frequency. Targets TOP-3, but
   *cut-off-include-all* on ties (final list may exceed 3). The config knob
   `github_tie_policy` is frozen at `cutoff_include_all` for v2.
8. **arXiv** uses an MCP. **Time windows**: arXiv past 3 months; top-tier
   venues within 1 year of the conference date. Same work across versions is
   deduplicated to one entry.
9. **Industry research is restricted** to Anthropic, OpenAI, DeepMind,
   ByteDance, Alibaba, Tencent, Meituan. Multiple sources for the same
   capability are listed separately, not collapsed.
10. **Tests derive from SRS + TDD only**, not from the user's raw
    natural-language input. Semantic alignment uses an LLM and must report
    confidence + reasoning chain.
11. **v2 §2.4.A/B/C — one structured insight report per accepted research
    source.** Reports MUST carry identification + core conclusions + auditable
    citation; the generator refuses to write artifacts that violate the
    v2 §2.5 minimum-content baseline.
12. **v2 §4.4 — four-layer tech doc pack (L1 → L2 → L3 → L4).** Every layer
    doc MUST include the `## 形式化定义` block populated with the
    layer-specific elements listed in §4.4.5. The generator refuses to write
    artifacts that lack the block (`FormalizationBlockMissingError`).
13. **v2 §2.6 / §2.7 — profile-aware demo gating.** When the effective
    profile is `research_and_docs_only` (default for scoped tasks),
    `BUILD_DEMO` / `GENERATE_TESTS_AND_CI` / `EXECUTE_TESTS` are SKIPPED.
    Producing a demo in that mode without explicit user opt-in is a
    regression.
14. **v2 §2.8 — knowledge base is opt-in.** When configured, the four-layer
    writer prefers existing KB docs via `kb_ref` and surfaces disagreements
    in `LayerDoc.conflicts`. Conflict events are recorded in the audit log.

## 3. Repository conventions

- **Python ≥ 3.11**, formatted via `ruff` (line length 100), typed where
  feasible (Pydantic v2 models for any cross-module data shape).
- **No vendoring of model SDKs.** The `protogenius.llm` module is the only
  place that talks to model providers; everything else takes a `LLMClient`
  protocol.
- **Search adapters** live under `protogenius/research/` and share the
  `SearchAdapter` Protocol in `protogenius/research/base.py`. New adapters
  must register themselves through `ResearchPipeline.register`.
- **Templates** (`templates/`) are Jinja2 sources rendered by
  `protogenius/docs/*`. Never inline IEEE 29148 section content inside Python
  source — keep it in `templates/`.
- **Audit & quotas**: any new tool call must go through `protogenius.quotas`
  (counting) and `protogenius.audit` (logging) — these are the spine of the
  compliance story.

## 4. Sub-agent registry (informational)

See `.cursor/agents/` for the canonical list. The orchestrator launches them
through `protogenius.orchestrator.Orchestrator.run` according to the state
machine in `protogenius/state_machine.py`. Adding a new sub-agent requires:

1. A markdown file in `.cursor/agents/<name>.md` declaring purpose / inputs /
   outputs / allowed tools.
2. A `Step` entry in `state_machine.py` (or a hook), with explicit predecessor
   and successor states.
3. Documentation in `docs/architecture.md`.

## 5. Hooks (informational)

- `pre_search` → `protogenius.hooks.quota_guard`
- `post_research` → `protogenius.hooks.citation_audit`
- `pre_stage_transition` → `protogenius.hooks.gate_check`

These are wired in `protogenius.hooks.registry`.

## 6. Testing

Run `pytest` from repo root. CI runs on Ubuntu and Windows; the E2E workflow
is optional and gated behind a label. Do not introduce tests that require the
real network or real MCP servers in the default suite — use the `httpx.MockTransport`
patterns already established under `tests/`.

## 7. When in doubt

- **Read the requirements document** (frozen v1).
- **Preserve the gates.** Skipping human confirmation breaks the product.
- **Prefer adding configuration over hardcoding policy.**
- **Record citations.** If you produce a research artifact you must log a
  citation entry through `protogenius.audit.log_citation`.
