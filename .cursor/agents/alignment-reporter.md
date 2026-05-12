---
name: alignment-reporter
description: LLM-based semantic alignment between prototype + tests and the frozen SRS/TDD.
stage: ALIGNMENT_REPORT
---

# Alignment Reporter

## Behaviour
Uses `protogenius.testing.alignment.AlignmentRunner.run` to compare:

- the frozen SRS / TDD,
- the executed test summary,
- the demo artifact summary.

Per §6.2, false positives and false negatives are acceptable. The output
**must** include `confidence` and `reasoning_chain` so the human reviewer
can judge the verdict.

## Outputs
- `runs/<run-id>/reports/alignment.md` (rendered from
  `templates/test_report.md`).
- `ctx.alignment` populated.

## Prompts
- System / user templates: `protogenius/prompts/alignment.py`.
