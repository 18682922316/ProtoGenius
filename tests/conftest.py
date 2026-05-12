"""Shared pytest fixtures for the ProtoGenius test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

from protogenius.audit import AuditLog
from protogenius.config import load_config
from protogenius.context import RunContext
from protogenius.quotas import QuotaLedger


@pytest.fixture()
def config():
    return load_config()


@pytest.fixture()
def run_context(config, tmp_path: Path):
    ctx = RunContext(
        config=config,
        task_description="test task",
        workspace=tmp_path,
        run_id="testrun",
    )
    ctx.ensure_dirs()
    ctx.ledger = QuotaLedger(caps=config.quotas)
    ctx.audit = AuditLog(path=ctx.run_dir / config.audit.artifact_file)
    return ctx
