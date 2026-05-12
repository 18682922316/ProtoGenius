"""Quota tracking — enforces §7.1 hard caps for a single ProtoGenius run.

Every tool call that consumes a quota dimension must go through `QuotaLedger`:

    ledger.charge_turn()
    ledger.charge_search(n=results)
    ledger.charge_tokens(prompt=..., completion=...)

The ledger raises `QuotaExceededError` on the *first* overflow and stays in
that state so the orchestrator can collect a single, well-formed abort event.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .config import QuotaCaps


class QuotaExceededError(RuntimeError):
    """Raised when a hard cap would be (or has been) exceeded."""

    def __init__(self, dimension: str, current: int, cap: int) -> None:
        super().__init__(
            f"quota exceeded on '{dimension}': {current} > {cap} (hard cap)"
        )
        self.dimension = dimension
        self.current = current
        self.cap = cap


@dataclass
class QuotaLedger:
    """Accumulator for turn / search / token / walltime usage."""

    caps: QuotaCaps
    turns: int = 0
    search_results: int = 0
    tokens: int = 0
    started_at: float = field(default_factory=time.monotonic)
    _tripped: str | None = None

    # ---- charging APIs -------------------------------------------------

    def charge_turn(self, n: int = 1) -> None:
        self.turns += n
        self._check("turns", self.turns, self.caps.max_turns)

    def charge_search(self, n: int = 1) -> None:
        self.search_results += n
        self._check(
            "search_results", self.search_results, self.caps.max_search_results
        )

    def charge_tokens(self, *, prompt: int = 0, completion: int = 0) -> None:
        self.tokens += max(prompt, 0) + max(completion, 0)
        self._check("tokens", self.tokens, self.caps.max_tokens)

    def check_walltime(self) -> None:
        elapsed = int(time.monotonic() - self.started_at)
        self._check("walltime_seconds", elapsed, self.caps.max_walltime_seconds)

    # ---- introspection -------------------------------------------------

    def snapshot(self) -> dict[str, int]:
        elapsed = int(time.monotonic() - self.started_at)
        return {
            "turns": self.turns,
            "search_results": self.search_results,
            "tokens": self.tokens,
            "walltime_seconds": elapsed,
        }

    def remaining(self) -> dict[str, int]:
        elapsed = int(time.monotonic() - self.started_at)
        return {
            "turns": max(0, self.caps.max_turns - self.turns),
            "search_results": max(0, self.caps.max_search_results - self.search_results),
            "tokens": max(0, self.caps.max_tokens - self.tokens),
            "walltime_seconds": max(0, self.caps.max_walltime_seconds - elapsed),
        }

    @property
    def tripped(self) -> str | None:
        return self._tripped

    # ---- internal ------------------------------------------------------

    def _check(self, dimension: str, current: int, cap: int) -> None:
        if current > cap:
            self._tripped = dimension
            raise QuotaExceededError(dimension, current, cap)
