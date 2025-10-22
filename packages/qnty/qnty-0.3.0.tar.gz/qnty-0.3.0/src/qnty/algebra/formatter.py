"""
Expression String Formatting System
===================================

Centralized formatting logic for mathematical expressions with proper
operator precedence handling and readable output generation.
"""

from __future__ import annotations

from typing import Any


class ExpressionFormatter:
    """
    Handles string representation of expressions with proper precedence rules.

    Centralizes complex formatting logic that was previously scattered across
    expression classes, making it easier to maintain and extend.
    """

    # Operator precedence levels (higher number = higher precedence)
    OPERATOR_PRECEDENCE = {
        # Comparison operators (lowest precedence)
        "<": 0,
        "<=": 0,
        ">": 0,
        ">=": 0,
        "==": 0,
        "!=": 0,
        # Arithmetic operators
        "+": 1,
        "-": 1,  # Addition/subtraction
        "*": 2,
        "/": 2,  # Multiplication/division
        "**": 3,  # Exponentiation (highest precedence)
    }

    # Left-associative operators that need special parenthesization
    LEFT_ASSOCIATIVE_SPECIAL = {"-", "/"}

    @staticmethod
    def format_binary_operation(binary_op: Any, can_auto_evaluate: bool = False, auto_eval_variables: dict[str, Any] | None = None) -> str:
        """
        Format binary operation with proper parenthesization.

        Args:
            binary_op: The binary operation to format
            can_auto_evaluate: Whether auto-evaluation should be attempted
            auto_eval_variables: Variables for auto-evaluation

        Returns:
            Formatted string representation
        """
        # Try auto-evaluation first if requested
        if can_auto_evaluate and auto_eval_variables:
            evaluation_result = ExpressionFormatter._try_evaluate(binary_op, auto_eval_variables)
            if evaluation_result is not None:
                return str(evaluation_result)

        # Get string representations of operands
        left_str = str(binary_op.left)
        right_str = str(binary_op.right)

        # Apply parenthesization rules
        left_str = ExpressionFormatter._maybe_parenthesize(binary_op.left, binary_op.operator, left_str, is_right_operand=False)
        right_str = ExpressionFormatter._maybe_parenthesize(binary_op.right, binary_op.operator, right_str, is_right_operand=True)

        return f"{left_str} {binary_op.operator} {right_str}"

    @staticmethod
    def _get_precedence_comparison(expr: Any, operator: str) -> tuple[int, int]:
        """Get expression precedence compared to operator precedence."""
        expr_precedence = ExpressionFormatter._get_expression_precedence(expr)
        operator_precedence = ExpressionFormatter.get_operator_precedence(operator)
        return expr_precedence, operator_precedence

    @staticmethod
    def _maybe_parenthesize(expr: Any, operator: str, expr_str: str, is_right_operand: bool = False) -> str:
        """Add parentheses to operand if needed for precedence and associativity."""
        if not ExpressionFormatter._is_binary_operation(expr):
            return expr_str

        expr_precedence, current_precedence = ExpressionFormatter._get_precedence_comparison(expr, operator)

        if is_right_operand:
            # Right side needs parentheses if:
            # 1. Its precedence is strictly lower, OR
            # 2. Same precedence AND current operator is left-associative (-, /)
            needs_parentheses = expr_precedence < current_precedence or (expr_precedence == current_precedence and operator in ExpressionFormatter.LEFT_ASSOCIATIVE_SPECIAL)
        else:
            # Left side needs parentheses only if its precedence is strictly lower
            needs_parentheses = expr_precedence < current_precedence

        return f"({expr_str})" if needs_parentheses else expr_str

    @staticmethod
    def format_unary_function(func: Any) -> str:
        """Format unary function call."""
        return f"{func.function_name}({func.operand})"

    @staticmethod
    def format_conditional_expression(cond_expr: Any) -> str:
        """Format conditional expression in if-then-else form."""
        return f"if({cond_expr.condition}, {cond_expr.true_expr}, {cond_expr.false_expr})"

    @staticmethod
    def format_match_expression(match_expr: Any) -> str:
        """Format match expression in match-case form."""
        select_var_name = getattr(match_expr.select_var, "name", str(match_expr.select_var))
        cases_str = ", ".join([f"{key}: {expr}" for key, expr in match_expr.cases.items()])
        return f"match({select_var_name}, {{{cases_str}}})"

    @staticmethod
    def format_variable_reference(var_ref: Any) -> str:
        """Format variable reference (just the name)."""
        return var_ref.name

    @staticmethod
    def format_constant(constant: Any) -> str:
        """Format constant value."""
        return str(constant.value)

    @staticmethod
    def get_operator_precedence(operator: str) -> int:
        """Get precedence level for operator."""
        return ExpressionFormatter.OPERATOR_PRECEDENCE.get(operator, 0)

    @staticmethod
    def _try_evaluate(expression: Any, variables: dict[str, Any]) -> Any | None:
        """
        Safely attempt to evaluate an expression.

        Args:
            expression: Expression to evaluate
            variables: Variable context for evaluation

        Returns:
            Evaluation result or None if evaluation failed
        """
        try:
            return expression.evaluate(variables)
        except (KeyError, ValueError, TypeError, ZeroDivisionError, AttributeError):
            # Catch specific exceptions that are expected during evaluation
            return None

    @staticmethod
    def _get_expression_type(expr: Any) -> str:
        """Determine expression type using duck typing."""
        if hasattr(expr, "operator") and hasattr(expr, "left") and hasattr(expr, "right"):
            return "binary_operation"
        elif hasattr(expr, "function_name") and hasattr(expr, "operand"):
            return "unary_function"
        elif hasattr(expr, "condition") and hasattr(expr, "true_expr") and hasattr(expr, "false_expr"):
            return "conditional"
        elif hasattr(expr, "name"):
            return "variable_reference"
        elif hasattr(expr, "value"):
            return "constant"
        else:
            return "unknown"

    @staticmethod
    def _is_binary_operation(expr: Any) -> bool:
        """Check if expression is a binary operation using duck typing."""
        return ExpressionFormatter._get_expression_type(expr) == "binary_operation"

    @staticmethod
    def _get_expression_precedence(expr: Any) -> int:
        """Get precedence of an expression if it's a binary operation."""
        if ExpressionFormatter._is_binary_operation(expr):
            # We know it's a binary operation from the check above, so it has an operator
            binary_op = expr  # type: ignore[assignment]
            return ExpressionFormatter.get_operator_precedence(binary_op.operator)  # type: ignore[attr-defined]
        return 0
