"""
Sub-problem composition system for EngineeringProblem.

This module provides the complete sub-problem integration system including:
- Sub-problem proxy objects for clean composition syntax
- Namespace handling and variable mapping
- Composite equation creation
- Metaclass system for automatic proxy creation

Combined from composition.py and composition_mixin.py for focused functionality.
"""

from __future__ import annotations

from typing import Any

from ..algebra import BinaryOperation, ConditionalExpression, Constant, Equation, VariableReference
from ..algebra.nodes import Expression, wrap_operand
from ..core.quantity import FieldQuantity
from ..core.quantity_catalog import Dimensionless
from ..utils.shared_utilities import (
    ArithmeticOperationsMixin,
    ContextDetectionHelper,
    SharedConstants,
    VariableReferenceHelper,
)
from .rules import Rules

# Constants for metaclass
RESERVED_ATTRIBUTES = SharedConstants.RESERVED_ATTRIBUTES
PRIVATE_ATTRIBUTE_PREFIX = SharedConstants.PRIVATE_ATTRIBUTE_PREFIX
SUB_PROBLEM_REQUIRED_ATTRIBUTES: tuple[str, ...] = ("variables", "equations")


# ========== HELPER FUNCTIONS ==========


def _safe_execute(func, *args, **kwargs):
    """Execute a function safely, returning None on any exception."""
    try:
        return func(*args, **kwargs)
    except Exception:
        return None


def _extract_variables_from_obj(obj, variables_set: set[str]) -> None:
    """Extract variables from an object and add them to the variables set."""
    if hasattr(obj, "get_variables"):
        variables_set.update(obj.get_variables())
    elif hasattr(obj, "symbol"):
        variables_set.add(obj.symbol)


# Use shared variable reference helper
_get_variable_from_obj = VariableReferenceHelper.extract_variable_from_obj


def _create_variable_reference_from_obj(obj, context: dict | None = None):
    """Create a VariableReference from various object types."""
    from ..algebra.nodes import VariableReference

    variable = _get_variable_from_obj(obj)
    if variable is None:
        return obj

    # Handle context-based resolution for namespaced variables
    if isinstance(obj, ConfigurableVariable) and context:
        namespaced_symbol = variable.symbol
        if namespaced_symbol in context:
            return VariableReference(context[namespaced_symbol])

    # Handle context-based resolution for regular variables
    if hasattr(variable, "symbol") and context and variable.symbol in context:
        return VariableReference(context[variable.symbol])

    return VariableReference(variable)


def _create_arithmetic_operation(self_obj, other, operator: str, reverse: bool = False):
    """Create arithmetic operation, using DelayedExpression or delegating to variable."""
    if hasattr(self_obj, "_should_use_delayed_arithmetic") and self_obj._should_use_delayed_arithmetic():
        if reverse:
            return DelayedExpression(operator, other, self_obj)
        else:
            return DelayedExpression(operator, self_obj, other)
    else:
        # Delegate to the wrapped variable
        method_map = {"+": "add", "-": "sub", "*": "mul", "/": "truediv", "**": "pow"}
        method_name = method_map.get(operator, operator)
        if reverse:
            return getattr(self_obj._variable, f"__r{method_name}__")(other)
        else:
            return getattr(self_obj._variable, f"__{method_name}__")(other)


# ========== COMPOSITION CLASSES ==========


def _create_arithmetic_methods():
    """Factory function that creates arithmetic methods dynamically."""
    operators = {"__add__": "+", "__radd__": "+", "__sub__": "-", "__rsub__": "-", "__mul__": "*", "__rmul__": "*", "__truediv__": "/", "__rtruediv__": "/", "__pow__": "**", "__rpow__": "**"}

    methods = {}
    for method_name, op in operators.items():
        is_reverse = method_name.startswith("__r")
        if is_reverse:
            methods[method_name] = lambda self, other, operator=op: DelayedExpression(operator, other, self)
        else:
            methods[method_name] = lambda self, other, operator=op: DelayedExpression(operator, self, other)

    return methods


# Dynamically add arithmetic methods to avoid code duplication
for method_name, method_func in _create_arithmetic_methods().items():
    setattr(ArithmeticOperationsMixin, method_name, method_func)


class DelayedEquation:
    """
    Stores an equation definition that will be evaluated later when proper context is available.
    """

    def __init__(self, lhs_symbol, rhs_factory, name=None):
        self.lhs_symbol = lhs_symbol
        self.rhs_factory = rhs_factory  # Function that creates the RHS expression
        self.name = name or f"{lhs_symbol}_equation"

    def evaluate(self, context):
        """Evaluate the equation with the given context (namespace with variables)."""
        if self.lhs_symbol not in context:
            return None

        lhs_var = context[self.lhs_symbol]

        try:
            # Call the factory function with the context to create the RHS
            rhs_expr = self.rhs_factory(context)
            return lhs_var.equals(rhs_expr)
        except Exception:
            return None


class SubProblemProxy:
    """
    Proxy object that represents a sub-problem and provides namespaced variable access
    during class definition. Returns properly namespaced variables immediately to prevent
    malformed expressions.
    """

    def __init__(self, sub_problem, namespace):
        self._sub_problem = sub_problem
        self._namespace = namespace
        self._variable_cache = {}
        self._variable_configurations = {}  # Track configurations applied to variables
        # Global registry to track which expressions involve proxy variables
        if not hasattr(SubProblemProxy, "_expressions_with_proxies"):
            SubProblemProxy._expressions_with_proxies = set()

    def __getattr__(self, name):
        # Guard against deepcopy and pickle operations that cause recursion
        if name in {
            '__setstate__', '__getstate__', '__getnewargs__', '__getnewargs_ex__',
            '__reduce__', '__reduce_ex__', '__copy__', '__deepcopy__',
            '__getattribute__', '__setattr__', '__delattr__',
            '__dict__', '__weakref__', '__class__'
        }:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        if name in self._variable_cache:
            return self._variable_cache[name]

        try:
            attr_value = getattr(self._sub_problem, name)
            if isinstance(attr_value, FieldQuantity):
                # Create a properly namespaced variable immediately
                namespaced_var = self._create_namespaced_variable(attr_value)
                self._variable_cache[name] = namespaced_var
                return namespaced_var
            elif hasattr(attr_value, "_wrapped_var") and isinstance(attr_value._wrapped_var, FieldQuantity):
                # This is a MainVariableWrapper - unwrap it to get the FieldQuantity
                wrapped_var = attr_value._wrapped_var
                namespaced_var = self._create_namespaced_variable(wrapped_var)
                self._variable_cache[name] = namespaced_var
                return namespaced_var
            return attr_value
        except AttributeError as e:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'") from e

    def _create_namespaced_variable(self, original_var):
        """Create a Variable with namespaced symbol for proper expression creation."""
        namespaced_symbol = f"{self._namespace}_{original_var.symbol}"

        # Create new Variable with namespaced symbol that tracks modifications
        namespaced_var = ConfigurableVariable(
            symbol=namespaced_symbol,
            name=f"{original_var.name} ({self._namespace.title()})",
            quantity=original_var.quantity,
            is_known=original_var.is_known,
            proxy=self,
            original_symbol=original_var.symbol,
            original_variable=original_var,  # Pass the original variable for type preservation
        )

        return namespaced_var

    def track_configuration(self, original_symbol, quantity, is_known):
        """Track a configuration change made to a variable."""
        self._variable_configurations[original_symbol] = {"quantity": quantity, "is_known": is_known}

    def get_configurations(self):
        """Get all tracked configurations."""
        return self._variable_configurations.copy()

    def __deepcopy__(self, memo):
        # Don't allow deepcopy of SubProblemProxy - just return self
        _ = memo  # Mark as used to avoid linting warnings
        return self


