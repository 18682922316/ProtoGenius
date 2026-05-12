"""Allow ``python -m protogenius`` to dispatch to the Typer CLI."""

from __future__ import annotations

from .cli import app

if __name__ == "__main__":  # pragma: no cover
    app()
