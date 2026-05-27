---
name: scope-router
description: When the task has a scoped_input, narrow search queries and the layer-doc generation set (v2 §2.7).
stage: ANALYZE_STACK   # runs as a query-narrowing helper between ANALYZE_STACK and RESEARCH_*
tools:
  - none (pure policy)
---

# Scope Router (v2 §2.7)

## Inputs

- `ctx.scoped_input` — type ∈ {topic, algorithm, theory, product}
- `ctx.config.scoped_input` — limits, default profile, quota scale factor

## Behaviour

- Prepends the scoped name (or description) to each search query so
  research adapters focus on the right subject.
- Multiplies each query's `max_results` by `quota_scale_factor` (default
  0.5) and floors at 1.
- Selects which layer docs to generate via
  `protogenius.research.select_layers(ctx.scoped_input)`.
- Per v2 §5 / §8, **no Demo** is produced unless the user explicitly
  opted in via `task_input.generate_prototype_demo == True` or a
  clarification confirms it.

## Code path

- `protogenius.research.scope.narrow_queries`
- `protogenius.research.scope.select_layers`
