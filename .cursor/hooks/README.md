# Hooks directory

Each Markdown file documents one hook point exposed by the ProtoGenius
runtime. Hooks are wired in `protogenius.hooks.registry.default_registry`
and intercept specific events in the orchestration pipeline.

| Hook                          | Trigger                              |
|-------------------------------|--------------------------------------|
| `pre-search-quota-guard`      | Before any research adapter searches |
| `post-research-citation-audit`| After a research adapter returns     |
| `pre-stage-gate-check`        | Before any stage transition          |
