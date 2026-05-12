"""Cheap runtime check: does the scaffold actually launch?

The orchestrator runs this in a sandbox immediately after scaffolding to give
the user an early failure signal. The check is **intentionally shallow**:

- Python scripts → ``python -c "import ast; ast.parse(open(p).read())"`` on
  every ``.py`` file.
- Node packages → ``node --check`` on the entry point if Node is available.

Anything deeper (HTTP probe of the FastAPI app, headless browser of the React
frontend) lives in the testing module, not here.
"""

from __future__ import annotations

import ast
import shutil
import subprocess
from pathlib import Path


def shallow_check(root: Path) -> list[str]:
    """Return a list of diagnostic strings; empty list means clean check."""
    diagnostics: list[str] = []
    for py_file in root.rglob("*.py"):
        try:
            ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            diagnostics.append(f"syntax error in {py_file.relative_to(root)}: {exc}")
    if shutil.which("node"):
        for js_file in root.rglob("*.js"):
            result = subprocess.run(
                ["node", "--check", str(js_file)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                diagnostics.append(
                    f"node --check failed for {js_file.relative_to(root)}: {result.stderr.strip()}"
                )
    return diagnostics
