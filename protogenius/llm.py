"""LLM client abstraction.

Sub-agents and skills depend on the `LLMClient` Protocol — never on a
specific provider SDK. The orchestrator picks a concrete client based on
``ProtoGeniusConfig.llm.provider``:

- ``cursor``  — :class:`CursorDelegatedLLMClient`. Use this when running as a
  Cursor Cloud Agent: the *Cursor agent itself* is the LLM, so the Python
  ``LLMClient`` is intentionally inert and raises a guidance error if
  anything actually tries to call it from outside Cursor.
- ``openai`` / any OpenAI-compatible endpoint — :class:`BaseHttpLLMClient`.
  Requires ``PROTOGENIUS_LLM_API_KEY``.
- ``recording`` — :class:`RecordingLLMClient` test double; selected
  automatically when ``--dry-run`` is passed to the CLI.

Tests may inject a `RecordingLLMClient` directly.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import LLMConfig


@dataclass
class LLMResponse:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    raw: dict[str, Any] = field(default_factory=dict)


class LLMClient(Protocol):
    """Minimum surface area required by sub-agents."""

    def complete(self, system: str, user: str, **kwargs: Any) -> LLMResponse:  # pragma: no cover
        ...


# ----- Default OpenAI-compatible HTTP client -----------------------------


class BaseHttpLLMClient:
    """Thin wrapper around an OpenAI-compatible ``/chat/completions`` endpoint.

    Provider-specific quirks belong in subclasses. Authentication is read from
    environment variables identified by ``LLMConfig.api_key_env`` /
    ``LLMConfig.base_url_env`` so the user can rotate keys without editing
    config files.
    """

    def __init__(self, config: LLMConfig, *, http_client: httpx.Client | None = None) -> None:
        self.config = config
        self._http = http_client or httpx.Client(timeout=120)

    @property
    def api_key(self) -> str:
        return os.environ.get(self.config.api_key_env, "")

    @property
    def base_url(self) -> str:
        return os.environ.get(self.config.base_url_env, "https://api.openai.com/v1").rstrip("/")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=20))
    def complete(self, system: str, user: str, **kwargs: Any) -> LLMResponse:
        if not self.api_key:
            raise RuntimeError(
                f"LLM API key not configured; set ${self.config.api_key_env}"
            )
        payload: dict[str, Any] = {
            "model": kwargs.get("model", self.config.model),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]
        response = self._http.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        choice = data["choices"][0]
        usage = data.get("usage", {}) or {}
        return LLMResponse(
            text=choice["message"]["content"] or "",
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
            raw=data,
        )


# ----- Test / offline client ---------------------------------------------


@dataclass
class RecordedCall:
    system: str
    user: str
    kwargs: dict[str, Any]


@dataclass
class RecordingLLMClient:
    """Stateless test double that returns a canned response.

    Useful in unit tests and for offline orchestrator dry runs (the CLI ships
    with a ``--dry-run`` flag that wires this client in).
    """

    canned: Sequence[str] = ()
    calls: list[RecordedCall] = field(default_factory=list)

    def complete(self, system: str, user: str, **kwargs: Any) -> LLMResponse:
        self.calls.append(RecordedCall(system=system, user=user, kwargs=kwargs))
        idx = min(len(self.calls) - 1, max(0, len(self.canned) - 1))
        text = self.canned[idx] if self.canned else ""
        return LLMResponse(text=text, prompt_tokens=len(user), completion_tokens=len(text))


class CursorDelegatedLLMClient:
    """Inert client used when ProtoGenius runs *inside* Cursor.

    In Cursor Cloud Agent mode the Cursor runtime itself is the LLM; the
    Python orchestration layer is a library called by the Cursor agent
    rather than a standalone driver. Hence this client should never be
    invoked. If it is, that almost always means the standalone CLI was
    started but configured for Cursor mode — surface a clear, actionable
    error rather than silently sending an unauthenticated request.
    """

    def complete(self, system: str, user: str, **kwargs: Any) -> LLMResponse:  # noqa: ARG002
        raise RuntimeError(
            "LLM provider is set to 'cursor' but a Python LLM call was "
            "attempted. Either:\n"
            "  (a) run ProtoGenius inside Cursor Cloud Agent (the intended "
            "mode for 'cursor' provider), or\n"
            "  (b) switch the standalone CLI to an actual provider — set "
            "`llm.provider: openai` in your config override (or the "
            "matching JSON env override) and export PROTOGENIUS_LLM_API_KEY."
        )


def build_client(config: LLMConfig, *, dry_run: bool = False) -> LLMClient:
    """Factory helper used by the orchestrator and CLI."""
    if dry_run:
        return RecordingLLMClient(canned=["[dry-run completion]"])
    provider = (config.provider or "").lower()
    if provider == "cursor":
        return CursorDelegatedLLMClient()
    return BaseHttpLLMClient(config)
