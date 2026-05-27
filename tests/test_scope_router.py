"""v2 §2.7 — scoped research router (query narrowing + layer selection)."""

from __future__ import annotations

from protogenius.config import ScopedInputConfig
from protogenius.research import narrow_queries, select_layers
from protogenius.research.base import SearchQuery
from protogenius.task_input import ScopedInput


def test_select_layers_per_scope_type():
    assert select_layers(None) == [
        "foundation_theory", "atomic_algorithm", "tech_topic", "ai_application"
    ]
    assert select_layers(ScopedInput(type="theory", name="x")) == ["foundation_theory"]
    assert select_layers(ScopedInput(type="algorithm", name="x")) == [
        "foundation_theory", "atomic_algorithm"
    ]
    assert select_layers(ScopedInput(type="topic", name="x")) == [
        "foundation_theory", "atomic_algorithm", "tech_topic"
    ]
    assert select_layers(ScopedInput(type="product", name="x")) == [
        "foundation_theory", "atomic_algorithm", "tech_topic", "ai_application"
    ]


def test_narrow_queries_prepends_scope_and_scales_results():
    queries = [SearchQuery(text="diffusion sampling", max_results=20)]
    out = narrow_queries(
        queries,
        scoped=ScopedInput(type="algorithm", name="DDIM"),
        config=ScopedInputConfig(quota_scale_factor=0.5),
    )
    assert len(out) == 1
    assert out[0].text.startswith("DDIM ")
    assert out[0].max_results == 10
    assert out[0].extras.get("scoped_to") == "algorithm"


def test_narrow_queries_passthrough_when_unscoped():
    queries = [SearchQuery(text="anything", max_results=5)]
    out = narrow_queries(queries, scoped=None, config=ScopedInputConfig())
    assert out == queries


def test_narrow_queries_floors_at_one():
    queries = [SearchQuery(text="x", max_results=2)]
    out = narrow_queries(
        queries,
        scoped=ScopedInput(type="theory", name="information theory"),
        config=ScopedInputConfig(quota_scale_factor=0.01),
    )
    assert out[0].max_results >= 1