class ConfigurableVariable:
    """
    A Variable wrapper that can track configuration changes and report them back to its proxy.
    This acts as a proxy around the actual qnty Variable rather than inheriting from it.
    """

    def __init__(self, symbol, name, quantity, is_known=True, proxy=None, original_symbol=None, original_variable=None):
        # Store the actual variable (we'll delegate to it)
        # Create a variable of the appropriate type based on the original

        # Import here to avoid circular dependency
        from ..core.quantity import Quantity as CoreQuantity

        if original_variable is not None:
            # Check if it's a Quantity (unified type)
            if isinstance(original_variable, CoreQuantity):
                # Check if it's a specialized quantity class (created by metaclass)
                # or the base Quantity class
                if hasattr(type(original_variable), "__init__") and type(original_variable).__name__ != "Quantity":
                    # It's a specialized quantity class (Length, Pressure, etc.)
                    # Use the specialized constructor (name, value, preferred) - dim is set by metaclass
                    self._variable = type(original_variable)(name=name, value=original_variable.value, preferred=original_variable.preferred)  # type: ignore[call-arg]
                    # Set additional attributes manually
                    self._variable._symbol = symbol
                    if hasattr(original_variable, "_output_unit"):
                        self._variable._output_unit = original_variable._output_unit
                else:
                    # It's the base Quantity class - use dataclass constructor
                    self._variable = type(original_variable)(
                        name=name,
                        dim=original_variable.dim,
                        value=original_variable.value,
                        preferred=original_variable.preferred,
                        _symbol=symbol,
                        _output_unit=getattr(original_variable, "_output_unit", None),
                    )
            else:
                # For other types (shouldn't happen with current codebase)
                self._variable = type(original_variable)(name)
        else:
            # Fallback to Dimensionless if no original variable provided
            self._variable = Dimensionless(name)

        # For non-Quantity types, set the symbol and other properties
        if original_variable is not None and not isinstance(original_variable, CoreQuantity):
            # Set the properties using private attributes (since properties may be read-only)
            self._variable._symbol = symbol
            # For the unified Quantity class, we set the value and preferred unit directly
            if quantity is not None and hasattr(quantity, "value") and hasattr(quantity, "preferred"):
                self._variable.value = quantity.value
                self._variable.preferred = quantity.preferred
        # Note: is_known is handled via the value being None or not in the unified Quantity API
        _ = is_known  # Mark as used to avoid linting warnings

        # The unified Quantity class may not have _arithmetic_mode
        # This is handled by the arithmetic operations in the class itself

        # Store proxy information
        self._proxy = proxy
        self._original_symbol = original_symbol

    def __getattr__(self, name):
        """Delegate all other attributes to the wrapped variable."""
        # Guard against deepcopy and pickle operations that cause recursion
        if name in {
            '__setstate__', '__getstate__', '__getnewargs__', '__getnewargs_ex__',
            '__reduce__', '__reduce_ex__', '__copy__', '__deepcopy__',
            '__getattribute__', '__setattr__', '__delattr__',
            '__dict__', '__weakref__', '__class__'
        }:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        # Handle special case for _arithmetic_mode since it's accessed in __mul__ etc.
        if name == "_arithmetic_mode":
            # First check if we have it directly using getattr for safety
            return getattr(self._variable, "_arithmetic_mode", "expression")

        # Prevent infinite recursion by checking if _variable exists
        if not hasattr(self, '_variable'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        return getattr(self._variable, name)

    def __deepcopy__(self, memo):
        # Don't allow deepcopy of ConfigurableVariable objects - just return self
        _ = memo  # Mark as used to avoid linting warnings
        return self

    def _should_use_delayed_arithmetic(self) -> bool:
        """Check if we should use delayed arithmetic based on context."""
        return ContextDetectionHelper.should_use_delayed_arithmetic()

    # Delegate arithmetic operations using a consolidated approach
    def _create_operation(self, other, operator: str, reverse: bool = False):
        """Create arithmetic operation based on context."""
        return _create_arithmetic_operation(self, other, operator, reverse)

    def __add__(self, other):
        return self._create_operation(other, "+")

    def __radd__(self, other):
        return self._create_operation(other, "+", True)

    def __sub__(self, other):
        return self._create_operation(other, "-")

    def __rsub__(self, other):
        return self._create_operation(other, "-", True)

    def __mul__(self, other):
        return self._create_operation(other, "*")

    def __rmul__(self, other):
        return self._create_operation(other, "*", True)

    def __truediv__(self, other):
        return self._create_operation(other, "/")

    def __rtruediv__(self, other):
        return self._create_operation(other, "/", True)

    def __pow__(self, other):
        return self._variable.__pow__(other)

    def __neg__(self):
        # Implement negation as multiplication by -1, consistent with other arithmetic operations
        return self._variable * (-1)

    def __lt__(self, other):
        return self._variable.__lt__(other)

    def __le__(self, other):
        return self._variable.__le__(other)

    def __gt__(self, other):
        return self._variable.__gt__(other)

    def __ge__(self, other):
        return self._variable.__ge__(other)

    def __eq__(self, other):  # type: ignore[override]
        return self._variable.__eq__(other)

    def __ne__(self, other):  # type: ignore[override]
        return self._variable.__ne__(other)

    def __setattr__(self, name, value):
        """Delegate attribute setting to the wrapped variable when appropriate."""
        if name.startswith("_") or name in ("_variable", "_proxy", "_original_symbol"):
            super().__setattr__(name, value)
        else:
            setattr(self._variable, name, value)
            # Track configuration changes for important attributes
            if name in ("value", "preferred", "is_known"):
                self._track_configuration_change()

    def _track_configuration_change(self):
        """Helper to track configuration changes to proxy."""
        if self._proxy and self._original_symbol:
            quantity_val = getattr(self._variable, "quantity", self._variable)
            is_known_val = getattr(self._variable, "is_known", self._variable.value is not None)
            self._proxy.track_configuration(self._original_symbol, quantity_val, is_known_val)

    def set(self, value):
        """Override set method to track configuration changes and return the correct setter."""
        # Create a wrapper setter that tracks changes after unit application
        original_setter = self._variable.set(value)

        if self._proxy and self._original_symbol:
            # Create tracking wrapper
            return TrackingSetterWrapper(original_setter, self._proxy, self._original_symbol, self._variable)
        else:
            return original_setter

    def update(self, value=None, unit=None, quantity=None, is_known=None):
        """Override update method to track configuration changes."""
        # Simplified version that handles the most common case
        try:
            # Try to call update if it exists
            result = self._variable.update(value, unit, quantity, is_known)  # type: ignore[attr-defined]
        except AttributeError:
            # Fall back to set method if update doesn't exist
            if value is not None and unit is not None:
                self._variable = self._variable.set(value, unit)
                result = self._variable
            else:
                result = self._variable
        self._track_configuration_change()
        return result


class TrackingSetterWrapper:
    """
    A wrapper around setter objects that tracks configuration changes after unit application.
    This ensures that when `proxy.set(value).unit` is called, the proxy tracks the final
    configuration after the unit is applied.
    """

    def __init__(self, original_setter, proxy, original_symbol, variable):
        self._original_setter = original_setter
        self._proxy = proxy
        self._original_symbol = original_symbol
        self._variable = variable

    def __getattr__(self, name):
        """
        Intercept property access for unit properties and track configuration after application.
        """
        # Guard against deepcopy and pickle operations that cause recursion
        if name in {
            '__setstate__', '__getstate__', '__getnewargs__', '__getnewargs_ex__',
            '__reduce__', '__reduce_ex__', '__copy__', '__deepcopy__',
            '__getattribute__', '__setattr__', '__delattr__',
            '__dict__', '__weakref__', '__class__'
        }:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        # Prevent infinite recursion by checking if _original_setter exists
        if not hasattr(self, '_original_setter'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        # Get the property from the original setter
        attr = getattr(self._original_setter, name)

        # If it's a property (unit setter), wrap it to track configuration
        if callable(attr):
            # It's a method, just delegate
            return attr
        else:
            # It's a property access, call it and then track configuration
            result = attr  # This will set the variable quantity and return the variable

            # Track the configuration after the unit is applied
            if self._proxy and self._original_symbol:
                self._proxy.track_configuration(self._original_symbol, self._variable.quantity, self._variable.is_known)

            return result

    def with_unit(self, unit):
        """Delegate with_unit method and track configuration."""
        result = self._original_setter.with_unit(unit)
        if self._proxy and self._original_symbol:
            self._proxy.track_configuration(self._original_symbol, self._variable.quantity, self._variable.is_known)
        return result

    def __deepcopy__(self, memo):
        # Don't allow deepcopy of TrackingSetterWrapper - just return self
        _ = memo  # Mark as used to avoid linting warnings
        return self


class DelayedVariableReference(ArithmeticOperationsMixin):
    """
    A placeholder for a variable that will be resolved to its namespaced version later.
    Supports arithmetic operations that create delayed expressions.
    """

    def __init__(self, namespace, symbol, original_var):
        self.namespace = namespace
        self.symbol = symbol
        self.original_var = original_var
        self._namespaced_symbol = f"{namespace}_{symbol}"

    def resolve(self, context):
        """Resolve to the actual namespaced variable from context."""
        return context.get(self._namespaced_symbol)


class DelayedExpression(ArithmeticOperationsMixin):
    """
    Represents an arithmetic expression that will be resolved later when context is available.
    Supports chaining of operations.
    """

    def __init__(self, operation, left, right):
        self.operation = operation
        self.left = left
        self.right = right

    @property
    def value(self):
        """
        DelayedExpression objects don't have values until resolved.
        Raise a more specific error to help with debugging.
        """
        raise AttributeError("DelayedExpression objects must be resolved before accessing their value. Use resolve(context) to convert this to a proper expression first.")

    def evaluate(self, variable_values):
        """
        DelayedExpression objects should be resolved before evaluation.
        This method raises an informative error to help debug issues.
        """
        # Mark variable as used to avoid linting warnings
        _ = variable_values
        raise RuntimeError(
            "DelayedExpression objects must be resolved before evaluation. "
            "This suggests that DelayedExpression.resolve() was not called properly "
            "or that an unresolved DelayedExpression made it into the expression tree."
        )

    def get_variables(self):
        """Extract variables from the expression operands."""
        variables = set()

        # Extract from both operands using helper function
        _extract_variables_from_obj(self.left, variables)
        _extract_variables_from_obj(self.right, variables)

        return variables

    def resolve(self, context):
        """Resolve this expression to actual Variable/Expression objects."""
        left_resolved = self._resolve_operand(self.left, context)
        right_resolved = self._resolve_operand(self.right, context)

        if left_resolved is None or right_resolved is None:
            return None

        # Create the actual expression
        if self.operation == "+":
            # Use wrap_operand to ensure proper expression type handling
            return BinaryOperation("+", wrap_operand(left_resolved), wrap_operand(right_resolved))
        elif self.operation == "-":
            return BinaryOperation("-", wrap_operand(left_resolved), wrap_operand(right_resolved))
        elif self.operation == "*":
            return BinaryOperation("*", wrap_operand(left_resolved), wrap_operand(right_resolved))
        elif self.operation == "/":
            return BinaryOperation("/", wrap_operand(left_resolved), wrap_operand(right_resolved))
        else:
            return BinaryOperation(self.operation, wrap_operand(left_resolved), wrap_operand(right_resolved))

    def _resolve_operand(self, operand, context):
        """Resolve a single operand to a Variable/Expression."""
        if isinstance(operand, DelayedVariableReference | DelayedExpression | DelayedFunction):
            return operand.resolve(context)
        else:
            return _create_variable_reference_from_obj(operand, context)


class DelayedFunction(Expression, ArithmeticOperationsMixin):
    """
    Represents a function call that will be resolved later when context is available.
    """

    def __init__(self, func_name, *args):
        self.func_name = func_name
        self.args = args

    def get_variables(self):
        """Extract variables from function arguments."""
        variables = set()
        for arg in self.args:
            _extract_variables_from_obj(arg, variables)
        return variables

    def evaluate(self, variable_values):
        """Evaluate the function with given variable values."""
        # This shouldn't normally be called - DelayedFunction should be resolved first
        # But provide a fallback that tries to resolve with available context
        try:
            # Try to resolve with the variable values as context
            resolved = self.resolve(variable_values)
            if resolved and hasattr(resolved, "evaluate"):
                return resolved.evaluate(variable_values)
        except Exception:
            pass
        raise RuntimeError(f"DelayedFunction {self.func_name} could not be evaluated. It should be resolved to an Expression first.")

    def simplify(self) -> Expression:
        """Return self as simplification since DelayedFunction is already simplified for its purpose."""
        return self

    def __str__(self) -> str:
        """String representation of the delayed function call."""
        if len(self.args) == 1:
            return f"{self.func_name}({self.args[0]})"
        return f"{self.func_name}({', '.join(str(arg) for arg in self.args)})"

    def resolve(self, context):
        """Resolve function call with given context."""
        # Resolve all arguments
        resolved_args = []
        for arg in self.args:
            if isinstance(arg, DelayedVariableReference | DelayedExpression | DelayedFunction):
                resolved_arg = arg.resolve(context)
                if resolved_arg is None:
                    return None
                resolved_args.append(resolved_arg)
            else:
                resolved_args.append(_create_variable_reference_from_obj(arg, context))

        # Call the appropriate function - create actual expressions, not more DelayedFunction objects
        if self.func_name == "sin":
            from ..algebra.nodes import UnaryFunction, wrap_operand

            return UnaryFunction("sin", wrap_operand(resolved_args[0]))
        elif self.func_name == "min_expr":
            from ..algebra.functions import _create_comparison_expr

            return _create_comparison_expr(tuple(resolved_args), "min")
        elif self.func_name == "max_expr":
            from ..algebra.functions import _create_comparison_expr

            return _create_comparison_expr(tuple(resolved_args), "max")
        elif self.func_name == "cond_expr":
            from ..algebra.nodes import ConditionalExpression, wrap_operand

            return ConditionalExpression(resolved_args[0], wrap_operand(resolved_args[1]), wrap_operand(resolved_args[2]))
        elif self.func_name == "match_expr":
            from ..algebra.nodes import MatchExpression, wrap_operand

            # First arg is the select variable, rest are option-expression pairs
            select_var = resolved_args[0]
            # Build cases dictionary from pairs
            cases_dict = {}
            for i in range(1, len(resolved_args), 2):
                option_value = resolved_args[i]
                expression = resolved_args[i + 1]
                cases_dict[option_value] = wrap_operand(expression)
            return MatchExpression(select_var, cases_dict)
        else:
            # Generic function call
            return None


# Delayed function factories
def delayed_sin(expr):
    return DelayedFunction("sin", expr)


def delayed_min_expr(*args):
    return DelayedFunction("min_expr", *args)


def delayed_max_expr(*args):
    return DelayedFunction("max_expr", *args)


# ========== COMPOSITION MIXIN ==========


class CompositionMixin:
    """Mixin class providing sub-problem composition functionality."""

    # These attributes/methods will be provided by other mixins in the final Problem class
    variables: dict[str, FieldQuantity]
    sub_problems: dict[str, Any]
    logger: Any
    equations: list[Any]

    def solve(self, max_iterations: int = 100, tolerance: float = 1e-9) -> dict[str, Any]:
        """
        SIMPLIFIED SOLVE: Treat composed problems exactly like simple problems.

        Variables and equations are already flattened during class initialization.
        Just delegate to the standard Problem.solve() method.

        No hardcoded patterns, no special recalculation methods.
        Works for any engineering equations.
        """
        try:
            # Variables and equations are already flattened during _extract_from_class_variables()
            # Just delegate to base Problem.solve() method
            return super().solve(max_iterations, tolerance)  # type: ignore[misc]
        except Exception as e:
            self.logger.error(f"Composed problem solving failed: {e}")
            raise

    # These methods will be provided by Problem class
    def add_variable(self, variable: FieldQuantity) -> None:
        """Add variable to problem. Provided by Problem class."""
        del variable  # Mark as used
        ...

    def add_equation(self, equation: Equation) -> None:
        """Add equation to problem. Provided by Problem class."""
        del equation  # Mark as used
        ...

    def _clone_variable(self, variable: FieldQuantity) -> FieldQuantity:  # type: ignore[return]
        """Clone a variable. Provided by Problem class."""
        del variable  # Mark as used
        ...

    def _recreate_validation_checks(self) -> None: ...

    def _extract_from_class_variables(self):
        """Extract variables, equations, and sub-problems from class-level definitions."""
        self._extract_sub_problems()
        self._extract_direct_variables()
        self._recreate_validation_checks()
        self._create_composite_equations()
        self._extract_equations()
        self._process_variable_sharing()
        # Ensure all equations use canonical variable references
        self._canonicalize_all_equation_variables()

        # Generic retrofitting - replace constants with variables where possible
        self._retrofit_constants_to_variables()

    def _extract_sub_problems(self):
        """Extract and integrate sub-problems from class-level definitions."""
        if hasattr(self.__class__, "_original_sub_problems"):
            original_sub_problems = getattr(self.__class__, "_original_sub_problems", {})
            for attr_name, sub_problem in original_sub_problems.items():
                self._integrate_sub_problem(sub_problem, attr_name)

    def _extract_direct_variables(self):
        """Extract direct variables from class-level definitions."""
        processed_symbols = set()

        # Single pass through class attributes to collect variables
        for attr_name, attr_value in self._get_class_attributes():
            # Handle both direct FieldQuantity objects and wrapped ones
            actual_var = attr_value
            if hasattr(attr_value, "_wrapped") and isinstance(attr_value._wrapped, FieldQuantity):
                actual_var = attr_value._wrapped
            elif not isinstance(attr_value, FieldQuantity):
                continue

            # Set symbol based on attribute name (T_bar, P, etc.)
            actual_var._symbol = attr_name

            # Skip if we've already processed this symbol
            if actual_var.symbol in processed_symbols:
                continue
            processed_symbols.add(actual_var.symbol)

            # Clone variable to avoid shared state between instances
            cloned_var = self._clone_variable(actual_var)
            self.add_variable(cloned_var)
            # Set the same cloned variable object as instance attribute
            # Use super() to bypass our custom __setattr__ during initialization
            super().__setattr__(attr_name, cloned_var)

    def _extract_equations(self):
        """Extract and process equations from class-level definitions."""
        equations_to_process = self._collect_class_equations()

        for attr_name, equation in equations_to_process:
            try:
                # Fix variable references in the equation
                final_equation = self._fix_equation_variable_references(equation)

                # Add equation to the problem
                self.add_equation(final_equation)
                # Set the equation as an instance attribute
                setattr(self, attr_name, final_equation)
            except Exception as e:
                # Log but continue - some equations might fail during class definition
                self.logger.warning(f"Failed to process equation {attr_name}: {e}")
                # Still set the original equation as attribute
                setattr(self, attr_name, equation)

    def replace_sub_variables(self, system_var, sub_vars):
        """
        Share a system variable with sub-problem variables by creating assignment equations.

        This is a cleaner alternative to manually creating equations like:
        header_P_eqn = equation(header.P, P)

        Args:
            system_var: The system-level variable to share
            sub_vars: List of sub-problem variables that should equal the system variable

        Example:
            self.replace_sub_variables(P, [header.P, branch.P])
        """
        from ..algebra.equation import Equation
        from ..algebra.nodes import VariableReference

        # Use the system variable directly - the composition system should ensure
        # the right variable is passed in from the class-level _variable_sharing
        actual_system_var = system_var

        system_ref = VariableReference(actual_system_var)

        for sub_var in sub_vars:
            # Reset the sub-variable to be unknown so it can be solved
            sub_var.value = None

            # Create assignment equation: sub_var = system_var
            sub_ref = VariableReference(sub_var)
            equation_name = f"{getattr(sub_var, 'name', 'unknown')}_shared_equation"

            equation = Equation(equation_name, sub_ref, system_ref)
            # Insert sharing equations at the beginning so they get solved first
            # This ensures that shared variables get their values before dependent equations are solved
            # This ensures pressure values are established before dependent equations
            self.equations.insert(0, equation)

    def _fix_equation_variable_references(self, equation):
        """Fix variable references in equations to use canonical variables from self.variables."""
        from ..algebra.equation import Equation
        from ..algebra.nodes import VariableReference

        try:
            new_lhs = equation.lhs
            new_rhs = equation.rhs
            changed = False

            # Fix LHS if it's a variable reference
            if isinstance(equation.lhs, VariableReference):
                lhs_var = equation.lhs.variable
                for canonical_var in self.variables.values():
                    if hasattr(lhs_var, "name") and hasattr(canonical_var, "name") and lhs_var.name == canonical_var.name and id(lhs_var) != id(canonical_var):
                        new_lhs = VariableReference(canonical_var)
                        changed = True
                        break

            # Fix RHS if it's a variable reference
            if isinstance(equation.rhs, VariableReference):
                rhs_var = equation.rhs.variable
                for canonical_var in self.variables.values():
                    if hasattr(rhs_var, "name") and hasattr(canonical_var, "name") and rhs_var.name == canonical_var.name and id(rhs_var) != id(canonical_var):
                        new_rhs = VariableReference(canonical_var)
                        changed = True
                        break

            # Return new equation if any references were fixed
            if changed:
                return Equation(equation.name, new_lhs, new_rhs)
            else:
                return equation

        except Exception:
            return equation

    def _process_variable_sharing(self):
        """Process the _variable_sharing class attribute to set up variable sharing automatically."""
        if not hasattr(self.__class__, "_variable_sharing"):
            return

        sharing_config = getattr(self.__class__, "_variable_sharing")  # noqa: B009
        for system_var, sub_vars in sharing_config:
            # Variables are already actual object references, no need to resolve paths
            self.replace_sub_variables(system_var, sub_vars)

    def _canonicalize_all_equation_variables(self):
        """Replace all variable references in equations with canonical ones from self.variables."""
        from ..algebra.equation import Equation

        for i, equation in enumerate(self.equations):
            new_lhs = self._canonicalize_expression(equation.lhs)
            new_rhs = self._canonicalize_expression(equation.rhs)

            if new_lhs != equation.lhs or new_rhs != equation.rhs:
                self.equations[i] = Equation(equation.name, new_lhs, new_rhs)

    def _canonicalize_expression(self, expr):
        """Replace variable references in an expression with canonical ones."""
        from ..algebra.nodes import VariableReference

        if isinstance(expr, VariableReference):
            var = expr.variable
            if hasattr(var, "name"):
                # First priority: Check if there's a system-level variable with this name
                # Look for system attributes that match this variable name
                for attr_name in dir(self):
                    if not attr_name.startswith("_"):  # Skip private attributes
                        attr_value = getattr(self, attr_name, None)
                        if (
                            attr_value
                            and hasattr(attr_value, "name")
                            and hasattr(attr_value, "value")  # Must be a variable
                            and attr_value.name == var.name
                        ):
                            if id(var) != id(attr_value):
                                return VariableReference(attr_value)
                            else:
                                return expr

                        # Also check sub-problem attributes (e.g., header.P, branch.P)
                        if hasattr(attr_value, "__dict__"):  # Check if it's an object with attributes
                            for sub_attr_name in dir(attr_value):
                                if not sub_attr_name.startswith("_"):
                                    try:
                                        sub_attr_value = getattr(attr_value, sub_attr_name, None)
                                        if (
                                            sub_attr_value
                                            and hasattr(sub_attr_value, "name")
                                            and hasattr(sub_attr_value, "value")  # Must be a variable
                                            and sub_attr_value.name == var.name
                                        ):
                                            if id(var) != id(sub_attr_value):
                                                return VariableReference(sub_attr_value)
                                            else:
                                                return expr
                                    except (AttributeError, TypeError):
                                        continue

                # Second priority: Find canonical variable with same name in self.variables
                for _, canonical_var in self.variables.items():
                    if hasattr(canonical_var, "name") and canonical_var.name == var.name:
                        if id(var) != id(canonical_var):
                            return VariableReference(canonical_var)
                        else:
                            return expr
            return expr
        else:
            return expr

    def _retrofit_constants_to_variables(self):
        """
        Generic retrofitting: replace constants in equations with variables where possible.
        Simplified version that avoids complex constant-to-variable matching.
        """
        # For most engineering problems, constants should remain as constants
        # This complex retrofitting is rarely needed and can cause issues
        pass

    def _get_class_attributes(self) -> list[tuple[str, Any]]:
        """Get all non-private class attributes efficiently."""
        return [(attr_name, getattr(self.__class__, attr_name)) for attr_name in dir(self.__class__) if not attr_name.startswith("_")]

    def _collect_class_equations(self) -> list[tuple[str, Any]]:
        """Collect all equation objects from class attributes."""
        equations_to_process = []
        for attr_name, attr_value in self._get_class_attributes():
            if isinstance(attr_value, Equation):
                equations_to_process.append((attr_name, attr_value))
        return equations_to_process

    def _integrate_sub_problem(self, sub_problem, namespace: str) -> None:
        """
        Integrate a sub-problem by flattening its variables with namespace prefixes.
        Creates a simple dotted access pattern: self.header.P becomes self.header_P
        """
        self.sub_problems[namespace] = sub_problem
        proxy_configs = getattr(self.__class__, "_proxy_configurations", {}).get(namespace, {})

        namespace_obj = self._create_namespace_object(sub_problem, namespace, proxy_configs)
        super().__setattr__(namespace, namespace_obj)

        self._integrate_sub_problem_equations(sub_problem, namespace)

    def _create_namespace_object(self, sub_problem, namespace: str, proxy_configs: dict):
        """Create namespace object with all sub-problem variables."""

        # Create a proper namespace class that can handle attribute updates
        class SubProblemNamespace:
            def __init__(self, parent_problem, namespace_prefix):
                self._parent_problem = parent_problem
                self._namespace_prefix = namespace_prefix

            def __setattr__(self, name, value):
                # Handle internal attributes normally
                if name.startswith("_"):
                    super().__setattr__(name, value)
                    return

                # For variable attributes, update both the namespace and main problem
                namespaced_name = f"{self._namespace_prefix}_{name}"
                if hasattr(self, "_parent_problem") and namespaced_name in self._parent_problem.variables:
                    # Update the main problem's variables dictionary
                    self._parent_problem.variables[namespaced_name] = value

                # Update the namespace attribute
                super().__setattr__(name, value)

        namespace_obj = SubProblemNamespace(self, namespace)

        for var_symbol, var in sub_problem.variables.items():
            namespaced_var = self._create_namespaced_variable(var, var_symbol, namespace, proxy_configs)
            self.add_variable(namespaced_var)

            # Create a wrapper that handles .set() calls
            wrapped_var = self._create_namespace_variable_wrapper(namespaced_var, namespace_obj, var_symbol)

            # Set both namespaced access (self.header_P) and dotted access (self.header.P)
            if namespaced_var.symbol is not None:
                super().__setattr__(namespaced_var.symbol, namespaced_var)
            setattr(namespace_obj, var_symbol, wrapped_var)

        return namespace_obj

    def _create_namespace_variable_wrapper(self, variable, namespace_obj, var_symbol):
        """Create a wrapper that intercepts .set() calls and updates the namespace."""

        class NamespaceVariableWrapper(ArithmeticOperationsMixin):
            def __init__(self, wrapped_var, namespace, symbol):
                self._wrapped_var = wrapped_var
                self._namespace = namespace
                self._symbol = symbol

            def __getattr__(self, name):
                # Guard against deepcopy and pickle operations that cause recursion
                if name.startswith('_') or name in {
                    '__setstate__', '__getstate__', '__getnewargs__', '__getnewargs_ex__',
                    '__reduce__', '__reduce_ex__', '__copy__', '__deepcopy__',
                    '__getattribute__', '__setattr__', '__delattr__',
                    '__dict__', '__weakref__', '__class__'
                }:
                    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

                # Prevent infinite recursion by checking if _wrapped_var exists
                if not hasattr(self, '_wrapped_var'):
                    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

                # For all other attributes, delegate to the wrapped variable
                try:
                    return getattr(self._wrapped_var, name)
                except AttributeError as err:
                    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'") from err

            def __deepcopy__(self, memo):
                # Don't allow deepcopy of NamespaceVariableWrapper - just return self
                _ = memo  # Mark as used to avoid linting warnings
                return self

            def __setattr__(self, name, value):
                # Handle wrapper's own attributes
                if name.startswith("_"):
                    super().__setattr__(name, value)
                else:
                    # Delegate to wrapped variable (this fixes the solver issue)
                    setattr(self._wrapped_var, name, value)

            def set(self, value, unit=None):
                # Call the original set method
                setter = self._wrapped_var.set(value, unit)

                if unit is not None:
                    # If unit is provided, we have the final variable
                    setattr(self._namespace, self._symbol, setter)
                    return setter
                else:
                    # Return a wrapped setter that updates namespace on unit access
                    return NamespaceSetterWrapper(setter, self._namespace, self._symbol)

            def __str__(self):
                return str(self._wrapped_var)

            def __repr__(self):
                return repr(self._wrapped_var)

        # Also define the setter wrapper class here
        class NamespaceSetterWrapper:
            def __init__(self, setter, namespace, symbol):
                self._setter = setter
                self._namespace = namespace
                self._symbol = symbol

            def __getattr__(self, name):
                # Guard against deepcopy and pickle operations that cause recursion
                if name.startswith('_') or name in {
                    '__setstate__', '__getstate__', '__getnewargs__', '__getnewargs_ex__',
                    '__reduce__', '__reduce_ex__', '__copy__', '__deepcopy__',
                    '__getattribute__', '__setattr__', '__delattr__',
                    '__dict__', '__weakref__', '__class__'
                }:
                    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

                # Prevent infinite recursion by checking if _setter exists
                if not hasattr(self, '_setter'):
                    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

                # When a unit is accessed (like .inch), get the final variable and update namespace
                final_var = getattr(self._setter, name)
                setattr(self._namespace, self._symbol, final_var)
                return final_var

            def __deepcopy__(self, memo):
                # Don't allow deepcopy of NamespaceSetterWrapper - just return self
                _ = memo  # Mark as used to avoid linting warnings
                return self

        return NamespaceVariableWrapper(variable, namespace_obj, var_symbol)

    def _integrate_sub_problem_equations(self, sub_problem, namespace: str):
        """Integrate equations from sub-problem with proper namespacing."""
        for equation in sub_problem.equations:
            try:
                # Skip conditional equations for variables that are overridden to known values in composition
                if self._should_skip_subproblem_equation(equation, namespace):
                    continue

                # Check if equation is already namespaced (contains namespace prefix)
                equation_str = str(equation)
                if f"{namespace}_" in equation_str:
                    # Equation is already namespaced, add it directly
                    self.add_equation(equation)
                else:
                    # Equation needs namespacing
                    namespaced_equation = self._namespace_equation(equation, namespace)
                    if namespaced_equation:
                        self.add_equation(namespaced_equation)
            except Exception as e:
                self.logger.debug(f"Failed to namespace equation from {namespace}: {e}")

    def _create_namespaced_variable(self, var: FieldQuantity, var_symbol: str, namespace: str, proxy_configs: dict) -> FieldQuantity:
        """Create a namespaced variable with proper configuration."""
        namespaced_symbol = f"{namespace}_{var_symbol}"
        namespaced_var = self._clone_variable(var)
        namespaced_var._symbol = namespaced_symbol
        namespaced_var.name = f"{var.name} ({namespace.title()})"

        # Apply proxy configuration if available
        if var_symbol in proxy_configs:
            config = proxy_configs[var_symbol]
            # For the unified Quantity API, set value and preferred instead of quantity
            quantity = config["quantity"]
            if quantity is not None and hasattr(quantity, "value") and hasattr(quantity, "preferred"):
                namespaced_var.value = quantity.value
                namespaced_var.preferred = quantity.preferred
            elif quantity is None and not config["is_known"]:
                # Handle the case where variable should be unknown (value = None)
                namespaced_var.value = None
            # is_known is handled by whether value is None or not

        return namespaced_var

    def _namespace_equation(self, equation, namespace: str):
        """
        Create a namespaced version of an equation by prefixing all variable references.
        """

        def _create_namespaced():
            # Get all variable symbols in the equation
            variables_in_eq = equation.get_all_variables()

            # Create mapping from original symbols to namespaced symbols
            symbol_mapping = self._create_symbol_mapping(variables_in_eq, namespace)
            if not symbol_mapping:
                return None

            # Create new equation with namespaced references
            return self._create_namespaced_equation(equation, symbol_mapping)

        return _safe_execute(_create_namespaced)

    def _create_symbol_mapping(self, variables_in_eq: set[str], namespace: str) -> dict[str, str]:
        """Create mapping from original symbols to namespaced symbols."""
        symbol_mapping = {}
        for var_symbol in variables_in_eq:
            namespaced_symbol = f"{namespace}_{var_symbol}"
            if namespaced_symbol in self.variables:
                symbol_mapping[var_symbol] = namespaced_symbol
        return symbol_mapping

    def _create_namespaced_equation(self, equation: Equation, symbol_mapping: dict[str, str]) -> Equation | None:
        """Create new equation with namespaced references."""
        # For LHS, we need a Variable object
        # For RHS, we need proper expression structure
        namespaced_lhs = self._namespace_expression_for_lhs(equation.lhs, symbol_mapping)
        namespaced_rhs = self._namespace_expression(equation.rhs, symbol_mapping)

        if namespaced_lhs and namespaced_rhs:
            # Use the new API equation() function instead of .equals() method
            from ..algebra import equation as create_equation

            namespaced_equation_name = f"{equation.name}_namespaced"
            return create_equation(namespaced_lhs, namespaced_rhs, namespaced_equation_name)
        return None

    def _namespace_expression(self, expr, symbol_mapping):
        """
        Create a namespaced version of an expression by replacing variable references.
        """
        # Mapping of expression types to their namespace processors
        processors = {
            VariableReference: self._namespace_variable_reference,
            BinaryOperation: self._namespace_binary_operation,
            ConditionalExpression: self._namespace_conditional_expression,
            Constant: self._namespace_constant_if_needed,
        }

        # Check direct type matches first
        for expr_type, processor in processors.items():
            if isinstance(expr, expr_type):
                return processor(expr, symbol_mapping)

        # Handle FieldQuantity with symbol check
        if isinstance(expr, FieldQuantity) and expr.symbol in symbol_mapping:
            return self._namespace_variable_object(expr, symbol_mapping)

        # Handle special cases with attribute checks
        if self._is_unary_operation(expr):
            return self._namespace_unary_operation(expr, symbol_mapping)
        elif self._is_binary_function(expr):
            return self._namespace_binary_function(expr, symbol_mapping)

        return expr

    def _namespace_constant_if_needed(self, expr: Constant, symbol_mapping: dict[str, str]):
        """
        Check if a Constant corresponds to a variable that should be namespaced.
        This handles cases where expressions were evaluated to constants at class definition time.
        """
        # For most cases, constants should remain as constants
        # This is a simplified version that avoids complex value matching
        _ = symbol_mapping  # Mark as intentionally unused
        return expr

    def _namespace_variable_reference(self, expr: VariableReference, symbol_mapping: dict[str, str]) -> VariableReference:
        """Namespace a VariableReference object."""
        # VariableReference uses the 'name' property which returns the symbol if available
        symbol = expr.name
        if symbol in symbol_mapping:
            namespaced_symbol = symbol_mapping[symbol]
            if namespaced_symbol in self.variables:
                return VariableReference(self.variables[namespaced_symbol])
        return expr

    def _namespace_variable_object(self, expr: FieldQuantity, symbol_mapping: dict[str, str]) -> VariableReference | FieldQuantity:
        """Namespace a Variable object."""
        if expr.symbol is None:
            return expr
        namespaced_symbol = symbol_mapping[expr.symbol]
        if namespaced_symbol in self.variables:
            # Return VariableReference for use in expressions, not the Variable itself
            return VariableReference(self.variables[namespaced_symbol])
        return expr

    def _namespace_binary_operation(self, expr: BinaryOperation, symbol_mapping: dict[str, str]) -> BinaryOperation:
        """Namespace a BinaryOperation."""
        namespaced_left = self._namespace_expression(expr.left, symbol_mapping)
        namespaced_right = self._namespace_expression(expr.right, symbol_mapping)
        return BinaryOperation(expr.operator, wrap_operand(namespaced_left), wrap_operand(namespaced_right))

    def _namespace_unary_operation(self, expr, symbol_mapping):
        """Namespace a UnaryFunction."""
        namespaced_operand = self._namespace_expression(expr.operand, symbol_mapping)
        return type(expr)(expr.operator, namespaced_operand)

    def _namespace_binary_function(self, expr, symbol_mapping):
        """Namespace a BinaryFunction."""
        namespaced_left = self._namespace_expression(expr.left, symbol_mapping)
        namespaced_right = self._namespace_expression(expr.right, symbol_mapping)
        return type(expr)(expr.function_name, namespaced_left, namespaced_right)

    def _namespace_conditional_expression(self, expr: ConditionalExpression, symbol_mapping: dict[str, str]) -> ConditionalExpression:
        """Namespace a ConditionalExpression."""
        namespaced_condition = self._namespace_expression(expr.condition, symbol_mapping)
        namespaced_true_expr = self._namespace_expression(expr.true_expr, symbol_mapping)
        namespaced_false_expr = self._namespace_expression(expr.false_expr, symbol_mapping)

        return ConditionalExpression(wrap_operand(namespaced_condition), wrap_operand(namespaced_true_expr), wrap_operand(namespaced_false_expr))

    def _namespace_expression_for_lhs(self, expr, symbol_mapping: dict[str, str]) -> FieldQuantity | None:
        """
        Create a namespaced version of an expression for LHS, returning Variable objects.
        """
        if isinstance(expr, VariableReference):
            # VariableReference uses the 'name' property which returns the symbol if available
            symbol = expr.name
            if symbol and symbol in symbol_mapping:
                namespaced_symbol = symbol_mapping[symbol]
                if namespaced_symbol in self.variables:
                    return self.variables[namespaced_symbol]
            # If we can't find a mapping, return None since VariableReference doesn't have .equals()
            return None
        elif isinstance(expr, FieldQuantity) and expr.symbol in symbol_mapping:
            # This is a Variable object
            namespaced_symbol = symbol_mapping[expr.symbol]
            if namespaced_symbol in self.variables:
                return self.variables[namespaced_symbol]
            return expr
        else:
            return expr

    def _is_unary_operation(self, expr) -> bool:
        """Check if expression is a unary operation."""
        # UnaryFunction and similar classes have an 'operand' attribute
        return hasattr(expr, "operand") and hasattr(expr, "operator")

    def _is_binary_function(self, expr) -> bool:
        """Check if expression is a binary function."""
        # BinaryFunction classes have 'function_name', 'left', and 'right' attributes
        return hasattr(expr, "function_name") and hasattr(expr, "left") and hasattr(expr, "right")

    def _should_skip_subproblem_equation(self, equation, namespace: str) -> bool:
        """
        Check if an equation from a sub-problem should be skipped during integration.

        Skip conditional equations for variables that are set to known values in the composed problem.
        """
        try:
            # Check if this is a conditional equation
            if not self._is_conditional_equation(equation):
                return False

            # Check if the LHS variable would be set to a known value in composition
            original_symbol = self._get_equation_lhs_symbol(equation)
            if original_symbol is not None:
                namespaced_symbol = f"{namespace}_{original_symbol}"

                # Check if this namespaced variable exists and is already known
                if namespaced_symbol in self.variables:
                    var = self.variables[namespaced_symbol]
                    if var.is_known:
                        # The variable is already set to a known value in composition,
                        # so skip the conditional equation that would override it
                        self.logger.debug(f"Skipping conditional equation for {namespaced_symbol} (already known: {var.quantity})")
                        return True

            return False

        except Exception:
            return False

    def _create_composite_equations(self):
        """
        Create composite equations for common patterns in sub-problems.
        This is a placeholder for future composite equation auto-generation.
        """
        # Auto-generation of composite equations is not currently used
        # but the method is kept for potential future use
        pass

    # These methods will be provided by Problem class
    def _process_equation(self, attr_name: str, equation: Equation) -> bool:
        """Stub method - will be provided by Problem class."""
        _, _ = attr_name, equation  # Mark parameters as intentionally unused
        return True

    def _is_conditional_equation(self, equation: Equation) -> bool:
        """Stub method - will be provided by Problem class."""
        _ = equation  # Mark parameter as intentionally unused
        return False

    def _get_equation_lhs_symbol(self, equation: Equation) -> str | None:
        """Stub method - will be provided by Problem class."""
        _ = equation  # Mark parameter as intentionally unused
        return None


# ========== METACLASS SYSTEM ==========


# Custom exceptions for better error handling
class MetaclassError(Exception):
    """Base exception for metaclass-related errors."""

    pass


class SubProblemProxyError(MetaclassError):
    """Raised when sub-problem proxy creation fails."""

    pass


class NamespaceError(MetaclassError):
    """Raised when namespace operations fail."""

    pass


class ProblemMeta(type):
    """
    Metaclass that processes class-level sub-problems to create proper namespace proxies
    BEFORE any equations are evaluated.

    This metaclass enables clean composition syntax like:
        class MyProblem(EngineeringProblem):
            header = create_pipe_problem()
            branch = create_pipe_problem()
            # Equations can reference header.P, branch.T, etc.
    """

    # Declare the attributes that will be dynamically added to created classes
    _original_sub_problems: dict[str, Any]
    _proxy_configurations: dict[str, dict[str, Any]]
    _class_checks: dict[str, Any]

    @classmethod
    def __prepare__(mcs, *args, **kwargs) -> ProxiedNamespace:
        """
        Called before the class body is evaluated.
        Returns a custom namespace that proxies sub-problems.

        Args:
            *args: Positional arguments (name, bases) - unused but required by protocol
            **kwargs: Additional keyword arguments - unused but required by protocol

        Returns:
            ProxiedNamespace that will handle sub-problem proxying
        """
        # Parameters are required by metaclass protocol but not used in this implementation
        del args, kwargs  # Explicitly acknowledge unused parameters
        return ProxiedNamespace()

    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: ProxiedNamespace, **kwargs) -> type:
        """
        Create the new class with properly integrated sub-problems.

        Args:
            name: Name of the class being created
            bases: Base classes
            namespace: The ProxiedNamespace containing proxied sub-problems
            **kwargs: Additional keyword arguments - unused but required by protocol

        Returns:
            The newly created class with metaclass attributes

        Raises:
            MetaclassError: If class creation fails due to metaclass issues
        """
        # kwargs is required by metaclass protocol but not used in this implementation
        del kwargs  # Explicitly acknowledge unused parameter
        try:
            # Validate the namespace
            if not isinstance(namespace, ProxiedNamespace):
                raise MetaclassError(f"Expected ProxiedNamespace, got {type(namespace)}")

            # Extract the original sub-problems and proxy objects from the namespace
            sub_problem_proxies = getattr(namespace, "_sub_problem_proxies", {})
            proxy_objects = getattr(namespace, "_proxy_objects", {})

            # Validate that proxy objects are consistent
            if set(sub_problem_proxies.keys()) != set(proxy_objects.keys()):
                raise MetaclassError("Inconsistent proxy state: sub-problem and proxy object keys don't match")

            # Create the class normally
            cls = super().__new__(mcs, name, bases, dict(namespace))

            # Store the original sub-problems and proxy configurations for later integration
            cls._original_sub_problems = sub_problem_proxies

            # Extract configurations safely with error handling
            proxy_configurations = {}
            for proxy_name, proxy in proxy_objects.items():
                try:
                    # Cache configurations to avoid recomputation
                    if not hasattr(proxy, "_cached_configurations"):
                        proxy._cached_configurations = proxy.get_configurations()
                    proxy_configurations[proxy_name] = proxy._cached_configurations
                except Exception as e:
                    raise SubProblemProxyError(f"Failed to get configurations from proxy '{proxy_name}': {e}") from e

            cls._proxy_configurations = proxy_configurations

            # Collect Check objects from class attributes
            checks = {}
            for attr_name, attr_value in namespace.items():
                if isinstance(attr_value, Rules):
                    checks[attr_name] = attr_value

            cls._class_checks = checks

            return cls

        except Exception as e:
            # Re-raise MetaclassError and SubProblemProxyError as-is
            if isinstance(e, MetaclassError | SubProblemProxyError):
                raise
            # Wrap other exceptions
            raise MetaclassError(f"Failed to create class '{name}': {e}") from e


class ProxiedNamespace(dict):
    """
    Custom namespace that automatically proxies sub-problems as they're added.

    This namespace intercepts class attribute assignments during class creation
    and automatically wraps EngineeringProblem objects in SubProblemProxy objects.
    This enables clean composition syntax where sub-problems can be referenced
    with dot notation in equations.

    Example:
        class ComposedProblem(EngineeringProblem):
            header = create_pipe_problem()  # Gets proxied automatically
            branch = create_pipe_problem()  # Gets proxied automatically
            # Now equations can use header.P, branch.T, etc.
    """

    def __init__(self) -> None:
        """Initialize the proxied namespace with empty storage."""
        super().__init__()
        self._sub_problem_proxies: dict[str, Any] = {}
        self._proxy_objects: dict[str, SubProblemProxy] = {}

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Intercept attribute assignment and proxy sub-problems automatically.

        Args:
            key: The attribute name being set
            value: The value being assigned

        Raises:
            NamespaceError: If namespace operation fails
            SubProblemProxyError: If proxy creation fails
        """
        try:
            if self._is_sub_problem(key, value):
                self._create_and_store_proxy(key, value)
            elif self._is_variable(value):
                self._set_variable_symbol_and_store(key, value)
            else:
                super().__setitem__(key, value)
        except Exception as e:
            if isinstance(e, NamespaceError | SubProblemProxyError):
                raise
            raise NamespaceError(f"Failed to set attribute '{key}': {e}") from e

    def _is_sub_problem(self, key: str, value: Any) -> bool:
        """
        Determine if a value should be treated as a sub-problem.

        Args:
            key: The attribute name
            value: The value being assigned

        Returns:
            True if this should be proxied as a sub-problem
        """
        # Quick checks first (fail fast)
        if key.startswith(PRIVATE_ATTRIBUTE_PREFIX) or key in RESERVED_ATTRIBUTES:
            return False

        # Check for None or basic types that definitely aren't sub-problems
        if value is None or isinstance(value, str | int | float | bool | list | dict):
            return False

        # Cache hasattr results to avoid repeated attribute lookups
        if not hasattr(self, "_attr_cache"):
            self._attr_cache = {}

        # Use object id as cache key since objects are unique
        cache_key = (id(value), tuple(SUB_PROBLEM_REQUIRED_ATTRIBUTES))
        if cache_key not in self._attr_cache:
            self._attr_cache[cache_key] = all(hasattr(value, attr) for attr in SUB_PROBLEM_REQUIRED_ATTRIBUTES)

        return self._attr_cache[cache_key]

    def _is_variable(self, value: Any) -> bool:
        """
        Determine if a value is a Variable (Quantity) that needs processing.

        Args:
            value: The value being assigned

        Returns:
            True if this is a Variable that should be processed
        """
        try:
            return isinstance(value, FieldQuantity)
        except ImportError:
            return False

    def _set_variable_symbol_and_store(self, key: str, value: Any) -> None:
        """
        Set the variable's symbol to the attribute name and store it.

        Args:
            key: The attribute name to use as symbol
            value: The Variable object
        """
        try:
            # Set the symbol to the attribute name (use private attribute)
            value._symbol = key
            # Add expression-building capability to the variable and get wrapped version
            enhanced_variable = self._add_expression_methods(value)
            # Store the enhanced variable
            super().__setitem__(key, enhanced_variable)
        except Exception as e:
            raise NamespaceError(f"Failed to set symbol for variable '{key}': {e}") from e

    def _add_expression_methods(self, variable):
        """
        Wrap the variable with expression-building methods that create DelayedExpression objects.
        This allows expressions like 'D - 2 * T' to work during Problem class definition
        even when variables have no values.
        """

        class ExpressionEnabledWrapper(ArithmeticOperationsMixin):
            def __init__(self, wrapped_var):
                self._wrapped = wrapped_var

            def __getattr__(self, name):
                # Guard against deepcopy and pickle operations that cause recursion
                if name.startswith('_') or name in {
                    '__setstate__', '__getstate__', '__getnewargs__', '__getnewargs_ex__',
                    '__reduce__', '__reduce_ex__', '__copy__', '__deepcopy__',
                    '__getattribute__', '__setattr__', '__delattr__',
                    '__dict__', '__weakref__', '__class__'
                }:
                    raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

                # Prevent infinite recursion by checking if _wrapped exists
                if not hasattr(self, '_wrapped'):
                    raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

                # Delegate all attribute access to the wrapped variable
                return getattr(self._wrapped, name)

            def __deepcopy__(self, memo):
                # Don't allow deepcopy of wrapper objects - just return self
                _ = memo  # Mark as used to avoid linting warnings
                return self

            def __setattr__(self, name, value):
                # Handle wrapper attributes normally
                if name == "_wrapped":
                    super().__setattr__(name, value)
                else:
                    # Delegate to wrapped variable
                    setattr(self._wrapped, name, value)

            @property
            def value(self):
                """Delegate value access to wrapped variable."""
                return getattr(self._wrapped, "value", None)

            def __float__(self):
                """Delegate float conversion to wrapped variable."""
                return float(self._wrapped)

        return ExpressionEnabledWrapper(variable)

    def _create_and_store_proxy(self, key: str, value: Any) -> None:
        """
        Create a proxy for the sub-problem and store references.

        Args:
            key: The attribute name for the sub-problem
            value: The sub-problem object to proxy

        Raises:
            SubProblemProxyError: If proxy creation fails
            NamespaceError: If key already exists as a sub-problem
        """
        # Check for conflicts
        if key in self._sub_problem_proxies:
            raise NamespaceError(f"Sub-problem '{key}' already exists in namespace")

        try:
            # Store the original sub-problem
            self._sub_problem_proxies[key] = value

            # Create and store the proxy
            proxy = SubProblemProxy(value, key)
            self._proxy_objects[key] = proxy

            # Set the proxy in the namespace
            super().__setitem__(key, proxy)

        except Exception as e:
            # Clean up partial state on failure
            self._sub_problem_proxies.pop(key, None)
            self._proxy_objects.pop(key, None)
            raise SubProblemProxyError(f"Failed to create proxy for sub-problem '{key}': {e}") from e


# Export all relevant classes
__all__ = [
    "CompositionMixin",
    "ProblemMeta",
    "ProxiedNamespace",
    "SubProblemProxy",
    "ConfigurableVariable",
    "DelayedEquation",
    "DelayedVariableReference",
    "DelayedExpression",
    "DelayedFunction",
    "delayed_sin",
    "delayed_min_expr",
    "delayed_max_expr",
    "MetaclassError",
    "SubProblemProxyError",
    "NamespaceError",
]
