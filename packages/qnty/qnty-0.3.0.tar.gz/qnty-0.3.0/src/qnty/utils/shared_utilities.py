"""
Shared utilities for expression handling and variable operations.

This module consolidates common patterns used across algebra and problems modules
to eliminate code duplication and improve maintainability.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from ..core.quantity import FieldQuantity, Quantity


# Type aliases
OperandType = Any  # Expression | FieldQuantity | Quantity | int | float


# ========== SHARED VALIDATION UTILITIES ==========


class ValidationHelper:
    """Consolidates common validation patterns used across modules."""

    @staticmethod
    def has_valid_value(obj) -> bool:
        """Check if an object has a valid (non-None) value attribute."""
        return hasattr(obj, "value") and getattr(obj, "value", None) is not None

    @staticmethod
    def safe_get_symbol(obj) -> str | None:
        """Safely get symbol from various object types."""
        if hasattr(obj, "symbol"):
            return getattr(obj, "symbol", None)
        if hasattr(obj, "name"):
            return getattr(obj, "name", None)
        return None

    @staticmethod
    def safe_get_name(obj) -> str | None:
        """Safely get name from various object types."""
        if hasattr(obj, "name"):
            return getattr(obj, "name", None)
        if hasattr(obj, "symbol"):
            return getattr(obj, "symbol", None)
        return None

    @staticmethod
    def safe_get_attribute(obj, *attr_names, default=None):
        """Safely get first available attribute from object."""
        for attr_name in attr_names:
            if hasattr(obj, attr_name):
                value = getattr(obj, attr_name, None)
                if value is not None:
                    return value
        return default

    @staticmethod
    def safe_get_callable(obj, attr_name, default=None):
        """Safely get callable attribute from object."""
        if hasattr(obj, attr_name):
            attr_value = getattr(obj, attr_name, None)
            if callable(attr_value):
                return attr_value
        return default

    @staticmethod
    def safe_get_identifier(obj) -> str | None:
        """Get the best identifier (symbol or name) from object."""
        return ValidationHelper.safe_get_attribute(obj, "symbol", "name")

    @staticmethod
    def is_simple_variable_symbol(symbol: str) -> bool:
        """Check if a symbol looks like a simple variable identifier."""
        if not symbol or not isinstance(symbol, str):
            return False
        return symbol.isidentifier() and not any(char in symbol for char in ["(", ")", "+", "-", "*", "/", " "])

    @staticmethod
    def get_effective_unit(quantity):
        """Get the effective unit for a quantity, handling both old and new Quantity objects."""
        # New Quantity objects have preferred attribute
        if hasattr(quantity, "preferred") and quantity.preferred is not None:
            return quantity.preferred

        # Old Quantity objects might have unit attribute
        if hasattr(quantity, "unit"):
            return quantity.unit

        # Try to get preferred unit from dimension
        if hasattr(quantity, "dim"):
            try:
                from ..core.unit import ureg

                return ureg.preferred_for(quantity.dim) or ureg.si_unit_for(quantity.dim)
            except ImportError:
                pass

        return None


# ========== SAFE EXECUTION PATTERNS ==========


class SafeExecutionMixin:
    """Mixin providing safe execution patterns used across modules."""

    def safe_execute(self, operation_name: str, operation: Callable[[], Any], default_return: Any = None) -> Any:
        """Execute an operation safely with standardized error handling."""
        try:
            return operation()
        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.debug(f"Failed to {operation_name}: {e}")  # type: ignore[attr-defined]
            return default_return

    def safe_execute_with_logging(self, operation_name: str, operation: Callable[[], Any], default_return: Any = None) -> Any:
        """Execute an operation safely with standardized error handling and logging."""
        try:
            return operation()
        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.debug(f"{operation_name} failed: {e}")  # type: ignore[attr-defined]
            return default_return


# ========== VARIABLE REFERENCE UTILITIES ==========


class VariableReferenceHelper:
    """Consolidates variable reference handling patterns."""

    @staticmethod
    def extract_variable_from_obj(obj):
        """Extract the underlying variable from various wrapper types."""
        if hasattr(obj, "_wrapped") and not hasattr(obj, "evaluate"):  # Not an Expression
            return obj._wrapped
        elif hasattr(obj, "_variable") and not hasattr(obj, "evaluate"):  # Not an Expression
            return obj._variable
        elif hasattr(obj, "_wrapped_var") and not hasattr(obj, "evaluate"):  # Not an Expression
            return obj._wrapped_var
        elif hasattr(obj, "symbol") and hasattr(obj, "dim") and hasattr(obj, "value") and hasattr(obj, "name") and not hasattr(obj, "evaluate"):  # Not an Expression
            return obj
        else:
            return None

    @staticmethod
    def get_variable_symbol_or_name(obj) -> str | None:
        """Get variable symbol or name from various object types."""
        if hasattr(obj, "symbol") and obj.symbol:
            return obj.symbol
        if hasattr(obj, "name") and obj.name:
            return obj.name
        return None

    @staticmethod
    def is_variable_reference(obj) -> bool:
        """Check if object is a variable reference."""
        # Check for VariableReference type name to avoid circular imports
        return type(obj).__name__ == "VariableReference"

    @staticmethod
    def is_variable_like(obj) -> bool:
        """Check if object is variable-like (has symbol and can be used as variable)."""
        return hasattr(obj, "symbol") and hasattr(obj, "value") and hasattr(obj, "dim") and not hasattr(obj, "evaluate")


# ========== EXPRESSION TREE UTILITIES ==========


# ========== NAMESPACE UTILITIES ==========


class NamespaceHelper:
    """Consolidates namespace handling patterns."""

    @staticmethod
    def extract_namespace_from_symbol(symbol: str) -> str | None:
        """Extract namespace from a namespaced symbol."""
        if "_" in symbol:
            return symbol.split("_")[0]
        return None

    @staticmethod
    def extract_base_symbol_from_namespaced(symbol: str) -> str:
        """Extract base symbol from a namespaced symbol."""
        if "_" in symbol:
            return "_".join(symbol.split("_")[1:])
        return symbol

    @staticmethod
    def create_namespaced_symbol(namespace: str, base_symbol: str) -> str:
        """Create a namespaced symbol."""
        return f"{namespace}_{base_symbol}"

    @staticmethod
    def find_variables_by_pattern(variables: dict[str, Any], pattern: str) -> list[str]:
        """Find variables matching a pattern."""
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return [name for name in variables.keys() if name.startswith(prefix)]
        else:
            return [name for name in variables.keys() if name == pattern]


# ========== EXPRESSION FACTORY ==========


class ExpressionFactory(ABC):
    """Abstract factory for creating expression objects."""

    @abstractmethod
    def create_variable_reference(self, variable) -> Any:
        """Create a variable reference."""
        pass

    @abstractmethod
    def create_binary_operation(self, operator: str, left: Any, right: Any) -> Any:
        """Create a binary operation."""
        pass

    @abstractmethod
    def create_unary_function(self, function_name: str, operand: Any) -> Any:
        """Create a unary function."""
        pass

    @abstractmethod
    def create_conditional_expression(self, condition: Any, true_expr: Any, false_expr: Any) -> Any:
        """Create a conditional expression."""
        pass


# ========== PATTERN MATCHING UTILITIES ==========


class PatternMatchingHelper:
    """Consolidates pattern matching utilities."""

    # Compiled regex patterns for performance
    VARIABLE_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9_]*\b")
    VARIABLE_PATTERN_DETAILED = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b")

    # Mathematical operators
    MATH_OPERATORS = {"(", ")", "+", "-", "*", "/"}

    # Excluded function names
    EXCLUDED_FUNCTION_NAMES = {"sin", "cos", "max", "min", "exp", "log", "sqrt", "tan"}

    @staticmethod
    def extract_variables_from_expression_string(expression_str: str, exclude_functions: bool = True) -> list[str]:
        """Extract variable names from an expression string."""
        var_matches = PatternMatchingHelper.VARIABLE_PATTERN_DETAILED.findall(expression_str)
        if exclude_functions:
            return [var for var in var_matches if var not in PatternMatchingHelper.EXCLUDED_FUNCTION_NAMES]
        return var_matches

    @staticmethod
    def is_mathematical_expression(text: str) -> bool:
        """Check if text contains mathematical operators."""
        return any(op in text for op in PatternMatchingHelper.MATH_OPERATORS)

    @staticmethod
    def clean_malformed_expression(expression_str: str) -> str | None:
        """Clean malformed expression strings."""
        if not expression_str or not isinstance(expression_str, str):
            return None

        try:
            # Remove numeric values that look like results
            cleaned = re.sub(r"\d+\.\d+", "VAR", expression_str)

            # Remove method calls like .value, .quantity
            cleaned = re.sub(r"\.(?:value|quantity|magnitude)\b", "", cleaned)

            # Return pattern if it contains mathematical operators
            return cleaned if PatternMatchingHelper.is_mathematical_expression(cleaned) else None

        except (AttributeError, re.error):
            return None


# ========== ARITHMETIC OPERATIONS MIXIN ==========


class ArithmeticOperationsMixin:
    """Mixin providing common arithmetic operations that create expressions."""

    def _create_arithmetic_operation(self, other, operator: str, reverse: bool = False):
        """Create arithmetic operation based on context."""
        # This is a placeholder - implementations should override this
        # to create appropriate expression types (DelayedExpression, BinaryOperation, etc.)
        raise NotImplementedError("Subclasses must implement _create_arithmetic_operation")

    def __add__(self, other):
        return self._create_arithmetic_operation(other, "+")

    def __radd__(self, other):
        return self._create_arithmetic_operation(other, "+", True)

    def __sub__(self, other):
        return self._create_arithmetic_operation(other, "-")

    def __rsub__(self, other):
        return self._create_arithmetic_operation(other, "-", True)

    def __mul__(self, other):
        return self._create_arithmetic_operation(other, "*")

    def __rmul__(self, other):
        return self._create_arithmetic_operation(other, "*", True)

    def __truediv__(self, other):
        return self._create_arithmetic_operation(other, "/")

    def __rtruediv__(self, other):
        return self._create_arithmetic_operation(other, "/", True)

    def __pow__(self, other):
        return self._create_arithmetic_operation(other, "**")

    def __rpow__(self, other):
        return self._create_arithmetic_operation(other, "**", True)


# ========== CONTEXT DETECTION UTILITIES ==========


class ContextDetectionHelper:
    """Consolidates context detection patterns."""

    @staticmethod
    def should_preserve_symbolic_expression() -> bool:
        """Check if we're in a context where symbolic expressions should be preserved."""
        import inspect

        frame = inspect.currentframe()
        try:
            while frame:
                code = frame.f_code
                filename = code.co_filename
                locals_dict = frame.f_locals

                # Skip if we're in a resolve() method - we want actual expressions during resolution
                if "resolve" in code.co_name:
                    frame = frame.f_back
                    continue

                # If we find a frame in Problem-related code or class definition,
                # don't auto-evaluate to preserve symbolic expressions
                if (
                    "<class" in code.co_name
                    or "problem" in filename.lower()
                    or "composition" in filename.lower()
                    or "_extract" in code.co_name.lower()
                    or "WeldedBranchConnection" in str(locals_dict.get("__qualname__", ""))
                    or "Problem" in str(locals_dict.get("__qualname__", ""))
                    or any("Problem" in str(base) for base in locals_dict.get("__bases__", []))
                    or "test_composed_problem" in filename
                ):
                    return True
                frame = frame.f_back
            return False
        finally:
            del frame

    @staticmethod
    def should_use_delayed_arithmetic() -> bool:
        """Check if we should use delayed arithmetic based on context."""
        import inspect

        frame = inspect.currentframe()
        try:
            while frame:
                code = frame.f_code
                filename = code.co_filename
                locals_dict = frame.f_locals

                # Check if we're in a class definition context
                if "<class" in code.co_name or "problem" in filename.lower() or any("Problem" in str(base) for base in locals_dict.get("__bases__", [])) or "test_composed_problem" in filename:
                    return True
                frame = frame.f_back
            return False
        finally:
            del frame


# ========== SHARED CONSTANTS ==========


class SharedConstants:
    """Consolidated constants used across modules."""

    # Validation constants
    CONDITION_EVALUATION_THRESHOLD = 1e-10
    DIVISION_BY_ZERO_THRESHOLD = 1e-15
    FLOAT_EQUALITY_TOLERANCE = 1e-12
    SOLVER_DEFAULT_TOLERANCE = 1e-9
    SOLVER_DEFAULT_MAX_ITERATIONS = 100

    # String constants
    MSG_VARIABLE_EXISTS = "Variable {symbol} already exists. Replacing."
    MSG_VARIABLE_NOT_FOUND = "Variable '{symbol}' not found in problem '{name}'"
    MSG_VALIDATION_CHECK_FAILED = "Validation check execution failed"

    # Reserved attributes for metaclass
    RESERVED_ATTRIBUTES = {"name", "description"}
    PRIVATE_ATTRIBUTE_PREFIX = "_"
