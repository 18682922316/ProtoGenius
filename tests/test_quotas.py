"""Quota ledger behaviour."""

from __future__ import annotations

import pytest

from protogenius.config import QuotaCaps
from protogenius.quotas import QuotaExceededError, QuotaLedger


def _caps(**kwargs) -> QuotaCaps:
    base = {
        "max_turns": 10,
        "max_search_results": 20,
        "max_tokens": 100,
        "max_walltime_seconds": 600,
    }
    base.update(kwargs)
    return QuotaCaps(**base)


def test_turn_charging_within_cap():
    ledger = QuotaLedger(caps=_caps(max_turns=3))
    ledger.charge_turn()
    ledger.charge_turn(2)
    assert ledger.turns == 3
    assert ledger.tripped is None


def test_turn_overflow_raises():
    ledger = QuotaLedger(caps=_caps(max_turns=2))
    ledger.charge_turn(2)
    with pytest.raises(QuotaExceededError) as excinfo:
        ledger.charge_turn()
    assert excinfo.value.dimension == "turns"
    assert ledger.tripped == "turns"


def test_search_overflow_raises():
    ledger = QuotaLedger(caps=_caps(max_search_results=5))
    ledger.charge_search(5)
    with pytest.raises(QuotaExceededError):
        ledger.charge_search(1)


def test_token_overflow_raises():
    ledger = QuotaLedger(caps=_caps(max_tokens=50))
    ledger.charge_tokens(prompt=20, completion=20)
    with pytest.raises(QuotaExceededError):
        ledger.charge_tokens(prompt=20)


def test_snapshot_and_remaining_consistent():
    ledger = QuotaLedger(caps=_caps())
    ledger.charge_turn()
    ledger.charge_search(7)
    ledger.charge_tokens(prompt=10, completion=15)
    snap = ledger.snapshot()
    rem = ledger.remaining()
    assert snap["turns"] == 1
    assert snap["search_results"] == 7
    assert snap["tokens"] == 25
    assert rem["turns"] == 9
    assert rem["search_results"] == 13
    assert rem["tokens"] == 75
