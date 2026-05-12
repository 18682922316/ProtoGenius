---
document: Research Summary (cross-comparison + common challenges)
generated_by: ProtoGenius
run_id: {{ run_id }}
gate: GATE_RESEARCH_ADOPTION (blocking)
---

# Research Summary

## 1. Comparison table

| Stream | Title | Source | Pros | Challenges |
|--------|-------|--------|------|------------|
{% for row in rows %}
| {{ row.stream }} | {{ row.title }} | [link]({{ row.url }}) | {{ row.pros }} | {{ row.challenges }} |
{% endfor %}

## 2. Common challenges

{% if common_challenges %}
{% for challenge in common_challenges %}
- {{ challenge }}
{% endfor %}
{% else %}
_No challenges shared across all streams._
{% endif %}

{% if algo_first_principles %}
## 3. Algorithm-task addendum

### First-principles framing

{{ algo_first_principles }}

### Algorithm logic (Mermaid)

```mermaid
{{ algo_diagram_mermaid }}
```

### Reproducible instances

{% for inst in algo_instances %}
**Instance {{ loop.index }}** — seed `{{ inst.seed }}`, inputs pinned at
`{{ inst.input_ref }}`.

{{ inst.description }}

{% endfor %}
{% endif %}

## 4. Adoption gate

This document drives the **research adoption** blocking gate. The user must
record adoption in the corresponding `gate` event before the SRS / TDD
generators run. See `audit.jsonl` for confirmation events.
