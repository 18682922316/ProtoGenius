---
name: requirement-clarifier
description: Detect ambiguity in the task and ask at most 3 rounds of clarifying questions. Abort on failure.
stage: CLARIFY
tools:
  - none (LLM only)
---

# Requirement Clarifier

## Purpose
Resolve ambiguity in the user's task before any expensive research or
drafting work happens. Adheres to the v1 contract: **at most three rounds**
of questions; on the third unsuccessful round, **abort**.

## Inputs
- `ctx.task_description` (raw user prompt)
- `ctx.clarifications` (any prior rounds)

## Outputs
- Appends to `ctx.clarifications` with question / answer pairs.
- Sets `ctx.structured_requirements` once clarification resolves.
- May raise the abort path by setting `ctx.aborted = True`.

## Prompts
- System / user templates: `protogenius/prompts/clarify.py`.
