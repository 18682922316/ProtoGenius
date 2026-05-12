"""State machine: pipeline order and gate identification."""

from __future__ import annotations

from protogenius.state_machine import Stage, StateMachine


def test_pipeline_starts_at_init_and_ends_at_done():
    sm = StateMachine()
    transitions = sm.transitions
    assert transitions[0].src == Stage.INIT
    assert any(t.dst == Stage.DONE for t in transitions)


def test_blocking_gates_match_contract():
    sm = StateMachine()
    gates = sm.blocking_gates()
    assert Stage.GATE_RESEARCH_ADOPTION in gates
    assert Stage.GATE_DOC_SIGNOFF in gates
    assert len(gates) == 2


def test_research_industry_branches_on_algorithm_task():
    sm = StateMachine()
    # Non-optional path: industry → cross_compare (algorithm task absent).
    # Optional path: industry → first_principles (algorithm task present).
    main = sm.next_stage(Stage.RESEARCH_INDUSTRY, took_optional_branch=False)
    optional = sm.next_stage(Stage.RESEARCH_INDUSTRY, took_optional_branch=True)
    assert {main, optional} == {Stage.CROSS_COMPARE, Stage.FIRST_PRINCIPLES}


def test_next_stage_walks_linearly_through_pipeline():
    sm = StateMachine()
    stage = Stage.INIT
    visited: list[Stage] = []
    safety = 0
    while stage != Stage.DONE and safety < 30:
        visited.append(stage)
        stage = sm.next_stage(stage, took_optional_branch=False)
        safety += 1
    assert Stage.CLARIFY in visited
    assert Stage.DRAFT_DOCS in visited
    assert Stage.ALIGNMENT_REPORT in visited
    assert stage == Stage.DONE
