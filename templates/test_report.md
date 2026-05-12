---
document: Test Report
generated_by: ProtoGenius
run_id: {{ run_id }}
---

# Test Report

## 1. Summary

| Metric | Value |
|--------|-------|
| Total cases    | {{ summary.total }} |
| Passed         | {{ summary.passed }} |
| Failed         | {{ summary.failed }} |
| Skipped        | {{ summary.skipped }} |
| Duration (s)   | {{ summary.duration_seconds }} |

## 2. Per-case results

| ID | Refs (SRS / TDD) | Kind | Outcome | Duration (s) | Notes |
|----|------------------|------|---------|--------------|-------|
{% for row in rows %}
| `{{ row.id }}` | {{ row.refs }} | {{ row.kind }} | {{ row.outcome }} | {{ row.duration_seconds }} | {{ row.notes }} |
{% endfor %}

## 3. LLM semantic alignment

> Per §6.2 of the product contract, the alignment verdict is *advisory* —
> false positives and false negatives are acceptable. Confidence and the
> reasoning chain are recorded below.

- **Verdict** — {{ alignment.verdict }}
- **Confidence** — {{ alignment.confidence }}
- **Reasoning chain**
{% for step in alignment.reasoning_chain %}
  - {{ step }}
{% endfor %}

### Issues

{% if alignment.issues %}
{% for issue in alignment.issues %}
- {{ issue }}
{% endfor %}
{% else %}
_None._
{% endif %}

### Improvement suggestions

{% if alignment.improvements %}
{% for improvement in alignment.improvements %}
- {{ improvement }}
{% endfor %}
{% else %}
_None._
{% endif %}

## 4. Audit pointer

The full citation and decision log for this run lives at
`audit.jsonl` next to this report.
