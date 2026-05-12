"""Audit log behaviour: append-only JSONL with citation validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from protogenius.audit import AuditLog, Citation


def _read_lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_citation_with_url(tmp_path: Path):
    log = AuditLog(tmp_path / "audit.jsonl")
    log.log_citation(Citation(title="paper", source_type="arxiv", url="https://arxiv.org/abs/x"))
    entries = _read_lines(tmp_path / "audit.jsonl")
    assert entries[0]["kind"] == "citation"
    assert entries[0]["title"] == "paper"


def test_citation_missing_url_and_doi_raises(tmp_path: Path):
    log = AuditLog(tmp_path / "audit.jsonl")
    with pytest.raises(ValueError):
        log.log_citation(Citation(title="paper", source_type="arxiv"))


def test_decision_quota_gate_events(tmp_path: Path):
    log = AuditLog(tmp_path / "audit.jsonl")
    log.log_decision("adopt", {"choice": "option-a"})
    log.log_quota_event("tokens", 800_000, 1_000_000, "soft")
    log.log_gate("GATE_RESEARCH_ADOPTION", "approved", reviewer="alice")
    entries = _read_lines(tmp_path / "audit.jsonl")
    kinds = [entry["kind"] for entry in entries]
    assert kinds == ["decision", "quota_event", "gate"]
    assert entries[2]["reviewer"] == "alice"
