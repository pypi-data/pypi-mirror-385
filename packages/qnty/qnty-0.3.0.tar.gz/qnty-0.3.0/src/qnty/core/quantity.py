"""
Unified Quantity class that combines the functionality of both Quantity and FieldQuantity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Self, TypeVar, cast, overload

from .dimension import Dimension
from .unit import Unit, ureg

if TYPE_CHECKING:
    from . import quantity_catalog

D = TypeVar("D")


@dataclass
class Quantity(Generic[D]):
    """
    A unified quantity that can be either:
    - A concrete value with dimension (when value is set)
    - A named placeholder (when value is None)

    Supports arithmetic, unit conversions, and all FieldQuantity features.
    """

    name: str
    dim: Dimension
    value: float | None = None
    preferred: Unit[D] | None = None
    _symbol: str | None = None
    _output_unit: Unit[D] | None = None

    def __post_init__(self):
        """Auto-detect symbol from variable assignment if not set."""
        # Only auto-detect variable names when needed for equation solving,
        # not for every quantity creation (performance optimization)
        pass

    def _detect_variable_name(self) -> str | None:
        """Detect the variable name from the assignment context."""
        import inspect
        import re

        try:
            # Get the frame where this quantity was created
            frame = inspect.currentframe()
            if frame is None:
                return None

            # Go up the stack to find the assignment
            for _ in range(10):  # Check up to 10 frames
                frame = frame.f_back
                if frame is None:
                    break

                # Get the code context
                code = frame.f_code
                local_vars = frame.f_locals

                # Look for assignment patterns in the source
                # This handles: var = Quantity(...), var = Q(...), var = Length(...).set(...).unit
                try:
                    import linecache

                    line = linecache.getline(code.co_filename, frame.f_lineno).strip()

                    # Match assignment patterns
                    # Pattern 1: var = expression
                    match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*=", line)
                    if match:
                        var_name = match.group(1)
                        # Verify this is actually our object being assigned
                        # by checking if we're in the process of creating it
                        return var_name

                    # Pattern 2: self.var = expression (for class attributes)
                    match = re.match(r"^self\.([a-zA-Z_][a-zA-Z0-9_]*)\s*=", line)
                    if match:
                        return match.group(1)

                except Exception:
                    continue

        except Exception:
            pass

        return None

    @property
    def symbol(self) -> str:
        """Get the symbol for this quantity (auto-detected or manually set)."""
        if self._symbol is None:
            # Lazy detection: only when symbol is actually needed
            self._symbol = self._detect_variable_name()
        return self._symbol or self.name

    # Factory methods for different use cases
    @classmethod
    def from_value(cls, value: float, unit: Unit[D], name: str = "unnamed") -> Quantity[D]:
        """Create a quantity from a value and unit (replaces Q function)."""
        return cls(name=name, dim=unit.dim, value=unit.si_factor * value + unit.si_offset)

    @classmethod
    def unknown(cls, name: str, dim: Dimension, preferred: Unit[D] | None = None) -> Quantity[D]:
        """Create an unknown/placeholder quantity."""
        return cls(name=name, dim=dim, preferred=preferred)

    # ---- Properties ----
    @property
    def is_known(self) -> bool:
        return self.value is not None

    @property
    def quantity(self) -> Quantity[D] | None:
        """Compatibility property for code expecting .q"""
        return self if self.value is not None else None

    def _require_value(self) -> float:
        if self.value is None:
            raise ValueError(f"Quantity '{self.name}' has no numeric value")
        return float(self.value)

    def _value_in_unit(self, unit: Unit[D]) -> float:
        """Return this quantity's magnitude expressed in the provided unit."""
        si_value = self._require_value()
        return (si_value - unit.si_offset) / unit.si_factor

    def magnitude(self, unit: Unit[D] | str | None = None) -> float:
        """Convenience accessor that returns the value expressed in a desired unit."""
        if unit is None:
            target = self.preferred or ureg.preferred_for(self.dim) or ureg.si_unit_for(self.dim)
            if target is None:
                return self._require_value()
            return self._value_in_unit(target)

        if isinstance(unit, str):
            resolved = ureg.resolve(unit, dim=self.dim)
            if resolved is None:
                raise ValueError(f"Unknown unit '{unit}'")
            unit = resolved

        return self._value_in_unit(unit)

    # ---- Setting values ----
    @overload
    def set(self, value: float) -> QuantitySetter[D]: ...
    @overload
    def set(self, value: float, unit: Unit[D]) -> Self: ...
    @overload
    def set(self, value: float, unit: str) -> Self: ...

    def set(self, value: float, unit: Unit[D] | str | None = None) -> QuantitySetter[D] | Self:
        """Set the value of this quantity."""
        if unit is None:
            return QuantitySetter(self, value)

        if isinstance(unit, str):
            resolved = ureg.resolve(unit, dim=self.dim)
            if resolved is None:
                raise ValueError(f"Unknown unit '{unit}'")
            unit = resolved

        # Create new instance with value set
        new_q = Quantity(name=self.name, dim=self.dim, value=unit.si_factor * value + unit.si_offset, preferred=self.preferred or unit)
        return new_q  # type: ignore

    def prefer(self, unit: Unit[D]) -> Quantity[D]:
        """Set preferred display unit."""
        return Quantity(name=self.name, dim=self.dim, value=self.value, preferred=unit)

    def output_unit(self, unit: Unit[D] | str) -> Quantity[D]:
        """Set desired output unit for display and reporting."""
        if isinstance(unit, str):
            resolved = ureg.resolve(unit, dim=self.dim)
            if resolved is None:
                raise ValueError(f"Unknown unit '{unit}'")
            unit = resolved

        # Create new instance with output unit set, preserving all other attributes
        new_q = Quantity(name=self.name, dim=self.dim, value=self.value, preferred=self.preferred, _symbol=self._symbol, _output_unit=unit)
        return new_q

    def to(self, unit: Unit[D] | str) -> Quantity[D]:
        """Direct conversion method for maximum performance."""
        if isinstance(unit, str):
            resolved = ureg.resolve(unit, dim=self.dim)
            if resolved is None:
                raise ValueError(f"Unknown unit '{unit}'")
            unit = resolved

        if self.value is None:
            raise ValueError(f"Cannot convert unknown quantity '{self.name}' to unit")

        si_value = float(self.value)

        # Optimized Quantity creation that preserves SI storage while
        # tagging the preferred display unit for callers.
        new_q = object.__new__(Quantity)
        new_q.name = "converted"
        new_q.dim = self.dim
        new_q.value = si_value
        new_q.preferred = unit
        new_q._symbol = None
        new_q._output_unit = self._output_unit
        return new_q

    @property
    def to_unit(self) -> UnitApplier[D]:
        """Convert to different unit via attribute access."""
        return UnitApplier(self)

    @property
    def as_unit(self) -> UnitChanger[D]:
        """Change display unit via attribute access."""
        return UnitChanger(self)

    # ----- arithmetic -----
    def __mul__(self, other: Quantity | float | int) -> Quantity:
        if isinstance(other, Quantity):
            if self.value is None or other.value is None:
                raise ValueError("Cannot perform arithmetic on unknown quantities")
            result_value = self.value * other.value
            return Quantity(name=f"{result_value}", dim=self.dim * other.dim, value=result_value)
        if self.value is None:
            raise ValueError("Cannot perform arithmetic on unknown quantities")
        result_value = self.value * float(other)
        return Quantity(name=f"{result_value}", dim=self.dim, value=result_value)

    def __truediv__(self, other: Quantity | float | int) -> Quantity:
        if isinstance(other, Quantity):
            if self.value is None or other.value is None:
                raise ValueError("Cannot perform arithmetic on unknown quantities")
            result_value = self.value / other.value
            return Quantity(name=f"{result_value}", dim=self.dim / other.dim, value=result_value)
        if self.value is None:
            raise ValueError("Cannot perform arithmetic on unknown quantities")
        result_value = self.value / float(other)
        return Quantity(name=f"{result_value}", dim=self.dim, value=result_value)

    def __pow__(self, k: int) -> Quantity:
        if self.value is None:
            raise ValueError("Cannot perform arithmetic on unknown quantities")
        result_value = self.value**k
        return Quantity(name=f"{result_value}", dim=self.dim**k, value=result_value)

    def __add__(self, other: Quantity | float | int) -> Quantity:
        if isinstance(other, Quantity):
            if self.dim != other.dim:
                raise TypeError("Dimension mismatch in addition")
            if self.value is None or other.value is None:
                raise ValueError("Cannot perform arithmetic on unknown quantities")
            result_value = self.value + other.value
            return Quantity(name=f"{result_value}", dim=self.dim, value=result_value)
        # Handle numeric types - only for dimensionless quantities
        # TODO: ensure dimensionless angles are handled correctly later
        if not self.dim.is_dimensionless():
            raise TypeError(f"Cannot add dimensionless number to dimensional quantity {self.dim}")
        if self.value is None:
            raise ValueError("Cannot perform arithmetic on unknown quantities")
        result_value = self.value + float(other)
        return Quantity(name=f"{result_value}", dim=self.dim, value=result_value)

    def __sub__(self, other: Quantity | float | int) -> Quantity:
        if isinstance(other, Quantity):
            if self.dim != other.dim:
                raise TypeError("Dimension mismatch in subtraction")
            if self.value is None or other.value is None:
                raise ValueError("Cannot perform arithmetic on unknown quantities")
            result_value = self.value - other.value
            return Quantity(name=f"{result_value}", dim=self.dim, value=result_value)
        # Handle numeric types - only for dimensionless quantities
        # TODO: ensure dimensionless angles are handled correctly later
        if not self.dim.is_dimensionless():
            raise TypeError(f"Cannot subtract dimensionless number from dimensional quantity {self.dim}")
        if self.value is None:
            raise ValueError("Cannot perform arithmetic on unknown quantities")
        result_value = self.value - float(other)
        return Quantity(name=f"{result_value}", dim=self.dim, value=result_value)

    # Reverse arithmetic operations
    def __radd__(self, other: float | int) -> Quantity:
        """Handle: number + quantity"""
        # Only allowed for dimensionless quantities
        # TODO: ensure dimensionless angles are handled correctly later
        if not self.dim.is_dimensionless():
            raise TypeError(f"Cannot add dimensional quantity {self.dim} to dimensionless number")
        if self.value is None:
            raise ValueError("Cannot perform arithmetic on unknown quantities")
        result_value = float(other) + self.value
        return Quantity(name=f"{result_value}", dim=self.dim, value=result_value)

    def __rsub__(self, other: float | int) -> Quantity:
        """Handle: number - quantity"""
        # Only allowed for dimensionless quantities
        # TODO: ensure dimensionless angles are handled correctly later
        if not self.dim.is_dimensionless():
            raise TypeError(f"Cannot subtract dimensional quantity {self.dim} from dimensionless number")
        if self.value is None:
            raise ValueError("Cannot perform arithmetic on unknown quantities")
        result_value = float(other) - self.value
        return Quantity(name=f"{result_value}", dim=self.dim, value=result_value)

    def __rmul__(self, other: float | int) -> Quantity:
        """Handle: number * quantity"""
        if self.value is None:
            raise ValueError("Cannot perform arithmetic on unknown quantities")
        result_value = float(other) * self.value
        return Quantity(name=f"{result_value}", dim=self.dim, value=result_value)

    def __rtruediv__(self, other: float | int) -> Quantity:
        """Handle: number / quantity"""
        if self.value is None:
            raise ValueError("Cannot perform arithmetic on unknown quantities")
        result_value = float(other) / self.value
        # Result dimension is 1/self.dim
        result_dim = self.dim**-1
        return Quantity(name=f"{result_value}", dim=result_dim, value=result_value)

    # ---- Comparison operators ----
    def __eq__(self, other: object) -> bool:
        """Check equality between quantities, accounting for units."""
        if not isinstance(other, Quantity):
            return NotImplemented

        # Check dimension compatibility
        if self.dim != other.dim:
            return False

        # If either value is unknown, they're not equal
        if self.value is None or other.value is None:
            return False

        # Compare SI values (both are stored in SI units internally)
        # Use a small tolerance for floating point comparison
        return abs(self.value - other.value) < 1e-10

    def __ne__(self, other: object) -> bool:
        """Check inequality between quantities."""
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __lt__(self, other: Quantity) -> bool:
        """Check if this quantity is less than another."""
        if not isinstance(other, Quantity):
            return NotImplemented

        # Check for None values first
        if self.value is None or other.value is None:
            raise ValueError("Cannot compare unknown quantities")

        # Allow comparison with dimensionless zero for convenience (e.g., T_r < 0)
        if self.dim != other.dim:
            if not (other.dim.is_dimensionless() and abs(other.value) < 1e-15):
                raise TypeError(f"Cannot compare quantities with different dimensions: {self.dim} vs {other.dim}")

        # Compare SI values
        return self.value < other.value

    def __le__(self, other: Quantity) -> bool:
        """Check if this quantity is less than or equal to another."""
        if not isinstance(other, Quantity):
            return NotImplemented

        # Check for None values first
        if self.value is None or other.value is None:
            raise ValueError("Cannot compare unknown quantities")

        # Allow comparison with dimensionless zero for convenience (e.g., T_r <= 0)
        if self.dim != other.dim:
            if not (other.dim.is_dimensionless() and abs(other.value) < 1e-15):
                raise TypeError(f"Cannot compare quantities with different dimensions: {self.dim} vs {other.dim}")

        # Compare SI values
        return self.value <= other.value

    def __gt__(self, other: Quantity) -> bool:
        """Check if this quantity is greater than another."""
        if not isinstance(other, Quantity):
            return NotImplemented

        # Check for None values first
        if self.value is None or other.value is None:
            raise ValueError("Cannot compare unknown quantities")

        # Allow comparison with dimensionless zero for convenience (e.g., T_r > 0)
        if self.dim != other.dim:
            if not (other.dim.is_dimensionless() and abs(other.value) < 1e-15):
                raise TypeError(f"Cannot compare quantities with different dimensions: {self.dim} vs {other.dim}")

        # Compare SI values
        return self.value > other.value

    def __ge__(self, other: Quantity) -> bool:
        """Check if this quantity is greater than or equal to another."""
        if not isinstance(other, Quantity):
            return NotImplemented

        # Check for None values first
        if self.value is None or other.value is None:
            raise ValueError("Cannot compare unknown quantities")

        # Allow comparison with dimensionless zero for convenience (e.g., T_r >= 0)
        if self.dim != other.dim:
            if not (other.dim.is_dimensionless() and abs(other.value) < 1e-15):
                raise TypeError(f"Cannot compare quantities with different dimensions: {self.dim} vs {other.dim}")

        # Compare SI values
        return self.value >= other.value

    def __float__(self) -> float:
        if not self.dim.is_dimensionless():
            raise TypeError("Cannot convert non-dimensionless quantity to float")
        if self.dim.is_angle():
            raise TypeError("NOT IMPLEMENTED YET")
        if self.value is None:
            raise ValueError("Cannot convert unknown quantity to float")
        return self.value

    # ---- Display ----
    def __str__(self) -> str:
        if self.value is None:
            return f"{self.name} (unknown)" if self.name else "Unknown quantity"

        # Use output unit first, then preferred, then system defaults
        unit = self._output_unit or self.preferred or ureg.preferred_for(self.dim) or ureg.si_unit_for(self.dim)
        if unit is None:
            return f"{self._require_value():.6g} [Dim={self.dim}]"

        display_value = self._value_in_unit(unit)
        return f"{display_value:.6g} {unit.symbol}"

    def __repr__(self) -> str:
        return self.__str__()


