"""
Reporting module for generating detailed calculation reports.

This module provides functionality to generate reports in various formats
(Markdown, LaTeX, PDF) from solved engineering problems in the qnty library.
"""

from .base import ReportGenerator
from .formats import LatexReportGenerator, MarkdownReportGenerator, PdfReportGenerator
from .generator import generate_report

__all__ = [
    "generate_report",
    "ReportGenerator",
    "MarkdownReportGenerator",
    "LatexReportGenerator",
    "PdfReportGenerator",
]

# Optional: Import vector diagram if matplotlib is available
try:
    from .vector_diagram import VectorDiagram, create_force_diagram
    __all__.extend(["VectorDiagram", "create_force_diagram"])
except ImportError:
    # Matplotlib not available, diagram generation will be skipped
    VectorDiagram = None  # type: ignore
    create_force_diagram = None  # type: ignore
