"""LLM client abstraction.

Sub-agents and skills should depend on the `LLMClient` Protocol, not on a
specific provider SDK. The orchestrator instantiates a real client based on
``ProtoGeniusConfig.llm``; tests may inject a `RecordingLLMClient`.

The default implementation is intentionally minimal — it formats a chat-style
request and uses ``httpx`` to call an OpenAI-compatible endpoint. Adding a new
provider is a matter of subclassing `BaseHttpLLMClient`.
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


def build_client(config: LLMConfig, *, dry_run: bool = False) -> LLMClient:
    """Factory helper used by the orchestrator and CLI."""
    if dry_run:
        return RecordingLLMClient(canned=["[dry-run completion]"])
    return BaseHttpLLMClient(config)
