# Configuration reference

ProtoGenius reads configuration in three layers:

1. **Defaults** — `config/default.yaml`, `config/quotas.yaml`,
   `config/models.yaml`, `config/search.yaml`.
2. **Override file** — passed to `protogenius run --config <path>`.
3. **Environment variables** — names beginning with `PROTOGENIUS_`.

The merged result is validated against the Pydantic schema in
`protogenius.config.ProtoGeniusConfig`.

## Frozen-by-contract knobs

These values are validated at load time and **cannot** be changed without
breaking the v1 product contract:

| Setting                          | Value                       | Source        |
|----------------------------------|-----------------------------|---------------|
| `runtime.acceptance_platforms`   | excludes `macos`            | §5            |
| `clarification.max_rounds`       | 1..3                        | §2.2          |
| `stack_analysis.max_options`     | 1..3                        | §2.3          |
| `research.github.tie_policy`     | `cutoff_include_all` ∨ `strict_cap_3` | §2.4.3 |
| `algo_task.instances.count`      | exactly 3                   | §2.4.1        |
| Quota hard caps                  | 50 / 100 / 1M / 21600s      | §7.1          |

## Environment variables

The runtime distinguishes between **secret / endpoint** variables (read
directly at call time by the relevant adapter) and **scalar overrides**
(folded into the validated config via `_apply_env_overrides`). Secrets
never enter the validated `ProtoGeniusConfig` object so they cannot leak
into snapshots.

### Secret / endpoint variables

| Variable                                  | Required for | Behavior if missing |
|-------------------------------------------|--------------|---------------------|
| `PROTOGENIUS_LLM_API_KEY`                 | Mode B only  | `BaseHttpLLMClient.complete()` raises `RuntimeError`. Mode A is unaffected. |
| `PROTOGENIUS_LLM_BASE_URL`                | Optional     | Defaults to `https://api.openai.com/v1`. |
| `PROTOGENIUS_ARXIV_MCP_URL`               | Optional     | arXiv adapter raises at call time; Semantic Scholar + OpenAlex still cover academic search. |
| `PROTOGENIUS_GITHUB_TOKEN`                | Strongly recommended | GitHub MCP adapter falls back to anonymous calls; the Copilot endpoint will reject them. |
| `PROTOGENIUS_SEMANTIC_SCHOLAR_API_KEY`    | Optional     | Anonymous tier — lower rate limit. |
| `PROTOGENIUS_OPENALEX_EMAIL`              | Optional     | No polite-pool routing; stricter rate limits. |

### Section overrides (advanced)

Variables that share a top-level config key name are interpreted as
**JSON** and replace the entire section. Example:

```bash
export PROTOGENIUS_LLM='{"provider":"cursor","model":"native"}'
```

### Scalar quota shortcuts

| Variable                            | Maps to                          |
|-------------------------------------|----------------------------------|
| `PROTOGENIUS_MAX_TURNS`             | `quotas.max_turns`               |
| `PROTOGENIUS_MAX_SEARCH_RESULTS`    | `quotas.max_search_results`      |
| `PROTOGENIUS_MAX_TOKENS`            | `quotas.max_tokens`              |
| `PROTOGENIUS_MAX_WALLTIME_SECS`     | `quotas.max_walltime_seconds`    |

These shortcuts **can only lower** the per-task caps. Values that exceed
the frozen v1 upper bounds (50 / 100 / 1 000 000 / 21 600) are rejected
by `QuotaCaps._enforce_v1_upper_bounds`.

## Per-run overrides

The Python API supports per-run overrides via a Pydantic model dump:

```python
from protogenius.config import load_config, ProtoGeniusConfig

cfg = load_config()
overridden = cfg.model_copy(update={"runtime": cfg.runtime.model_copy(update={"random_seed": 42})})
```

## Secrets

`config/*.yaml` files are safe to commit. Secrets are read **only** from the
environment, never from disk. The CLI's `doctor` command verifies that the
expected env vars are set without printing their values.
