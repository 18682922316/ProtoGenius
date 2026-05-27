"""GitHub-backed KB source.

A locator of the form ``owner/repo@ref:subdir`` is materialized into a
local working tree via ``git clone --depth 1 --branch <ref>``. After
cloning, the indexer walks ``<subdir>`` (defaulting to the repo root) and
returns a :class:`KnowledgeBaseSnapshot`.

This module intentionally **does not require** a GitHub MCP — it uses
plain ``git`` so the same path works offline against a cached clone and
in CI against a real repo. Authentication, when needed, is delegated to
the user's git credential helper.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from ..context import KnowledgeBaseSnapshot
from ..task_input import KnowledgeBaseRef
from .indexer import discover_layer_docs

_LOCATOR_RE = re.compile(
    r"^(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)(?:@(?P<ref>[\w./-]+))?(?::(?P<subdir>[^\s]+))?$"
)


@dataclass(frozen=True)
class ParsedLocator:
    owner: str
    repo: str
    ref: str = ""
    subdir: str = ""

    @property
    def clone_url(self) -> str:
        return f"https://github.com/{self.owner}/{self.repo}.git"


def parse_locator(locator: str) -> ParsedLocator:
    match = _LOCATOR_RE.match(locator.strip())
    if not match:
        raise ValueError(
            f"github_repo locator {locator!r} does not match owner/repo[@ref][:subdir]"
        )
    return ParsedLocator(
        owner=match.group("owner"),
        repo=match.group("repo"),
        ref=match.group("ref") or "",
        subdir=match.group("subdir") or "",
    )


@dataclass
class GitHubKb:
    """Materialize a KB from a GitHub repo via ``git clone --depth 1``."""

    ref: KnowledgeBaseRef
    cache_dir: Path | None = None
    git_executable: str = "git"

    def materialize(self) -> KnowledgeBaseSnapshot:
        if not self.ref.github_repo:
            raise ValueError("GitHubKb requires KnowledgeBaseRef.github_repo")
        parsed = parse_locator(self.ref.github_repo)
        clone_root = self._ensure_clone(parsed)
        scan_root = clone_root / parsed.subdir if parsed.subdir else clone_root
        if not scan_root.is_dir():
            raise FileNotFoundError(
                f"subdir {parsed.subdir!r} not found inside {clone_root!s}"
            )

        commit = self._head_commit(clone_root)
        index = discover_layer_docs(scan_root)
        versions = {
            str(path.relative_to(scan_root)): commit
            for paths in index.values()
            for path in paths
        }
        return KnowledgeBaseSnapshot(
            ref=self.ref,
            root=scan_root,
            layer_index=index,
            doc_versions=versions,
        )

    # ---- internals -----------------------------------------------------

    def _ensure_clone(self, parsed: ParsedLocator) -> Path:
        if not shutil.which(self.git_executable):
            raise RuntimeError(
                f"git executable {self.git_executable!r} not found on PATH; "
                "GitHub-backed KB requires git"
            )
        cache = self.cache_dir or Path(tempfile.gettempdir()) / "protogenius-kb"
        cache.mkdir(parents=True, exist_ok=True)
        target = cache / f"{parsed.owner}-{parsed.repo}-{parsed.ref or 'default'}"
        if target.is_dir() and (target / ".git").is_dir():
            return target
        if target.exists():
            shutil.rmtree(target)
        cmd = [
            self.git_executable, "clone", "--depth", "1",
        ]
        if parsed.ref:
            cmd.extend(["--branch", parsed.ref])
        cmd.extend([parsed.clone_url, str(target)])
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
        if result.returncode != 0:
            raise RuntimeError(
                f"git clone failed: {result.stderr.strip() or result.stdout.strip()}"
            )
        return target

    def _head_commit(self, repo_path: Path) -> str:
        try:
            result = subprocess.run(
                [self.git_executable, "rev-parse", "HEAD"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout.strip()[:12] or "unknown"
        except OSError:
            return "unknown"
