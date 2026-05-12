# MCP integration

ProtoGenius depends on two MCP (Model Context Protocol) servers in the
default configuration:

## 1. arXiv MCP

| Item     | Value |
|----------|-------|
| Purpose  | Recent paper search (3-month window). |
| URL env  | `PROTOGENIUS_ARXIV_MCP_URL` |
| Stdio cmd| `mcp.arxiv.command` in `config/default.yaml` |
| Tool     | `arxiv.search` |
| Code     | `protogenius.research.arxiv_mcp.ArxivMcpAdapter` |

Any arXiv-MCP implementation that exposes a `tools/call` endpoint with a
search-style tool will work. If the tool name differs, pass `tool_name=…`
when constructing the adapter.

## 2. GitHub Copilot hosted MCP

| Item     | Value |
|----------|-------|
| Purpose  | Repository search + release metadata. |
| URL      | `https://api.githubcopilot.com/mcp/` (frozen). |
| Auth     | `Authorization: Bearer ${env:PROTOGENIUS_GITHUB_TOKEN}` |
| Tools    | `github.search_repositories`, `github.releases` |
| Code     | `protogenius.research.github_mcp.GitHubMcpAdapter` |

Cursor users can pre-configure this MCP via `.cursor/mcp.json` (already
shipped in the repo); standalone CLI users must export
`PROTOGENIUS_GITHUB_TOKEN`.

## Adding a new MCP

1. Add a server entry to `config/default.yaml → mcp.*` (and to
   `.cursor/mcp.json` if you want Cursor to surface it).
2. Implement an adapter that conforms to
   `protogenius.research.base.SearchAdapter` (or another protocol if the use
   case is non-search).
3. Register the adapter at orchestrator construction time.

## Authentication etiquette

- Tokens **must** live in environment variables, not in YAML.
- Hosted MCPs may rate-limit; the orchestrator's tenacity-driven retries
  cover transient 429 / 503 errors with exponential backoff.
- The quota guard hook short-circuits before a network call when the
  projected results would exceed the search cap.
