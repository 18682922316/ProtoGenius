"""Demo kind selection."""

from __future__ import annotations

from protogenius.demo import DemoKind, choose_demo_kind


def test_algorithm_keyword_triggers_algo(run_context):
    run_context.task_description = "Design an algorithm for graph search"
    assert choose_demo_kind(run_context) is DemoKind.ALGO


def test_fullstack_hint(run_context):
    run_context.task_description = "Build a small web app with a chat UI"
    assert choose_demo_kind(run_context) is DemoKind.FULLSTACK


def test_script_hint(run_context):
    run_context.task_description = "Generate a CLI tool to convert csv to json"
    assert choose_demo_kind(run_context) is DemoKind.SCRIPT


def test_preferred_kind_overrides(run_context):
    run_context.task_description = "anything"
    assert choose_demo_kind(run_context, preferred_kind=DemoKind.ALGO) is DemoKind.ALGO
