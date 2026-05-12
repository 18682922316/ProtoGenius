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
