"""Static project-tree scaffolds for each demo flavor.

These are intentionally small "hello-world" trees — the LLM-driven demo
builder will rewrite source files later in the pipeline. The point of this
module is to guarantee a **runnable** baseline before any LLM call, so the
testing & CI stages always have something to operate on.
"""

from __future__ import annotations

from pathlib import Path

from .selector import DemoKind


def scaffold(kind: DemoKind, root: Path) -> None:
    """Write the minimal project tree for ``kind`` at ``root``."""
    root.mkdir(parents=True, exist_ok=True)
    {
        DemoKind.FULLSTACK: _scaffold_fullstack,
        DemoKind.SCRIPT: _scaffold_script,
        DemoKind.ALGO: _scaffold_algo,
    }[kind](root)


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _scaffold_fullstack(root: Path) -> None:
    _write(
        root / "README.md",
        "# Fullstack prototype\n\n"
        "Run the backend then the frontend:\n\n"
        "```bash\n"
        "cd backend && pip install -r requirements.txt && uvicorn app:app --reload\n"
        "cd frontend && npm install && npm run dev\n"
        "```\n",
    )
    _write(
        root / "backend" / "requirements.txt",
        "fastapi>=0.110\nuvicorn>=0.27\n",
    )
    _write(
        root / "backend" / "app.py",
        'from fastapi import FastAPI\n\n'
        "app = FastAPI()\n\n"
        '@app.get("/health")\n'
        "def health() -> dict[str, str]:\n"
        '    return {"status": "ok"}\n',
    )
    _write(
        root / "frontend" / "package.json",
        '{\n  "name": "protogenius-prototype",\n'
        '  "private": true,\n'
        '  "version": "0.0.1",\n'
        '  "scripts": { "dev": "echo \\"replace with vite / next / etc.\\"" }\n'
        "}\n",
    )


def _scaffold_script(root: Path) -> None:
    _write(
        root / "README.md",
        "# Script prototype\n\n"
        "```bash\npython main.py --help\n```\n",
    )
    _write(
        root / "main.py",
        '"""Generated CLI entry point — replace body with task logic."""\n\n'
        "from __future__ import annotations\n\n"
        "import argparse\n\n\n"
        "def main(argv: list[str] | None = None) -> int:\n"
        '    parser = argparse.ArgumentParser(description="ProtoGenius script prototype")\n'
        '    parser.add_argument("--echo", default="hello", help="value to print")\n'
        "    args = parser.parse_args(argv)\n"
        "    print(args.echo)\n"
        "    return 0\n\n\n"
        'if __name__ == "__main__":\n'
        '    raise SystemExit(main())\n',
    )


def _scaffold_algo(root: Path) -> None:
    _write(
        root / "README.md",
        "# Algorithm prototype\n\n"
        "Three reproducible instances live in `instances/`. Each instance pins\n"
        "its random seed and data so results are bit-for-bit reproducible.\n",
    )
    _write(
        root / "algo" / "__init__.py",
        "",
    )
    _write(
        root / "algo" / "core.py",
        '"""Replace with the actual algorithm under study."""\n\n'
        "from __future__ import annotations\n\n"
        "import random\n\n\n"
        "def solve(seed: int, n: int) -> list[int]:\n"
        '    """Deterministic placeholder — returns a permutation of range(n)."""\n'
        "    rng = random.Random(seed)\n"
        "    data = list(range(n))\n"
        "    rng.shuffle(data)\n"
        "    return data\n",
    )
    for i in (1, 2, 3):
        _write(
            root / "instances" / f"instance_{i}.py",
            f'"""Reproducible instance {i}. Fixed seed + pinned input."""\n\n'
            "from algo.core import solve\n\n"
            f"SEED = {i * 17}\n"
            f"N = {10 * i}\n\n"
            'if __name__ == "__main__":\n'
            "    result = solve(SEED, N)\n"
            "    print(result)\n",
        )
