# Usage guide

## Two modes

ProtoGenius runs in one of two modes. **The choice determines which
secrets you need.** A single quick check (`protogenius doctor`) reports
which mode is active and what's missing.

| Mode | Who drives the LLM? | `PROTOGENIUS_LLM_API_KEY` required? | Best for |
|------|---------------------|-------------------------------------|----------|
| **A — Cursor Cloud Agent** (default delivery form) | The Cursor agent itself (uses your IDE's subscribed model). The Python package is consumed as a library by the Cursor agent through the subagent / skill / hook surface under `.cursor/`. | **No.** Set `llm.provider: cursor` in your override to install an inert client that errors if called from outside Cursor. | Day-to-day use through the Cursor IDE. |
| **B — Standalone Python CLI** (`protogenius run ...`) | The Python `LLMClient` calls an OpenAI-compatible endpoint. | **Yes.** | Headless servers, CI pipelines, scripted automation. |

The research adapters (arXiv MCP, GitHub MCP, Semantic Scholar,
OpenAlex, industry blog crawler) are mode-independent — they always read
their credentials directly from environment variables at call time, so the
same `PROTOGENIUS_GITHUB_TOKEN` / `PROTOGENIUS_ARXIV_MCP_URL` / … work in
both modes.

> **Mode A FAQ — "do I need to do anything to enable Cursor mode?"** No.
> The default config is already mode-A safe in the sense that the Python
> orchestrator is never spun up. If you also want the Python CLI to
> *refuse* to run accidentally without a key, set `llm.provider: cursor`
> in your override; then `protogenius run ...` raises a clear error
> instead of trying to hit an OpenAI endpoint with no key.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate            # PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Configure secrets

Copy `.env.example` to `.env` and fill in the keys you have. At minimum you
will want:

- `PROTOGENIUS_LLM_API_KEY`
- `PROTOGENIUS_GITHUB_TOKEN` (for the GitHub Copilot MCP)
- One of `PROTOGENIUS_ARXIV_MCP_URL` *or* a local arXiv MCP command in
  `config/default.yaml → mcp.arxiv.command`.

The other env vars are optional but recommended (Semantic Scholar API key,
OpenAlex contact email).

## Run a task

```bash
protogenius run "Build a Slack-style chat with E2E search over message history"
```

The CLI prints the run id and the artifacts directory:

```
Run complete. Artifacts: runs/20260512-121300-2bd3a1
```

Inside the run directory you will find:

```
runs/20260512-121300-2bd3a1/
├── documents/srs.md
├── documents/tdd.md
├── research/
├── prototype/
├── tests/
├── reports/alignment.md
└── audit.jsonl
```

## Driving from Cursor

Open the repository in Cursor Cloud. The agent will:

1. Load the rules in `.cursor/rules/` (always-applied).
2. Wait for you to run `/start-task <task>` from the chat input.
3. At each blocking gate, surface the snapshot and wait for
   `/confirm-research` or `/confirm-docs`.

## Dry-run mode

Use `protogenius run --dry-run "<task>"` to use the recording LLM client
(returns canned responses). Useful for shape-testing the pipeline without
spending tokens.

## Aborting

`Ctrl-C` aborts the active run. The audit log records an `abort` event with
the stage you were in at the time. You can resume from a checkpoint by
re-running with the same `--workspace` and a new task; ProtoGenius does not
attempt mid-run resume in v1.

## Troubleshooting

| Symptom                                | Probable cause                         |
|----------------------------------------|----------------------------------------|
| `RuntimeError: LLM API key not configured` | Missing `PROTOGENIUS_LLM_API_KEY`  |
| `MissingCitationError`                 | An adapter returned an item with no URL / DOI |
| `QuotaExceededError: turns`            | Pipeline took too many turns; review the LLM responses for unstructured outputs that prevented progress |
| `arXiv MCP URL is not configured`      | Set `PROTOGENIUS_ARXIV_MCP_URL` or `mcp.arxiv.command` |
