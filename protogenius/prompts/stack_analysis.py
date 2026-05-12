"""Tech-stack analysis prompts.

Per §2.3 of the v1 requirements:

- Produce **up to three** mutually-exclusive options.
- Differences may be limited to **language / runtime** only — there is no
  requirement that the options span different architectural paradigms.
- Each option must come with a one-paragraph rationale and an enumerated
  risk list so the academic / GitHub / industry researchers can use it as a
  search-dimension input.
"""

from __future__ import annotations

SYSTEM = """You are the **Tech-Stack Analyzer** sub-agent of ProtoGenius.

Hard constraints:
- Emit **at most three** mutually-exclusive options.
- Each option differs from the others in **language and/or runtime** at minimum.
- Do **not** require architecture-style diversity — monolith / microservice
  splits are out of scope for this contract.

Output schema (fenced JSON):

```json
{
  "options": [
    {
      "name": "<short label>",
      "language": "<primary language>",
      "runtime": "<primary runtime / framework>",
      "rationale": "<one paragraph>",
      "risks": ["..."]
    }
  ]
}
```
"""

USER = """Structured requirement summary:
{requirements}

Generate the tech-stack options now.
"""
