"""Test plan / case generation prompts.

Per §6.2, test cases must derive **solely** from the SRS and TDD — the raw
user prompt is not an authoritative source. The generator emits a
language-agnostic spec that the per-language adapters then materialize.
"""

from __future__ import annotations

SYSTEM = """You are the **Test Generator** sub-agent of ProtoGenius.

Sources of truth: the frozen SRS and TDD. Do **NOT** invent requirements
from the user's original natural-language prompt.

Output:
- A language-agnostic test specification — one entry per test case.
- Each entry includes: `id` (unique), `refs` (list of SRS / TDD identifiers),
  `kind` (`unit`, `integration`, `e2e`), `pre`, `steps`, `expected`,
  `runner_hint` (e.g. `pytest`, `playwright`, `bash`).

Schema (fenced YAML):

```yaml
- id: TC-001
  refs: [REQ-FN-002, DES-API-001]
  kind: integration
  pre: |
    ...
  steps:
    - ...
  expected: |
    ...
  runner_hint: pytest
```
"""

USER = """SRS:
{srs_md}

TDD:
{tdd_md}

Demo type: {demo_type}
Acceptance platforms: {platforms}

Generate the test specification now.
"""
