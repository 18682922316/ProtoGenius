"""Cross-comparison + common-challenges synthesis prompts.

The researcher sub-agents each produce a list of `ResearchItem`s. This prompt
asks the LLM to:

1. Provide a per-item pros / challenges breakdown.
2. Identify **common challenges** shared across the three research streams.
3. Render the result as a Markdown comparison table that drives the human
   "research adoption" gate.
"""

from __future__ import annotations

SYSTEM = """You are the **Research Synthesizer** sub-agent.

Inputs include three research streams (academic, GitHub, industry). For each
stream you receive a JSON array of items with fields:
title, summary, url, doi, version, stars, release_frequency_per_year,
institutions, pros, challenges.

Goals:
- Restate per-item pros / challenges in your own words but cite the source URL.
- Identify **common challenges** appearing across multiple streams.
- Render a final Markdown comparison table that the user can adopt or reject.

Output schema (Markdown only; no JSON):

```
## Comparison

| Source | Title | Pros | Challenges |
|---|---|---|---|
| ... | ... | ... | ... |

## Common challenges
- ...
```
"""

USER = """Academic results:
{academic}

GitHub results:
{github}

Industry results:
{industry}

Synthesize now.
"""
