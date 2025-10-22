"""
Engineering problem checks and validation system.

This module provides a clean API for defining engineering code compliance checks,
warnings, and validation rules at the problem level rather than variable level.
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import Any, Literal

from ..algebra import Expression
from ..core.quantity import FieldQuantity, Quantity

# Constants for warning types
WARNING_TYPE_VALIDATION = "VALIDATION"
WARNING_TYPE_CODE_COMPLIANCE = "CODE_COMPLIANCE"
WARNING_TYPE_EVALUATION_ERROR = "EVALUATION_ERROR"

# Constants for severity levels
SEVERITY_INFO = "INFO"
SEVERITY_WARNING = "WARNING"
SEVERITY_ERROR = "ERROR"

# Default values
DEFAULT_WARNING_TYPE = WARNING_TYPE_VALIDATION
DEFAULT_SEVERITY = SEVERITY_WARNING

# Threshold for boolean conversion
BOOLEAN_THRESHOLD = 0.5


@dataclass
class Rules:
    """
    Represents an engineering problem check (code compliance, validation, etc.).

    Checks are defined at the EngineeringProblem class level and evaluated after solving.
    They can represent code compliance rules, engineering judgment warnings, or
    validation conditions.
    """

    condition: Expression
    message: str
    warning_type: str = DEFAULT_WARNING_TYPE
    severity: Literal["INFO", "WARNING", "ERROR"] = DEFAULT_SEVERITY
    name: str | None = None

    def __post_init__(self):
        """Generate a name if not provided."""
        if self.name is None:
            self.name = f"{self.warning_type}_{self.severity}"

    def evaluate(self, variables: dict[str, FieldQuantity]) -> dict[str, Any] | None:
        """
        Evaluate the check condition and return a warning dict if condition is True.

        Args:
            variables: Dictionary of variable name -> FieldQnty object mappings

        Returns:
            Warning dictionary if condition is met, None otherwise
        """
        try:
            # Evaluate the condition expression using qnty's evaluation system
            result = self._evaluate_expression(self.condition, variables)

            if result:
                return self._create_warning_dict(warning_type=self.warning_type, severity=self.severity, message=self.message)

        except Exception as e:
            # If evaluation fails, return an error warning
            return self._create_error_dict(e, variables)

        return None

    def _evaluate_expression(self, expr: Expression, variables: dict[str, FieldQuantity]) -> bool:
        """
        Evaluate a qnty expression with current variable values.

        Args:
            expr: The expression to evaluate
            variables: Dictionary of variable name -> FieldQnty object mappings

        Returns:
            Boolean result of the expression evaluation
        """
        # Evaluate the expression using the qnty evaluation system
        result = expr.evaluate(variables)

        # Convert result to boolean based on type
        return self._convert_result_to_bool(result)

    def _convert_result_to_bool(self, result: Quantity | bool) -> bool:
        """
        Convert an evaluation result to a boolean.

        Args:
            result: The result from expression evaluation

        Returns:
            Boolean interpretation of the result
        """
        # If already boolean, return as is
        if isinstance(result, bool):
            return result

        # For qnty Quantity objects, check the value
        if isinstance(result, Quantity) and result.value is not None:
            return bool(result.value > BOOLEAN_THRESHOLD)

        # Fallback for any numeric types
        try:
            return bool(float(result) > BOOLEAN_THRESHOLD)  # type: ignore[arg-type]
        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot convert expression result to boolean: {result}") from e

    def _create_warning_dict(self, warning_type: str, severity: str, message: str) -> dict[str, Any]:
        """
        Create a standardized warning dictionary.

        Args:
            warning_type: Type of warning
            severity: Severity level
            message: Warning message

        Returns:
            Warning dictionary with standard fields
        """
        return {"type": warning_type, "severity": severity, "message": message, "check_name": self.name, "condition": str(self.condition)}

    def _create_error_dict(self, exception: Exception, variables: dict[str, FieldQuantity]) -> dict[str, Any]:
        """
        Create a standardized error dictionary for evaluation failures.

        Args:
            exception: The exception that occurred
            variables: Dictionary of variables for debugging context

        Returns:
            Error dictionary with debugging information
        """
        return {
            "type": WARNING_TYPE_EVALUATION_ERROR,
            "severity": SEVERITY_ERROR,
            "message": f"Failed to evaluate check '{self.name}': {str(exception)}",
            "check_name": self.name,
            "condition": str(self.condition),
            "debug_info": f"Expression type: {type(self.condition)}, Variables: {list(variables.keys())}",
            "traceback": traceback.format_exc(),
        }


def add_rule(condition: Expression, message: str, warning_type: str = DEFAULT_WARNING_TYPE, severity: Literal["INFO", "WARNING", "ERROR"] = DEFAULT_SEVERITY, name: str | None = None) -> Rules:
    """
    Create a new engineering problem check.

    This function is intended to be called at the class level when defining
    EngineeringProblem subclasses. It creates Check objects that will be
    automatically collected by the metaclass.

    Args:
        condition: A qnty Expression that evaluates to True when the check should trigger.
                  Use comparison functions like geq() for natural syntax.
        message: Descriptive message explaining what the check means
        warning_type: Category of check (e.g., "CODE_COMPLIANCE", "VALIDATION")
        severity: Severity level of the check
        name: Optional name for the check

    Returns:
        Check object that can be assigned to a class attribute

    Example:
        class MyProblem(EngineeringProblem):
            # Variables...
            P = Pressure(90, "psi")
            t = Length(0.1, "inch")
            D = Length(1.0, "inch")

            # Checks defined at class level using comparison functions
            thick_wall_check = add_rule(
                geq(t, D / 6),
                "Thick wall condition detected - requires special consideration",
                warning_type="CODE_COMPLIANCE",
                severity="WARNING"
            )
    """
    return Rules(condition=condition, message=message, warning_type=warning_type, severity=severity, name=name)


__all__ = ["add_rule", "Rules"]
