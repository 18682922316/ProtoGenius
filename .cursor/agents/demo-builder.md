---
name: demo-builder
description: Generate a runnable prototype matching the SRS + TDD.
stage: BUILD_DEMO
---

# Demo Builder

## Selection
Calls `protogenius.demo.choose_demo_kind` to pick between FULLSTACK / SCRIPT /
ALGO. Default preference is FULLSTACK; the orchestrator can override.

## Scaffolding
1. Calls `protogenius.demo.scaffolds.scaffold(kind, root)` to lay down a
   runnable baseline.
2. Refines source files based on the TDD.
3. Runs the shallow runtime check (`runtime_check.shallow_check`) before
   handing off to the testing stage.

## Outputs
- `runs/<run-id>/prototype/...`
- `ctx.demo_root` is set.
