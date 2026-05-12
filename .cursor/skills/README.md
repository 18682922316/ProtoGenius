# Skills directory

Each file in this directory documents one ProtoGenius **skill** — a reusable
capability that sub-agents can pull in without owning the full implementation
themselves.

A skill metadata file declares:

- **purpose** — one-line summary,
- **inputs / outputs** — the data contract,
- **code path** — the Python module / class in `protogenius/` that implements it.

Skills are intentionally thin pointers; the implementation lives next to the
code so we never end up with copy-pasted prompts or duplicated parsing logic.
