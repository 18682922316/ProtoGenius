"""Small utility helpers shared by orchestration, research and doc layers."""

from .ids import new_run_id, slugify
from .platform import current_platform, is_supported

__all__ = ["new_run_id", "slugify", "current_platform", "is_supported"]
