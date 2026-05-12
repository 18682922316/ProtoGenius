---
name: ci-generation
description: Generate a GitHub Actions workflow for the prototype.
inputs: TestSpec
outputs: prototype-ci.yml
code: protogenius.testing.ci_generator.render_github_actions_workflow
---

# ci-generation skill

Emits an Actions workflow with an `ubuntu-latest` + `windows-latest` unit
matrix (mirrors v1 acceptance platforms). Adds an `e2e` job on
`ubuntu-latest` when the spec contains at least one E2E case.
