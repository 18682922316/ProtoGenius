---
description: Abort the active run with an explicit reason.
argument-hint: <abort reason>
---

Mark the active ProtoGenius run as aborted with reason: **$ARGUMENTS**.

Actions:

1. Set `ctx.aborted = True` and `ctx.abort_reason = "$ARGUMENTS"`.
2. Append an `abort` event to `audit.jsonl`.
3. Stop dispatching further stages.
