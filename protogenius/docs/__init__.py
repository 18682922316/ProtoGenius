"""IEEE 29148-aligned document generation + v2 four-layer / insight docs."""

from .architecture import render_architecture_diagram
from .insight_generator import (
    InsightGenerator,
    InsightMinimumContentError,
    render_insights,
)
from .interfaces import InterfaceSpec, render_interfaces_section
from .layer_docs import (
    LAYER_SPECS,
    FormalizationBlockMissingError,
    LayerDocMinimumContentError,
    LayerDocsGenerator,
)
from .srs_generator import SrsGenerator
from .tdd_generator import TddGenerator

__all__ = [
    "FormalizationBlockMissingError",
    "InsightGenerator",
    "InsightMinimumContentError",
    "InterfaceSpec",
    "LAYER_SPECS",
    "LayerDocMinimumContentError",
    "LayerDocsGenerator",
    "SrsGenerator",
    "TddGenerator",
    "render_architecture_diagram",
    "render_insights",
    "render_interfaces_section",
]
