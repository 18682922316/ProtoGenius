"""Hook behaviour: quota guard + citation audit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from protogenius.context import ResearchItem
from protogenius.hooks.citation_audit import MissingCitationError, citation_audit_hook
from protogenius.hooks.gate_check import GateCheckRefused, gate_check_hook
from protogenius.hooks.quota_guard import quota_guard_hook
from protogenius.quotas import QuotaExceededError
from protogenius.state_machine import Stage


def test_quota_guard_charges_search(run_context):
    quota_guard_hook(run_context, projected_results=10)
    assert run_context.ledger.search_results == 10


def test_quota_guard_rejects_overflow(run_context):
    # default cap is 100; 90 + 20 should overflow.
    quota_guard_hook(run_context, projected_results=90)
    with pytest.raises(QuotaExceededError):
        quota_guard_hook(run_context, projected_results=20)


def test_citation_audit_writes_jsonl(run_context, tmp_path: Path):
    items = [
        ResearchItem(title="paper", source_type="arxiv", url="https://example.com/x"),
        ResearchItem(title="repo", source_type="github", url="https://github.com/x/y"),
    ]
    citation_audit_hook(run_context, items)
    log_path = run_context.run_dir / run_context.config.audit.artifact_file
    entries = [json.loads(line) for line in log_path.read_text().splitlines()]
    titles = [e["title"] for e in entries if e["kind"] == "citation"]
    assert titles == ["paper", "repo"]


def test_citation_audit_rejects_missing_source(run_context):
    items = [ResearchItem(title="bad", source_type="industry")]
    with pytest.raises(MissingCitationError):
        citation_audit_hook(run_context, items)


def test_gate_check_logs_and_enforces_invariants(run_context):
    # logging-only transitions don't raise.
    gate_check_hook(run_context, Stage.INIT, Stage.UNDERSTAND_REQUIREMENT)
    # entering DRAFT_DOCS with empty research raises.
    with pytest.raises(GateCheckRefused):
        gate_check_hook(run_context, Stage.GATE_RESEARCH_ADOPTION, Stage.DRAFT_DOCS)
