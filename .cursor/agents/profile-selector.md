---
name: profile-selector
description: Pick the v2 run profile (full_pipeline vs research_and_docs_only) based on the task envelope.
stage: SELECT_PROFILE
tools:
  - none (deterministic policy)
---

# Profile Selector (v2 §2.6 / §2.7)

## Decision policy

1. If the user explicitly sets ``profile`` in the `TaskInput` envelope, honor it.
2. Otherwise:
   - With **no** `scoped_input` → `full_pipeline`.
   - With a `scoped_input` AND `generate_prototype_demo == False` → `research_and_docs_only`.
   - With a `scoped_input` AND `generate_prototype_demo == True` → `full_pipeline`
     (the user has explicitly opted into a Demo).

## Side effects

- Logs an audit `decision` event named `profile_selected` with the source
  of the decision (env / explicit / scoped-default).
- Sets `RunContext.task_input.profile` so all subsequent stages observe
  the chosen profile.
- When `research_and_docs_only` is selected, the orchestrator will later
  SKIP `BUILD_DEMO` / `GENERATE_TESTS_AND_CI` / `EXECUTE_TESTS` per §5.
