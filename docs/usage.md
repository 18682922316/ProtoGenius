# Usage guide

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
