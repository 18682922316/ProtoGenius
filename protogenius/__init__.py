"""ProtoGenius — Autonomous Research-to-Prototype Agent for Task Validation.

Public API surface (stable contracts for sub-agents and skills):

    from protogenius.config import load_config, ProtoGeniusConfig
    from protogenius.context import RunContext
    from protogenius.orchestrator import Orchestrator
    from protogenius.state_machine import StateMachine, Stage

Anything not re-exported below should be considered internal and subject to
change between releases.
"""

from __future__ import annotations

from .config import ProtoGeniusConfig, load_config
from .context import RunContext
from .orchestrator import Orchestrator
from .state_machine import Stage, StateMachine, Transition

__all__ = [
    "Orchestrator",
    "ProtoGeniusConfig",
    "RunContext",
    "Stage",
    "StateMachine",
    "Transition",
    "load_config",
]

__version__ = "0.1.0"
