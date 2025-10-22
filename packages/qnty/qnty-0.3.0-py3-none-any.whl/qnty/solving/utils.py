"""
Shared utilities for the solving module.

This module provides common functionality used across different solvers
and solving components to eliminate code duplication.
"""

from __future__ import annotations

from typing import Any

from ..core.quantity import FieldQuantity


class SolvingUtils:
    """Utility functions for solving operations."""

    @staticmethod
    def get_known_variables(variables: dict[str, FieldQuantity]) -> set[str]:
        """Get symbols of known variables."""
        return {s for s, v in variables.items() if v.is_known}

    @staticmethod
    def get_unknown_variables(variables: dict[str, FieldQuantity]) -> set[str]:
        """Get symbols of unknown variables."""
        return {s for s, v in variables.items() if not v.is_known}

    @staticmethod
    def partition_variables(variables: dict[str, FieldQuantity]) -> tuple[set[str], set[str]]:
        """Partition variables into known and unknown sets efficiently.

        Args:
            variables: Dictionary of variables

        Returns:
            Tuple of (known_symbols, unknown_symbols)
        """
        known = set()
        unknown = set()
        for symbol, variable in variables.items():
            if variable.is_known:
                known.add(symbol)
            else:
                unknown.add(symbol)
        return known, unknown

    @staticmethod
    def resolve_preferred_unit(variable: FieldQuantity, variable_name: str | None = None):
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
            from ..core.unit import ureg

            preferred_unit = ureg.si_unit_for(variable.dim)
            if preferred_unit is None:
                var_name = variable_name or getattr(variable, "name", "unknown")
                raise ValueError(f"Cannot determine unit for variable {var_name}")
        return preferred_unit

    @staticmethod
    def extract_numerical_value(value: Any) -> float:
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


class SolverConstants:
    """Constants used across different solvers."""

    # Numerical stability
    DEFAULT_TOLERANCE = 1e-10
    MAX_CONDITION_NUMBER = 1e12
    MIN_SYSTEM_SIZE = 2

    # Performance optimization thresholds
    LARGE_SYSTEM_THRESHOLD = 100
    SPARSE_THRESHOLD = 0.1

    # Default limits
    DEFAULT_MAX_ITERATIONS = 100

    # Convergence criteria
    CONVERGENCE_TOLERANCE = 1e-9
    MAX_RESIDUAL = 1e-8
