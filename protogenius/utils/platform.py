"""Platform helpers (Linux + Windows only per v1 acceptance contract)."""

from __future__ import annotations

import platform

SUPPORTED_PLATFORMS = {"linux", "windows"}


def current_platform() -> str:
    """Return ``linux`` / ``windows`` / ``darwin`` — lowercased."""
    return platform.system().lower()


def is_supported(name: str | None = None) -> bool:
    """Return True iff ``name`` (or the current platform) is an acceptance target."""
    return (name or current_platform()) in SUPPORTED_PLATFORMS
