"""Append-only audit log for citations, decisions and quota events.

The log lives at ``<workspace>/<run_id>/audit.jsonl`` and records:

- every citation produced by a research adapter (URL / DOI / version),
- every blocking-gate confirmation event,
- every quota soft / hard threshold crossing,
- every license record for copied code.

The format is JSON lines — one event per line — chosen so that downstream
tooling (e.g. CI reviewers, internal compliance) can read and replay the
audit trail without parsing a custom binary format.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

EventKind = Literal[
    "citation",
    "decision",
    "quota_event",
    "license_record",
    "gate",
    "abort",
    "info",
]


@dataclass(frozen=True)
class Citation:
    """A single citation. At least one of url / doi must be supplied."""

    title: str
    source_type: str            # arxiv | conference | github | industry | other
    url: str = ""
    doi: str = ""
    version: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def is_complete(self) -> bool:
        return bool(self.url) or bool(self.doi)


class AuditLog:
    """Thread-safe append-only JSONL audit log."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    # ---- public APIs ---------------------------------------------------

    def log_citation(self, citation: Citation, *, fail_on_missing: bool = True) -> None:
        if fail_on_missing and not citation.is_complete():
            raise ValueError(
                f"citation {citation.title!r} has neither URL nor DOI; cannot record"
            )
        self._emit("citation", asdict(citation))

    def log_decision(self, name: str, detail: dict[str, Any]) -> None:
        self._emit("decision", {"name": name, **detail})

    def log_quota_event(self, dimension: str, current: int, cap: int, level: str) -> None:
        self._emit(
            "quota_event",
            {"dimension": dimension, "current": current, "cap": cap, "level": level},
        )

    def log_license(self, *, artifact: str, spdx: str, source: str) -> None:
        self._emit("license_record", {"artifact": artifact, "spdx": spdx, "source": source})

    def log_gate(self, gate: str, decision: str, reviewer: str = "") -> None:
        self._emit("gate", {"gate": gate, "decision": decision, "reviewer": reviewer})

    def log_abort(self, reason: str, stage: str) -> None:
        self._emit("abort", {"reason": reason, "stage": stage})

    def log_info(self, message: str, **extra: Any) -> None:
        self._emit("info", {"message": message, **extra})

    # ---- internal ------------------------------------------------------

    def _emit(self, kind: EventKind, payload: dict[str, Any]) -> None:
        record = {"ts": time.time(), "kind": kind, **payload}
        line = json.dumps(record, ensure_ascii=False)
        with self._lock, self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
