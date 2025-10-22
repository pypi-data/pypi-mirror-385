"""
Format-specific report generators for Markdown, LaTeX, and PDF.
"""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from .base import ReportGenerator


def _is_vector_equilibrium_problem(problem) -> bool:
    """Check if problem is a VectorEquilibriumProblem."""
    # Avoid circular import by checking class name in MRO
    class_names = [cls.__name__ for cls in problem.__class__.__mro__]
    return 'VectorEquilibriumProblem' in class_names


def _generate_diagram_if_needed(problem, output_dir: Path) -> Path | None:
    """Generate vector diagram for VectorEquilibriumProblem if applicable."""
    if not _is_vector_equilibrium_problem(problem):
        return None

    try:
        from .vector_diagram import create_force_diagram

        # Generate diagram in same directory as report
        # Sanitize filename - remove problematic characters
        safe_name = problem.name.replace(' ', '_').replace(':', '').replace('/', '_').replace('\\', '_')
        diagram_path = output_dir / f"{safe_name}_diagram.png"
        return create_force_diagram(problem, diagram_path, show_components=False)
    except Exception as e:
        # Log but don't fail if diagram generation not available
        import logging
        logging.debug(f"Could not generate diagram: {e}")
        return None


class MarkdownReportGenerator(ReportGenerator):
    """Generate reports in Markdown format."""

    def generate(self, output_path: str | Path) -> None:
        """Generate a Markdown report."""
        output_path = Path(output_path)

        # Generate vector diagram if applicable
        diagram_path = _generate_diagram_if_needed(self.problem, output_path.parent)

        # Build the report content
        content = []

        # Title and header
        content.append(f"# Engineering Calculation Report: {self.problem.name}")
        content.append("")
        content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")

        if self.problem.description:
            content.append(f"**Description:** {self.problem.description}")
            content.append("")

        # Known variables table
        content.append("## 1. Known Variables")
        content.append("")
        known_vars, _ = self._format_variable_table_data()

        if known_vars:
            # Check if this is vector equilibrium format (has 'magnitude' and 'angle' keys)
            if known_vars and 'magnitude' in known_vars[0]:
                # Get the unit from the first variable for the header
                unit = known_vars[0].get('unit', 'unit')
                content.append(f"| Symbol | Magnitude ({unit}) | Angle (°) |")
                content.append("|--------|------------------|-----------|")
                for var in known_vars:
                    # Unit is already in the header, so just show the magnitude value
                    content.append(f"| {var['symbol']} | {var['magnitude']} | {var['angle']} |")
            else:
                content.append("| Symbol | Name | Value | Unit |")
                content.append("|--------|------|-------|------|")
                for var in known_vars:
                    content.append(f"| {var['symbol']} | {var['name']} | {var['value']} | {var['unit']} |")
        else:
            content.append("*No known variables*")
        content.append("")

        # Unknown variables table
        content.append("## 2. Unknown Variables (To Calculate)")
        content.append("")
        _, unknown_vars = self._format_variable_table_data()

        if unknown_vars:
            # Check if this is vector equilibrium format
            if unknown_vars and 'magnitude' in unknown_vars[0]:
                # Get the unit from the first variable for the header
                unit = unknown_vars[0].get('unit', 'unit')
                content.append(f"| Symbol | Magnitude ({unit}) | Angle (°) |")
                content.append("|--------|------------------|-----------|")
                for var in unknown_vars:
                    # Unit is already in the header, so just show the magnitude value
                    content.append(f"| {var['symbol']} | {var['magnitude']} | {var['angle']} |")
            else:
                content.append("| Symbol | Name | Unit |")
                content.append("|--------|------|------|")
                for var in unknown_vars:
                    content.append(f"| {var['symbol']} | {var['name']} | {var['unit']} |")
        else:
            content.append("*No unknown variables*")
        content.append("")

        # Equations
        content.append("## 3. Equations Used")
        content.append("")
        equations = self._format_equation_list()
        for i, eq in enumerate(equations, 1):
            content.append(f"{i}. `{eq}`")
        content.append("")

        # Solution steps
        content.append("## 4. Step-by-Step Solution")
        content.append("")
        steps = self._extract_solution_steps()

        if steps:
            for i, step in enumerate(steps, 1):
                # Use the target variable name (now contains just the variable)
                content.append(f"### Step {i}: Solve for {step.equation_name}")
                content.append("")

                # Show the original equation with indentation
                content.append("    **Equation:**")
                content.append("    ```")
                content.append(f"    {step.equation_str}")
                content.append("    ```")
                content.append("")

                # Show the substituted equation if different
                if step.substituted_equation and step.substituted_equation != step.equation_str:
                    content.append("    **Substitution:**")
                    content.append("    ```")
                    content.append(f"    {step.substituted_equation}")
                    content.append("    ```")
                    content.append("")

                # Format result as variable = value unit with indentation and large font
                content.append("    **Result:**")
                content.append("    ```")
                content.append(f"    {step.equation_name} = {step.result_value} {step.result_unit}")
                content.append("    ```")
                content.append("")
        else:
            content.append("*No detailed solution steps available*")
            content.append("")

        # Final results summary
        content.append("## 5. Summary of Results")
        content.append("")

        # Use special table format for vector equilibrium problems
        if _is_vector_equilibrium_problem(self.problem):
            content.extend(self._format_vector_results_table_md())
        else:
            results = self._format_final_results()
            if results:
                content.append("| Variable | Name | Final Value | Unit |")
                content.append("|----------|------|-------------|------|")
                for res in results:
                    content.append(f"| {res['symbol']} | {res['name']} | {res['value']} | {res['unit']} |")
            else:
                content.append("*No results to summarize*")
        content.append("")

        # Include vector diagram after results if generated
        if diagram_path and diagram_path.exists():
            content.append("## 6. Vector Diagram")
            content.append("")
            content.append(f"![Vector Diagram]({diagram_path.name})")
            content.append("")
            content.append("*Figure: Vector diagram showing all forces and their orientations*")
            content.append("")

        # Add disclaimer section
        content.extend(self._format_disclaimer())

        # Write to file
        output_path.write_text("\n".join(content), encoding="utf-8")

    def _format_vector_results_table_md(self) -> list[str]:
        """Format results table for vector equilibrium problems with force components (Markdown)."""
        content = []

        # Get forces from the problem
        if not hasattr(self.problem, 'forces'):
            return ["*No results to summarize*"]

        # Table header
        content.append("| Symbol | Magnitude (N) | Angle (°) | F_x (N) | F_y (N) |")
        content.append("|--------|---------------|-----------|---------|---------|")

        # Process each force
        for force_name, force in self.problem.forces.items():
            symbol = force.name

            # Get magnitude
            if force.magnitude and force.magnitude.value is not None:
                mag_value = force.magnitude.value
                if force.magnitude.preferred:
                    mag_value = mag_value / force.magnitude.preferred.si_factor
                magnitude = f"{mag_value:.6g}"
            else:
                magnitude = "?"

            # Get angle in degrees
            if force.angle and force.angle.value is not None:
                import math
                angle_deg = force.angle.value * 180 / math.pi
                # Normalize to 0-360 degrees (counterclockwise from positive x-axis)
                angle_deg = angle_deg % 360
                angle = f"{angle_deg:.6g}"
            else:
                angle = "?"

            # Get components
            if force.x and force.x.value is not None:
                x_value = force.x.value
                if force.x.preferred:
                    x_value = x_value / force.x.preferred.si_factor
                fx = f"{x_value:.6g}"
            else:
                fx = "?"

            if force.y and force.y.value is not None:
                y_value = force.y.value
                if force.y.preferred:
                    y_value = y_value / force.y.preferred.si_factor
                fy = f"{y_value:.6g}"
            else:
                fy = "?"

            # Add row
            content.append(f"| {symbol} | {magnitude} | {angle} | {fx} | {fy} |")

        return content

    def _format_disclaimer(self) -> list[str]:
        """Format disclaimer section for Markdown."""
        current_date = datetime.now().strftime("%B %d, %Y")

        content = [
            "",
            "---",
            "",
            "## Disclaimer",
            "",
            "While every effort has been made to ensure the accuracy and reliability of the calculations provided, "
            + "we do not guarantee that the information is complete, up-to-date, or suitable for any specific purpose. "
            + "Users must independently verify the results and assume full responsibility for any decisions or actions "
            + "taken based on its output. Use of this calculator is entirely at your own risk, and we expressly "
            + "disclaim any liability for errors or omissions in the information provided.",
            "",
            "**Report Details:**",
            f"- **Generated Date:** {current_date}",
            "- **Generated Using:** Qnty Library",
            "- **Version:** Beta (Independent verification required for production use)",
            "",
            "**Signatures:**",
            "",
            "| Role | Name | Signature | Date |",
            "|------|------|-----------|------|",
            "| Calculated By | _________________ | _________________ | _______ |",
            "| Reviewed By | _________________ | _________________ | _______ |",
            "| Approved By | _________________ | _________________ | _______ |",
            "",
            "*Report generated using qnty library*",
        ]

        return content