# Compatibility function with automatic dimension detection and proper typing
@overload
def Q(val: float, unit: str) -> Quantity: ...


@overload
def Q(val: float, unit: Unit[D]) -> Quantity[D]: ...


if TYPE_CHECKING:
    from .unit_catalog import AccelerationUnits, DimensionlessUnits, LengthUnits

    @overload
    def Q(val: float, unit: type[AccelerationUnits]) -> quantity_catalog.Acceleration: ...

    @overload
    def Q(val: float, unit: type[LengthUnits]) -> quantity_catalog.Length: ...

    @overload
    def Q(val: float, unit: type[DimensionlessUnits]) -> quantity_catalog.Dimensionless: ...


def Q(val: float, unit: Unit[D] | str | type) -> Quantity:
    """Create a quantity from value and unit string with automatic dimension detection and proper quantity type."""
    if isinstance(unit, str):
        resolved_unit = ureg.resolve(unit)
        if resolved_unit is None:
            raise ValueError(f"Unknown unit '{unit}'")
        unit = resolved_unit
    elif isinstance(unit, type):
        # Check if it's a UnitNamespace class
        from .unit import UnitNamespace

        if issubclass(unit, UnitNamespace):
            # Get the preferred unit from the UnitNamespace class
            preferred_name = getattr(unit, "__preferred__", None)
            if preferred_name is None:
                raise ValueError(f"UnitNamespace {unit.__name__} has no __preferred__ attribute")
            unit = getattr(unit, preferred_name)
        else:
            raise ValueError(f"Invalid unit type: {type(unit)}")

    # Import quantity classes here to avoid circular imports
    from . import quantity_catalog

    # At this point, unit is guaranteed to be a Unit object, not a string or type
    assert not isinstance(unit, str | type)

    # Fast path: use generic Quantity for better performance
    # (specialized quantity classes can be created explicitly when needed)
    si_value = unit.si_factor * val + unit.si_offset

    # Optimized Quantity creation - bypass dataclass overhead
    new_q = object.__new__(Quantity)
    new_q.name = "Q"
    new_q.dim = unit.dim
    new_q.value = si_value
    new_q.preferred = unit
    new_q._symbol = None
    return new_q


