"""GitHub ranking — primary by stars, secondary by release frequency.

The v1 contract:

- Sort primarily by stars.
- Within a tied stars bucket (or globally as a tie-breaker), sort by release
  frequency. Items with **no releases** are sorted by stars alone.
- The target list size is 3 — but the tie policy is ``cutoff_include_all``:
  every repository tied with the third-place item is included, so the final
  list may be larger.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..context import ResearchItem


@dataclass
class RepoRanking:
    target_top_n: int = 3
    tie_policy: str = "cutoff_include_all"

    def rank(self, items: list[ResearchItem]) -> list[ResearchItem]:
        # Stable sort: primary stars desc, then release frequency desc.
        def primary_key(item: ResearchItem) -> tuple[int, float]:
            stars = item.stars or 0
            if item.release_frequency_per_year is None:
                return (stars, -1.0)  # sentinel: keeps no-release items in the right bucket
            return (stars, item.release_frequency_per_year)

        sorted_items = sorted(items, key=primary_key, reverse=True)
        if len(sorted_items) <= self.target_top_n:
            return sorted_items

        if self.tie_policy == "strict_cap_3":
            return sorted_items[: self.target_top_n]

        # cutoff_include_all: include everyone tied with position N.
        cutoff = sorted_items[self.target_top_n - 1]
        cutoff_key = primary_key(cutoff)
        result: list[ResearchItem] = []
        for item in sorted_items:
            if primary_key(item) >= cutoff_key:
                result.append(item)
            else:
                break
        return result
