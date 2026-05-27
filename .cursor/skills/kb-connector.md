---
name: kb-connector
description: Read and index an optional domain knowledge base (local dir or GitHub repo).
inputs: KnowledgeBaseRef
outputs: KnowledgeBaseSnapshot
code:
  - protogenius.kb.local.LocalKb
  - protogenius.kb.github.GitHubKb
  - protogenius.kb.indexer.discover_layer_docs
  - protogenius.kb.indexer.resolve_kb_ref
  - protogenius.kb.indexer.detect_conflicts
---

# kb-connector skill (v2 §2.8)

Loads a knowledge base from one of:

- a local directory (`local_path`), or
- a GitHub repo locator of the form `owner/repo[@ref][:subdir]`
  (`github_repo`), cloned via `git --depth 1`.

The indexer walks layer subdirectories (`foundation_theory`,
`atomic_algorithm`, `tech_topic`, `ai_application`) and falls back to
parsing the `layer:` frontmatter key for flat layouts. Every reused KB
doc is referenced as `kb://<layer>/<path>@<revision>`.
