# Knowledge base (v2 §2.8)

ProtoGenius optionally consumes a **domain knowledge base** of
historically-curated Markdown layer docs. When a KB is configured, the
four-layer doc writer prefers existing entries over re-deriving content
and surfaces any conflicts at the doc-signoff gate.

## Layout

The recommended layout is one directory per layer:

```
kb_root/
├── foundation_theory/
│   ├── information_theory.md
│   └── ...
├── atomic_algorithm/
│   └── ...
├── tech_topic/
│   └── ...
└── ai_application/
    └── ...
```

A flat layout is also supported — `protogenius.kb.indexer.discover_layer_docs`
falls back to parsing each file's YAML frontmatter `layer:` key.

## Sources

Two sources are accepted; only one needs to be configured.

### `local_path`

A directory on the local filesystem. Materialized via
`protogenius.kb.local.LocalKb` without external dependencies.

```yaml
knowledge_base:
  local_path: /var/protogenius/kb
```

### `github_repo`

A locator of the form `owner/repo[@ref][:subdir]`. Materialized via
`protogenius.kb.github.GitHubKb` with a shallow `git clone --depth 1`.
Authentication is delegated to the user's git credential helper.

```yaml
knowledge_base:
  github_repo: acme/kb@main:layers
```

## `kb_ref` discipline

Every reused KB entry is referenced as:

```
kb://<layer>/<relative-path>@<revision>
```

- `<layer>` ∈ `{foundation_theory, atomic_algorithm, tech_topic, ai_application}`.
- `<revision>` is the commit short hash for GitHub-backed KBs and the
  file mtime for local-backed KBs.

The four-layer generator stores `kb_ref` values on
`LayerDoc.kb_refs` and renders them in a dedicated section at the end of
each layer doc.

## Conflict handling

When a freshly generated layer doc disagrees with a KB entry on the same
subject, the generator:

1. Records the disagreement on `LayerDoc.conflicts`.
2. Renders a `⚠ 与知识库冲突` block at the bottom of the doc.
3. Logs an audit `decision: kb_conflict` event.

The doc-signoff gate surfaces conflicts to the user. The user's
confirmation outcome wins per v2 §2.8.

## Failure modes

| Failure                                | Behavior                                  |
|----------------------------------------|-------------------------------------------|
| `local_path` does not exist            | `FileNotFoundError` aborts the run.       |
| `github_repo` clone fails              | `RuntimeError` aborts the run.            |
| Locator malformed                      | `ValidationError` rejects the task input. |
| Both `local_path` and `github_repo` set| `local_path` wins; override recorded.     |

## Disable / opt out

The KB is opt-in. Leave `task.knowledge_base` unset or null and the
`INGEST_KB` stage becomes a no-op, recording `info: kb skipped — not configured`.
