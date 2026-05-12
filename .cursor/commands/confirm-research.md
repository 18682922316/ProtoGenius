---
description: Confirm the research adoption gate.
argument-hint: <optional reviewer note>
---

Mark the **GATE_RESEARCH_ADOPTION** gate as approved.

Actions:

1. Append a `gate` event with `decision: approved` to `audit.jsonl`.
2. Continue the pipeline into the `DRAFT_DOCS` stage.

Reviewer note: $ARGUMENTS
