"""
Expression Helper Functions
==========================

Convenience functions for creating mathematical expressions.
"""

from collections.abc import Callable

from ..core.quantity import FieldQuantity, Quantity
from ..utils.shared_utilities import ContextDetectionHelper
from .nodes import BinaryOperation, ConditionalExpression, Expression, UnaryFunction, wrap_operand

# Type aliases for better maintainability
ExpressionOperand = Expression | FieldQuantity | Quantity | int | float
ConditionalOperand = Expression | BinaryOperation


# Use shared context detection
_should_preserve_symbolic_expression = ContextDetectionHelper.should_preserve_symbolic_expression


def _create_unary_function(name: str, docstring: str) -> "Callable[[ExpressionOperand], Expression | Quantity | float]":
    """Factory function for creating unary mathematical functions."""

    def func(expr: ExpressionOperand) -> Expression | Quantity | float:
        # Check if we should preserve symbolic expressions (in class definition context)
        if _should_preserve_symbolic_expression():
            from ..problems.composition import DelayedFunction

            return DelayedFunction(name, expr)

        wrapped_expr = wrap_operand(expr)

        # For known quantities (FieldQnty with known values), check context before auto-evaluating
        if hasattr(expr, "quantity") and getattr(expr, "quantity", None) is not None:
            # No Problem class context found, safe to auto-evaluate
            try:
                unary_func = UnaryFunction(name, wrapped_expr)
                # Use an empty variable dict since we have the quantity directly
                result = unary_func.evaluate({})
                return result
            except (ValueError, TypeError, AttributeError):
                # Fall back to expression if evaluation fails
                pass

        # For unknown variables or expressions, return the UnaryFunction
        return UnaryFunction(name, wrapped_expr)

    func.__name__ = name
    func.__doc__ = docstring
    return func


def _create_comparison_expr(expressions: tuple[ExpressionOperand, ...], comparator: str) -> Expression:
    """Create min/max expression using specified comparator."""
    if len(expressions) < 2:
        raise ValueError(f"{comparator}_expr requires at least 2 arguments")

    wrapped_expressions = [wrap_operand(expr) for expr in expressions]
    result = wrapped_expressions[0]

    for expr in wrapped_expressions[1:]:
        if comparator == "min":
            # min(a, b) = if(a < b, a, b)
            result = cond_expr(result < expr, result, expr)
        else:  # max
            # max(a, b) = if(a > b, a, b)
            result = cond_expr(result > expr, result, expr)

    return result


# Mathematical functions (generated via factory)
sin = _create_unary_function("sin", "Sine function.")
cos = _create_unary_function("cos", "Cosine function.")
tan = _create_unary_function("tan", "Tangent function.")
sqrt = _create_unary_function("sqrt", "Square root function.")
abs_expr = _create_unary_function("abs", "Absolute value function.")
ln = _create_unary_function("ln", "Natural logarithm function.")
log10 = _create_unary_function("log10", "Base-10 logarithm function.")
exp = _create_unary_function("exp", "Exponential function.")


def cond_expr(
    condition: ConditionalOperand,
    true_expr: ExpressionOperand,
    false_expr: ExpressionOperand,
) -> ConditionalExpression | Expression:
    """Conditional expression: if condition then true_expr else false_expr."""
    # Check if we should preserve symbolic expressions (in class definition context)
    if _should_preserve_symbolic_expression():
        from ..problems.composition import DelayedFunction

        return DelayedFunction("cond_expr", condition, true_expr, false_expr)
    wrapped_condition = condition if isinstance(condition, Expression) else condition
    return ConditionalExpression(wrapped_condition, wrap_operand(true_expr), wrap_operand(false_expr))


def _create_expr_function(func_name: str, comparator: str):
    """Factory function to create min/max expression functions."""

    def expr_func(*expressions: ExpressionOperand) -> Expression:
        # Check if we should preserve symbolic expressions (in class definition context)
        if _should_preserve_symbolic_expression():
            from ..problems.composition import DelayedFunction

            return DelayedFunction(func_name, *expressions)
        return _create_comparison_expr(expressions, comparator)

    expr_func.__name__ = func_name
    expr_func.__doc__ = f"{comparator.title()} of multiple expressions."
    return expr_func


min_expr = _create_expr_function("min_expr", "min")
max_expr = _create_expr_function("max_expr", "max")
