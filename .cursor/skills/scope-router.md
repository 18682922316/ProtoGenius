---
name: scope-router
description: Narrow research queries and pick the layer-doc set for a scoped task (topic / algorithm / theory / product).
inputs:
  - List[SearchQuery]
  - ScopedInput
outputs:
  - List[SearchQuery] (narrowed)
  - List[str] (layer ids to generate)
code:
  - protogenius.research.scope.narrow_queries
  - protogenius.research.scope.select_layers
---

# scope-router skill (v2 §2.7)

Two pure functions:

- `narrow_queries(...)` prepends the scope keyword to each query and
  scales `max_results` by `scoped_input.quota_scale_factor` (frozen
  default 0.5).
- `select_layers(scoped)` returns the ordered layer ids the doc-pack
  generator should produce; an unscoped run returns all four layers.
