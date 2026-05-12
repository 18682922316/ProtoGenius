# AGENTS.md — top-level instructions for agents working in this repo

This file is consumed by Cursor / Claude / OpenAI Codex-style agents that
operate **on the ProtoGenius repository itself**, and is also the entry point
that the ProtoGenius runtime uses to orient sub-agents.

> If you are a user reading this file: this is *not* end-user documentation.
> See [`README.md`](README.md) and [`docs/`](docs/) instead.

---

## 1. Mission

ProtoGenius is an **end-to-end autonomous task validation agent**. The product
contract is frozen at requirements v1 (see the issue / PR body that created
the repo). Your job, as an agent operating on this repo, is to keep the system
faithful to that contract.

## 2. Non-negotiable rules (lifted from v1 requirements)

1. **Two blocking human gates** must remain in the pipeline:
   - *Research adoption* — between research output and SRS/TDD drafting.
   - *Document sign-off* — between SRS/TDD finalization and demo build.
   Removing or auto-bypassing these gates is a regression.
2. **Clarification is capped at 3 rounds.** On failure the system **aborts**;
   it must not silently invent default requirements.
3. **Tech-stack analysis emits ≤ 3 mutually-exclusive options.** Differences
   may be limited to language / runtime — do not require architecture-style
   diversity.
4. **Quotas are hard caps**: 50 turns, 100 search results, 1M tokens, < 6h
   wall time per task. The quota guard hook must be honored.
5. **Acceptance platforms are Windows + Linux.** macOS is explicitly out of v1
   scope for acceptance — do not add it as a required CI matrix entry.
6. **Algorithm tasks trigger** first-principles writeup + Mermaid algo
   diagram + **exactly 3 reproducible instances** (fixed seed, pinned data).
7. **GitHub ranking**: Stars then Release-frequency. Targets TOP-3, but
   *cut-off-include-all* on ties (final list may exceed 3). The config knob
   `github_tie_policy` is frozen at `cutoff_include_all` for v1.
8. **arXiv** uses an MCP. **Time windows**: arXiv past 3 months; top-tier
   venues within 1 year of the conference date. Same work across versions is
   deduplicated to one entry.
9. **Industry research is restricted** to Anthropic, OpenAI, DeepMind,
   ByteDance, Alibaba, Tencent, Meituan. Multiple sources for the same
   capability are listed separately, not collapsed.
10. **Tests derive from SRS + TDD only**, not from the user's raw
    natural-language input. Semantic alignment uses an LLM and must report
    confidence + reasoning chain.

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
