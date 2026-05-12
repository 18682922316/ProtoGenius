---
name: algo-first-principles
description: Conditional sub-agent for algorithm / model / optimization tasks. Produces first-principles writeup, Mermaid algorithm diagram, and exactly 3 reproducible instances.
stage: FIRST_PRINCIPLES
tools:
  - LLM only
---

# Algorithm First-Principles Writer

## Trigger
Activates only when the task description contains keywords from
`config.algo_task.trigger_keywords` (default: algorithm / model /
optimization / 算法 / 模型 / 优化).

## Outputs (mandatory if triggered)
1. **First-principles framing** — assumptions, objective, equivalent
   formulations.
2. **Mermaid algorithm diagram** — emitted via
   `protogenius.utils.mermaid.flowchart`.
3. **Exactly three reproducible instances** — each pins a random seed,
   dataset version and dependency set. See
   `config.algo_task.instances.reproducibility_checklist`.

## Code path
- Stores all three outputs on `ctx.research`:
  - `algo_first_principles`
  - `algo_diagram_mermaid`
  - `algo_instances`
