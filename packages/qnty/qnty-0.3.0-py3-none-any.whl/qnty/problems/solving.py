"""
Problem solving system with equation reconstruction capabilities.

This module provides the complete solving system including:
- High-level solve orchestration (formerly solving.py)
- Equation reconstruction for malformed expressions (formerly reconstruction.py)
- Expression parsing and rebuilding (formerly expression_parser.py)
- Namespace mapping for variables (formerly namespace_mapper.py)
- Composite expression rebuilding (formerly composite_expression_rebuilder.py)
- Delayed expression resolution (formerly delayed_expression_resolver.py)

All consolidated into a focused solving system.
"""

from __future__ import annotations

import ast
import operator
import re
from logging import Logger
from typing import Any

from ..algebra import BinaryOperation, ConditionalExpression, Constant, Equation, UnaryFunction, VariableReference, cos, sin
from ..algebra import equation as create_equation
from ..core.quantity import Quantity
from ..utils.shared_utilities import (
    PatternMatchingHelper,
    SafeExecutionMixin,
)

# Type aliases for better readability
VariableDict = dict[str, Quantity]
ReconstructionResult = Equation | None
NamespaceMapping = dict[str, str]


class SafeExpressionEvaluator:
    """Safe mathematical expression evaluator using AST instead of eval()."""

    ALLOWED_NODES = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Name,
        ast.Load,
        ast.Store,
        ast.Del,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.LShift,
        ast.RShift,
        ast.BitOr,
        ast.BitXor,
        ast.BitAnd,
        ast.FloorDiv,
        ast.UAdd,
        ast.USub,
        ast.Not,
        ast.Invert,
        ast.Compare,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.Is,
        ast.IsNot,
        ast.In,
        ast.NotIn,
        ast.BoolOp,
        ast.And,
        ast.Or,
        ast.Call,
        ast.keyword,
        ast.Attribute,
    )

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.LShift: operator.lshift,
        ast.RShift: operator.rshift,
        ast.BitOr: operator.or_,
        ast.BitXor: operator.xor,
        ast.BitAnd: operator.and_,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
        ast.Not: operator.not_,
        ast.Invert: operator.invert,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Is: operator.is_,
        ast.IsNot: operator.is_not,
        ast.In: lambda a, b: a in b,
        ast.NotIn: lambda a, b: a not in b,
    }

    # Standard allowed functions for safe evaluation
    DEFAULT_ALLOWED_FUNCTIONS = {
        "sin": sin,
        "cos": cos,
        "abs": abs,
        "min": min,
        "max": max,
    }

    def __init__(self, variables: dict[str, Any], allowed_functions: dict[str, Any] | None = None):
        self.variables = variables
        self.allowed_functions = allowed_functions or self.DEFAULT_ALLOWED_FUNCTIONS.copy()

    def safe_eval(self, expr_string: str) -> Any:
        """Safely evaluate a mathematical expression string."""
        try:
            tree = ast.parse(expr_string, mode="eval")
            self._validate_ast(tree)
            return self._eval_node(tree.body)
        except (SyntaxError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid expression: {e}") from e

    def _validate_ast(self, node: ast.AST) -> None:
        """Validate that AST only contains allowed nodes."""
        for child in ast.walk(node):
            if not isinstance(child, self.ALLOWED_NODES):
                raise ValueError(f"Disallowed node type: {type(child).__name__}")

    def _eval_node(self, node: ast.AST) -> Any:
        """Recursively evaluate AST nodes."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in self.variables:
                return self.variables[node.id]
            elif node.id in self.allowed_functions:
                return self.allowed_functions[node.id]
            else:
                raise NameError(f"Unknown variable or function: {node.id}")
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = self.OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op = self.OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            return op(operand)
        elif isinstance(node, ast.Compare):
            left = self._eval_node(node.left)
            for op, comparator in zip(node.ops, node.comparators, strict=False):
                right = self._eval_node(comparator)
                comp_op = self.OPERATORS.get(type(op))
                if comp_op is None:
                    raise ValueError(f"Unsupported comparison operator: {type(op).__name__}")
                if not comp_op(left, right):
                    return False
                left = right  # For chained comparisons
            return True
        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(self._eval_node(value) for value in node.values)
            elif isinstance(node.op, ast.Or):
                return any(self._eval_node(value) for value in node.values)
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name is None or func_name not in self.allowed_functions:
                raise ValueError(f"Function not allowed: {func_name}")
            func = self.allowed_functions[func_name]
            args = [self._eval_node(arg) for arg in node.args]
            kwargs = {kw.arg: self._eval_node(kw.value) for kw in node.keywords if kw.arg is not None}
            return func(*args, **kwargs)
        elif isinstance(node, ast.Attribute):
            obj = self._eval_node(node.value)
            return getattr(obj, node.attr)
        else:
            raise ValueError(f"Unsupported node type: {type(node).__name__}")


# Use shared pattern matching utilities
MATH_OPERATORS = PatternMatchingHelper.MATH_OPERATORS
EXCLUDED_FUNCTION_NAMES = PatternMatchingHelper.EXCLUDED_FUNCTION_NAMES
VARIABLE_PATTERN_DETAILED = PatternMatchingHelper.VARIABLE_PATTERN_DETAILED
VARIABLE_PATTERN = PatternMatchingHelper.VARIABLE_PATTERN

# Tuple of types for isinstance() checks
VALID_EXPRESSION_TYPES = (VariableReference, Quantity, int, float, BinaryOperation, ConditionalExpression, Constant, UnaryFunction)


# ========== CUSTOM EXCEPTIONS ==========


class EquationReconstructionError(Exception):
    """Base exception for equation reconstruction errors."""

    pass


# ========== SHARED UTILITIES ==========


class DependencyAwareSolver:
    """Solver that handles equations with dependency ordering."""

    def __init__(self, variables: VariableDict):
        """Initialize the dependency-aware solver.

        Args:
            variables: Dictionary of variables available for solving
        """
        self.variables = variables

    def can_evaluate_expression(self, expression_str: str) -> bool:
        """Check if an expression can be evaluated with current known variables.

        Args:
            expression_str: The expression string to check

        Returns:
            True if all variables in the expression have known values
        """
        try:
            # Extract variables from the expression
            var_names = PatternMatchingHelper.extract_variables_from_expression_string(expression_str)

            # Check if all variables have known values
            for var_name in var_names:
                if var_name in self.variables:
                    var = self.variables[var_name]
                    if hasattr(var, "value") and var.value is None:
                        return False
                else:
                    return False  # Variable not found

            return True
        except Exception:
            return False

    def solve_equations_with_dependencies(self, equation_specs: list[tuple[str, str]]) -> bool:
        """Solve equations in dependency order.

        Args:
            equation_specs: List of (target_var, expression) tuples

        Returns:
            True if all equations were solved successfully
        """
        from qnty.algebra import solve

        # Track which equations have been solved
        remaining_equations = list(equation_specs)
        max_iterations = len(equation_specs) * 2  # Prevent infinite loops
        iterations = 0

        while remaining_equations and iterations < max_iterations:
            iterations += 1
            progress_made = False

            # Try to solve equations that can be evaluated now
            for i, (target_var, expression) in enumerate(remaining_equations):
                if self.can_evaluate_expression(expression):
                    try:
                        # Evaluate the expression
                        evaluator = SafeExpressionEvaluator(self.variables)
                        rhs = evaluator.safe_eval(expression)

                        # Solve for the target variable
                        success = solve(self.variables[target_var], rhs)
                        if success:
                            # Remove this equation from remaining list
                            remaining_equations.pop(i)
                            progress_made = True
                            break

                    except Exception:
                        # Skip this equation for now
                        continue

            # If no progress was made, we might have unsolvable dependencies
            if not progress_made:
                break

        return len(remaining_equations) == 0


class ExpressionEvaluationMixin:
    """Mixin providing shared expression evaluation utilities."""

    @staticmethod
    def create_safe_evaluator(variables: VariableDict) -> SafeExpressionEvaluator:
        """Create a standardized safe expression evaluator.

        Args:
            variables: Dictionary of available variables

        Returns:
            Configured SafeExpressionEvaluator instance
        """
        eval_context = dict(variables)
        return SafeExpressionEvaluator(eval_context, SafeExpressionEvaluator.DEFAULT_ALLOWED_FUNCTIONS.copy())

    @staticmethod
    def extract_variables_from_expression(expression_str: str, exclude_functions: bool = True) -> list[str]:
        """Extract variable names from an expression string.

        Args:
            expression_str: The expression string to parse
            exclude_functions: Whether to exclude known function names

        Returns:
            List of variable names found in the expression
        """
        return PatternMatchingHelper.extract_variables_from_expression_string(expression_str, exclude_functions)


class BaseExpressionHandler(ExpressionEvaluationMixin, SafeExecutionMixin):
    """Base class for expression handling components."""

    def __init__(self, variables: VariableDict, logger: Logger):
        """Initialize the base expression handler.

        Args:
            variables: Dictionary of available variables
            logger: Logger for debugging
        """
        self.variables = variables
        self.logger = logger


# ========== EXPRESSION PARSER ==========


class ExpressionParser(BaseExpressionHandler):
    """
    Focused class for parsing and rebuilding mathematical expressions.

    Handles conversion from string patterns to Expression objects using
    safe evaluation techniques and proper namespace management.
    """

    def parse_composite_expression_pattern(self, composite_symbol: str) -> Any | None:
        """
        Parse a composite expression pattern and reconstruct it using available variables.

        Args:
            composite_symbol: The composite expression string to parse

        Returns:
            Reconstructed expression if successful, None otherwise

        Examples:
            "D - T * 2" -> header_D - header_T * 2
            "(P - S) / E" -> (header_P - header_S) / header_E
        """
        if not composite_symbol or not isinstance(composite_symbol, str):
            return None

        return self.safe_execute(f"parse composite expression '{composite_symbol}'", lambda: self._parse_composite_expression_impl(composite_symbol))

    def _parse_composite_expression_impl(self, composite_symbol: str) -> Any | None:
        """Implementation of composite expression parsing."""
        # Extract variable names from the composite expression
        var_matches = self.extract_variables_from_expression(composite_symbol)
        if not var_matches:
            return None

        # Find the namespace that contains most of these variables
        best_namespace = self._find_best_namespace_for_variables(var_matches)
        if not best_namespace:
            return None

        # Create substitution mapping
        substitution_map = {}
        for var_name in var_matches:
            namespaced_name = f"{best_namespace}_{var_name}"
            if namespaced_name in self.variables:
                substitution_map[var_name] = namespaced_name

        if not substitution_map:
            return None

        # Substitute variables in the expression string
        substituted_expr = composite_symbol
        for original, namespaced in substitution_map.items():
            # Use word boundary regex for precise replacement
            pattern = r"\b" + re.escape(original) + r"\b"
            substituted_expr = re.sub(pattern, namespaced, substituted_expr)

        # Try to build the expression from the substituted string
        return self._build_expression_from_string(substituted_expr)

    def _find_best_namespace_for_variables(self, var_names: list[str]) -> str | None:
        """Find the namespace that contains the most variables from the list."""
        namespace_scores = {}

        # Score each namespace based on how many variables it contains
        for var_name in self.variables:
            if "_" in var_name:
                namespace = var_name.split("_")[0]
                base_var = "_".join(var_name.split("_")[1:])

                if base_var in var_names:
                    namespace_scores[namespace] = namespace_scores.get(namespace, 0) + 1

        if not namespace_scores:
            return None

        # Return the namespace with the highest score
        return max(namespace_scores.items(), key=lambda x: x[1])[0]

    def _build_expression_from_string(self, expr_string: str) -> Any | None:
        """
        Build an expression from a string by safely evaluating with variable substitution.

        Args:
            expr_string: The expression string to evaluate

        Returns:
            Built expression object if successful, None otherwise
        """
        return self.safe_execute(f"build expression from string '{expr_string}'", lambda: self.create_safe_evaluator(self.variables).safe_eval(expr_string))

    def parse_malformed_variable_pattern(self, malformed_symbol: str) -> Any | None:
        """
        Parse a malformed variable pattern from proxy evaluation.

        Args:
            malformed_symbol: The malformed variable symbol to parse

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        if not malformed_symbol or not isinstance(malformed_symbol, str):
            return None

        try:
            # Check if this looks like a mathematical expression with embedded values
            if any(char in malformed_symbol for char in MATH_OPERATORS):
                # Try to parse as a composite expression
                return self.parse_composite_expression_pattern(malformed_symbol)

            # Check for specific malformed patterns
            if "." in malformed_symbol and "(" in malformed_symbol:
                # Looks like a method call result - try to extract the base pattern
                base_pattern = self._extract_base_pattern_from_malformed(malformed_symbol)
                if base_pattern:
                    return self.parse_composite_expression_pattern(base_pattern)

            return None

        except Exception as e:
            self.logger.debug(f"Failed to parse malformed variable '{malformed_symbol}': {e}")
            return None

    def _extract_base_pattern_from_malformed(self, malformed_symbol: str) -> str | None:
        """Extract the base mathematical pattern from a malformed symbol."""
        if not malformed_symbol or not isinstance(malformed_symbol, str):
            return None

        try:
            # Remove numeric values that look like results
            cleaned = re.sub(r"\d+\.\d+", "VAR", malformed_symbol)

            # Remove method calls like .value, .quantity
            cleaned = re.sub(r"\.(?:value|quantity|magnitude)\b", "", cleaned)

            # Return pattern if it contains mathematical operators
            return cleaned if any(char in cleaned for char in MATH_OPERATORS) else None

        except (AttributeError, re.error):
            return None

    def parse_and_rebuild_expression(self, expr: Any, missing_vars: list[str]) -> Any | None:
        """
        Parse composite expressions and rebuild them using existing variables.

        Args:
            expr: The expression to parse and rebuild
            missing_vars: List of missing variable names

        Returns:
            Rebuilt expression if successful, None otherwise
        """
        if not missing_vars:
            return expr

        try:
            # For each missing variable, try to reconstruct it
            reconstructed_components = {}

            for missing_var in missing_vars:
                if any(char in missing_var for char in MATH_OPERATORS):
                    # This is a composite expression
                    rebuilt = self.parse_composite_expression_pattern(missing_var)
                    if rebuilt:
                        reconstructed_components[missing_var] = rebuilt

            if not reconstructed_components:
                return None

            # Try to substitute the reconstructed components back into the original expression
            return self._substitute_in_expression(expr, reconstructed_components)

        except Exception as e:
            self.logger.debug(f"Failed to parse and rebuild expression: {e}")
            return None

    def _substitute_in_expression(self, _: Any, substitutions: dict[str, Any]) -> Any | None:
        """
        Substitute reconstructed components back into an expression tree.

        Args:
            _expr: The original expression (unused in current implementation)
            substitutions: Map of missing variables to their reconstructed versions

        Returns:
            Expression with substitutions applied
        """
        if not substitutions:
            return None

        # Return the first successful substitution
        # TODO: Implement full expression tree traversal for complex substitutions
        return next(iter(substitutions.values()))


# ========== NAMESPACE MAPPER ==========


class NamespaceMapper(BaseExpressionHandler):
    """
    Focused class for handling variable namespace mapping operations.

    Provides efficient mapping of base variable names to their namespaced
    counterparts with caching for performance optimization.
    """

    def __init__(self, variables: VariableDict, logger: Logger):
        """
        Initialize the namespace mapper.

        Args:
            variables: Dictionary of available variables
            logger: Logger for debugging
        """
        super().__init__(variables, logger)

        # Performance optimization caches
        self._namespace_cache: dict[str, set[str]] = {}
        self._variable_mapping_cache: dict[frozenset, NamespaceMapping] = {}
        self._all_variable_names: set[str] | None = None

    def extract_base_variables_from_composites(self, missing_vars: list[str]) -> set[str]:
        """
        Extract base variable names from composite expressions.

        Args:
            missing_vars: List of missing variable expressions

        Returns:
            Set of base variable names found in the expressions
        """
        base_vars = set()

        for missing_var in missing_vars:
            if not isinstance(missing_var, str):
                continue

            # Extract variable names using the shared utility
            matches = self.extract_variables_from_expression(missing_var)
            base_vars.update(matches)

        return base_vars

    def find_namespace_mappings(self, base_vars: set[str]) -> NamespaceMapping:
        """
        Find namespace mappings for a set of base variables.

        Args:
            base_vars: Set of base variable names

        Returns:
            Dictionary mapping base variables to their namespaced versions
        """
        # Use cache for performance
        cache_key = frozenset(base_vars)
        if cache_key in self._variable_mapping_cache:
            return self._variable_mapping_cache[cache_key]

        mappings = {}

        # Build all variable names cache if needed
        if self._all_variable_names is None:
            self._all_variable_names = set(self.variables.keys())

        # For each base variable, find its namespaced version
        for base_var in base_vars:
            namespaced_var = self._find_namespaced_variable(base_var)
            if namespaced_var:
                mappings[base_var] = namespaced_var

        # Cache the result
        self._variable_mapping_cache[cache_key] = mappings
        return mappings

    def _find_namespaced_variable(self, base_var: str) -> str | None:
        """
        Find the namespaced version of a base variable.

        Args:
            base_var: Base variable name

        Returns:
            Namespaced variable name if found, None otherwise
        """
        if not base_var or not isinstance(base_var, str):
            return None

        # Build all variable names cache if needed
        if self._all_variable_names is None:
            self._all_variable_names = set(self.variables.keys())

        # Direct match first (most efficient)
        if base_var in self._all_variable_names:
            return base_var

        # Look for namespaced versions
        suffix = f"_{base_var}"
        candidates = [name for name in self._all_variable_names if name.endswith(suffix)]

        # Return shortest match (least nested namespace)
        return min(candidates, key=len) if candidates else None

    def clear_caches(self) -> None:
        """Clear all internal caches."""
        self._namespace_cache.clear()
        self._variable_mapping_cache.clear()
        self._all_variable_names = None


# ========== COMPOSITE EXPRESSION REBUILDER ==========


class CompositeExpressionRebuilder(BaseExpressionHandler):
    """
    Focused class for rebuilding composite expressions from malformed patterns.

    Handles reconstruction of expressions that were malformed during proxy
    evaluation and provides methods to recover the original mathematical structure.
    """

    def identify_malformed_variables(self, missing_vars: list[str]) -> list[str]:
        """
        Identify which missing variables are malformed from proxy evaluation.

        Args:
            missing_vars: List of missing variable names

        Returns:
            List of variables that appear to be malformed
        """
        malformed = []

        for var in missing_vars:
            if self._is_malformed_variable(var):
                malformed.append(var)

        return malformed

    def _is_malformed_variable(self, var_name: str) -> bool:
        """
        Check if a variable name appears to be malformed from proxy evaluation.

        Args:
            var_name: Variable name to check

        Returns:
            True if the variable appears malformed
        """
        if not isinstance(var_name, str) or not var_name:
            return False

        # Check for numeric values embedded in expressions
        if re.search(r"\d+\.\d+", var_name):
            return True

        # Check for method calls in variable names
        if ".value" in var_name or ".quantity" in var_name:
            return True

        # Check for unbalanced parentheses
        if var_name.count("(") != var_name.count(")"):
            return True

        # Check for very long names with multiple operations
        if len(var_name) > 50 and any(op in var_name for op in MATH_OPERATORS):
            return True

        return False

    def reconstruct_malformed_proxy_expression(self, equation: Equation, _: list[str]) -> Any | None:
        """
        Generically reconstruct expressions that were malformed due to proxy evaluation.

        Args:
            equation: The equation containing malformed expressions
            _malformed_vars: List of malformed variable names (kept for signature compatibility)

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        try:
            # Try to extract a meaningful pattern from the equation's RHS
            rhs_str = str(equation.rhs)

            # Look for recognizable mathematical patterns
            pattern = self._extract_mathematical_pattern(rhs_str)
            if pattern:
                # Try to reconstruct the pattern with proper variable references
                return self._reconstruct_pattern(pattern)

            # If direct pattern extraction fails, try alternative approaches
            return self._attempt_fallback_reconstruction(equation)

        except Exception as e:
            self.logger.debug(f"Failed to reconstruct malformed proxy expression: {e}")
            return None

    def _extract_mathematical_pattern(self, expression_str: str) -> str | None:
        """
        Extract a mathematical pattern from an expression string.

        Args:
            expression_str: String representation of the expression

        Returns:
            Cleaned mathematical pattern if extractable, None otherwise
        """
        try:
            # Remove common method calls and numeric results
            cleaned = expression_str

            # Remove .value, .quantity, etc.
            cleaned = re.sub(r"\.(?:value|quantity|magnitude)\b", "", cleaned)

            # Replace numeric constants with placeholders
            cleaned = re.sub(r"\d+\.\d+", "NUM", cleaned)

            # If we still have mathematical operators, this might be reconstructable
            if any(op in cleaned for op in MATH_OPERATORS):
                return cleaned

            return None

        except Exception:
            return None

    def _reconstruct_pattern(self, pattern: str) -> Any | None:
        """
        Reconstruct a mathematical pattern using available variables.

        Args:
            pattern: The mathematical pattern to reconstruct

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        try:
            # Extract variable names from the pattern
            var_matches = VARIABLE_PATTERN.findall(pattern)

            # Try to map these to existing variables
            var_mapping = {}
            for var_name in var_matches:
                if var_name not in EXCLUDED_FUNCTION_NAMES and var_name != "NUM":
                    # Look for a matching variable in our namespace
                    matching_var = self._find_matching_variable(var_name)
                    if matching_var:
                        var_mapping[var_name] = matching_var

            if not var_mapping:
                return None

            # Substitute the variables back into the pattern
            reconstructed_pattern = pattern
            for original, replacement in var_mapping.items():
                reconstructed_pattern = re.sub(r"\b" + re.escape(original) + r"\b", replacement, reconstructed_pattern)

            # Replace NUM placeholders with appropriate constants
            reconstructed_pattern = re.sub(r"\bNUM\b", "1.0", reconstructed_pattern)

            # Try to evaluate the reconstructed pattern
            return self._safe_evaluate_pattern(reconstructed_pattern)

        except Exception as e:
            self.logger.debug(f"Failed to reconstruct pattern '{pattern}': {e}")
            return None

    def _find_matching_variable(self, var_name: str) -> str | None:
        """Find a variable in our namespace that matches the given name."""
        # Direct match first
        if var_name in self.variables:
            return var_name

        # Look for namespaced versions
        candidates = [v for v in self.variables.keys() if v.endswith(f"_{var_name}")]

        if candidates:
            # Return the shortest match (least nested)
            return min(candidates, key=len)

        return None

    def _safe_evaluate_pattern(self, pattern: str) -> Any | None:
        """Safely evaluate a reconstructed pattern."""
        return self.safe_execute(f"evaluate pattern '{pattern}'", lambda: self.create_safe_evaluator(self.variables).safe_eval(pattern))

    def _attempt_fallback_reconstruction(self, equation: Equation) -> Any | None:
        """Attempt fallback reconstruction methods."""
        try:
            # Try to get variables from the LHS and create a simple reconstruction
            if isinstance(equation.lhs, Quantity | VariableReference):
                symbol = getattr(equation.lhs, "symbol", None)
                if isinstance(symbol, str) and symbol in self.variables:
                    lhs_var = self.variables[symbol]

                    # Look for similar variables that might be used in a simple expression
                    namespace = self._extract_namespace_from_variable(symbol)
                    if namespace:
                        return self._create_simple_reconstruction(namespace, lhs_var)

            return None

        except (AttributeError, TypeError):
            return None

    def _extract_namespace_from_variable(self, var_symbol: str) -> str | None:
        """Extract namespace from a variable symbol."""
        if "_" in var_symbol:
            return var_symbol.split("_")[0]
        return None

    def _create_simple_reconstruction(self, namespace: str, target_var: Quantity) -> Any | None:
        """Create a simple reconstruction based on namespace variables."""
        try:
            # Find other variables in the same namespace
            namespace_vars = [v for name, v in self.variables.items() if name.startswith(f"{namespace}_") and v != target_var]

            if namespace_vars:
                # Return the first other variable as a simple reconstruction
                # This is a fallback - in practice, more sophisticated logic would be needed
                return namespace_vars[0]

            return None

        except Exception:
            return None


# ========== DELAYED EXPRESSION RESOLVER ==========


class DelayedExpressionResolver(BaseExpressionHandler):
    """
    Focused class for resolving delayed expressions and equations.

    Handles components that have deferred evaluation needs and provides
    safe resolution with proper type checking and context management.
    """

    def contains_delayed_expressions(self, equation: Equation) -> bool:
        """
        Check if an equation contains delayed expressions that need resolution.

        Args:
            equation: The equation to check for delayed expressions

        Returns:
            True if equation contains delayed expressions
        """
        try:
            # Check for common delayed expression patterns
            equation_str = str(equation)

            # Look for delayed expression markers
            delayed_markers = ["DelayedExpression", "DelayedVariable", "DelayedFunction", "resolve(", "delayed_", "proxy_"]

            return any(marker in equation_str for marker in delayed_markers)

        except Exception:
            return False

    def resolve_delayed_equation(self, equation: Equation) -> ReconstructionResult:
        """
        Resolve a delayed equation by evaluating its delayed expressions.

        Args:
            equation: The equation with delayed expressions to resolve

        Returns:
            Resolved equation if successful, None otherwise
        """
        try:
            # Try to resolve the RHS if it has delayed components
            resolved_rhs = self._resolve_delayed_expression(equation.rhs)

            if resolved_rhs is None:
                return None

            # Create new equation with resolved RHS
            if isinstance(equation.lhs, Quantity):
                return create_equation(equation.lhs, resolved_rhs)

            return None

        except Exception as e:
            self.logger.debug(f"Failed to resolve delayed equation: {e}")
            return None

    def _resolve_delayed_expression(self, expr: Any) -> Any | None:
        """
        Resolve a delayed expression by calling its resolve method if available.

        Args:
            expr: Expression that might be delayed

        Returns:
            Resolved expression if successful, None otherwise
        """
        try:
            # Check if this is a valid expression type that doesn't need resolution
            if isinstance(expr, VALID_EXPRESSION_TYPES):
                # Check if this expression has a resolve method
                if hasattr(expr, "resolve") and callable(getattr(expr, "resolve", None)):
                    context = self.variables.copy()
                    return expr.resolve(context)  # type: ignore[attr-defined]
                return expr

            # Try to recursively resolve components for binary operations
            if isinstance(expr, BinaryOperation):
                resolved_left = self._resolve_delayed_expression(expr.left)
                resolved_right = self._resolve_delayed_expression(expr.right)

                if resolved_left is not None and resolved_right is not None:
                    return BinaryOperation(expr.operator, resolved_left, resolved_right)

            return None

        except (AttributeError, TypeError) as e:
            self.logger.debug(f"Failed to resolve delayed expression: {e}")
            return None


# ========== MAIN EQUATION RECONSTRUCTOR ==========


class EquationReconstructor:
    """
    Handles reconstruction of equations with composite expressions.

    This refactored class provides equation reconstruction capabilities by
    coordinating focused component classes for parsing, namespace mapping,
    delayed resolution, and composite expression rebuilding.

    Key Features:
    - Delegates to focused component classes for specific responsibilities
    - Generic composite expression reconstruction
    - Malformed equation recovery from proxy operations
    - Namespace variable mapping and resolution
    - Mathematical pattern parsing and rebuilding
    - Performance optimization through focused caching

    Example Usage:
        reconstructor = EquationReconstructor(problem)
        fixed_equation = reconstructor._reconstruct_composite_expressions(broken_equation, missing_vars)
    """

    def __init__(self, problem: Any) -> None:
        """
        Initialize the equation reconstructor.

        Args:
            problem: The EngineeringProblem instance containing variables and logger

        Raises:
            ValueError: If problem doesn't have required attributes
        """
        # Type-safe attribute access
        try:
            self.variables: VariableDict = problem.variables
            self.logger: Logger = problem.logger
        except AttributeError as e:
            raise ValueError(f"Problem must have 'variables' and 'logger' attributes: {e}") from e

        if not isinstance(self.variables, dict):
            raise ValueError("Problem.variables must be a dictionary")
        if not isinstance(self.logger, Logger):
            raise ValueError("Problem.logger must be a Logger instance")

        self.problem = problem

        # Initialize focused component classes
        self.expression_parser = ExpressionParser(self.variables, self.logger)
        self.namespace_mapper = NamespaceMapper(self.variables, self.logger)
        self.delayed_resolver = DelayedExpressionResolver(self.variables, self.logger)
        self.composite_rebuilder = CompositeExpressionRebuilder(self.variables, self.logger)

    def _reconstruct_composite_expressions(self, equation: Equation, missing_vars: list[str]) -> ReconstructionResult:
        """
        Generic reconstruction of equations with composite expressions.

        Delegates to NamespaceMapper for variable mapping and ExpressionParser
        for substitution operations.

        Args:
            equation: The equation to reconstruct
            missing_vars: List of missing variable names

        Returns:
            Reconstructed equation if successful, None otherwise

        Raises:
            EquationReconstructionError: If namespace mapping fails
        """
        if not missing_vars:
            return None

        try:
            # Extract variable symbols from composite expressions
            composite_vars = self.namespace_mapper.extract_base_variables_from_composites(missing_vars)

            if not composite_vars:
                self.logger.debug("No composite variables found to extract")
                return None

            # Find which namespaces contain these variables
            namespace_mappings = self.namespace_mapper.find_namespace_mappings(composite_vars)

            if not namespace_mappings:
                self.logger.debug("No namespace mappings found")
                return None

            # Reconstruct the equation by substituting composite expressions
            return self._substitute_composite_expressions(equation, missing_vars, namespace_mappings)

        except Exception as e:
            self.logger.debug(f"Error in _reconstruct_composite_expressions: {e}")
            return None

    def _substitute_composite_expressions(self, equation: Equation, missing_vars: list[str], namespace_mappings: dict[str, str]) -> ReconstructionResult:
        """
        Substitute composite expressions with properly namespaced variables.

        Args:
            equation: The equation to substitute expressions in
            missing_vars: List of missing variable names
            namespace_mappings: Mapping from base variables to namespaced variables

        Returns:
            Reconstructed equation if successful, None otherwise
        """
        if not missing_vars or not namespace_mappings:
            return None

        try:
            # Get the equation string representation for debugging
            eq_str = str(equation)
            self.logger.debug(f"Substituting expressions in equation: {eq_str}")

            # For each missing composite expression, try to rebuild it
            for missing_var in missing_vars:
                if missing_var in eq_str:
                    reconstructed_expr = self._reconstruct_expression_from_mapping(missing_var, namespace_mappings)
                    if reconstructed_expr:
                        # Replace the original equation's RHS or LHS
                        lhs_var = self._get_lhs_variable(equation)
                        if lhs_var:
                            return create_equation(lhs_var, reconstructed_expr)

            return None

        except Exception as e:
            self.logger.debug(f"Error in _substitute_composite_expressions: {e}")
            return None

    def _reconstruct_expression_from_mapping(self, composite_expr: str, namespace_mappings: dict[str, str]) -> Any | None:
        """
        Reconstruct a composite expression using the namespace mappings.

        Args:
            composite_expr: The composite expression string to reconstruct
            namespace_mappings: Mapping from base variables to namespaced variables

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        if not composite_expr or not namespace_mappings:
            return None

        try:
            # Create a substitution pattern for the expression
            substituted_expr = composite_expr

            # Replace base variable names with their namespaced counterparts
            for base_var, namespaced_var in namespace_mappings.items():
                if namespaced_var in self.variables:
                    # Use word boundary regex to avoid partial matches
                    pattern = r"\b" + re.escape(base_var) + r"\b"
                    substituted_expr = re.sub(pattern, namespaced_var, substituted_expr)

            # Try to evaluate the substituted expression using the expression parser
            return self.expression_parser.parse_composite_expression_pattern(substituted_expr)

        except Exception as e:
            self.logger.debug(f"Error in expression reconstruction: {e}")
            return None

    def _get_lhs_variable(self, equation: Equation) -> Quantity | None:
        """
        Safely extract the left-hand side variable from an equation.

        Args:
            equation: The equation to extract LHS from

        Returns:
            The LHS variable if valid, None otherwise
        """
        try:
            # Check if lhs is a VariableReference
            if isinstance(equation.lhs, VariableReference):
                var_name = equation.lhs.name
                if var_name in self.variables:
                    return self.variables[var_name]
            # Check if lhs is a FieldQnty with symbol attribute
            elif isinstance(equation.lhs, Quantity):
                symbol = getattr(equation.lhs, "symbol", None)
                if isinstance(symbol, str) and symbol in self.variables:
                    return self.variables[symbol]
        except (AttributeError, TypeError):
            pass

        return None

    def contains_delayed_expressions(self, equation: Equation) -> bool:
        """
        Check if an equation contains delayed expressions that need resolution.

        Args:
            equation: The equation to check for delayed expressions

        Returns:
            True if equation contains delayed expressions
        """
        return self.delayed_resolver.contains_delayed_expressions(equation)

    def resolve_delayed_equation(self, equation: Equation) -> ReconstructionResult:
        """
        Resolve a delayed equation by evaluating its delayed expressions.

        Args:
            equation: The equation with delayed expressions to resolve

        Returns:
            Resolved equation if successful, None otherwise
        """
        return self.delayed_resolver.resolve_delayed_equation(equation)

    # Delegation methods for public API compatibility
    def parse_composite_expression_pattern(self, composite_symbol: str) -> Any | None:
        """
        Parse a composite expression pattern using the expression parser.

        Args:
            composite_symbol: The composite expression string to parse

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        return self.expression_parser.parse_composite_expression_pattern(composite_symbol)

    def parse_malformed_variable_pattern(self, malformed_symbol: str) -> Any | None:
        """
        Parse a malformed variable pattern using the expression parser.

        Args:
            malformed_symbol: The malformed variable symbol to parse

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        return self.expression_parser.parse_malformed_variable_pattern(malformed_symbol)

    def parse_and_rebuild_expression(self, expr: Any, missing_vars: list[str]) -> Any | None:
        """
        Parse composite expressions and rebuild them using existing variables.

        Args:
            expr: The expression to parse and rebuild
            missing_vars: List of missing variable names

        Returns:
            Rebuilt expression if successful, None otherwise
        """
        return self.expression_parser.parse_and_rebuild_expression(expr, missing_vars)


# Export all relevant classes
__all__ = [
    "EquationReconstructor",
    "ExpressionParser",
    "NamespaceMapper",
    "CompositeExpressionRebuilder",
    "DelayedExpressionResolver",
    "SafeExpressionEvaluator",
    "EquationReconstructionError",
]
