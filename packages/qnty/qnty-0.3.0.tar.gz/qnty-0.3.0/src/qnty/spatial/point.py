"""
Point class for 3D spatial positions with units.

Represents a position in 3D space where all coordinates share the same unit.
Internally stores values in SI units for consistency with qnty's architecture.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from typing import TYPE_CHECKING, Generic, TypeVar

from ..core.dimension import Dimension
from ..core.quantity import Quantity
from ..core.unit import Unit

if TYPE_CHECKING:
    from .vector import Vector

D = TypeVar("D")


class Point(Generic[D]):
    """
    3D point with uniform units across all coordinates.

    All coordinates (x, y, z) share the same unit for consistency
    and performance. Internally stores values in SI units.

    Examples:
        >>> from qnty.core.unit_catalog import LengthUnits
        >>> p1 = Point(10.0, 20.0, 30.0, unit=LengthUnits.meter)
        >>> p2 = Point(5.0, 10.0, 0.0, unit=LengthUnits.meter)
        >>> distance = p1.distance_to(p2)
        >>> print(distance)
        26.9258 m
    """

    __slots__ = ("_coords", "_dim", "_unit")

    def __init__(self, x: float, y: float, z: float = 0.0, unit: Unit[D] | None = None):
        """
        Create a 3D point with units.

        Args:
            x: X coordinate value in the specified unit
            y: Y coordinate value in the specified unit
            z: Z coordinate value in the specified unit (default: 0.0)
            unit: Unit for all coordinates (if None, assumes SI units)
        """
        # Store as numpy array for vectorized operations
        if unit is None:
            # Store directly as dimensionless SI values
            self._coords = np.array([x, y, z], dtype=float)
            self._dim = None
            self._unit = None
        else:
            # Convert to SI for internal storage
            si_values = unit.si_factor * np.array([x, y, z], dtype=float) + unit.si_offset
            self._coords = si_values
            self._dim = unit.dim
            self._unit = unit  # Preferred display unit

    @classmethod
    def from_quantities(cls, x: Quantity[D], y: Quantity[D], z: Quantity[D] | None = None) -> Point[D]:
        """
        Create point from Quantity objects (must have same dimension).

        Args:
            x: X coordinate as Quantity
            y: Y coordinate as Quantity
            z: Z coordinate as Quantity (default: 0 in same unit as x)

        Returns:
            Point with coordinates from the quantities

        Raises:
            ValueError: If quantities have different dimensions
        """
        if z is None:
            # Create zero z-coordinate with same unit as x
            if x.preferred is None:
                raise ValueError("Cannot create point from quantity without preferred unit")
            z = Quantity(name="z", dim=x.dim, value=0.0, preferred=x.preferred)

        # Validate dimensions match
        if not (x.dim == y.dim == z.dim):
            raise ValueError(f"All coordinates must have the same dimension: x={x.dim}, y={y.dim}, z={z.dim}")

        # Validate all have values
        if x.value is None or y.value is None or z.value is None:
            raise ValueError("Cannot create point from unknown quantities")

        # Create point directly from SI values
        result = object.__new__(cls)
        result._coords = np.array([x.value, y.value, z.value], dtype=float)
        result._dim = x.dim
        result._unit = x.preferred or y.preferred or z.preferred
        return result

    # Properties for coordinate access
    @property
    def x(self) -> Quantity[D]:
        """X coordinate as Quantity."""
        return self._make_quantity(0, "x")

    @property
    def y(self) -> Quantity[D]:
        """Y coordinate as Quantity."""
        return self._make_quantity(1, "y")

    @property
    def z(self) -> Quantity[D]:
        """Z coordinate as Quantity."""
        return self._make_quantity(2, "z")

    def _make_quantity(self, index: int, name: str) -> Quantity[D]:
        """Create Quantity from coordinate index."""
        if self._dim is None:
            # Dimensionless point
            raise ValueError("Cannot create Quantity from dimensionless point coordinates")

        # Optimized Quantity creation - bypass dataclass overhead
        q = object.__new__(Quantity)
        q.name = name
        q.dim = self._dim
        q.value = self._coords[index]
        q.preferred = self._unit
        q._symbol = None
        q._output_unit = None
        return q

    # Vector operations
    def __sub__(self, other: Point[D]) -> Vector[D]:
        """
        Compute displacement vector from other to self.

        Args:
            other: Point to subtract from self

        Returns:
            Vector pointing from other to self

        Raises:
            ValueError: If points have different dimensions
        """
        if not isinstance(other, Point):
            return NotImplemented

        if self._dim != other._dim:
            raise ValueError(f"Cannot subtract points with different dimensions: {self._dim} vs {other._dim}")

        # Import here to avoid circular imports
        from .vector import Vector

        # Vectorized subtraction (SI values)
        delta = self._coords - other._coords

        # Create Vector directly
        result = object.__new__(Vector)
        result._coords = delta
        result._dim = self._dim
        result._unit = self._unit
        return result

    def displaced(self, vector: Vector[D], times: float = 1.0) -> Point[D]:
        """
        Create new point displaced by vector * times.

        Args:
            vector: Displacement vector
            times: Scaling factor for the displacement (default: 1.0)

        Returns:
            New point at displaced position

        Raises:
            ValueError: If vector has different dimension than point
        """
        from .vector import Vector

        if not isinstance(vector, Vector):
            raise TypeError(f"Expected Vector, got {type(vector)}")

        if self._dim != vector._dim:
            raise ValueError(f"Cannot displace point with vector of different dimension: {self._dim} vs {vector._dim}")

        # Vectorized displacement (SI values)
        new_coords = self._coords + times * vector._coords

        # Create new Point directly
        result = object.__new__(Point)
        result._coords = new_coords
        result._dim = self._dim
        result._unit = self._unit
        return result

    def distance_to(self, other: Point[D]) -> Quantity[D]:
        """
        Compute Euclidean distance to another point.

        Args:
            other: Point to compute distance to

        Returns:
            Distance as Quantity with same dimension as point coordinates

        Raises:
            ValueError: If points have different dimensions
        """
        if not isinstance(other, Point):
            raise TypeError(f"Expected Point, got {type(other)}")

        if self._dim != other._dim:
            raise ValueError(f"Cannot compute distance between points with different dimensions: {self._dim} vs {other._dim}")

        # Vectorized distance calculation (SI values)
        delta = self._coords - other._coords
        distance_si = float(np.sqrt(np.sum(delta**2)))

        # Return as Quantity
        q = object.__new__(Quantity)
        q.name = "distance"
        q.dim = self._dim
        q.value = distance_si
        q.preferred = self._unit
        q._symbol = None
        q._output_unit = None
        return q

    def to_unit(self, unit: Unit[D] | str) -> Point[D]:
        """
        Convert to different display unit (SI values unchanged).

        Args:
            unit: Target unit for display

        Returns:
            New Point with updated display unit
        """
        if isinstance(unit, str):
            from ..core.unit import ureg

            resolved = ureg.resolve(unit, dim=self._dim)
            if resolved is None:
                raise ValueError(f"Unknown unit '{unit}'")
            unit = resolved

        # Create new Point with same SI values, different display unit
        result = object.__new__(Point)
        result._coords = self._coords.copy()  # Copy to avoid aliasing
        result._dim = self._dim
        result._unit = unit
        return result

    def to_array(self) -> NDArray[np.float64]:
        """
        Get coordinates as numpy array (in current display unit).

        Returns:
            Array of [x, y, z] coordinates in display units
        """
        if self._unit is None:
            return self._coords.copy()
        return (self._coords - self._unit.si_offset) / self._unit.si_factor

    def __eq__(self, other: object) -> bool:
        """
        Check equality between points (same coordinates and dimension).

        Args:
            other: Point to compare with

        Returns:
            True if points are equal within tolerance
        """
        if not isinstance(other, Point):
            return NotImplemented

        if self._dim != other._dim:
            return False

        # Use small tolerance for floating point comparison
        return bool(np.allclose(self._coords, other._coords, rtol=1e-10, atol=1e-10))

    def __str__(self) -> str:
        """String representation of the point."""
        coords = self.to_array()
        unit_str = f" {self._unit.symbol}" if self._unit else ""
        return f"Point({coords[0]:.6g}, {coords[1]:.6g}, {coords[2]:.6g}{unit_str})"

    def __repr__(self) -> str:
        """Representation of the point."""
        return self.__str__()