# ---- Setter classes ----
class QuantitySetter(Generic[D]):
    """Fluent setter for quantities when unit not specified."""

    __slots__ = ("_owner", "_value", "_dim")

    def __init__(self, owner: Quantity[D], value: float):
        self._owner = owner
        self._value = float(value)
        self._dim = owner.dim

    def using(self, unit_name: str) -> Quantity[D]:
        """Set by unit name/alias string."""
        unit = ureg.resolve(unit_name, dim=self._dim)
        if unit is None:
            raise AttributeError(f"Unknown unit '{unit_name}'")
        return self._owner.set(self._value, unit)

    def in_(self, unit: Unit[D]) -> Quantity[D]:
        return self._owner.set(self._value, unit)

    def __getattr__(self, name: str) -> Quantity[D]:
        """Resolve attribute name to a Unit and apply."""
        # Guard against deepcopy and pickle operations that cause recursion
        if name in {
            '__setstate__', '__getstate__', '__getnewargs__', '__getnewargs_ex__',
            '__reduce__', '__reduce_ex__', '__copy__', '__deepcopy__',
            '__getattribute__', '__setattr__', '__delattr__',
            '__dict__', '__weakref__', '__class__'
        }:
            raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")

        unit = ureg.resolve(name, dim=self._dim)
        if unit is None:
            raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")
        return self._owner.set(self._value, unit)

    def __dir__(self):
        base = super().__dir__()
        try:
            if self._dim is not None:
                names = ureg.names_for(self._dim)
            else:
                names = ureg.all_names()
            return sorted(set(list(base) + list(names)))
        except Exception:
            return base


