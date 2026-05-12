---
name: post-research-citation-audit
event: post_research
code: protogenius.hooks.citation_audit.citation_audit_hook
---

# post-research citation audit

Walks every `ResearchItem` returned by an adapter and logs a citation entry
to `audit.jsonl`. Items missing both URL and DOI cause a hard failure
(`audit.fail_on_missing_citation: true`).