class LatexReportGenerator(ReportGenerator):
    """Generate reports in LaTeX format."""

    def generate(self, output_path: str | Path) -> None:
        """Generate a LaTeX report."""
        output_path = Path(output_path)

        # Generate vector diagram if applicable
        diagram_path = _generate_diagram_if_needed(self.problem, output_path.parent)

        # Build the LaTeX document
        content = []

        # Document preamble
        content.append(r"\documentclass[11pt,a4paper]{article}")
        content.append(r"\usepackage{amsmath}")
        content.append(r"\usepackage{amssymb}")
        content.append(r"\usepackage{booktabs}")
        content.append(r"\usepackage{longtable}")
        content.append(r"\usepackage{geometry}")
        content.append(r"\geometry{margin=1in}")
        content.append(r"\usepackage{hyperref}")
        content.append(r"\usepackage{enumitem}")  # For customized list environments
        content.append(r"\usepackage{graphicx}")  # For including images
        content.append(r"\usepackage{siunitx}")  # For decimal-aligned columns
        content.append("")
        content.append(r"\title{Engineering Calculation Report: " + self._escape_latex(self.problem.name) + "}")
        content.append(r"\date{" + datetime.now().strftime("%B %d, %Y") + "}")
        content.append("")
        content.append(r"\begin{document}")
        content.append(r"\maketitle")
        content.append("")

        if self.problem.description:
            content.append(r"\section*{Description}")
            # Split description into paragraphs and wrap properly
            desc_paragraphs = self.problem.description.strip().split('\n\n')
            for i, para in enumerate(desc_paragraphs):
                # Clean up extra whitespace and newlines within paragraph
                para = ' '.join(para.split())
                if para:
                    if i == 0:
                        content.append(r"\noindent")
                    # Format variable names in the description text
                    para = self._format_description_variables(para)
                    # Use a parbox or minipage to ensure proper text wrapping
                    content.append(r"\begin{minipage}{\textwidth}")
                    content.append(para)
                    content.append(r"\end{minipage}")
                    content.append(r"\par")
            content.append("")

        # Known variables
        content.append(r"\section{Known Variables}")
        content.append("")
        known_vars, _ = self._format_variable_table_data()

        if known_vars:
            # Check if this is vector equilibrium format
            if known_vars and 'magnitude' in known_vars[0]:
                # Get the unit from the first variable for the header
                unit = self._escape_latex(known_vars[0].get('unit', 'unit'))
                content.append(r"\begin{longtable}{lSS}")
                content.append(r"\toprule")
                content.append(f"Symbol & {{Magnitude ({unit})}} & {{Angle ($^\\circ$)}} \\\\")
                content.append(r"\midrule")
                content.append(r"\endhead")

                for var in known_vars:
                    # Unit is already in the header, so just show the magnitude value
                    content.append(f"${self._format_latex_variable(var['symbol'])}$ & {var['magnitude']} & {var['angle']} \\\\")

                content.append(r"\bottomrule")
                content.append(r"\end{longtable}")
            else:
                content.append(r"\begin{longtable}{llSl}")
                content.append(r"\toprule")
                content.append(r"Symbol & Name & {Value} & Unit \\")
                content.append(r"\midrule")
                content.append(r"\endhead")

                for var in known_vars:
                    content.append(f"${self._format_latex_variable(var['symbol'])}$ & {self._escape_latex(var['name'])} & {var['value']} & {self._escape_latex(var['unit'])} \\\\")

                content.append(r"\bottomrule")
                content.append(r"\end{longtable}")
        else:
            content.append(r"\textit{No known variables}")
        content.append("")

        # Unknown variables
        content.append(r"\section{Unknown Variables (To Calculate)}")
        content.append("")
        _, unknown_vars = self._format_variable_table_data()

        if unknown_vars:
            # Check if this is vector equilibrium format
            if unknown_vars and 'magnitude' in unknown_vars[0]:
                # Get the unit from the first variable for the header
                unit = self._escape_latex(unknown_vars[0].get('unit', 'unit'))
                content.append(r"\begin{longtable}{lll}")
                content.append(r"\toprule")
                content.append(f"Symbol & Magnitude ({unit}) & Angle ($^\\circ$) \\\\")
                content.append(r"\midrule")
                content.append(r"\endhead")

                for var in unknown_vars:
                    # Unit is already in the header, so just show the magnitude value
                    mag_display = var['magnitude']
                    angle_display = var['angle']
                    content.append(f"${self._format_latex_variable(var['symbol'])}$ & {mag_display} & {angle_display} \\\\")

                content.append(r"\bottomrule")
                content.append(r"\end{longtable}")
            else:
                content.append(r"\begin{longtable}{lll}")
                content.append(r"\toprule")
                content.append(r"Symbol & Name & Unit \\")
                content.append(r"\midrule")
                content.append(r"\endhead")

                for var in unknown_vars:
                    content.append(f"${self._format_latex_variable(var['symbol'])}$ & {self._escape_latex(var['name'])} & {self._escape_latex(var['unit'])} \\\\")

                content.append(r"\bottomrule")
                content.append(r"\end{longtable}")
        else:
            content.append(r"\textit{No unknown variables}")
        content.append("")

        # Equations
        content.append(r"\section{Equations Used}")
        content.append("")
        content.append(r"\begin{enumerate}")
        equations = self._format_equation_list()
        for eq in equations:
            # Try to convert to LaTeX math if possible
            latex_eq = self._to_latex_math(eq)
            # Use displaystyle with Large for bigger equations on the same line as item numbers
            content.append(r"\item $\displaystyle\Large " + latex_eq + "$")
        content.append(r"\end{enumerate}")
        content.append("")

        # Solution steps
        content.append(r"\section{Step-by-Step Solution}")
        content.append("")
        steps = self._extract_solution_steps()

        if steps:
            # Start one enumerate environment for all steps with custom label
            content.append(r"\begin{enumerate}[label=\textbf{Step \arabic*:},leftmargin=2cm]")

            for _i, step in enumerate(steps, 1):
                # Format equation name properly for LaTeX
                formatted_eq_name = step.equation_name
                if "=" in formatted_eq_name:
                    # This is an equation like "T = T_bar * (1 - U_m)"
                    parts = formatted_eq_name.split("=", 1)
                    if len(parts) == 2:
                        lhs = parts[0].strip()
                        rhs = parts[1].strip()
                        formatted_eq_name = f"${self._format_latex_variable(lhs)} = {self._to_latex_math(rhs)}$"
                    else:
                        formatted_eq_name = self._escape_latex(formatted_eq_name)
                else:
                    # Just a variable name
                    formatted_eq_name = f"${self._format_latex_variable(formatted_eq_name)}$"

                # Create step item - the label will automatically add "Step X:"
                content.append(r"\item \textbf{Solve for $" + self._format_latex_variable(step.equation_name) + "$}")
                content.append("")

                # Use description list for equation components with proper line breaks
                content.append(r"\begin{description}[leftmargin=2cm]")

                # Show the original equation
                content.append(r"\item[\textbf{Equation:}] \mbox{}")
                content.append("")
                original_latex_eq = self._to_latex_math(step.equation_str)
                # Use flalign* for left-aligned equations
                content.append(r"\begin{flalign*}")
                content.append(r"\Large " + original_latex_eq + r" &&")
                content.append(r"\end{flalign*}")
                content.append("")

                # Show the substituted equation if different
                if step.substituted_equation and step.substituted_equation != step.equation_str:
                    content.append(r"\item[\textbf{Substitution:}] \mbox{}")
                    content.append("")
                    # Protect spaces in values like "90 psi" by replacing them with LaTeX space commands
                    latex_eq = self._to_latex_math(step.substituted_equation)
                    # Replace spaces between numbers and units with protected spaces
                    # Use \mathrm for units to avoid them inheriting \Large size
                    import re

                    latex_eq = re.sub(r"([0-9\.e\-\+]+)\s+([a-zA-Z]+)", r"\1\\,\\mathrm{\2}", latex_eq)
                    # Use flalign* for left-aligned equations
                    content.append(r"\begin{flalign*}")
                    content.append(r"\Large " + latex_eq + r" &&")
                    content.append(r"\end{flalign*}")
                    content.append("")

                # Format result as variable = value unit
                content.append(r"\item[\textbf{Result:}] \mbox{}")
                content.append("")
                # Handle degree symbol in result unit (convert to LaTeX)
                result_unit_formatted = step.result_unit.replace("°", r"^\circ") if step.result_unit else ""
                # Wrap unit in \mathrm to avoid inheriting \Large size
                if result_unit_formatted:
                    result_unit_formatted = r"\mathrm{" + result_unit_formatted + "}"
                result_eq = self._format_latex_variable(step.equation_name) + " = " + self._escape_latex(str(step.result_value)) + r"\," + result_unit_formatted
                # Use flalign* for left-aligned equations
                content.append(r"\begin{flalign*}")
                content.append(r"\Large " + result_eq + r" &&")
                content.append(r"\end{flalign*}")
                content.append("")

                content.append(r"\end{description}")
                content.append("")

            # Close the enumerate environment
            content.append(r"\end{enumerate}")
            content.append("")
        else:
            content.append(r"\textit{No detailed solution steps available}")
        content.append("")

        # Summary
        content.append(r"\section{Summary of Results}")
        content.append("")

        # Use special table format for vector equilibrium problems
        if _is_vector_equilibrium_problem(self.problem):
            content.extend(self._format_vector_results_table())
        else:
            results = self._format_final_results()
            if results:
                content.append(r"\begin{longtable}{llSl}")
                content.append(r"\toprule")
                content.append(r"Variable & Name & {Final Value} & Unit \\")
                content.append(r"\midrule")
                content.append(r"\endhead")

                for res in results:
                    content.append(f"${self._format_latex_variable(res['symbol'])}$ & {self._escape_latex(res['name'])} & {res['value']} & {self._escape_latex(res['unit'])} \\\\")

                content.append(r"\bottomrule")
                content.append(r"\end{longtable}")
            else:
                content.append(r"\textit{No results to summarize}")
        content.append("")

        # Include vector diagram after results if generated
        if diagram_path and diagram_path.exists():
            content.append(r"\section{Vector Diagram}")
            content.append("")
            content.append(r"\begin{center}")
            content.append(r"\includegraphics[width=0.7\textwidth]{" + diagram_path.name + "}")
            content.append(r"\end{center}")
            content.append("")
            content.append(r"\begin{center}")
            content.append(r"\textit{Figure: Vector diagram showing all forces and their orientations}")
            content.append(r"\end{center}")
            content.append("")

        # Add disclaimer section
        content.extend(self._format_disclaimer())

        content.append("")
        content.append(r"\end{document}")

        # Write to file
        output_path.write_text("\n".join(content), encoding="utf-8")

    def _format_description_variables(self, text: str) -> str:
        """
        Format variable names in description text using LaTeX math mode.

        Converts patterns like F_1, F_2, T_bar etc. to proper LaTeX math notation.
        Escapes other special characters that aren't part of variable names.
        """
        import re

        # Pattern to match variable names (letter followed by optional underscore and more characters)
        # Matches: F_1, F_2, T_bar, F_R, etc.
        var_pattern = r'\b([A-Z][a-zA-Z]*_[a-zA-Z0-9]+)\b'

        # Find all variable names and their positions
        matches = list(re.finditer(var_pattern, text))

        # Build the result by processing text segments
        result = []
        last_end = 0

        for match in matches:
            # Add the text before this variable (escaped)
            before_text = text[last_end:match.start()]
            result.append(self._escape_latex(before_text))

            # Add the variable in math mode
            var_name = match.group(1)
            formatted_var = self._format_latex_variable(var_name)
            result.append(f"${formatted_var}$")

            last_end = match.end()

        # Add any remaining text after the last match (escaped)
        if last_end < len(text):
            result.append(self._escape_latex(text[last_end:]))

        return ''.join(result)

    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters."""
        if not isinstance(text, str):
            text = str(text)

        # Special handling for _bar pattern (should be overline)
        # Don't escape these - we'll handle them in _format_latex_variable
        if "_bar" in text:
            return text

        replacements = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
            "\\": r"\textbackslash{}",
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)

        return text

    def _format_latex_variable(self, var_symbol: str) -> str:
        """Format a variable symbol for LaTeX with proper handling of special patterns."""
        if not isinstance(var_symbol, str):
            var_symbol = str(var_symbol)

        # Handle magnitude notation like |F_1| - extract the variable inside pipes
        if var_symbol.startswith("|") and var_symbol.endswith("|"):
            inner_var = var_symbol[1:-1]  # Remove pipes
            formatted_inner = self._format_latex_variable(inner_var)  # Recursively format
            return f"|{formatted_inner}|"

        # Handle _bar pattern - should be overline
        if var_symbol.endswith("_bar"):
            base_var = var_symbol[:-4]  # Remove "_bar"
            return f"\\overline{{{base_var}}}"

        # Handle other underscore patterns as subscripts
        if "_" in var_symbol:
            parts = var_symbol.split("_", 1)  # Split on first underscore only
            base = parts[0]
            subscript = parts[1]
            return f"{base}_{{{subscript}}}"

        # No special formatting needed
        return var_symbol

    def _to_latex_math(self, equation_str: str) -> str:
        r"""
        Convert equation string to properly formatted LaTeX math.

        This handles:
        1. Equations with assignment (e.g., "P = (a * b) / c" -> "P = \frac{a \cdot b}{c}")
        2. Pure expressions (e.g., "(a * b) / c" -> "\frac{a \cdot b}{c}")
        3. Complex nested expressions
        4. Variable name formatting with proper subscripts/overlines
        """
        import re

        # Clean up the input
        result = equation_str.strip()

        # Replace common operators first (before parsing structure)
        result = result.replace("==", "=")
        result = result.replace("sqrt(", r"\sqrt{")

        # Parse equation structure: check if it contains an equals sign
        if " = " in result or "=" in result:
            # Split on equals sign to get LHS and RHS
            parts = result.split("=", 1)
            if len(parts) == 2:
                lhs = parts[0].strip()
                rhs = parts[1].strip()

                # Check if LHS is just a simple variable
                if re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", lhs):
                    # Simple variable on left, format as such
                    formatted_lhs = self._format_latex_variable(lhs)
                else:
                    # LHS is an expression (like "sin(alpha) / F_1")
                    formatted_lhs = self._format_expression(lhs)

                # Format the RHS expression
                formatted_rhs = self._format_expression(rhs)

                return f"{formatted_lhs} = {formatted_rhs}"

        # No equals sign, this is a pure expression
        return self._format_expression(result)

    def _format_expression(self, expr: str) -> str:
        r"""
        Format a mathematical expression (RHS of equation or standalone expression).

        Handles:
        - Fractions: (a*b)/(c*d) -> \frac{a \cdot b}{c \cdot d}
        - Multiplication: * -> \cdot
        - Variables: T_bar -> \overline{T}, P_max -> P_{max}
        - Functions: sqrt, sin, cos, etc.
        - Parentheses and complex nesting
        """
        expr = expr.strip()

        # Replace degree symbol with LaTeX command
        expr = expr.replace("°", r"^\circ")

        # Handle fractions by finding division operations at the right level
        # We need to be careful about parentheses nesting
        expr = self._convert_fractions(expr)

        # Replace multiplication operators
        expr = expr.replace("*", r" \cdot ")

        # Format exponents: ^2 -> ^{2}, etc.
        import re
        expr = re.sub(r'\^(\d+)', r'^{\1}', expr)
        expr = re.sub(r'\^([a-zA-Z_]\w*)', r'^{\1}', expr)

        # Format variable names
        expr = self._format_variables_in_expression(expr)

        # Handle mathematical functions
        expr = self._format_math_functions(expr)

        return expr

    def _convert_fractions(self, expr: str) -> str:
        r"""
        Convert division operations to LaTeX fractions intelligently.

        Examples:
        - "a / b" -> "\frac{a}{b}"
        - "(a * b) / (c + d)" -> "\frac{a \cdot b}{c + d}"
        - "2 * (a / b) + c" -> "2 \cdot \frac{a}{b} + c"
        """
        # Handle the main division in the expression
        if "/" not in expr:
            return expr

        # Find the main division (not inside parentheses) - take the first one
        paren_level = 0
        division_pos = -1

        for i, char in enumerate(expr):
            if char == "(":
                paren_level += 1
            elif char == ")":
                paren_level -= 1
            elif char == "/" and paren_level == 0:
                division_pos = i
                break  # Take the first top-level division

        if division_pos == -1:
            return expr

        # Extract left and right parts
        left_part = expr[:division_pos].strip()
        right_part = expr[division_pos + 1 :].strip()

        # Clean up parentheses if they wrap the entire expression
        if left_part.startswith("(") and left_part.endswith(")"):
            left_part = left_part[1:-1].strip()
        if right_part.startswith("(") and right_part.endswith(")"):
            right_part = right_part[1:-1].strip()

        return f"\\frac{{{left_part}}}{{{right_part}}}"

    def _format_variables_in_expression(self, expr: str) -> str:
        """Format variable names in an expression, preserving LaTeX commands."""
        import re

        def replace_variable(match):
            var_name = match.group(0)
            # Don't replace LaTeX commands or Greek letters with subscripts
            if any(cmd in var_name.lower() for cmd in ["frac", "sqrt", "cdot", "overline", "theta", "alpha", "beta", "gamma", "delta"]):
                return var_name
            return self._format_latex_variable(var_name)

        # Pattern to match variable names, but not LaTeX commands
        var_pattern = r"\b[a-zA-Z][a-zA-Z0-9_]*\b"

        # Split by backslash to avoid replacing LaTeX commands
        parts = expr.split("\\")

        # Format variables in the first part (before any LaTeX commands)
        parts[0] = re.sub(var_pattern, replace_variable, parts[0])

        # For subsequent parts, be more careful
        for i in range(1, len(parts)):
            if parts[i]:
                # Don't replace if this part starts with a LaTeX command
                # theta_, alpha_, etc. are protected because the subscript content should not be reformatted
                if not any(parts[i].startswith(cmd) for cmd in ["frac{", "sqrt{", "cdot", "overline{", "theta_", "alpha_", "beta_", "gamma_", "delta_"]):
                    # Find content after the command and format variables there
                    # This is a simplified approach - for more complex cases, we'd need a proper parser
                    parts[i] = re.sub(var_pattern, replace_variable, parts[i])

        return "\\".join(parts)

    def _format_vector_results_table(self) -> list[str]:
        """Format results table for vector equilibrium problems with force components."""
        content = []

        # Get forces from the problem
        if not hasattr(self.problem, 'forces'):
            return [r"\textit{No results to summarize}"]

        # Table header
        content.append(r"\begin{longtable}{lSSSSS}")
        content.append(r"\toprule")
        content.append(r"Symbol & {Magnitude (N)} & {Angle ($^\circ$)} & {$F_x$ (N)} & {$F_y$ (N)} \\")
        content.append(r"\midrule")
        content.append(r"\endhead")

        # Process each force
        for force_name, force in self.problem.forces.items():
            # Get the formatted symbol
            symbol = self._format_latex_variable(force.name)

            # Get magnitude
            if force.magnitude and force.magnitude.value is not None:
                mag_value = force.magnitude.value
                if force.magnitude.preferred:
                    # Convert to preferred unit
                    mag_value = mag_value / force.magnitude.preferred.si_factor
                magnitude = f"{mag_value:.6g}"
            else:
                magnitude = "?"

            # Get angle in degrees
            if force.angle and force.angle.value is not None:
                import math
                angle_deg = force.angle.value * 180 / math.pi  # Convert radians to degrees
                # Normalize to 0-360 degrees (counterclockwise from positive x-axis)
                angle_deg = angle_deg % 360
                angle = f"{angle_deg:.6g}"
            else:
                angle = "?"

            # Get components
            if force.x and force.x.value is not None:
                x_value = force.x.value
                if force.x.preferred:
                    x_value = x_value / force.x.preferred.si_factor
                fx = f"{x_value:.6g}"
            else:
                fx = "?"

            if force.y and force.y.value is not None:
                y_value = force.y.value
                if force.y.preferred:
                    y_value = y_value / force.y.preferred.si_factor
                fy = f"{y_value:.6g}"
            else:
                fy = "?"

            # Add row
            content.append(f"${symbol}$ & {magnitude} & {angle} & {fx} & {fy} \\\\")

        content.append(r"\bottomrule")
        content.append(r"\end{longtable}")

        return content

    def _format_math_functions(self, expr: str) -> str:
        """Format mathematical functions for LaTeX."""
        import re

        # Handle common mathematical functions
        functions = {"sin": "\\sin", "cos": "\\cos", "tan": "\\tan", "log": "\\log", "ln": "\\ln", "exp": "\\exp"}

        for func, latex_func in functions.items():
            # Replace function calls like sin(x) or cos(135.0°) with \sin{(x)} or \cos{(135.0°)}
            # Use regex to properly match the function call and its argument
            pattern = func + r'\(([^)]+)\)'
            # Use lambda to avoid escape sequence issues in replacement string
            # Wrap the argument in parentheses for proper LaTeX formatting
            expr = re.sub(pattern, lambda m: latex_func + '{(' + m.group(1) + ')}', expr)

        return expr

    def _format_disclaimer(self) -> list[str]:
        """Format disclaimer section for LaTeX/PDF with beautiful styling."""
        current_date = datetime.now().strftime("%B %d, %Y")

        content = [
            "",
            r"\clearpage",  # Start on a new page
            "",
            r"\section*{Disclaimer}",
            r"\addcontentsline{toc}{section}{Disclaimer}",  # Add to table of contents
            "",
            r"\begin{center}",
            r"\rule{\textwidth}{0.4pt}",  # Horizontal rule
            r"\end{center}",
            "",
            r"\noindent\textbf{IMPORTANT NOTICE:}",
            "",
            r"\noindent While every effort has been made to ensure the accuracy and reliability of the "
            + r"calculations provided, we do not guarantee that the information is complete, up-to-date, or "
            + r"suitable for any specific purpose. Users must independently verify the results and assume full "
            + r"responsibility for any decisions or actions taken based on its output. Use of this calculator is "
            + r"entirely at your own risk, and we expressly disclaim any liability for errors or omissions in "
            + r"the information provided.",
            "",
            r"\vspace{1em}",
            "",
            r"\noindent\textbf{Report Details:}",
            r"\begin{itemize}",
            r"\item \textbf{Generated Date:} " + current_date,
            r"\item \textbf{Generated Using:} Qnty Library",
            r"\item \textbf{Version:} Beta (Independent verification required for production use)",
            r"\end{itemize}",
            "",
            r"\vspace{2em}",
            "",
            r"\noindent\textbf{Professional Review and Approval:}",
            "",
            r"\vspace{1em}",
            "",
            # Beautiful signature table with professional styling
            r"\begin{longtable}{|p{3cm}|p{4cm}|p{4cm}|p{2.5cm}|}",
            r"\hline",
            r"\textbf{Role} & \textbf{Name} & \textbf{Signature} & \textbf{Date} \\",
            r"\hline",
            r"\hline",
            r"Calculated By & \rule{0pt}{1.5cm} & & \\",
            r"\hline",
            r"Reviewed By & \rule{0pt}{1.5cm} & & \\",
            r"\hline",
            r"Approved By & \rule{0pt}{1.5cm} & & \\",
            r"\hline",
            r"\end{longtable}",
            "",
            r"\vspace{1em}",
            "",
            r"\begin{center}",
            r"\rule{\textwidth}{0.4pt}",  # Bottom horizontal rule
            r"\vspace{0.5em}",
            r"\textit{Report generated using Qnty Library}",
            r"\vspace{0.5em}",
            r"{\footnotesize For questions or support, please refer to the Qnty documentation}",
            r"\end{center}",
        ]

        return content


class PdfReportGenerator(LatexReportGenerator):
    """Generate reports in PDF format using tectonic or system LaTeX."""

    def generate(self, output_path: str | Path) -> None:
        """Generate a PDF report by first creating LaTeX then compiling to PDF."""
        output_path = Path(output_path)

        # Create a temporary LaTeX file
        import os
        import tempfile

        # Create temp file and close it immediately to avoid file locking issues
        fd, temp_path = tempfile.mkstemp(suffix=".tex", text=True)
        os.close(fd)
        tex_path = Path(temp_path)

        try:
            # Generate LaTeX content
            super().generate(tex_path)

            # Try different PDF compilation methods
            pdf_generated = False

            # Method 1: Try tectonic executable
            if not pdf_generated:
                pdf_generated = self._try_tectonic_binary(tex_path, output_path)

            # Method 2: Try system tectonic command
            if not pdf_generated:
                pdf_generated = self._try_system_tectonic(tex_path, output_path)

            # Method 3: Try pdflatex
            if not pdf_generated:
                pdf_generated = self._try_pdflatex(tex_path, output_path)

            # If no method worked, keep the LaTeX file and inform the user
            if not pdf_generated:
                # Copy LaTeX file to output location with .tex extension
                tex_output = output_path.with_suffix(".tex")
                import shutil

                shutil.copy2(tex_path, tex_output)

                raise RuntimeError(
                    f"PDF generation failed. LaTeX file saved to {tex_output}. "
                    "Please install tectonic (https://tectonic-typesetting.github.io/) "
                    "or a LaTeX distribution (TeX Live, MiKTeX) to generate PDFs."
                )
        finally:
            # Clean up temporary file
            if tex_path.exists():
                try:
                    tex_path.unlink()
                except Exception:
                    pass  # Ignore errors during cleanup

    def _try_tectonic_binary(self, tex_path: Path, output_path: Path) -> bool:
        """Try to use the bundled tectonic binary."""
        import platform

        # Determine the correct binary name based on platform
        system = platform.system().lower()
        if system == "windows":
            binary_name = "tectonic.exe"
        elif system == "darwin":  # macOS
            binary_name = "tectonic"
        else:  # Linux and others
            binary_name = "tectonic"

        tectonic_path = Path(__file__).parent / binary_name

        # Also try without extension (for binaries downloaded without .exe)
        if not tectonic_path.exists():
            tectonic_path_no_ext = Path(__file__).parent / "tectonic"
            if tectonic_path_no_ext.exists():
                tectonic_path = tectonic_path_no_ext
            else:
                return False

        try:
            # Make sure it's executable on Unix-like systems
            if system != "windows":
                import os
                import stat

                st = os.stat(tectonic_path)
                os.chmod(tectonic_path, st.st_mode | stat.S_IEXEC)

            result = subprocess.run(
                [str(tectonic_path), str(tex_path), "-o", str(output_path.parent)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                # Tectonic outputs to the directory specified by -o with the same basename as the tex file
                # So if tex_path is /tmp/tmpXXX.tex and -o is /reports, PDF will be /reports/tmpXXX.pdf
                temp_pdf_name = tex_path.stem + ".pdf"
                generated_pdf = output_path.parent / temp_pdf_name
                if generated_pdf.exists():
                    if generated_pdf != output_path:
                        # Remove existing output file if it exists (Windows requires this)
                        if output_path.exists():
                            output_path.unlink()
                        generated_pdf.rename(output_path)
                    return True
        except Exception:
            pass

        return False

    def _try_system_tectonic(self, tex_path: Path, output_path: Path) -> bool:
        """Try to use system-installed tectonic."""
        try:
            # Check if tectonic is available in PATH
            check_result = subprocess.run(["tectonic", "--version"], capture_output=True, timeout=5)

            if check_result.returncode != 0:
                return False

            # Run tectonic
            result = subprocess.run(
                ["tectonic", str(tex_path), "-o", str(output_path.parent)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                # Tectonic outputs to the directory specified by -o with the same basename as the tex file
                temp_pdf_name = tex_path.stem + ".pdf"
                generated_pdf = output_path.parent / temp_pdf_name
                if generated_pdf.exists():
                    if generated_pdf != output_path:
                        # Remove existing output file if it exists (Windows requires this)
                        if output_path.exists():
                            output_path.unlink()
                        generated_pdf.rename(output_path)
                    return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return False

    def _try_pdflatex(self, tex_path: Path, output_path: Path) -> bool:
        """Try to use system-installed pdflatex."""
        try:
            # Check if pdflatex is available
            check_result = subprocess.run(["pdflatex", "--version"], capture_output=True, timeout=5)

            if check_result.returncode != 0:
                return False

            # Run pdflatex (need to run twice for references)
            for _ in range(2):
                subprocess.run(["pdflatex", "-interaction=nonstopmode", "-output-directory", str(tex_path.parent), str(tex_path)], capture_output=True, text=True, timeout=60, cwd=str(tex_path.parent))

            # Check if PDF was generated
            generated_pdf = tex_path.with_suffix(".pdf")
            if generated_pdf.exists():
                # Move to final location
                import shutil

                shutil.move(str(generated_pdf), str(output_path))

                # Clean up auxiliary files
                for ext in [".aux", ".log", ".out"]:
                    aux_file = tex_path.with_suffix(ext)
                    if aux_file.exists():
                        aux_file.unlink()

                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return False
