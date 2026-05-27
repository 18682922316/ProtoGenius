"""Local-filesystem KB source."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..context import KnowledgeBaseSnapshot
from ..task_input import KnowledgeBaseRef
from .indexer import discover_layer_docs


@dataclass
class LocalKb:
    """Read a knowledge base from a local directory."""

    ref: KnowledgeBaseRef

    def materialize(self) -> KnowledgeBaseSnapshot:
        if not self.ref.local_path:
            raise ValueError("LocalKb requires KnowledgeBaseRef.local_path")
        root = Path(self.ref.local_path).expanduser().resolve()
        if not root.is_dir():
            raise FileNotFoundError(
                f"local_path {root!s} is not a readable directory"
            )
        index = discover_layer_docs(root)
        versions = {
            str(path.relative_to(root)): f"mtime:{int(path.stat().st_mtime)}"
            for paths in index.values()
            for path in paths
        }
        return KnowledgeBaseSnapshot(
            ref=self.ref,
            root=root,
            layer_index=index,
            doc_versions=versions,
        )
