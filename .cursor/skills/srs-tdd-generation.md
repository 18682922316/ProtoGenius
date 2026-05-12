---
name: srs-tdd-generation
description: IEEE 29148-aligned SRS and TDD generation.
inputs: RunContext
outputs:
  - runs/<id>/documents/srs.md
  - runs/<id>/documents/tdd.md
code:
  - protogenius.docs.srs_generator.SrsGenerator
  - protogenius.docs.tdd_generator.TddGenerator
  - protogenius.docs.architecture.render_architecture_diagram
  - protogenius.docs.interfaces.render_interfaces_section
templates:
  - templates/srs_ieee29148.md
  - templates/tdd_ieee29148.md
---

# srs-tdd-generation skill

Jinja templates own the section ordering; Python generators wire the
structured run-context data into them. LLM-driven prose fills in each
section via the prompts under `protogenius/prompts/`.
