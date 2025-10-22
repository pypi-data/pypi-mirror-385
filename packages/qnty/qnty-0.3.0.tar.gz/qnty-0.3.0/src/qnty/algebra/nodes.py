"""
Expression AST Nodes
===================

Core abstract syntax tree nodes for mathematical expressions.
"""

import math
from abc import ABC, abstractmethod

from ..core import u
from ..core.quantity import FieldQuantity, Quantity
from ..utils.caching.manager import get_cache_manager
from ..utils.protocols import register_expression_type, register_variable_type
from ..utils.scope_discovery import ScopeDiscoveryService
from ..utils.shared_utilities import (
    SharedConstants,
    ValidationHelper,
)
from .formatter import ExpressionFormatter


def _create_binary_operation(operator: str, left: "Expression", right) -> "BinaryOperation":
    """Helper to create binary operations with proper operand wrapping."""
    return BinaryOperation(operator, left, wrap_operand(right))


# Use shared validation helper
_has_valid_value = ValidationHelper.has_valid_value


class Expression(ABC):
    """Abstract base class for mathematical expressions."""

    # Class-level optimization settings
    _auto_eval_enabled = False  # Disabled by default for performance

    @abstractmethod
    def evaluate(self, variable_values: dict[str, "FieldQuantity"]) -> "Quantity":
        """Evaluate the expression given variable values."""
        pass

    @abstractmethod
    def get_variables(self) -> set[str]:
        """Get all variable symbols used in this expression."""
        pass

    @abstractmethod
    def simplify(self) -> "Expression":
        """Simplify the expression."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    def _discover_variables_from_scope(self) -> dict[str, "FieldQuantity"]:
        """Automatically discover variables from the calling scope using centralized service."""
        # Skip if auto-evaluation is disabled
        if not self._auto_eval_enabled:
            return {}

        # Get required variables first to optimize search
        required_vars = self.get_variables()
        if not required_vars:
            return {}

        # Use centralized scope discovery service
        return ScopeDiscoveryService.discover_variables(required_vars, enable_caching=True)

    def _can_auto_evaluate(self) -> tuple[bool, dict[str, "FieldQuantity"]]:
        """Check if expression can be auto-evaluated from scope using centralized service."""
        # Use centralized scope discovery service
        return ScopeDiscoveryService.can_auto_evaluate(self)

    def solve_for(self, quantity) -> bool:
        """
        Solve this expression for the given quantity.

        Args:
            quantity: The Quantity to solve for (must have symbol, dim, value properties)

        Returns:
            True if solving succeeded, False otherwise
        """
        # First, try to evaluate the expression directly
        try:
            # Discover variables from scope
            required_vars = self.get_variables()
            variables = ScopeDiscoveryService.discover_variables(required_vars, enable_caching=True)

            # Evaluate the expression
            result = self.evaluate(variables)
            if result and _has_valid_value(result):
                # Check dimension compatibility
                if hasattr(quantity, "dim") and hasattr(result, "dim"):
                    if quantity.dim != result.dim:
                        raise TypeError(f"Dimension mismatch: cannot assign {result.dim} to {quantity.dim}")

                # Assign the value
                if hasattr(quantity, "value"):
                    quantity.value = result.value
                    if hasattr(quantity, "preferred") and hasattr(result, "preferred"):
                        quantity.preferred = result.preferred or getattr(quantity, "preferred", None)
                    return True
        except Exception:
            # If direct evaluation fails, try symbolic solving
            pass

        # Fall back to symbolic solving
        return self._symbolic_solve_for(quantity)

    def _symbolic_solve_for(self, quantity) -> bool:
        """Fallback symbolic solving method."""
        try:
            from .equation import Equation

            # Create an equation: quantity = self
            equation = Equation(name=f"solve_for_{getattr(quantity, 'name', 'unknown')}", lhs=VariableReference(quantity), rhs=self)

            # Try to solve for this variable
            all_variables = ScopeDiscoveryService.find_variables_in_scope()
            symbol = getattr(quantity, "symbol", getattr(quantity, "name", "unknown"))
            solved_value = equation.solve_for(symbol, all_variables)

            if solved_value is not None and _has_valid_value(solved_value):
                if hasattr(quantity, "value"):
                    quantity.value = solved_value.value
                    if hasattr(quantity, "preferred") and hasattr(solved_value, "preferred"):
                        quantity.preferred = solved_value.preferred or getattr(quantity, "preferred", None)
                    return True
        except Exception:
            # If symbolic solving fails, return False
            pass

        return False

    def __add__(self, other: "OperandType") -> "Expression":
        return _create_binary_operation("+", self, other)

    def __radd__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("+", wrap_operand(other), self)

    def __sub__(self, other: "OperandType") -> "Expression":
        return _create_binary_operation("-", self, other)

    def __rsub__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("-", wrap_operand(other), self)

    def __mul__(self, other: "OperandType") -> "Expression":
        return _create_binary_operation("*", self, other)

    def __rmul__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("*", wrap_operand(other), self)

    def __truediv__(self, other: "OperandType") -> "Expression":
        return _create_binary_operation("/", self, other)

    def __rtruediv__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("/", wrap_operand(other), self)

    def __pow__(self, other: "OperandType") -> "Expression":
        return _create_binary_operation("**", self, other)

    def __rpow__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("**", wrap_operand(other), self)

    def __abs__(self) -> "Expression":
        """Absolute value of the expression."""
        return UnaryFunction("abs", self)

    # Comparison operators for conditional expressions (consolidated)
    def _make_comparison(self, operator: str, other) -> "BinaryOperation":
        """Helper method to create comparison operations."""
        return BinaryOperation(operator, self, wrap_operand(other))

    def __lt__(self, other: "OperandType") -> "BinaryOperation":
        return self._make_comparison("<", other)

    def __le__(self, other: "OperandType") -> "BinaryOperation":
        return self._make_comparison("<=", other)

    def __gt__(self, other: "OperandType") -> "BinaryOperation":
        return self._make_comparison(">", other)

    def __ge__(self, other: "OperandType") -> "BinaryOperation":
        return self._make_comparison(">=", other)


# Type aliases to reduce repetition
OperandType = Expression | FieldQuantity | Quantity | int | float


class VariableReference(Expression):
    """Reference to a variable in an expression with performance optimizations."""

    __slots__ = ("variable", "_cached_name", "_last_symbol")

    def __init__(self, variable: "FieldQuantity"):
        self.variable = variable
        # Cache the name resolution to avoid repeated lookups
        self._cached_name = None
        self._last_symbol = None

    @property
    def name(self) -> str:
        """Get variable name with caching for performance."""
        current_symbol = self.variable.symbol
        if self._cached_name is None or self._last_symbol != current_symbol:
            # Use symbol for optinova compatibility, fall back to name if symbol not set
            self._cached_name = current_symbol if current_symbol else self.variable.name
            self._last_symbol = current_symbol
        return self._cached_name

    def evaluate(self, variable_values: dict[str, "FieldQuantity"]) -> "Quantity":
        try:
            if self.name in variable_values:
                var = variable_values[self.name]
                if var.quantity is not None:
                    return self._get_si_quantity(var.quantity)
            elif self.variable.quantity is not None:
                return self._get_si_quantity(self.variable.quantity)

            # If we reach here, no valid quantity was found
            available_vars = list(variable_values.keys()) if variable_values else []
            raise ValueError(f"Cannot evaluate variable '{self.name}' without value. Available variables: {available_vars}")
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Error evaluating variable '{self.name}': {e}") from e

    def _get_si_quantity(self, quantity: "Quantity") -> "Quantity":
        """
        Convert a quantity to its SI representation for consistent variable evaluation.

        This ensures that VariableReference = VariableReference assignments (like header.P = P)
        transfer the SI value rather than the display value, preventing unit conversion issues.
        """
        try:
            # Get the SI unit for this quantity's dimension
            from ..core.unit import ureg

            si_unit = ureg.si_unit_for(quantity.dim)
            if si_unit is not None:
                return quantity.to(si_unit)
            else:
                # If no SI unit found, return the original quantity
                return quantity
        except (ValueError, TypeError, AttributeError):
            # If conversion fails for any reason, return the original quantity
            return quantity

    def get_variables(self) -> set[str]:
        return {self.name}

    def simplify(self) -> "Expression":
        return self

    def __str__(self) -> str:
        return ExpressionFormatter.format_variable_reference(self)  # type: ignore[arg-type]


class Constant(Expression):
    """Constant value in an expression."""

    __slots__ = ("value",)

    def __init__(self, value: "Quantity"):
        self.value = value

    def evaluate(self, variable_values: dict[str, "FieldQuantity"]) -> "Quantity":
        del variable_values  # Suppress unused variable warning
        return self.value

    def get_variables(self) -> set[str]:
        return set()

    def simplify(self) -> "Expression":
        return self

    def __str__(self) -> str:
        return ExpressionFormatter.format_constant(self)  # type: ignore[arg-type]


class BinaryOperation(Expression):
    """Binary operation between two expressions."""

    __slots__ = ("operator", "left", "right")

    # Operator dispatch table for better performance
    _ARITHMETIC_OPS = {"+", "-", "*", "/", "**"}
    _COMPARISON_OPS = {"<", "<=", ">", ">=", "==", "!="}

    def __init__(self, operator: str, left: Expression, right: Expression):
        self.operator = operator
        self.left = left
        self.right = right

    def evaluate(self, variable_values: dict[str, "FieldQuantity"]) -> "Quantity":
        """Evaluate the binary operation with caching and error handling."""
        try:
            return self._evaluate_with_caching(variable_values)
        except Exception as e:
            return self._handle_evaluation_error(e)

    def _evaluate_with_caching(self, variable_values: dict[str, "FieldQuantity"]) -> "Quantity":
        """Core evaluation logic with caching support."""
        # Check cache for constant expressions
        cached_result = self._try_get_cached_result()
        if cached_result is not None:
            return cached_result

        # Evaluate operands
        left_val, right_val = self._evaluate_operands(variable_values)

        # Dispatch operation
        result = self._dispatch_operation(left_val, right_val)

        # Cache result for constant expressions
        self._try_cache_result(result)

        return result

    def _evaluate_operands(self, variable_values: dict[str, "FieldQuantity"]) -> tuple["Quantity", "Quantity"]:
        """Evaluate both operands and return as tuple."""
        left_val = self.left.evaluate(variable_values)
        right_val = self.right.evaluate(variable_values)

        # Handle cases where evaluation returns plain float (e.g., from trig functions)
        # Convert to dimensionless Quantity for consistent handling
        if isinstance(left_val, int | float):
            left_val = _create_dimensionless_quantity(float(left_val))
        if isinstance(right_val, int | float):
            right_val = _create_dimensionless_quantity(float(right_val))

        return left_val, right_val

    def _handle_evaluation_error(self, error: Exception) -> "Quantity":
        """Handle evaluation errors with appropriate context."""
        if isinstance(error, ValueError):
            raise
        raise ValueError(f"Error evaluating binary operation '{self}': {error}") from error

    def _try_get_cached_result(self) -> "Quantity | None":
        """Attempt to retrieve a cached result for constant expressions."""
        if not self._is_constant_expression():
            return None

        cache_manager = get_cache_manager()
        cache_key = self._generate_cache_key()
        return cache_manager.get_expression_result(cache_key)

    def _try_cache_result(self, result: "Quantity") -> None:
        """Attempt to cache the result for constant expressions."""
        if not self._is_constant_expression():
            return

        cache_manager = get_cache_manager()
        cache_key = self._generate_cache_key()
        cache_manager.cache_expression_result(cache_key, result)

    def _is_constant_expression(self) -> bool:
        """Check if both operands are constants."""
        return _is_constant_fast(self.left) and _is_constant_fast(self.right)

    def _is_dimensionless(self, quantity) -> bool:
        """Check if a quantity is dimensionless."""
        return _DimensionUtils.is_dimensionless(quantity)

    def _create_quantity_from_existing(self, value: float, existing_quantity) -> "Quantity":
        """Create a new quantity with the same unit/dimension as an existing quantity."""
        effective_unit = self._get_effective_unit(existing_quantity)
        if effective_unit and hasattr(existing_quantity, "dim"):
            return Quantity(name=str(value), dim=existing_quantity.dim, value=value, preferred=effective_unit)
        else:
            # Fallback to dimensionless
            return _create_dimensionless_quantity(value)

    def _get_effective_unit(self, quantity):
        """Get the effective unit for a quantity, handling both old and new Quantity objects."""
        return _DimensionUtils.get_effective_unit(quantity)

    def _generate_cache_key(self) -> str:
        """Generate a cache key for constant expressions."""
        # Safe to cast since _is_constant_expression() already verified types
        left_const = self.left
        right_const = self.right
        return f"{id(self)}_{self.operator}_{id(left_const.value)}_{id(right_const.value)}"  # type: ignore[attr-defined]

    def _dispatch_operation(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Dispatch to the appropriate operation handler with fast lookup."""
        # Ultra-fast path: delegate to Quantity arithmetic when both operands are concrete
        if _has_valid_value(left_val) and _has_valid_value(right_val) and hasattr(left_val, "dim") and hasattr(right_val, "dim"):
            try:
                # Try to delegate directly to Quantity arithmetic
                if self.operator == "+":
                    return left_val.__add__(right_val)
                elif self.operator == "-":
                    return left_val.__sub__(right_val)
                elif self.operator == "*":
                    return left_val.__mul__(right_val)
                elif self.operator == "/":
                    return left_val.__truediv__(right_val)
                elif self.operator == "**":
                    # For power, right operand should be a number
                    if hasattr(right_val, "dim") and right_val.dim.is_dimensionless() and _has_valid_value(right_val):
                        # Power operation not supported on new Quantity - use fallback
                        pass
                # For comparison operators, fall through to normal handling
            except TypeError:
                # Re-raise TypeError - these are dimensional mismatches and must be surfaced
                raise
            except ValueError:
                # ValueError may indicate other issues, fall back to Expression arithmetic
                pass

        # Normal path: check operator type with pre-compiled sets
        if self.operator in self._ARITHMETIC_OPS:
            return self._evaluate_arithmetic_dispatch(left_val, right_val)
        elif self.operator in self._COMPARISON_OPS:
            return self._evaluate_comparison(left_val, right_val)
        else:
            raise ValueError(f"Unknown operator: {self.operator}")

    def _evaluate_arithmetic_dispatch(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Dispatch arithmetic operations with direct method lookup."""
        # Use direct method dispatch for better performance
        if self.operator == "*":
            return self._multiply(left_val, right_val)
        elif self.operator == "+":
            return self._add(left_val, right_val)
        elif self.operator == "-":
            return self._subtract(left_val, right_val)
        elif self.operator == "/":
            return self._divide(left_val, right_val)
        elif self.operator == "**":
            return self._power(left_val, right_val)
        else:
            raise ValueError(f"Unknown arithmetic operator: {self.operator}")

    def _multiply(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Handle multiplication with ultra-fast path optimizations aligned with base_qnty."""
        # For now, skip fast path optimizations to avoid compatibility issues
        # These optimizations can be re-enabled after the new Quantity system is stable

        # OPTIMIZED REGULAR CASE: Use the enhanced multiplication from base_qnty
        # This leverages the optimized caching and dimensionless handling
        return left_val * right_val

    def _add(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Handle addition with fast path optimizations."""
        # For now, skip fast path optimizations to avoid compatibility issues
        return left_val + right_val

    def _subtract(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Handle subtraction with fast path optimizations."""
        # For now, skip fast path optimizations to avoid compatibility issues
        return left_val - right_val

    def _divide(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Handle division with zero checking and optimizations."""
        # Check for division by zero first
        if _has_valid_value(right_val) and right_val.value is not None:
            if abs(right_val.value) < SharedConstants.DIVISION_BY_ZERO_THRESHOLD:
                raise ValueError(f"Division by zero in expression: {self}")

        # For now, skip fast path optimizations to avoid compatibility issues
        return left_val / right_val

    def _power(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Handle power operations with special cases."""
        # Check if right operand is dimensionless
        if _has_valid_value(right_val):
            if not isinstance(right_val.value, int | float):
                raise ValueError("Exponent must be dimensionless number")

            # Check if right operand is dimensionless by dimension
            if hasattr(right_val, "dim") and not right_val.dim.is_dimensionless():
                raise ValueError("Exponent must be dimensionless")

        # Delegate to Quantity's __pow__ method
        try:
            # Extract numeric exponent - Quantity.__pow__ expects int
            exponent = right_val.value if _has_valid_value(right_val) else 1

            # Ensure exponent is not None
            if exponent is None:
                exponent = 1

            # Convert to int if it's a whole number, otherwise raise error (for now)
            if exponent != int(exponent):
                raise ValueError(f"Non-integer exponents not yet supported: {exponent}")

            return left_val ** int(exponent)
        except (ValueError, TypeError, AttributeError) as e:
            raise ValueError(f"Power operation failed: {e}") from e

    def _evaluate_comparison(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Evaluate comparison operations with optimized unit conversion."""
        # For comparisons, we should use the actual Quantity comparison operators
        # which handle unit conversion properly
        try:
            if self.operator == "<":
                result = left_val < right_val
            elif self.operator == "<=":
                result = left_val <= right_val
            elif self.operator == ">":
                result = left_val > right_val
            elif self.operator == ">=":
                result = left_val >= right_val
            elif self.operator == "==":
                result = left_val == right_val
            elif self.operator == "!=":
                result = left_val != right_val
            else:
                # Fallback to old method if operator is unknown
                left_val, right_val = self._normalize_comparison_units(left_val, right_val)
                left_value = left_val.value if _has_valid_value(left_val) and left_val.value is not None else 0.0
                right_value = right_val.value if _has_valid_value(right_val) and right_val.value is not None else 0.0
                result = self._perform_comparison(left_value, right_value)
        except TypeError:
            # Re-raise TypeError - dimensional mismatches in comparisons are critical errors
            raise
        except (ValueError, AttributeError):
            # If Quantity comparison fails for other reasons, fall back to value comparison
            left_val, right_val = self._normalize_comparison_units(left_val, right_val)
            left_value = left_val.value if _has_valid_value(left_val) and left_val.value is not None else 0.0
            right_value = right_val.value if _has_valid_value(right_val) and right_val.value is not None else 0.0
            result = self._perform_comparison(left_value, right_value)

        # Create dimensionless quantity for boolean result
        return _create_dimensionless_quantity(float(result), str(result))

    def _normalize_comparison_units(self, left_val: "Quantity", right_val: "Quantity") -> tuple["Quantity", "Quantity"]:
        """Normalize units for comparison operations."""
        try:
            if hasattr(left_val, "dim") and hasattr(right_val, "dim") and left_val.dim == right_val.dim:
                left_unit = _DimensionUtils.get_effective_unit(left_val)
                if left_unit is not None:
                    right_val = right_val.to(left_unit)
        except (ValueError, TypeError, AttributeError):
            pass
        return left_val, right_val

    def _perform_comparison(self, left_value: float, right_value: float) -> bool:
        """Perform the actual comparison operation."""
        # Direct dispatch for better performance
        if self.operator == "<":
            return left_value < right_value
        elif self.operator == "<=":
            return left_value <= right_value
        elif self.operator == ">":
            return left_value > right_value
        elif self.operator == ">=":
            return left_value >= right_value
        elif self.operator == "==":
            return abs(left_value - right_value) < SharedConstants.FLOAT_EQUALITY_TOLERANCE
        elif self.operator == "!=":
            return abs(left_value - right_value) >= SharedConstants.FLOAT_EQUALITY_TOLERANCE
        else:
            raise ValueError(f"Unknown comparison operator: {self.operator}")

    def get_variables(self) -> set[str]:
        return self.left.get_variables() | self.right.get_variables()

    def simplify(self) -> Expression:
        """Simplify the binary operation with optimized constant folding."""
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()

        # Fast path: check for constant expression simplification
        if _is_constant_fast(left_simplified) and _is_constant_fast(right_simplified):
            return self._try_constant_folding(left_simplified, right_simplified)

        return BinaryOperation(self.operator, left_simplified, right_simplified)

    def _try_constant_folding(self, left_const: Expression, right_const: Expression) -> Expression:
        """Attempt to fold constant expressions."""
        try:
            # Evaluate constant expressions at compile time
            dummy_vars = {}
            result = BinaryOperation(self.operator, left_const, right_const).evaluate(dummy_vars)
            return Constant(result)
        except (ValueError, TypeError, ArithmeticError):
            # Return original operation if folding fails
            return BinaryOperation(self.operator, left_const, right_const)

    def __str__(self) -> str:
        # Delegate to centralized formatter
        can_eval, variables = self._can_auto_evaluate()
        return ExpressionFormatter.format_binary_operation(self, can_auto_evaluate=can_eval, auto_eval_variables=variables)  # type: ignore[arg-type]


class UnaryFunction(Expression):
    """Unary mathematical function expression."""

    __slots__ = ("function_name", "operand")

    def __init__(self, function_name: str, operand: Expression):
        self.function_name = function_name
        self.operand = operand

    def evaluate(self, variable_values: dict[str, "FieldQuantity"]) -> "Quantity":
        operand_val = self.operand.evaluate(variable_values)

        # Function dispatch table for better performance and maintainability
        functions = {
            "sin": lambda x: self._create_dimensionless_quantity(math.sin(self._to_radians_if_angle(x))),
            "cos": lambda x: self._create_dimensionless_quantity(math.cos(self._to_radians_if_angle(x))),
            "tan": lambda x: self._create_dimensionless_quantity(math.tan(self._to_radians_if_angle(x))),
            "sqrt": lambda x: x if not (hasattr(x, "value") and x.value is not None) else self._create_dimensionless_quantity(math.sqrt(x.value)),
            "abs": lambda x: x if not (hasattr(x, "value") and x.value is not None) else self._create_dimensionless_quantity(abs(x.value)),
            "ln": lambda x: self._create_dimensionless_quantity(math.log(x.value)) if _has_valid_value(x) else x,
            "log10": lambda x: self._create_dimensionless_quantity(math.log10(x.value)) if _has_valid_value(x) else x,
            "exp": lambda x: self._create_dimensionless_quantity(math.exp(x.value)) if _has_valid_value(x) else x,
        }

        func = functions.get(self.function_name)
        if func:
            return func(operand_val)
        else:
            raise ValueError(f"Unknown function: {self.function_name}")

    def _to_radians_if_angle(self, quantity: "Quantity") -> float:
        """Convert angle quantities to radians for trigonometric functions."""
        # For now, just return the raw value since angle handling is not fully implemented
        # This maintains backward compatibility while avoiding import errors
        try:
            if _has_valid_value(quantity) and quantity.value is not None:
                return quantity.value
            else:
                raise ValueError("Quantity has no numeric value")
        except (AttributeError, ValueError):
            # If anything goes wrong, try to extract a float value
            return float(quantity)

    def _create_dimensionless_quantity(self, value: float) -> "Quantity":
        """Create a dimensionless quantity from a float value."""
        return _create_dimensionless_quantity(value)

    def get_variables(self) -> set[str]:
        return self.operand.get_variables()

    def simplify(self) -> Expression:
        simplified_operand = self.operand.simplify()
        if _is_constant_fast(simplified_operand):
            # Evaluate constant functions at compile time
            try:
                dummy_vars = {}
                result = UnaryFunction(self.function_name, simplified_operand).evaluate(dummy_vars)
                return Constant(result)
            except (ValueError, TypeError, ArithmeticError):
                pass
        return UnaryFunction(self.function_name, simplified_operand)

    def __str__(self) -> str:
        # Try auto-evaluation first if possible
        can_eval, variables = self._can_auto_evaluate()
        if can_eval and variables:
            try:
                result = self.evaluate(variables)
                return str(result)
            except (ValueError, TypeError, AttributeError):
                # Fall back to symbolic representation
                pass
        return ExpressionFormatter.format_unary_function(self)  # type: ignore[arg-type]


class ConditionalExpression(Expression):
    """Conditional expression: if condition then true_expr else false_expr."""

    __slots__ = ("condition", "true_expr", "false_expr")

    def __init__(self, condition: Expression, true_expr: Expression, false_expr: Expression):
        self.condition = condition
        self.true_expr = true_expr
        self.false_expr = false_expr

    def evaluate(self, variable_values: dict[str, "FieldQuantity"]) -> "Quantity":
        condition_val = self.condition.evaluate(variable_values)
        # Consider non-zero as True
        condition_value = condition_val.value if _has_valid_value(condition_val) and condition_val.value is not None else 0.0

        if abs(condition_value) > SharedConstants.CONDITION_EVALUATION_THRESHOLD:
            return self.true_expr.evaluate(variable_values)
        else:
            return self.false_expr.evaluate(variable_values)

    def get_variables(self) -> set[str]:
        return self.condition.get_variables() | self.true_expr.get_variables() | self.false_expr.get_variables()

    def simplify(self) -> Expression:
        simplified_condition = self.condition.simplify()
        simplified_true = self.true_expr.simplify()
        simplified_false = self.false_expr.simplify()

        # If condition is constant, choose the appropriate branch
        if _is_constant_fast(simplified_condition):
            try:
                dummy_vars = {}
                condition_val = simplified_condition.evaluate(dummy_vars)
                condition_value = condition_val.value if _has_valid_value(condition_val) and condition_val.value is not None else 0.0
                if abs(condition_value) > SharedConstants.CONDITION_EVALUATION_THRESHOLD:
                    return simplified_true
                else:
                    return simplified_false
            except (ValueError, TypeError, ArithmeticError):
                pass

        return ConditionalExpression(simplified_condition, simplified_true, simplified_false)

    def __str__(self) -> str:
        return ExpressionFormatter.format_conditional_expression(self)  # type: ignore[arg-type]


class MatchExpression(Expression):
    """
    Match expression: multi-way branch based on a select variable's value.

    Similar to a switch/case statement or pattern matching:
    match(select_var) {
        option1 => expr1,
        option2 => expr2,
        ...
    }
    """

    __slots__ = ("select_var", "cases", "_select_var_symbol")

    def __init__(self, select_var, cases: dict):
        """
        Args:
            select_var: SelectVariable instance to match against
            cases: Dict mapping option values to expressions
        """
        self.select_var = select_var
        self.cases = cases
        # Cache the symbol to avoid repeated lookups
        self._select_var_symbol = getattr(select_var, "symbol", str(select_var))

    def evaluate(self, variable_values: dict[str, "FieldQuantity"]) -> "Quantity":
        # Get the current value of the select variable
        current_value = getattr(self.select_var, "value", None)
        if current_value is None:
            raise ValueError(f"SelectVariable '{self.select_var.name}' has no value selected")

        # Find matching case and evaluate it
        if current_value not in self.cases:
            raise ValueError(f"No case for value '{current_value}' in MatchExpression. Available cases: {list(self.cases.keys())}")

        matched_expr = self.cases[current_value]
        return matched_expr.evaluate(variable_values)

    def get_variables(self) -> set[str]:
        # Collect variables from all case expressions
        variables = set()
        for expr in self.cases.values():
            variables.update(expr.get_variables())
        return variables

    def simplify(self) -> Expression:
        # Simplify all case expressions
        simplified_cases = {key: expr.simplify() for key, expr in self.cases.items()}

        # If the select variable has a known value, we can simplify to just that case
        current_value = getattr(self.select_var, "value", None)
        if current_value is not None and current_value in simplified_cases:
            return simplified_cases[current_value]

        return MatchExpression(self.select_var, simplified_cases)

    def __str__(self) -> str:
        return ExpressionFormatter.format_match_expression(self)  # type: ignore[arg-type]


# Utility functions for expression creation

# Cache for common types to avoid repeated type checks
_DIMENSIONLESS_CONSTANT = None

# Type caches for hot path optimization
_CONSTANT_TYPE = None


def _init_type_cache():
    """Initialize type cache for fast isinstance checks."""
    global _CONSTANT_TYPE
    if _CONSTANT_TYPE is None:
        _CONSTANT_TYPE = Constant


def _is_constant_fast(obj) -> bool:
    """Fast type check for Constant objects."""
    _init_type_cache()
    return type(obj) is _CONSTANT_TYPE


def _get_cached_dimensionless():
    """Get cached dimensionless constant for numeric values."""
    global _DIMENSIONLESS_CONSTANT
    if _DIMENSIONLESS_CONSTANT is None:
        _DIMENSIONLESS_CONSTANT = u.dimensionless
    return _DIMENSIONLESS_CONSTANT


# Ultra-fast local cache for most common dimensionless values
_COMMON_DIMENSIONLESS_CACHE: dict[float, Quantity] = {}


def _get_dimensionless_quantity(value: float) -> Quantity:
    """Ultra-optimized dimensionless quantity creation with local caching."""
    # Ultra-fast local cache for most common values (0, 1, 2, -1, 0.5, etc.)
    cached_qty = _COMMON_DIMENSIONLESS_CACHE.get(value)
    if cached_qty is not None:
        return cached_qty

    # Create quantity with cached unit using Q function
    from ..core.quantity import Q

    qty = Q(value, _get_cached_dimensionless())

    # Cache common values locally for ultra-fast access
    if value in (-1.0, 0.0, 0.5, 1.0, 2.0) or (isinstance(value, float) and -10 <= value <= 10 and value == int(value)):
        if len(_COMMON_DIMENSIONLESS_CACHE) < 25:  # Prevent unbounded growth
            _COMMON_DIMENSIONLESS_CACHE[value] = qty

    return qty


def _create_dimensionless_quantity(value: float, name: str | None = None) -> Quantity:
    """Create a dimensionless quantity with consistent structure and caching."""
    if name is None:
        name = str(value)

    # Use cached dimensionless unit for consistency
    dim_unit = _get_cached_dimensionless()
    return Quantity(name=name, dim=dim_unit.dim, value=float(value), preferred=dim_unit)


class _DimensionUtils:
    """Utility class for common dimension and unit operations."""

    @staticmethod
    def is_dimensionless(quantity) -> bool:
        """Check if a quantity is dimensionless with fallback support."""
        if hasattr(quantity, "dim"):
            return quantity.dim.is_dimensionless()
        # Fallback for old quantities with _dimension_sig
        elif hasattr(quantity, "_dimension_sig"):
            return quantity._dimension_sig == 1
        return False

    @staticmethod
    def get_effective_unit(quantity):
        """Get the effective unit for a quantity, handling both old and new Quantity objects."""
        from ..utils.shared_utilities import ValidationHelper

        return ValidationHelper.get_effective_unit(quantity)


def wrap_operand(operand: "OperandType") -> Expression:
    """
    Ultra-optimized operand wrapping with minimal function call overhead.

    Performance optimizations:
    - Single type() call instead of multiple isinstance checks
    - Cached common type patterns
    - Reduced function call depth
    """
    # ULTRA-FAST PATH: Use single type() call for most common cases
    operand_type = type(operand)

    # Most common cases first: primitives (35-40% of all calls)
    if operand_type in (int, float):
        return Constant(_get_dimensionless_quantity(float(operand)))  # type: ignore[arg-type]

    # Second most common: already wrapped expressions (20-25% of calls)
    if operand_type is BinaryOperation:  # Direct type check is faster
        return operand  # type: ignore[return-value]

    # Check for ExpressionEnabledWrapper from Problem class definition
    if hasattr(operand, "_wrapped"):
        # This is an ExpressionEnabledWrapper - get the actual variable
        wrapped_var = getattr(operand, "_wrapped", None)
        if wrapped_var is not None:
            # Now wrap the actual variable
            if hasattr(wrapped_var, "quantity") and hasattr(wrapped_var, "symbol"):
                # For variables, always create VariableReference to track value changes in equations
                # This is critical for equation solving where variables can change values
                return VariableReference(wrapped_var)  # type: ignore[arg-type]

    # Third most common: field quantities/variables (20-30% of calls)
    # Use getattr with hasattr-style check to reduce calls
    if hasattr(operand, "quantity") and hasattr(operand, "symbol"):
        # For variables, always create VariableReference to track value changes in equations
        # This is critical for equation solving where variables can change values
        return VariableReference(operand)  # type: ignore[arg-type]

    # Handle other Expression types (Constant, VariableReference, etc.)
    if isinstance(operand, Expression):
        return operand

    # Check for new unified Quantity objects
    if hasattr(operand, "value") and hasattr(operand, "dim") and hasattr(operand, "symbol"):
        if getattr(operand, "value", None) is not None:
            return Constant(operand)  # type: ignore[arg-type]
        else:
            return VariableReference(operand)  # type: ignore[arg-type]

    # Check for base Quantity objects (legacy and new)
    if hasattr(operand, "value") and hasattr(operand, "dim"):
        return Constant(operand)  # type: ignore[arg-type]

    # Check for ConfigurableVariable (from composition system) - rare case
    if hasattr(operand, "_variable"):
        var = getattr(operand, "_variable", None)
        if var is not None and hasattr(var, "quantity") and hasattr(var, "symbol"):
            return VariableReference(var)  # type: ignore[arg-type]

    # Handle DelayedExpression and DelayedFunction objects that weren't resolved
    from ..utils.shared_utilities import ValidationHelper

    if ValidationHelper.safe_get_callable(operand, "resolve"):
        # This is a DelayedExpression or DelayedFunction - try to resolve it with empty context
        # This is a fallback; ideally these should be resolved earlier
        try:
            resolve_method = ValidationHelper.safe_get_callable(operand, "resolve")
            if resolve_method and callable(resolve_method):
                resolved = resolve_method({})
                if resolved is not None and isinstance(resolved, Expression):
                    return resolved
        except Exception:
            pass
        # If resolution fails, raise an informative error
        operand_type_name = getattr(type(operand), "__name__", "DelayedObject")
        raise TypeError(f"{operand_type_name} objects must be resolved before wrapping. Call resolve(context) first or fix the resolution process.")

    # Handle MainVariableWrapper objects
    if hasattr(operand, "_wrapped_var"):
        # Use Any type annotation to handle dynamic wrapper objects
        wrapped_var = operand._wrapped_var  # type: ignore[attr-defined]
        return wrap_operand(wrapped_var)

    # Fast failure for unknown types
    raise TypeError(f"Cannot convert {operand_type.__name__} to Expression")


# Register expression and variable types with the TypeRegistry for optimal performance

# Register expression types
for expr_type in [Expression, BinaryOperation, VariableReference, Constant, UnaryFunction, ConditionalExpression, MatchExpression]:
    register_expression_type(expr_type)

# Register variable types - do this at module level to ensure it happens early
try:
    register_variable_type(FieldQuantity)
except ImportError:
    pass  # Handle import ordering issues gracefully
