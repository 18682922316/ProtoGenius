"""Demo scaffolding.

Three demo flavors per §5:

- ``fullstack``  : a runnable frontend + backend pair (Node + React + FastAPI etc.).
- ``script``     : a CLI / library prototype.
- ``algo``       : an algorithm / model prototype with reproducible instances.

The selector chooses one based on the task description and clarifications;
each generator writes a self-contained project tree under
``<run>/prototype/`` together with run-instructions in ``README.md``.
"""

from .selector import DemoKind, choose_demo_kind

__all__ = ["DemoKind", "choose_demo_kind"]
