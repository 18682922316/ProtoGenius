---
name: e2e-generation
description: Generate Playwright E2E specs for fullstack prototypes.
inputs: TestSpec
outputs: tests/e2e/*.spec.ts, tests/playwright.config.ts
code: protogenius.testing.e2e.PlaywrightE2EGenerator
---

# e2e-generation skill

Activated when at least one test case carries `kind: e2e`. Emits a
`playwright.config.ts` configured for headless mode and an
`@playwright/test` JUnit reporter so CI can ingest the report.