class UnitApplier(Generic[D]):
    """Helper for .to_unit property."""

    __slots__ = ("_q", "_dim", "_unit_cache")

    def __init__(self, q: Quantity[D]):
        self._q = q
        self._dim = q.dim
        # Cache for commonly used units to avoid repeated ureg.resolve calls
        self._unit_cache = {}

    def __call__(self, unit: Unit[D] | str) -> Quantity[D]:
        if isinstance(unit, str):
            # Check cache first for string units too
            resolved = self._unit_cache.get(unit)
            if resolved is None:
                resolved = ureg.resolve(unit, dim=self._dim)
                if resolved is None:
                    raise ValueError(f"Unknown unit '{unit}'")
                # Cache the resolved unit
                self._unit_cache[unit] = resolved
            unit = resolved

        if self._q.value is None:
            raise ValueError(f"Cannot convert unknown quantity '{self._q.name}' to unit")

        # Optimized Quantity creation - bypass dataclass overhead, retaining SI storage
        new_q = object.__new__(Quantity)
        new_q.name = "converted"
        new_q.dim = self._dim
        new_q.value = float(self._q.value)
        new_q.preferred = unit
        new_q._symbol = None
        return new_q

    def __getattr__(self, name: str) -> Quantity[D]:
        # Guard against deepcopy and pickle operations that cause recursion
        if name in {
            '__setstate__', '__getstate__', '__getnewargs__', '__getnewargs_ex__',
            '__reduce__', '__reduce_ex__', '__copy__', '__deepcopy__',
            '__getattribute__', '__setattr__', '__delattr__',
            '__dict__', '__weakref__', '__class__'
        }:
            raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")

        # Check cache first for performance
        unit = self._unit_cache.get(name)
        if unit is None:
            unit = ureg.resolve(name, dim=self._dim)
            if unit is None:
                raise AttributeError(f"No unit '{name}' for dimension {self._dim}")
            # Cache the resolved unit for future use
            self._unit_cache[name] = unit

        # Inline conversion for maximum speed (avoid __call__ overhead)
        if self._q.value is None:
            raise ValueError(f"Cannot convert unknown quantity '{self._q.name}' to unit")

        # Optimized Quantity creation
        new_q = object.__new__(Quantity)
        new_q.name = "converted"
        new_q.dim = self._dim
        new_q.value = float(self._q.value)
        new_q.preferred = unit
        new_q._symbol = None
        return new_q


