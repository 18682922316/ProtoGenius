# Compliance notes (§7.3 of the v1 requirements)

## Open-source licenses

- ProtoGenius respects upstream OSS licenses. Whenever the demo builder
  copies code from a research item it must call
  `AuditLog.log_license(artifact=..., spdx=..., source=...)` so the
  copied-from source and the SPDX identifier are recorded.
- The default config has `compliance.record_spdx_for_copied_code: true`. Do
  not disable this in production runs.

## Personal data

- `compliance.collect_pii_by_default = false`. Tasks that require PII
  collection must enable the relevant flag in the override config file and
  the operator is responsible for ensuring local-law compliance (GDPR /
  CCPA / PIPL etc.).
- The orchestrator never logs the raw LLM prompts at `info` level; only
  citation entries (with source identifiers) land in `audit.jsonl`.

## Internal company codebases

- Off by default. Enable explicitly:

  ```yaml
  compliance:
    internal_codebase_research:
      enabled: true
      repositories:
        - acme/private-monolith
        - acme/internal-tools
      credentials_env: ACME_GITHUB_TOKEN
  ```

- The orchestrator refuses to query private repositories unless `enabled`
  is true **and** `credentials_env` resolves to a non-empty value.

## Network egress

- v1 contract: network is open by default; no allow-list is required.
- If your environment requires an allow-list, restrict it at the runner /
  container level rather than inside ProtoGenius; the runtime does not
  attempt to model network policy.

## Audit retention

- The audit log is append-only. It is the **only** authoritative source for
  reconstructing run history.
- Operators are responsible for archiving `audit.jsonl` per their own
  retention policy; ProtoGenius does not rotate or truncate it.
