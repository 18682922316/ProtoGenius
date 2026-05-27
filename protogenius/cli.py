"""ProtoGenius CLI.

Entry points:

- ``protogenius run "<task>"``        : execute one full pipeline pass.
- ``protogenius show-config``          : print the merged, validated config.
- ``protogenius show-quotas``          : print the configured quota caps.
- ``protogenius doctor``               : verify the environment (Python ver,
                                         platform, MCP URLs configured).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .config import load_config
from .orchestrator import Orchestrator, OrchestratorOptions
from .state_machine import Stage
from .utils.platform import current_platform, is_supported

app = typer.Typer(
    add_completion=False,
    help="ProtoGenius — Task In, Researched Prototype Out.",
)
console = Console()


def _on_gate(stage: Stage, snapshot: dict) -> bool:
    """Interactive gate handler — prompt at the terminal for yes/no."""
    console.rule(f"[bold]Blocking gate[/bold] — {stage.value}")
    console.print_json(json.dumps(snapshot, default=str, ensure_ascii=False))
    return typer.confirm("Confirm and continue?", default=True)


@app.command()
def run(
    task: str = typer.Argument(..., help="Natural-language task description."),
    workspace: Path = typer.Option(Path("runs"), "--workspace", help="Root for run artifacts."),
    config_path: Path | None = typer.Option(
        None, "--config", help="Optional config override file."
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Use the recording LLM client."),
    non_interactive: bool = typer.Option(
        False, "--yes", help="Auto-confirm every blocking gate (use with care)."
    ),
) -> None:
    """Execute one ProtoGenius pipeline pass."""
    config = load_config(override_path=config_path)
    options = OrchestratorOptions(
        dry_run=dry_run,
        interactive=not non_interactive,
        on_gate=(lambda *_: True) if non_interactive else _on_gate,
    )
    orchestrator = Orchestrator(config, options=options)
    ctx = orchestrator.run(task, workspace=workspace)
    if ctx.aborted:
        console.print(f"[red]Run aborted:[/red] {ctx.abort_reason}")
        raise typer.Exit(code=2)
    console.print(f"[green]Run complete.[/green] Artifacts: {ctx.run_dir}")


@app.command("show-config")
def show_config(config_path: Path | None = typer.Option(None, "--config")) -> None:
    config = load_config(override_path=config_path)
    console.print_json(json.dumps(config.model_dump(), default=str))


@app.command("show-quotas")
def show_quotas(config_path: Path | None = typer.Option(None, "--config")) -> None:
    config = load_config(override_path=config_path)
    table = Table(title="ProtoGenius quotas (hard caps)")
    table.add_column("Dimension")
    table.add_column("Cap", justify="right")
    for name, value in (
        ("turns", config.quotas.max_turns),
        ("search_results", config.quotas.max_search_results),
        ("tokens", config.quotas.max_tokens),
        ("walltime_seconds", config.quotas.max_walltime_seconds),
    ):
        table.add_row(name, f"{value:,}")
    console.print(table)


@app.command()
def doctor() -> None:
    """Quick environment check.

    Prints which operating mode is configured (Cursor vs standalone CLI),
    which required secrets are present, and which optional research
    credentials are available. Exits non-zero only if there is a HARD
    blocker for the configured mode.
    """
    import os

    ok = True
    console.print(f"ProtoGenius version: [bold]{__version__}[/bold]")
    console.print(f"Python: {sys.version.split()[0]}")
    plat = current_platform()
    if is_supported(plat):
        console.print(f"Platform: [green]{plat}[/green] (acceptance target)")
    else:
        console.print(
            f"Platform: [yellow]{plat}[/yellow] (not in v1 acceptance set; demos will be skipped)"
        )
        ok = False

    config = load_config()

    # ---- mode detection ------------------------------------------------
    provider = config.llm.provider.lower()
    if provider == "cursor":
        console.print(
            "[cyan]Mode A — Cursor Cloud Agent[/cyan] "
            "(Python LLM client is intentionally inert)."
        )
    else:
        console.print(
            f"[cyan]Mode B — Standalone CLI[/cyan] (provider={provider}, "
            f"model={config.llm.model})"
        )
        if not os.environ.get("PROTOGENIUS_LLM_API_KEY"):
            console.print(
                "  [red]MISSING[/red] PROTOGENIUS_LLM_API_KEY — required for "
                "Mode B. Set it or switch to `llm.provider: cursor`."
            )
            ok = False
        else:
            console.print("  [green]ok[/green] PROTOGENIUS_LLM_API_KEY is set")

    # ---- research credentials -----------------------------------------
    arxiv_ok = bool(
        os.environ.get(config.mcp.arxiv.url_env or "")
        or config.mcp.arxiv.command
    )
    console.print(
        f"  arXiv MCP: {'[green]configured[/green]' if arxiv_ok else '[yellow]unset[/yellow] (arXiv adapter will fail; Semantic Scholar / OpenAlex still work)'}"
    )
    gh_token = os.environ.get(config.mcp.github.token_env or "PROTOGENIUS_GITHUB_TOKEN", "")
    console.print(
        f"  GitHub MCP token: {'[green]set[/green]' if gh_token else '[yellow]unset[/yellow] (Copilot MCP will reject anonymous calls)'}"
    )
    s2_ok = bool(os.environ.get("PROTOGENIUS_SEMANTIC_SCHOLAR_API_KEY"))
    oa_ok = bool(os.environ.get("PROTOGENIUS_OPENALEX_EMAIL"))
    console.print(
        f"  Semantic Scholar API key: {'[green]set[/green]' if s2_ok else '[dim]unset (anonymous)[/dim]'}"
    )
    console.print(
        f"  OpenAlex mailto: {'[green]set[/green]' if oa_ok else '[dim]unset (no polite pool)[/dim]'}"
    )

    # ---- quotas --------------------------------------------------------
    console.print(
        f"Quotas (effective): turns={config.quotas.max_turns}, "
        f"search={config.quotas.max_search_results}, "
        f"tokens={config.quotas.max_tokens:,}, "
        f"walltime={config.quotas.max_walltime_seconds}s"
    )

    raise typer.Exit(code=0 if ok else 1)


if __name__ == "__main__":  # pragma: no cover
    app()
