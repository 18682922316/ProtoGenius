"""v2 §2.8 — knowledge base indexer + local connector + locator parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from protogenius.context import LayerDoc
from protogenius.kb import (
    LocalKb,
    detect_conflicts,
    discover_layer_docs,
    parse_locator,
    resolve_kb_ref,
)
from protogenius.task_input import KnowledgeBaseRef


def _make_kb_tree(root: Path) -> None:
    (root / "foundation_theory").mkdir(parents=True)
    (root / "foundation_theory" / "info_theory.md").write_text(
        "---\nname: Information Theory\nlayer: foundation_theory\n---\n# body\n",
        encoding="utf-8",
    )
    (root / "atomic_algorithm").mkdir()
    (root / "atomic_algorithm" / "beam_search.md").write_text(
        "---\nname: Beam Search\nlayer: atomic_algorithm\n---\n# body\n",
        encoding="utf-8",
    )
    # Flat-layout fallback file:
    (root / "flat_doc.md").write_text(
        "---\nname: Flat\nlayer: tech_topic\n---\n# body\n",
        encoding="utf-8",
    )


def test_discover_layer_docs_finds_hierarchical_and_flat(tmp_path: Path):
    _make_kb_tree(tmp_path)
    idx = discover_layer_docs(tmp_path)
    assert len(idx["foundation_theory"]) == 1
    assert len(idx["atomic_algorithm"]) == 1
    assert len(idx["tech_topic"]) == 1


def test_resolve_kb_ref_uses_directory_layout(tmp_path: Path):
    _make_kb_tree(tmp_path)
    p = tmp_path / "foundation_theory" / "info_theory.md"
    ref = resolve_kb_ref(root=tmp_path, file_path=p, revision="abc1234")
    assert ref == "kb://foundation_theory/foundation_theory/info_theory.md@abc1234"


def test_local_kb_materializes_snapshot(tmp_path: Path):
    _make_kb_tree(tmp_path)
    snap = LocalKb(ref=KnowledgeBaseRef(local_path=str(tmp_path))).materialize()
    assert snap.root == tmp_path
    assert "foundation_theory" in snap.layer_index
    assert snap.doc_versions  # mtime-based versions


def test_parse_locator_variants():
    p1 = parse_locator("acme/kb")
    assert (p1.owner, p1.repo, p1.ref, p1.subdir) == ("acme", "kb", "", "")
    p2 = parse_locator("acme/kb@main")
    assert p2.ref == "main"
    p3 = parse_locator("acme/kb@main:docs/layers")
    assert (p3.ref, p3.subdir) == ("main", "docs/layers")
    with pytest.raises(ValueError):
        parse_locator("not a locator")


def test_detect_conflicts_flags_same_layer_different_name(tmp_path: Path):
    kb_file = tmp_path / "atomic_algorithm" / "beam_search.md"
    kb_file.parent.mkdir(parents=True)
    kb_file.write_text(
        "---\nname: Vintage Beam Search\nlayer: atomic_algorithm\n---\nbeam search content\n",
        encoding="utf-8",
    )
    generated = LayerDoc(
        layer="atomic_algorithm",
        name="Beam Search",
        description="generated",
        path=tmp_path / "out.md",
    )
    conflicts = detect_conflicts(
        generated_layer=generated,
        kb_doc_paths=[kb_file],
        same_topic_keywords=["beam"],
    )
    assert len(conflicts) == 1
    assert "Vintage Beam Search" in conflicts[0].summary
