"""Configuration loading & frozen-knob validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from protogenius.config import ProtoGeniusConfig, load_config


def test_defaults_load_cleanly():
    cfg = load_config()
    assert isinstance(cfg, ProtoGeniusConfig)
    assert cfg.runtime.acceptance_platforms == ["linux", "windows"]
    assert cfg.clarification.max_rounds == 3
    assert cfg.stack_analysis.max_options == 3
    assert cfg.algo_task.instances.count == 3
    assert cfg.research.github.tie_policy == "cutoff_include_all"


def test_macos_rejected(monkeypatch):
    monkeypatch.setenv("PROTOGENIUS_RUNTIME", '{"acceptance_platforms": ["linux", "macos"]}')
    with pytest.raises(ValidationError):
        load_config()


def test_invalid_clarification_rounds_rejected(monkeypatch):
    monkeypatch.setenv("PROTOGENIUS_CLARIFICATION", '{"max_rounds": 5}')
    with pytest.raises(ValidationError):
        load_config()


def test_quota_caps_match_contract():
    cfg = load_config()
    assert cfg.quotas.max_turns == 50
    assert cfg.quotas.max_search_results == 100
    assert cfg.quotas.max_tokens == 1_000_000
    assert cfg.quotas.max_walltime_seconds == 21_600


def test_max_tokens_env_shortcut_lowers_cap(monkeypatch):
    monkeypatch.setenv("PROTOGENIUS_MAX_TOKENS", "250000")
    cfg = load_config()
    assert cfg.quotas.max_tokens == 250_000


def test_max_tokens_env_shortcut_cannot_raise_above_v1(monkeypatch):
    monkeypatch.setenv("PROTOGENIUS_MAX_TOKENS", "9999999")
    with pytest.raises(ValidationError):
        load_config()


def test_quota_env_shortcut_rejects_non_integer(monkeypatch):
    monkeypatch.setenv("PROTOGENIUS_MAX_TURNS", "not-a-number")
    with pytest.raises(ValueError, match="must be an integer"):
        load_config()
