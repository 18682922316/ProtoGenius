"""Language-agnostic test specification.

Per §6.1, test cases are first expressed in a neutral form and then
materialized into a language-specific suite by an adapter. The neutral
form is a list of `TestCase`s; serialization to / from YAML is provided so
the spec can be persisted under ``<run>/tests/spec.yaml``.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

import yaml

TestKind = Literal["unit", "integration", "e2e"]


@dataclass
class TestCase:
    __test__ = False  # not a pytest test class
    id: str
    refs: list[str]                       # SRS / TDD identifiers
    kind: TestKind
    steps: list[str]
    expected: str
    runner_hint: str = "pytest"
    pre: str = ""
    description: str = ""


@dataclass
class TestSpec:
    __test__ = False  # not a pytest test class
    cases: list[TestCase] = field(default_factory=list)

    @classmethod
    def from_iterable(cls, items: Iterable[TestCase]) -> TestSpec:
        return cls(cases=list(items))

    def to_yaml(self) -> str:
        return yaml.safe_dump([asdict(c) for c in self.cases], sort_keys=False)

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_yaml(), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> TestSpec:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        return cls(cases=[TestCase(**entry) for entry in data])
