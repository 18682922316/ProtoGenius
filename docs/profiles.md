# Run profiles (v2 §2.6 / §2.7)

ProtoGenius v2 introduces two named run profiles:

| Profile                  | When picked (default)                                    | Demo? |
|--------------------------|----------------------------------------------------------|-------|
| `full_pipeline`          | No `scoped_input`                                        | yes   |
| `research_and_docs_only` | `scoped_input` present AND `generate_prototype_demo: false` | **no** |

The profile is decided in the `SELECT_PROFILE` stage immediately after
`CLARIFY` and recorded as an audit-log `decision` event.

## Choosing a profile

| Scenario                                                                                       | Profile                  |
|------------------------------------------------------------------------------------------------|--------------------------|
| "Build a chat tool with hybrid search" (no scoped input)                                       | `full_pipeline`          |
| "Survey beam-search variants" + `scoped_input.type: algorithm`                                 | `research_and_docs_only` |
| "Survey beam-search variants AND give me a prototype" + `generate_prototype_demo: true`        | `full_pipeline`          |
| "Document our information-theory layer" + `scoped_input.type: theory`                           | `research_and_docs_only` |

## What changes under `research_and_docs_only`

- `BUILD_DEMO`, `GENERATE_TESTS_AND_CI`, and `EXECUTE_TESTS` are SKIPPED
  by the orchestrator. Each skip is recorded in `audit.jsonl` as
  `info: stage skipped — research_and_docs_only profile`.
- `ALIGNMENT_REPORT` still runs against the SRS/TDD so the audit trail
  carries a coverage verdict.
- Search quotas are scaled by
  `scoped_input.quota_scale_factor` (default 0.5) — caps are tightened,
  never relaxed.
- The DoD checklist (§8) accepts a missing Demo as long as the run
  artifact carries the profile name.

## Scoped types vs. layer focus

| `scoped_input.type` | Default layer docs                                          |
|---------------------|--------------------------------------------------------------|
| `topic`             | `foundation_theory + atomic_algorithm + tech_topic`          |
| `algorithm`         | `foundation_theory + atomic_algorithm`                       |
| `theory`            | `foundation_theory`                                          |
| `product`           | all four layers                                              |

Implementation: `protogenius.research.scope.select_layers` /
`protogenius.research.scope.narrow_queries`.

## Task envelope (Appendix A of the v2 spec)

```yaml
task:
  description: "自然语言任务描述"
  profile: full_pipeline                  # full_pipeline | research_and_docs_only
  generate_prototype_demo: false          # see §2.7 — default off when scoped
  scoped_input:
    type: topic                           # topic | algorithm | theory | product
    name: "retrieval-augmented generation"
  knowledge_base:
    github_repo: acme/kb@main:layers
  structured_requirements_summary:
    core_objectives: ["..."]
    challenges: ["..."]
    constraints: ["..."]
```

Load it via `protogenius.task_input.TaskInput.from_yaml(path)` or pass a
`TaskInput` instance to `Orchestrator.run`. The orchestrator records the
resolved profile, demo flag, scope and KB presence in the run-started
audit event.
