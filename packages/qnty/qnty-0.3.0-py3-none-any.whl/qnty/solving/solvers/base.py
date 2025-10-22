from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ...algebra import Equation
from ...core.quantity import FieldQuantity
from ..order import Order


@dataclass
class SolveResult:
    """Result of a solve operation."""

    variables: dict[str, FieldQuantity]
    steps: list[dict[str, Any]] = field(default_factory=list)
    success: bool = True
    message: str = ""
    method: str = ""
    iterations: int = 0


class BaseSolver(ABC):
    """Base class for all equation solvers."""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger
        self.steps: list[dict[str, Any]] = []

    @abstractmethod
    def can_handle(self, equations: list[Equation], unknowns: set[str], dependency_graph: Order | None = None, analysis: dict[str, Any] | None = None) -> bool:
        """
        Check if this solver can handle the given problem.

        Args:
            equations: List of equations to solve
            unknowns: Set of unknown variable symbols
            dependency_graph: Optional dependency graph for analysis
            analysis: Optional system analysis results

        Returns:
            True if this solver can handle the problem
        """
        ...

    @abstractmethod
    def solve(self, equations: list[Equation], variables: dict[str, FieldQuantity], dependency_graph: Order | None = None, max_iterations: int = 100, tolerance: float = 1e-10) -> SolveResult:
        """
        Solve the system of equations.

        Args:
            equations: List of equations to solve
            variables: Dictionary of all variables (known and unknown)
            dependency_graph: Optional dependency graph
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance

        Returns:
            SolveResult containing the solution
        """
        ...

    def _log_step(
        self, iteration: int, variable: str, equation: str, result: str, method: str | None = None, equation_obj: Equation | None = None, variables_state: dict[str, FieldQuantity] | None = None
    ):
        """Log a solving step with detailed information for reporting.

        Args:
            iteration: Current iteration number
            variable: Symbol of variable being solved
            equation: String representation of the equation
            result: String representation of the result
            method: Solving method used
            equation_obj: The actual Equation object for more details
            variables_state: Current state of all variables for substitution info
        """
        step = {
            "iteration": iteration,
            "variable": variable,
            "equation": equation,
            "result": result,
            "method": method or self.__class__.__name__,
            "target": variable,  # For compatibility with existing code
        }

        # Add additional details for reporting
        if equation_obj:
            step["equation_name"] = getattr(equation_obj, "name", variable)
            step["equation_str"] = str(equation_obj)

            # Try to create substituted equation with actual values
            if variables_state:
                try:
                    # Create a proper substituted equation by replacing variables with their values
                    equation_str = str(equation_obj)
                    substituted_eq = equation_str

                    # Replace each known variable with its value and unit (but NOT the target variable)
                    equation_vars = equation_obj.get_all_variables()
                    for var_sym in equation_vars:
                        # Skip the target variable being solved for
                        if var_sym == variable:
                            continue

                        if var_sym in variables_state and variables_state[var_sym].is_known:
                            var = variables_state[var_sym]

                            # Use the original value and unit (before SI conversion)
                            if var.preferred and hasattr(var.preferred, "si_factor") and var.value is not None:
                                # Get the value in the preferred unit
                                original_value = var.value / var.preferred.si_factor
                                formatted_value = f"{original_value:.6g} {var.preferred.symbol}"
                            elif hasattr(var, "_output_unit") and var._output_unit and hasattr(var._output_unit, "si_factor") and var.value is not None:
                                # Get the value in the output unit
                                original_value = var.value / var._output_unit.si_factor
                                formatted_value = f"{original_value:.6g} {var._output_unit.symbol}"
                            else:
                                # Fallback to SI value if no unit info available
                                value = var.value
                                formatted_value = f"{value:.6g}" if value is not None else "0"

                            # Replace the variable symbol with the formatted value
                            # Use word boundaries to avoid partial replacements
                            import re

                            pattern = r"\b" + re.escape(var_sym) + r"\b"
                            substituted_eq = re.sub(pattern, formatted_value, substituted_eq)

                    step["substituted"] = substituted_eq
                except Exception:
                    pass  # Don't fail if we can't create substitution string

        # Extract numerical result and unit
        try:
            if " " in result:
                parts = result.split(" ", 1)
                step["result_value"] = parts[0]
                step["result_unit"] = parts[1] if len(parts) > 1 else ""
            else:
                step["result_value"] = result
                step["result_unit"] = ""
        except Exception:
            step["result_value"] = str(result)
            step["result_unit"] = ""

        self.steps.append(step)
        if self.logger:
            self.logger.debug("Solved %s = %s", variable, result)

    def _get_known_variables(self, variables: dict[str, FieldQuantity]) -> set[str]:
        """Get symbols of known variables."""
        return {s for s, v in variables.items() if v.is_known}

    def _get_unknown_variables(self, variables: dict[str, FieldQuantity]) -> set[str]:
        """Get symbols of unknown variables."""
        return {s for s, v in variables.items() if not v.is_known}

    def _partition_variables(self, variables: dict[str, FieldQuantity]) -> tuple[set[str], set[str]]:
        """Partition variables into known and unknown sets efficiently."""
        known = set()
        unknown = set()
        for symbol, variable in variables.items():
            if variable.is_known:
                known.add(symbol)
            else:
                unknown.add(symbol)
        return known, unknown

    def _resolve_preferred_unit(self, variable: FieldQuantity, variable_name: str | None = None):
        """Resolve preferred unit for a variable, falling back to SI unit.

        Args:
            variable: The variable to resolve unit for
            variable_name: Optional name for error messages (defaults to variable.name)

        Returns:
            Unit object for the variable

        Raises:
            ValueError: If no unit can be determined
        """
        preferred_unit = variable.preferred
        if preferred_unit is None:
            from ...core.unit import ureg

            preferred_unit = ureg.si_unit_for(variable.dim)
            if preferred_unit is None:
                var_name = variable_name or getattr(variable, "name", "unknown")
                raise ValueError(f"Cannot determine unit for variable {var_name}")
        return preferred_unit

    def _create_error_result(self, variables: dict[str, FieldQuantity], message: str, iterations: int = 0) -> SolveResult:
        """Create a standardized error result.

        Args:
            variables: Current state of variables
            message: Error message
            iterations: Number of iterations completed

        Returns:
            SolveResult indicating failure
        """
        return SolveResult(variables=variables, steps=self.steps, success=False, message=message, method=self.__class__.__name__, iterations=iterations)

    def _extract_numerical_value(self, value: Any) -> float:
        """Extract numerical value from various quantity types.

        Args:
            value: Value to extract from (Quantity, int, float, or object with .value)

        Returns:
            Float representation of the value

        Raises:
            ValueError: If value cannot be converted to float
        """
        try:
            if hasattr(value, "value") and value.value is not None:
                return float(value.value)
            elif isinstance(value, int | float):
                return float(value)
            else:
                return float(value)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot extract numerical value from {type(value)}: {value}") from e
