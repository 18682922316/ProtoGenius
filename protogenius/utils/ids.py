"""Identifier helpers (run IDs, slug normalization)."""

from __future__ import annotations

import os
import time
import uuid

from slugify import slugify as _slugify


def new_run_id(label: str | None = None) -> str:
    """Generate a sortable, slug-friendly run id of the form ``YYYYMMDD-HHMMSS-<short>``.

    A label, if supplied, is appended as a slug so directory listings remain
    human readable.
    """
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    short = uuid.uuid4().hex[:6]
    base = f"{stamp}-{short}"
    if label:
        base = f"{base}-{slugify(label)[:40]}"
    return base


def slugify(value: str) -> str:
    return _slugify(value, max_length=64, lowercase=True)


def env_or(name: str, default: str = "") -> str:
    return os.environ.get(name, default)
