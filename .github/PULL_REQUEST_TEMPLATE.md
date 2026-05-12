# Pull request

## Summary

(brief description of the change)

## v1 contract checklist

- [ ] Both blocking gates remain (research adoption, doc sign-off).
- [ ] Clarification cap is still 3 rounds with abort-on-failure.
- [ ] Tech-stack analyzer still emits ≤ 3 mutually-exclusive options.
- [ ] Hard quotas unchanged (50 turns / 100 results / 1M tokens / 6h).
- [ ] Acceptance platforms still `linux, windows` (no macOS in v1).
- [ ] Citations carry URL or DOI; audit log entries unaffected.

## Validation

- [ ] `ruff check .` clean
- [ ] `pytest` green on Ubuntu and Windows (CI matrix).
- [ ] Any new sub-agent has a `.cursor/agents/*.md` declaration.
- [ ] Any new skill has a `.cursor/skills/*.md` pointer.

## Notes for reviewers

(call out anything that touches the state machine or the gating story)
