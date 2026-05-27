"""LLM provider selection + Cursor-mode inert client behavior."""

from __future__ import annotations

import pytest

from protogenius.config import LLMConfig
from protogenius.llm import (
    BaseHttpLLMClient,
    CursorDelegatedLLMClient,
    RecordingLLMClient,
    build_client,
)


def test_dry_run_returns_recording_client():
    client = build_client(LLMConfig(), dry_run=True)
    assert isinstance(client, RecordingLLMClient)


def test_cursor_provider_returns_inert_client():
    client = build_client(LLMConfig(provider="cursor"))
    assert isinstance(client, CursorDelegatedLLMClient)


def test_openai_provider_returns_http_client():
    client = build_client(LLMConfig(provider="openai"))
    assert isinstance(client, BaseHttpLLMClient)


def test_cursor_client_raises_on_call_with_guidance():
    client = CursorDelegatedLLMClient()
    with pytest.raises(RuntimeError) as excinfo:
        client.complete("sys", "user")
    msg = str(excinfo.value)
    assert "cursor" in msg.lower()
    assert "PROTOGENIUS_LLM_API_KEY" in msg
