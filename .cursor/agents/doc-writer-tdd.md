---
name: doc-writer-tdd
description: Technical Design Document drafter — companion to the SRS.
stage: DRAFT_DOCS
---

# TDD Drafter

Renders `templates/tdd_ieee29148.md`. Adds:

- Traceability matrix linking every `REQ-*` to design elements.
- Mermaid component view (via `protogenius.docs.architecture`).
- Interface definitions (via `protogenius.docs.interfaces`).
- Data structures (Pydantic-style or JSON Schema).
- Deployment topology that explicitly covers Linux and Windows.
- Risk register seeded from the research bundle's common-challenges list.

## Prompts
- System / user templates: `protogenius/prompts/tdd.py`.
