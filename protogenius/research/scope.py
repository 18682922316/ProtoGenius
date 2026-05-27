"""v2 §2.7 — scoped research router.

When the task input carries a ``scoped_input`` the orchestrator narrows
search queries and the four-layer doc-generation set:

| ScopedInput.type | Research focus                  | Layer generation default            |
|------------------|---------------------------------|-------------------------------------|
| ``topic``        | tech-topic-only insights        | tech_topic + (optional) lower deps  |
| ``algorithm``    | atomic-algorithm-only insights  | atomic_algorithm + foundation_theory|
| ``theory``       | foundation-theory-only insights | foundation_theory                   |
| ``product``      | product / app insights          | ai_application + dep chain          |

Two helpers live here:

- :func:`narrow_queries` adjusts a list of :class:`SearchQuery`
  candidates given the ``scoped_input``. It returns a new list that
  prepends the scoped keyword to the original query text and tightens
  ``max_results`` according to ``ScopedInputConfig.quota_scale_factor``.
- :func:`select_layers` returns the ordered list of layer ids to
  generate for the given ``ScopedInput.type``.
"""

from __future__ import annotations

from collections.abc import Iterable

from ..config import ScopedInputConfig
from ..task_input import ScopedInput
from .base import SearchQuery

_LAYER_SETS: dict[str, list[str]] = {
    "topic": ["foundation_theory", "atomic_algorithm", "tech_topic"],
    "algorithm": ["foundation_theory", "atomic_algorithm"],
    "theory": ["foundation_theory"],
    "product": [
        "foundation_theory",
        "atomic_algorithm",
        "tech_topic",
        "ai_application",
    ],
}


def select_layers(scoped: ScopedInput | None) -> list[str]:
    """Return the layer ids the four-layer generator should produce.

    For unscoped (full-pipeline) runs we still emit all four layers.
    """
    if scoped is None:
        return ["foundation_theory", "atomic_algorithm", "tech_topic", "ai_application"]
    return list(_LAYER_SETS.get(scoped.type, _LAYER_SETS["product"]))


def narrow_queries(
    queries: Iterable[SearchQuery],
    *,
    scoped: ScopedInput | None,
    config: ScopedInputConfig,
) -> list[SearchQuery]:
    """Adjust ``queries`` for a scoped run.

    When ``scoped`` is ``None`` the queries are returned untouched.
    Otherwise:

    - The scoped name (or description, if no name) is **prepended** to
      ``query.text`` so the search engines focus on the right subject.
    - ``max_results`` is multiplied by ``config.quota_scale_factor`` and
      floored at 1; the result is still subject to the per-task §7.1
      hard cap once charged through the quota guard.
    """
    if scoped is None:
        return list(queries)
    scope_label = (scoped.name or scoped.description).strip()
    if not scope_label:
        return list(queries)
    factor = max(0.0, min(1.0, float(config.quota_scale_factor)))

    narrowed: list[SearchQuery] = []
    for q in queries:
        scaled = max(1, int(round(q.max_results * factor))) if factor else q.max_results
        narrowed.append(
            SearchQuery(
                text=f"{scope_label} {q.text}".strip(),
                max_results=scaled,
                window_days=q.window_days,
                sort=q.sort,
                extras={**q.extras, "scoped_to": scoped.type},
            )
        )
    return narrowed
