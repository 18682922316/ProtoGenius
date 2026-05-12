---
name: tech-stack-analyzer
description: Emit ≤ 3 mutually-exclusive tech-stack options (language / runtime only).
stage: ANALYZE_STACK
tools:
  - none (LLM only)
---

# Tech-Stack Analyzer

## Purpose
Produce up to **three** mutually-exclusive options for implementing the
prototype. Differences may be limited to language / runtime; architectural
diversity is not required.

## Inputs
- `ctx.structured_requirements`

## Outputs
- Populates `ctx.stack_options` (list of `TechStackOption`).
- Picks `ctx.chosen_stack` (often after a brief user confirmation later
  during gating; not blocking).

## Prompts
- System / user templates: `protogenius/prompts/stack_analysis.py`.
