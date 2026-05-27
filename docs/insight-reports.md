# Insight reports (v2 §2.4.A / §2.4.B / §2.4.C)

ProtoGenius v2 produces **one structured insight report per accepted
research source**. Reports live under `runs/<id>/research/insights/` and
follow the relevant template:

| `source_type`        | `insight_type` | Template                             |
|----------------------|----------------|--------------------------------------|
| `arxiv`, `conference`| `academic`     | `templates/insight_academic.md`      |
| `github`             | `oss`          | `templates/insight_oss.md`           |
| `industry`           | `enterprise`   | `templates/insight_enterprise.md`    |

## Identifier scheme

`insight_id = INS-<TYPE3>-<title-slug>-<sha1(url|doi|title)[0:8]>`

The id is deterministic so re-running the same task produces the same
artifact name. The audit log cross-references insights by id.

## Recommended body fields (v2 §2.4.A/B/C)

The recommended-completeness set is enumerated in
`protogenius.docs.insight_generator._TEMPLATE_FIELDS`. Field names map
directly to template placeholders, so a sub-agent can fill in just the
fields it has evidence for.

Each absent field is recorded in the `coverage_note` block at the top
of the artifact, alongside a one-line reason from
`protogenius.coverage.REASON_*`:

- `REASON_TASK_TYPE` — field not applicable to this task type.
- `REASON_EVIDENCE_MISSING` — no auditable evidence found.
- `REASON_USER_CLARIFICATION` — explicitly ruled out during clarification.
- `REASON_SCOPED_RESEARCH` — outside the scoped-research target.
- `REASON_KB_PROVIDED` — preferred existing KB doc.

## Minimum-content baseline (v2 §2.5)

Every insight artifact MUST carry:

1. **Identification** — `insight_id`, `insight_type`, `title`, source link.
2. **Core conclusions** — populated `core_conclusions` field.
3. **Auditable citation** — at least one of URL / DOI.

The generator raises `InsightMinimumContentError` if these are missing,
unless `insights.enforce_minimum_content: false` is set in the config.

## Industry uncertainty (v2 §2.4.C)

`enterprise` insights inherit the uncertainty label from
`ResearchItem.extra.uncertainty` (default
`"Inferred from public web; may be incomplete or stale."`). The label is
rendered in the YAML frontmatter (`uncertainty:`) and as a banner at the
top of the artifact so reviewers cannot miss it.

## Citation block

Every report ends with an auditable citation block:

```
## § 引用与可审计来源

- URL: <https://...>
- DOI: `10.xxxx/yyyy`
- 版本: `v2`
- 访问日期: 2026-05-27T07:46:00Z
- 知识库引用: `kb://academic/foo.md@abc1234`
```

The `accessed_at` field is set by the generator at write time. The
`kb_ref` line appears only when the insight reuses a KB entry.
