---
name: semantic-alignment
description: LLM-based semantic alignment between prototype and the frozen SRS/TDD.
inputs:
  - srs.md
  - tdd.md
  - test_summary
  - demo_summary
outputs: AlignmentReport
code: protogenius.testing.alignment.AlignmentRunner
---

# semantic-alignment skill

Per §6.2 the alignment verdict is **advisory** — false positives and false
negatives are acceptable. The skill records both a confidence score and a
step-by-step reasoning chain so the human reviewer can judge.
