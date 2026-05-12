---
description: Kick off a new ProtoGenius run.
argument-hint: <natural-language task description>
---

Begin a new ProtoGenius pipeline pass for the task: **$ARGUMENTS**

Steps:

1. Load configuration via `protogenius.config.load_config()`.
2. Construct an `Orchestrator`, register all sub-agents from `.cursor/agents/`,
   and call `orchestrator.run("$ARGUMENTS")`.
3. Stop at each blocking gate; surface the snapshot and prompt the user to
   run `/confirm-research` or `/confirm-docs`.
