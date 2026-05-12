---
description: Confirm the document sign-off gate.
argument-hint: <optional reviewer note>
---

Mark the **GATE_DOC_SIGNOFF** gate as approved.

Actions:

1. Append a `gate` event with `decision: approved` to `audit.jsonl`.
2. Continue the pipeline into `BUILD_DEMO`.

Reviewer note: $ARGUMENTS
