---
name: kb-connector
description: Optional domain knowledge-base connector (v2 §2.8). Reads local path or GitHub repo and indexes layer docs.
stage: INGEST_KB
tools:
  - filesystem (local_path)
  - git (github_repo)
---

# Knowledge Base Connector (v2 §2.8)

## Behaviour

1. If `task_input.knowledge_base` is missing / empty, log
   `info: kb skipped — not configured` and return without side effects.
2. If `local_path` is set, materialize via `protogenius.kb.LocalKb`.
3. If `github_repo` is set (format `owner/repo[@ref][:subdir]`), clone
   via `protogenius.kb.GitHubKb` (shallow, depth 1).
4. Walk the result with `discover_layer_docs` and store the
   :class:`KnowledgeBaseSnapshot` on `ctx.kb_snapshot`.

## kb_ref discipline

When a downstream sub-agent reuses a KB document, it MUST mark the layer
doc with the matching ``kb_ref`` via `LayerDoc.kb_refs.append(...)`. The
audit log records every reuse for traceability.

## Conflict marking

When a generated layer doc disagrees with a KB doc on the same subject,
the layer doc must surface the conflict in its ``conflicts`` field and
the audit log records a `decision: kb_conflict` event. The orchestrator
exposes the conflict via the doc sign-off gate so the user can resolve
it.
