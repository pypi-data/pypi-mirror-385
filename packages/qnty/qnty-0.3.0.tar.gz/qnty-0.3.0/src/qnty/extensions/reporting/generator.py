"""
Main report generation interface.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal


def generate_report(
    problem: Any,
    output_path: str | Path,
    format: Literal["markdown", "latex", "pdf"] = "markdown",
) -> None:
    """
    Generate a detailed engineering calculation report from a solved problem.

    Args:
        problem: A solved Problem instance from the qnty library
        output_path: Path where the report should be saved
        format: Output format - 'markdown', 'latex', or 'pdf'

    Raises:
        ValueError: If the problem is not solved or format is invalid

    Example:
        >>> from qnty import Problem
        >>> problem = MyEngineeringProblem()
        >>> problem.solve()
        >>> generate_report(problem, "report.md", format="markdown")
    """
    if not problem.is_solved:
        raise ValueError("Problem must be solved before generating a report")

    # Import the appropriate generator based on format
    if format == "markdown":
        from .formats import MarkdownReportGenerator

        generator = MarkdownReportGenerator(problem)
    elif format == "latex":
        from .formats import LatexReportGenerator

        generator = LatexReportGenerator(problem)
    elif format == "pdf":
        from .formats import PdfReportGenerator

        generator = PdfReportGenerator(problem)
    else:
        raise ValueError(f"Invalid format '{format}'. Must be 'markdown', 'latex', or 'pdf'")

    # Generate the report
    generator.generate(output_path)
