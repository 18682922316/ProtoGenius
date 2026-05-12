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

| Variable                                  | Purpose                                |
|-------------------------------------------|----------------------------------------|
| `PROTOGENIUS_LLM_API_KEY`                 | LLM provider key                       |
| `PROTOGENIUS_LLM_BASE_URL`                | LLM provider base URL                  |
| `PROTOGENIUS_ARXIV_MCP_URL`               | arXiv MCP endpoint                     |
| `PROTOGENIUS_GITHUB_TOKEN`                | GitHub PAT for the Copilot MCP         |
| `PROTOGENIUS_SEMANTIC_SCHOLAR_API_KEY`    | Polite-pool routing                    |
| `PROTOGENIUS_OPENALEX_EMAIL`              | OpenAlex `mailto`                      |

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
