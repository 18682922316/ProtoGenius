# ProtoGenius architecture

## Layered view

```
+-----------------------------------------------------------+
| Cursor surface (.cursor/)                                 |
|   rules · commands · agents · skills · hooks · mcp.json   |
+-----------------------------------------------------------+
| Orchestrator (protogenius.orchestrator.Orchestrator)      |
|   walks state_machine.Stage, dispatches handlers,         |
|   honors hooks, enforces gates and quotas.                |
+-----------------------------------------------------------+
| Sub-agents                                                |
|   clarifier · stack-analyzer · researchers (academic /    |
|   github / industry) · synthesizer · srs / tdd drafters · |
|   demo-builder · tester · alignment-reporter              |
+-----------------------------------------------------------+
| Skills (Python modules)                                   |
|   research adapters · doc generators · demo scaffolds ·   |
|   test gen / E2E / CI · semantic alignment                |
+-----------------------------------------------------------+
| Cross-cutting                                             |
|   LLMClient · QuotaLedger · AuditLog · ProtoGeniusConfig  |
+-----------------------------------------------------------+
```

## Data flow

1. The CLI / Cursor surface invokes `Orchestrator.run(task)`.
2. The orchestrator builds a `RunContext` (workspace, audit log, quota
   ledger) and walks `StateMachine.transitions`.
3. Each stage handler reads from / writes to the `RunContext`. Outputs land
   on disk under `runs/<run-id>/`.
4. Blocking gates (`GATE_RESEARCH_ADOPTION`, `GATE_DOC_SIGNOFF`) call the
   user-supplied `OrchestratorOptions.on_gate` callback. The CLI uses an
   interactive `typer.confirm`; Cursor uses the `/confirm-research` and
   `/confirm-docs` slash commands.
5. Quotas are charged per stage entry and per search. The `QuotaLedger`
   raises `QuotaExceededError` on overflow; the orchestrator catches it and
   aborts with a single audit entry.
6. The final alignment report is rendered from `templates/test_report.md`
   and stored at `runs/<run-id>/reports/alignment.md`.

## Subsystem reference

| Subsystem        | Module(s)                                                     |
|------------------|----------------------------------------------------------------|
| Configuration    | `protogenius.config`, `config/*.yaml`                          |
| State machine    | `protogenius.state_machine`                                    |
| Orchestrator     | `protogenius.orchestrator`                                     |
| LLM abstraction  | `protogenius.llm`                                              |
| Quotas + audit   | `protogenius.quotas`, `protogenius.audit`                      |
| Hooks            | `protogenius.hooks.{registry,quota_guard,citation_audit,gate_check}` |
| Task envelope (v2) | `protogenius.task_input`                                     |
| Coverage notes (v2) | `protogenius.coverage`                                      |
| Research adapters| `protogenius.research.{arxiv_mcp,semantic_scholar,openalex,conference_proc,github_mcp,industry,scope}` |
| Knowledge base (v2) | `protogenius.kb.{local,github,indexer}`                     |
| Docs generators  | `protogenius.docs.{srs_generator,tdd_generator,interfaces,architecture,insight_generator,layer_docs}` |
| Demo scaffolds   | `protogenius.demo.{selector,scaffolds,runtime_check}`          |
| Testing          | `protogenius.testing.{spec_layer,generator,e2e,ci_generator,alignment}` |
| Templates        | `templates/*.md` (incl. `insight_*.md`, `layer_l{1,2,3,4}_*.md`) |

## Adding a new sub-agent

1. Create `.cursor/agents/<name>.md` declaring purpose / inputs / outputs.
2. Add a stage to `protogenius.state_machine.Stage` (only if it represents a
   new transition; otherwise hook into an existing stage).
3. Register the handler via `Orchestrator.register(stage, handler)`.
4. Document the change here.

## Adding a new skill

1. Implement the Python module under `protogenius/`.
2. Add a `.cursor/skills/<name>.md` pointer.
3. Wire it from the relevant sub-agent's `code` field.