class UnitChanger(Generic[D]):
    """Helper for .as_unit property."""

    __slots__ = ("_q", "_dim")

    def __init__(self, q: Quantity[D]):
        self._q = q
        self._dim = q.dim

    def __call__(self, unit: Unit[D] | str) -> Quantity[D]:
        if isinstance(unit, str):
            resolved = ureg.resolve(unit, dim=self._dim)
            if resolved is None:
                raise ValueError(f"Unknown unit '{unit}'")
            unit = resolved

        # For as_unit, we want to keep the display value the same
        # So if current display is "25 ft/s²", we want new display to be "25 m/s²"
        if self._q.value is None:
            raise ValueError(f"Cannot change unit of unknown quantity '{self._q.name}'")

        current_unit = self._q.preferred or ureg.preferred_for(self._dim) or ureg.si_unit_for(self._dim)
        if current_unit:
            # Convert from SI to current display unit: (si_value - offset) / factor
            display_value = (self._q.value - current_unit.si_offset) / current_unit.si_factor
        else:
            display_value = self._q.value

        # Convert this display value to SI for storage
        si_value = unit.si_factor * display_value + unit.si_offset

        return Quantity(name=self._q.name, dim=self._dim, value=si_value, preferred=unit)

    def __getattr__(self, name: str) -> Quantity[D]:
        # Guard against deepcopy and pickle operations that cause recursion
        if name in {
            '__setstate__', '__getstate__', '__getnewargs__', '__getnewargs_ex__',
            '__reduce__', '__reduce_ex__', '__copy__', '__deepcopy__',
            '__getattribute__', '__setattr__', '__delattr__',
            '__dict__', '__weakref__', '__class__'
        }:
            raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")

        unit = ureg.resolve(name, dim=self._dim)
        if unit is None:
            raise AttributeError(f"No unit '{name}' for dimension {self._dim}")
        return self(unit)


# For backwards compatibility
FieldQuantity = Quantity
FieldSetter = QuantitySetter
