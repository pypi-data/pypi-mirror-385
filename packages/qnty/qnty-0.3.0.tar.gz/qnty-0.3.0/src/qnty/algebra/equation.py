"""
Equation System
===============

Mathematical equations for qnty variables with solving capabilities.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Protocol, cast

from ..core.quantity import FieldQuantity
from ..utils.scope_discovery import ScopeDiscoveryService
from ..utils.shared_utilities import SharedConstants, ValidationHelper
from .nodes import BinaryOperation, Expression, VariableReference

if TYPE_CHECKING:
    from ..core.quantity import Quantity

_logger = logging.getLogger(__name__)

# Global optimization flags
_SCOPE_DISCOVERY_ENABLED = False  # Disabled by default due to high overhead


class OperandSide(Enum):
    """Which side of a binary operation contains a variable."""

    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"
    NEITHER = "neither"


@dataclass
class BinaryOperationAnalysis:
    """Analysis result for a binary operation."""

    target_side: OperandSide
    target_expr: Expression | None
    other_expr: Expression | None


class OperatorInverter(Protocol):
    """Protocol for operator inversion functions."""

    def __call__(self, result: Quantity, other: Quantity, is_left: bool) -> Quantity | None: ...


class AlgebraicInverter:
    """Handles algebraic inversions for solving equations."""

    def __init__(self, equation: Equation):
        self.equation = equation
        self._inverters: dict[str, OperatorInverter] = {
            "+": self._invert_addition,
            "-": self._invert_subtraction,
            "*": self._invert_multiplication,
            "/": self._invert_division,
            "**": self._invert_power,
        }

    def _invert_addition(self, result: Quantity, other: Quantity, is_left: bool) -> Quantity:
        """Invert addition: A + B = C => A = C - B"""
        del is_left  # Unused parameter for addition
        return result - other

    def _invert_subtraction(self, result: Quantity, other: Quantity, is_left: bool) -> Quantity:
        """Invert subtraction based on position."""
        if is_left:
            # A - B = C => A = C + B
            return result + other
        else:
            # B - A = C => A = B - C
            return other - result

    def _invert_multiplication(self, result: Quantity, other: Quantity, is_left: bool) -> Quantity:
        """Invert multiplication: A * B = C => A = C / B"""
        del is_left  # Unused parameter for multiplication
        return result / other

    def _invert_division(self, result: Quantity, other: Quantity, is_left: bool) -> Quantity:
        """Invert division based on position."""
        if is_left:
            # A / B = C => A = C * B
            return result * other
        else:
            # B / A = C => A = B / C
            return other / result

    def _invert_power(self, result: Quantity, other: Quantity, is_left: bool) -> Quantity | None:
        """Invert power operation if possible."""
        if not is_left:
            return None  # B ** A = C is complex

        # A ** B = C => A = C ** (1/B)
        other_val = self.equation._get_quantity_value(other)
        result_val = self.equation._get_quantity_value(result)

        if other_val and result_val:
            try:
                exponent = 1.0 / other_val
                new_value = result_val**exponent
                return self.equation._create_quantity_with_value(result, new_value, "power_result")
            except (ZeroDivisionError, ValueError):
                pass
        return None

    def invert(self, operator: str, result: Quantity, other: Quantity, is_left: bool) -> Quantity | None:
        """Invert an operation to solve for unknown."""
        inverter = self._inverters.get(operator)
        if inverter:
            try:
                return inverter(result, other, is_left)
            except TypeError:
                # Re-raise TypeError for dimensional mismatches - these are critical errors
                raise
            except (ZeroDivisionError, ValueError, AttributeError):
                # Other errors indicate the operation cannot be inverted, return None
                return None
        return None


class Equation:
    """
    Represents a mathematical equation with left-hand side equal to right-hand side.
    Optimized with __slots__ for memory efficiency.
    """

    __slots__ = ("name", "lhs", "rhs", "_variables", "_inverter")

    def __init__(self, name: str, lhs: FieldQuantity | Expression, rhs: Expression):
        self.name = name
        self.lhs = self._to_expression(lhs)
        self.rhs = rhs
        self._variables: set[str] | None = None  # Lazy initialization for better performance
        self._inverter = AlgebraicInverter(self)  # Create inverter for algebraic operations

    @staticmethod
    def _to_expression(value: FieldQuantity | Expression) -> Expression:
        """Convert a value to an Expression, wrapping FieldQuantity in VariableReference."""
        if isinstance(value, FieldQuantity):
            return VariableReference(value)
        # Handle ConfigurableVariable from composition system
        elif hasattr(value, "_variable") and hasattr(value, "symbol") and not isinstance(value, Expression):
            return VariableReference(value._variable)  # type: ignore[attr-defined]
        # Handle ExpressionEnabledWrapper from composition system
        elif hasattr(value, "_wrapped") and not isinstance(value, Expression):
            return VariableReference(value._wrapped)  # type: ignore[attr-defined]
        return cast(Expression, value)

    def _is_variable_known(self, var_name: str, variable_values: dict[str, FieldQuantity]) -> bool:
        """Check if a variable exists in variable_values and is marked as known."""
        if var_name not in variable_values:
            return False
        var = variable_values[var_name]
        return hasattr(var, "is_known") and var.is_known

    def _get_known_variable(self, var_name: str, variable_values: dict[str, FieldQuantity]) -> FieldQuantity | None:
        """Get a variable if it exists and is known, otherwise return None."""
        if self._is_variable_known(var_name, variable_values):
            return variable_values[var_name]
        return None

    @staticmethod
    def _get_quantity_value(quantity: Quantity) -> float | None:
        """Safely extract numeric value from a Quantity."""
        if ValidationHelper.has_valid_value(quantity) and quantity.value is not None:
            return float(quantity.value)
        return None

    @staticmethod
    def _has_valid_value(quantity: Quantity) -> bool:
        """Check if a quantity has a valid numeric value."""
        return ValidationHelper.has_valid_value(quantity)

    def _create_quantity_with_value(self, template: Quantity, value: float, name: str = "result") -> Quantity | None:
        """Create a new quantity with the given value, using template for type/dimension."""
        try:
            result_unit = self._get_effective_unit(template)
            if result_unit is not None and hasattr(template, "dim"):
                return type(template)(name=name, dim=template.dim, value=value, preferred=result_unit)
            elif hasattr(template, "dim"):
                return type(template)(name=name, dim=template.dim, value=value)
        except (TypeError, AttributeError):
            pass
        return None

    def _analyze_binary_operation(self, expr: BinaryOperation, target_var: str) -> BinaryOperationAnalysis:
        """Analyze which side of a binary operation contains the target variable."""
        left_has_target = target_var in expr.left.get_variables()
        right_has_target = target_var in expr.right.get_variables()

        if left_has_target and right_has_target:
            return BinaryOperationAnalysis(OperandSide.BOTH, None, None)
        elif left_has_target:
            return BinaryOperationAnalysis(OperandSide.LEFT, expr.left, expr.right)
        elif right_has_target:
            return BinaryOperationAnalysis(OperandSide.RIGHT, expr.right, expr.left)
        else:
            return BinaryOperationAnalysis(OperandSide.NEITHER, None, None)

    def get_all_variables(self) -> set[str]:
        """Get all variable names used in this equation."""
        if self._variables is None:
            # Both lhs and rhs should be Expressions after __init__ conversion
            lhs_vars = self.lhs.get_variables()
            rhs_vars = self.rhs.get_variables()
            self._variables = lhs_vars | rhs_vars
        return self._variables

    @property
    def variables(self) -> set[str]:
        """Get all variable names used in this equation (cached property)."""
        return self.get_all_variables()

    def get_unknown_variables(self, known_vars: set[str]) -> set[str]:
        """Get variables that are unknown (not in known_vars set)."""
        return self.variables - known_vars

    def get_known_variables(self, known_vars: set[str]) -> set[str]:
        """Get variables that are known (in known_vars set)."""
        return self.variables & known_vars

    def can_solve_for(self, target_var: str, known_vars: set[str]) -> bool:
        """Check if this equation can solve for target_var given known_vars."""
        if target_var not in self.variables:
            return False

        # Direct assignment case: lhs is the variable
        if isinstance(self.lhs, VariableReference) and self.lhs.name == target_var:
            rhs_vars = self.rhs.get_variables()
            return rhs_vars.issubset(known_vars)

        # General case: can solve if target_var is the only unknown
        unknown_vars = self.get_unknown_variables(known_vars)
        return unknown_vars == {target_var}

    def _solve_algebraically(self, target_var: str, variable_values: dict[str, FieldQuantity]) -> Quantity | None:
        """
        Attempt to solve equation algebraically for target_var.
        Handles common algebraic manipulations.
        """
        # Case 1: LHS is a simple variable (X = expression)
        # But we need to solve for a variable in the RHS
        if isinstance(self.lhs, VariableReference):
            if self._is_variable_known(self.lhs.name, variable_values):
                # LHS is known, need to solve RHS = LHS for target_var
                return self._solve_expression_for_var(self.rhs, target_var, self.lhs.evaluate(variable_values), variable_values)

        # Case 2: RHS is a simple variable (expression = X)
        # And we need to solve for a variable in the LHS
        if isinstance(self.rhs, VariableReference):
            if self._is_variable_known(self.rhs.name, variable_values):
                # RHS is known, need to solve LHS = RHS for target_var
                return self._solve_expression_for_var(self.lhs, target_var, self.rhs.evaluate(variable_values), variable_values)

        # Case 3: Both sides are expressions
        # Try to isolate target_var
        return self._isolate_variable(target_var, variable_values)

    def _solve_expression_for_var(self, expr: Expression, target_var: str, known_value: Quantity, variable_values: dict[str, FieldQuantity]) -> Quantity | None:
        """
        Solve expression = known_value for target_var.
        Handles common patterns like A + B = C, A * B = C, etc.
        """
        if not isinstance(expr, BinaryOperation):
            return None

        analysis = self._analyze_binary_operation(expr, target_var)

        if analysis.target_side in (OperandSide.BOTH, OperandSide.NEITHER):
            return None  # Too complex or target not present

        # Evaluate the non-target side
        if analysis.other_expr is None or analysis.target_expr is None:
            return None

        other_val = analysis.other_expr.evaluate(variable_values)
        is_left = analysis.target_side == OperandSide.LEFT

        return self._invert_operation(expr.operator, analysis.target_expr, other_val, known_value, target_var, variable_values, is_left)

    def _invert_operation(
        self, operator: str, target_expr: Expression, other_val: Quantity, result_val: Quantity, target_var: str, variable_values: dict[str, FieldQuantity], is_left: bool
    ) -> Quantity | None:
        """
        Invert a binary operation to solve for target_var.

        If is_left=True: solve target_expr op other_val = result_val for target_var in target_expr
        If is_left=False: solve other_val op target_expr = result_val for target_var in target_expr
        """
        # Simple case: target_expr is just the variable we're looking for
        if isinstance(target_expr, VariableReference) and target_expr.name == target_var:
            return self._inverter.invert(operator, result_val, other_val, is_left)

        # Recursively solve if target_expr is also a binary operation
        return self._solve_expression_for_var(target_expr, target_var, result_val, variable_values)

    def _isolate_variable(self, target_var: str, variable_values: dict[str, FieldQuantity]) -> Quantity | None:
        """
        Try to isolate target_var when both LHS and RHS are complex expressions.
        This is a simplified version that handles basic cases.
        """
        del target_var, variable_values  # Suppress unused parameter warnings
        # For now, we don't handle complex equation rearrangement
        # This could be expanded in the future with a proper algebraic solver
        return None

    def solve_for(self, target_var: str, variable_values: dict[str, FieldQuantity]) -> FieldQuantity:
        """
        Solve the equation for target_var.
        Returns the target variable with updated quantity.
        """
        if target_var not in self.variables:
            raise ValueError(f"Variable '{target_var}' not found in equation")

        # Case 1: Direct assignment: target = expression
        if isinstance(self.lhs, VariableReference) and self.lhs.name == target_var:
            # Direct assignment: target_var = rhs
            result_qty = self.rhs.evaluate(variable_values)

        # Case 2: Try algebraic manipulation for simple cases
        else:
            result_qty = self._solve_algebraically(target_var, variable_values)
            if result_qty is None:
                raise NotImplementedError(f"Cannot solve for {target_var} in equation {self}. Algebraic manipulation not supported for this equation form.")

        # Get the variable object to update
        var_obj = variable_values.get(target_var)
        if var_obj is None:
            raise ValueError(f"Variable '{target_var}' not found in variable_values")

        # Convert result to preferred unit or original unit if available
        target_unit_constant = None

        # First priority: existing quantity unit
        if var_obj.quantity is not None:
            target_unit_constant = self._get_effective_unit(var_obj.quantity)
        # Second priority: preferred unit from the variable itself
        elif hasattr(var_obj, "preferred") and var_obj.preferred is not None:
            target_unit_constant = var_obj.preferred
        # Third priority: preferred_unit attribute (legacy)
        elif hasattr(var_obj, "preferred_unit") and getattr(var_obj, "preferred_unit", None) is not None:
            # Look up unit constant from string name
            preferred_unit_name = getattr(var_obj, "preferred_unit", None)
            try:
                # Get the dimension-specific units class
                class_name = var_obj.__class__.__name__
                units_class_name = f"{class_name}Units"

                # Import unit catalog dynamically to avoid circular imports
                from ..core import unit_catalog

                units_class = getattr(unit_catalog, units_class_name, None)
                if units_class and preferred_unit_name and hasattr(units_class, preferred_unit_name):
                    target_unit_constant = getattr(units_class, preferred_unit_name)
                    _logger.debug(f"Found preferred unit constant: {preferred_unit_name}")
                else:
                    _logger.debug(f"Could not find unit constant for {preferred_unit_name} in {units_class_name}")
            except (ImportError, AttributeError) as e:
                _logger.debug(f"Failed to lookup preferred unit {preferred_unit_name}: {e}")

        # Extract SI value before any unit conversion
        si_value = None
        if result_qty.value is not None:
            # Convert to SI unit to get the SI value
            try:
                from ..core.unit import ureg

                si_unit = ureg.si_unit_for(result_qty.dim)
                if si_unit is not None:
                    si_quantity = result_qty.to(si_unit)
                    si_value = si_quantity.value
                else:
                    si_value = result_qty.value
            except (ValueError, TypeError, AttributeError):
                si_value = result_qty.value

        if target_unit_constant is not None:
            try:
                result_qty = result_qty.to(target_unit_constant)
                _logger.debug(f"Converted {target_var} result to preferred unit: {target_unit_constant.symbol}")
            except (ValueError, TypeError, AttributeError) as e:
                _logger.debug(f"Unit conversion failed for {target_var} to {target_unit_constant}: {e}. Using calculated unit.")

        # Update the variable and return it
        if si_value is not None:
            # Always store the SI value, not the converted value
            var_obj.value = si_value

            # For new Quantity objects, also update preferred if it came from result
            if hasattr(var_obj, "preferred") and hasattr(result_qty, "preferred") and result_qty.preferred is not None:
                var_obj.preferred = result_qty.preferred

            # Try to set legacy quantity and known status attributes if they exist (for compatibility)
            try:
                # Only attempt assignments if attributes actually exist and are settable
                if hasattr(var_obj, "quantity") and not isinstance(getattr(type(var_obj), "quantity", None), property):
                    var_obj.quantity = result_qty  # type: ignore[misc]
            except (AttributeError, TypeError):
                pass  # Quantity assignment not supported

        # For new Quantity objects, is_known is automatically derived from value != None
        # So no need to set it explicitly. Legacy _is_known attribute is handled if it exists.
        try:
            if hasattr(var_obj, "_is_known"):
                var_obj._is_known = True  # type: ignore[misc]
        except (AttributeError, TypeError):
            pass  # Known status setting not supported
        return var_obj

    def check_residual(self, variable_values: dict[str, FieldQuantity], tolerance: float = SharedConstants.SOLVER_DEFAULT_TOLERANCE) -> bool:
        """
        Check if equation is satisfied by evaluating residual (LHS - RHS).
        Returns True if |residual| < tolerance, accounting for units.
        """
        try:
            # Both lhs and rhs should be Expressions after __init__ conversion
            lhs_value = self.lhs.evaluate(variable_values)
            rhs_value = self.rhs.evaluate(variable_values)

            # Check dimensional compatibility using public API
            if not self._are_dimensionally_compatible(lhs_value, rhs_value):
                return False

            # Convert to same units for comparison
            lhs_unit = self._get_effective_unit(lhs_value)
            if lhs_unit is not None and hasattr(rhs_value, "to"):
                rhs_converted = rhs_value.to(lhs_unit)
                lhs_val = self._get_quantity_value(lhs_value)
                rhs_val = self._get_quantity_value(rhs_converted)
                if lhs_val is not None and rhs_val is not None:
                    residual = abs(lhs_val - rhs_val)
                else:
                    residual = float("inf")
            else:
                lhs_val = self._get_quantity_value(lhs_value)
                rhs_val = self._get_quantity_value(rhs_value)
                if lhs_val is not None and rhs_val is not None:
                    residual = abs(lhs_val - rhs_val)
                else:
                    residual = float("inf")

            return residual < tolerance
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            _logger.debug(f"Expected error in residual check for equation '{self.name}': {e}")
            return False
        except Exception as e:
            error_msg = f"Unexpected error in residual check for equation '{self.name}': {e}"
            _logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _discover_variables_from_scope(self) -> dict[str, FieldQuantity]:
        """
        Automatically discover variables from the calling scope using centralized service.
        """
        if not _SCOPE_DISCOVERY_ENABLED:
            return {}

        # Use centralized scope discovery service
        return ScopeDiscoveryService.discover_variables(self.variables, enable_caching=True)

    def _get_effective_unit(self, quantity):
        """Get the effective unit for a quantity, handling both old and new Quantity objects."""
        from ..utils.shared_utilities import ValidationHelper

        return ValidationHelper.get_effective_unit(quantity)

    def _are_dimensionally_compatible(self, lhs_value, rhs_value) -> bool:
        """Check if two quantities are dimensionally compatible."""
        try:
            # Try to convert - if successful, they're compatible
            lhs_unit = self._get_effective_unit(lhs_value)
            if lhs_unit is not None:
                rhs_value.to(lhs_unit)
                return True
            return False
        except (ValueError, TypeError, AttributeError):
            return False

    def _analyze_variable_states(self, discovered: dict[str, FieldQuantity]) -> dict[str, str]:
        """Analyze which variables are known vs unknown."""
        states = {}
        for var_name in self.variables:
            if var_name not in discovered:
                states[var_name] = "missing"
            else:
                var = discovered[var_name]
                if hasattr(var, "is_known") and not var.is_known:
                    states[var_name] = "unknown"
                elif hasattr(var, "quantity") and var.quantity is not None:
                    states[var_name] = "known"
                else:
                    states[var_name] = "unknown"
        return states

    def _determine_solvability(self, states: dict[str, str], discovered: dict[str, FieldQuantity]) -> tuple[bool, str, dict[str, FieldQuantity]]:
        """Determine if equation can be solved based on variable states."""
        if "missing" in states.values():
            return False, "", {}

        unknowns = [name for name, state in states.items() if state == "unknown"]

        # Can only auto-solve if there's exactly one unknown
        if len(unknowns) == 1:
            return True, unknowns[0], discovered

        return False, "", {}

    def _can_auto_solve(self) -> tuple[bool, str, dict[str, FieldQuantity]]:
        """Check if equation can be auto-solved from scope using centralized service."""
        try:
            discovered = self._discover_variables_from_scope()
            if not discovered:
                return False, "", {}

            variable_states = self._analyze_variable_states(discovered)
            return self._determine_solvability(variable_states, discovered)

        except (AttributeError, KeyError, ValueError, TypeError) as e:
            _logger.debug(f"Cannot auto-solve equation '{self.name}': {e}")
            return False, "", {}

    def _try_auto_solve(self) -> bool:
        """Try to automatically solve the equation if possible."""
        try:
            can_solve, target_var, variables = self._can_auto_solve()
            if can_solve:
                self.solve_for(target_var, variables)
                return True
            return False
        except (AttributeError, KeyError, ValueError, TypeError) as e:
            _logger.debug(f"Auto-solve failed for equation '{self.name}': {e}")
            return False

    def __str__(self) -> str:
        # Try to auto-solve if possible before displaying
        self._try_auto_solve()
        return f"{self.lhs} = {self.rhs}"

    def __repr__(self) -> str:
        return f"Equation(name='{self.name}', lhs={self.lhs!r}, rhs={self.rhs!r})"
