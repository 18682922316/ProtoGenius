# Sample task

Use this file as the input to `protogenius run "$(cat examples/sample_task.md)"`.

---

Build a single-user knowledge-base prototype that ingests Markdown files from
a local directory, embeds them with a configurable embedding model, and lets
the user query the corpus via a small web UI. The system should support
hybrid search (BM25 + dense), highlight matched spans, and run on both
Linux and Windows without requiring a GPU.

Specific expectations:

- Configurable corpus location via CLI flag or environment variable.
- Indexing must be incremental — re-running on a partially-changed corpus
  should re-index only the changed files.
- A minimal web UI is acceptable; the search experience matters more than
  the visual design.
- The prototype is for personal use; multi-tenant features are out of scope.
