"""GitHub ranking: cutoff_include_all tie policy."""

from __future__ import annotations

from protogenius.context import ResearchItem
from protogenius.research.ranking import RepoRanking


def _repo(name: str, stars: int, release_freq: float | None) -> ResearchItem:
    return ResearchItem(
        title=name,
        source_type="github",
        url=f"https://github.com/{name}",
        stars=stars,
        release_frequency_per_year=release_freq,
    )


def test_ranking_by_stars_then_release_frequency():
    ranking = RepoRanking()
    repos = [
        _repo("a", 100, 1.0),
        _repo("b", 200, 0.5),
        _repo("c", 200, 4.0),
        _repo("d", 50, 10.0),
    ]
    out = ranking.rank(repos)
    titles = [r.title for r in out]
    assert titles[:3] == ["c", "b", "a"]


def test_no_release_only_uses_stars():
    ranking = RepoRanking()
    repos = [
        _repo("with_releases", 100, 3.0),
        _repo("no_releases", 100, None),
    ]
    out = ranking.rank(repos)
    # release-bearing repo wins the tie.
    assert out[0].title == "with_releases"


def test_cutoff_include_all_keeps_ties_at_position_three():
    ranking = RepoRanking(target_top_n=3, tie_policy="cutoff_include_all")
    repos = [
        _repo("first", 500, 5.0),
        _repo("second", 400, 4.0),
        _repo("third_a", 300, 2.0),
        _repo("third_b", 300, 2.0),
        _repo("third_c", 300, 2.0),
        _repo("fourth", 100, 1.0),
    ]
    out = ranking.rank(repos)
    titles = [r.title for r in out]
    assert "fourth" not in titles
    assert {"third_a", "third_b", "third_c"}.issubset(set(titles))
    assert len(titles) == 5


def test_strict_cap_3_truncates():
    ranking = RepoRanking(target_top_n=3, tie_policy="strict_cap_3")
    repos = [
        _repo("first", 500, 5.0),
        _repo("second", 400, 4.0),
        _repo("third_a", 300, 2.0),
        _repo("third_b", 300, 2.0),
    ]
    out = ranking.rank(repos)
    assert len(out) == 3
