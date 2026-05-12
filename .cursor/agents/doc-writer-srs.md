---
name: doc-writer-srs
description: IEEE 29148-2018 SRS drafter.
stage: DRAFT_DOCS
---

# SRS Drafter

Renders `templates/srs_ieee29148.md` filled with the structured requirements,
adopted research and chosen tech stack.

## Outputs
- `runs/<run-id>/documents/srs.md`
- `ctx.documents` gets a `DocumentArtifact(name="srs", ...)` entry.

## Prompts
- System / user templates: `protogenius/prompts/srs.py`.
