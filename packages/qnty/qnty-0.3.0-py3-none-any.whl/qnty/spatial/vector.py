"""
Vector class for 3D directions/displacements with units.

Represents a direction or displacement in 3D space where all components
share the same unit. Supports standard vector operations like addition,
scaling, dot product, cross product, and normalization.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from typing import Generic, TypeVar

from ..core.dimension import Dimension
from ..core.quantity import Quantity
from ..core.unit import Unit

D = TypeVar("D")


class Vector(Generic[D]):
    """
    3D vector with uniform units across all components.

    Represents a direction or displacement in 3D space. All components
    (u, v, w) share the same unit. Internally stores values in SI units.

    Examples:
        >>> from qnty.core.unit_catalog import LengthUnits
        >>> v1 = Vector(3.0, 4.0, 0.0, unit=LengthUnits.meter)
        >>> magnitude = v1.magnitude
        >>> print(magnitude)
        5 m
        >>> v2 = v1.normalized()
        >>> print(v2.magnitude)
        1 m
    """

    __slots__ = ("_coords", "_dim", "_unit")

    def __init__(self, u: float, v: float, w: float = 0.0, unit: Unit[D] | None = None):
        """
        Create a 3D vector with units.

        Args:
            u: First component value in the specified unit
            v: Second component value in the specified unit
            w: Third component value in the specified unit (default: 0.0)
            unit: Unit for all components (if None, assumes SI units)
        """
        if unit is None:
            # Store directly as dimensionless SI values
            self._coords = np.array([u, v, w], dtype=float)
            self._dim = None
            self._unit = None
        else:
            # Convert to SI for internal storage
            si_values = unit.si_factor * np.array([u, v, w], dtype=float) + unit.si_offset
            self._coords = si_values
            self._dim = unit.dim
            self._unit = unit  # Preferred display unit

    @classmethod
    def from_quantities(cls, u: Quantity[D], v: Quantity[D], w: Quantity[D] | None = None) -> Vector[D]:
        """
        Create vector from Quantity objects (must have same dimension).

        Args:
            u: First component as Quantity
            v: Second component as Quantity
            w: Third component as Quantity (default: 0 in same unit as u)

        Returns:
            Vector with components from the quantities

        Raises:
            ValueError: If quantities have different dimensions
        """
        if w is None:
            # Create zero w-component with same unit as u
            if u.preferred is None:
                raise ValueError("Cannot create vector from quantity without preferred unit")
            w = Quantity(name="w", dim=u.dim, value=0.0, preferred=u.preferred)

        # Validate dimensions match
        if not (u.dim == v.dim == w.dim):
            raise ValueError(f"All components must have the same dimension: u={u.dim}, v={v.dim}, w={w.dim}")

        # Validate all have values
        if u.value is None or v.value is None or w.value is None:
            raise ValueError("Cannot create vector from unknown quantities")

        # Create vector directly from SI values
        result = object.__new__(cls)
        result._coords = np.array([u.value, v.value, w.value], dtype=float)
        result._dim = u.dim
        result._unit = u.preferred or v.preferred or w.preferred
        return result

    # Properties for component access
    @property
    def u(self) -> Quantity[D]:
        """First component as Quantity."""
        return self._make_quantity(0, "u")

    @property
    def v(self) -> Quantity[D]:
        """Second component as Quantity."""
        return self._make_quantity(1, "v")

    @property
    def w(self) -> Quantity[D]:
        """Third component as Quantity."""
        return self._make_quantity(2, "w")

    def _make_quantity(self, index: int, name: str) -> Quantity[D]:
        """Create Quantity from component index."""
        if self._dim is None:
            raise ValueError("Cannot create Quantity from dimensionless vector components")

        # Get component value and apply tolerance for near-zero values
        # This prevents floating-point precision errors like 3.06e-14 appearing as non-zero
        value = self._coords[index]
        if abs(value) < 1e-10:  # Tolerance: ~10 orders of magnitude below typical engineering values
            value = 0.0

        # Optimized Quantity creation - bypass dataclass overhead
        q = object.__new__(Quantity)
        q.name = name
        q.dim = self._dim
        q.value = value
        q.preferred = self._unit
        q._symbol = None
        q._output_unit = None
        return q

    @property
    def magnitude(self) -> Quantity[D]:
        """
        Vector magnitude/length.

        Returns:
            Magnitude as Quantity with same dimension as components
        """
        if self._dim is None:
            raise ValueError("Cannot compute magnitude of dimensionless vector")

        mag_si = float(np.sqrt(np.sum(self._coords**2)))

        # Return as Quantity
        q = object.__new__(Quantity)
        q.name = "magnitude"
        q.dim = self._dim
        q.value = mag_si
        q.preferred = self._unit
        q._symbol = None
        q._output_unit = None
        return q

    def normalized(self) -> Vector[D]:
        """
        Return unit vector in same direction.

        Returns:
            Normalized vector with magnitude 1

        Raises:
            ValueError: If vector is zero (cannot normalize)
        """
        mag = np.sqrt(np.sum(self._coords**2))
        if mag == 0:
            raise ValueError("Cannot normalize zero vector")

        # Create normalized vector
        result = object.__new__(Vector)
        result._coords = self._coords / mag
        result._dim = self._dim
        result._unit = self._unit
        return result

    def with_magnitude(self, magnitude: Quantity[D] | float) -> Vector[D]:
        """
        Return vector in same direction with specified magnitude.

        Args:
            magnitude: Target magnitude (Quantity or float in SI units)

        Returns:
            Scaled vector with specified magnitude

        Raises:
            ValueError: If vector is zero (no direction to scale)
        """
        current_mag = np.sqrt(np.sum(self._coords**2))
        if current_mag == 0:
            raise ValueError("Cannot scale zero vector")

        if isinstance(magnitude, Quantity):
            if magnitude.dim != self._dim:
                raise ValueError(f"Magnitude dimension {magnitude.dim} doesn't match vector dimension {self._dim}")
            if magnitude.value is None:
                raise ValueError("Cannot use unknown quantity as magnitude")
            target_mag = magnitude.value
        else:
            target_mag = float(magnitude)

        scale = target_mag / current_mag

        # Create scaled vector
        result = object.__new__(Vector)
        result._coords = self._coords * scale
        result._dim = self._dim
        result._unit = self._unit
        return result

    # Vector operations
    def __add__(self, other: Vector[D]) -> Vector[D]:
        """
        Vector addition.

        Args:
            other: Vector to add

        Returns:
            Sum of vectors

        Raises:
            ValueError: If vectors have different dimensions
        """
        if not isinstance(other, Vector):
            return NotImplemented

        if self._dim != other._dim:
            raise ValueError(f"Cannot add vectors with different dimensions: {self._dim} vs {other._dim}")

        # Vectorized addition (SI values)
        result = object.__new__(Vector)
        result._coords = self._coords + other._coords
        result._dim = self._dim
        result._unit = self._unit
        return result

    def __sub__(self, other: Vector[D]) -> Vector[D]:
        """
        Vector subtraction.

        Args:
            other: Vector to subtract

        Returns:
            Difference of vectors

        Raises:
            ValueError: If vectors have different dimensions
        """
        if not isinstance(other, Vector):
            return NotImplemented

        if self._dim != other._dim:
            raise ValueError(f"Cannot subtract vectors with different dimensions: {self._dim} vs {other._dim}")

        # Vectorized subtraction (SI values)
        result = object.__new__(Vector)
        result._coords = self._coords - other._coords
        result._dim = self._dim
        result._unit = self._unit
        return result

    def __mul__(self, scalar: float | int) -> Vector[D]:
        """
        Scalar multiplication.

        Args:
            scalar: Scaling factor

        Returns:
            Scaled vector
        """
        result = object.__new__(Vector)
        result._coords = self._coords * float(scalar)
        result._dim = self._dim
        result._unit = self._unit
        return result

    __rmul__ = __mul__

    def __truediv__(self, scalar: float | int) -> Vector[D]:
        """
        Scalar division.

        Args:
            scalar: Divisor

        Returns:
            Scaled vector

        Raises:
            ZeroDivisionError: If scalar is zero
        """
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")

        result = object.__new__(Vector)
        result._coords = self._coords / float(scalar)
        result._dim = self._dim
        result._unit = self._unit
        return result

    def __neg__(self) -> Vector[D]:
        """
        Negation (opposite direction).

        Returns:
            Vector pointing in opposite direction
        """
        result = object.__new__(Vector)
        result._coords = -self._coords
        result._dim = self._dim
        result._unit = self._unit
        return result

    def dot(self, other: Vector[D]) -> Quantity:
        """
        Dot product (scalar product).

        Args:
            other: Vector to compute dot product with

        Returns:
            Dot product as Quantity (dimension is self.dim * other.dim)

        Raises:
            ValueError: If vectors have incompatible dimensions
        """
        if not isinstance(other, Vector):
            raise TypeError(f"Expected Vector, got {type(other)}")

        # Dot product of SI values
        dot_product = float(np.sum(self._coords * other._coords))

        # Result dimension is product of vector dimensions
        if self._dim is None or other._dim is None:
            result_dim = None
        else:
            result_dim = self._dim * other._dim

        # Return as Quantity
        q = object.__new__(Quantity)
        q.name = "dot_product"
        q.dim = result_dim
        q.value = dot_product
        q.preferred = None  # No obvious preferred unit for product
        q._symbol = None
        q._output_unit = None
        return q

    def cross(self, other: Vector[D]) -> Vector:
        """
        Cross product (vector product).

        Args:
            other: Vector to compute cross product with

        Returns:
            Cross product vector (dimension is self.dim * other.dim)

        Note:
            The resulting vector is perpendicular to both input vectors.
            Magnitude equals area of parallelogram formed by the vectors.
        """
        if not isinstance(other, Vector):
            raise TypeError(f"Expected Vector, got {type(other)}")

        # Cross product of SI values
        cross_coords = np.cross(self._coords, other._coords)

        # Result dimension is product of vector dimensions
        if self._dim is None or other._dim is None:
            result_dim = None
        else:
            result_dim = self._dim * other._dim

        # Create result vector
        result = object.__new__(Vector)
        result._coords = cross_coords
        result._dim = result_dim
        result._unit = None  # Cross product may have different units
        return result

    def is_parallel_to(self, other: Vector[D], tolerance: float = 1e-10) -> bool:
        """
        Test whether vector is parallel to another.

        Args:
            other: Vector to compare with
            tolerance: Tolerance for parallelism test

        Returns:
            True if vectors are parallel (cross product near zero)
        """
        if not isinstance(other, Vector):
            raise TypeError(f"Expected Vector, got {type(other)}")

        cross_coords = np.cross(self._coords, other._coords)
        cross_magnitude = np.sqrt(np.sum(cross_coords**2))

        return bool(cross_magnitude < tolerance)

    def is_perpendicular_to(self, other: Vector[D], tolerance: float = 1e-10) -> bool:
        """
        Test whether vector is perpendicular to another.

        Args:
            other: Vector to compare with
            tolerance: Tolerance for perpendicularity test

        Returns:
            True if vectors are perpendicular (dot product near zero)
        """
        if not isinstance(other, Vector):
            raise TypeError(f"Expected Vector, got {type(other)}")

        dot_product = np.sum(self._coords * other._coords)

        return bool(abs(dot_product) < tolerance)

    def angle_to(self, other: Vector[D]) -> Quantity:
        """
        Compute angle between this vector and another.

        Args:
            other: Vector to compute angle to

        Returns:
            Angle as dimensionless Quantity (in radians)

        Raises:
            ValueError: If either vector is zero
        """
        if not isinstance(other, Vector):
            raise TypeError(f"Expected Vector, got {type(other)}")

        mag_self = np.sqrt(np.sum(self._coords**2))
        mag_other = np.sqrt(np.sum(other._coords**2))

        if mag_self == 0 or mag_other == 0:
            raise ValueError("Cannot compute angle with zero vector")

        # Compute angle using dot product
        cos_angle = np.sum(self._coords * other._coords) / (mag_self * mag_other)

        # Clamp to [-1, 1] to handle numerical errors
        cos_angle = np.clip(cos_angle, -1.0, 1.0)

        angle_rad = float(np.arccos(cos_angle))

        # Return as dimensionless Quantity
        from ..core.dimension_catalog import dim

        q = object.__new__(Quantity)
        q.name = "angle"
        q.dim = dim.angle_plane  # Angle dimension (dimensionless but special)
        q.value = angle_rad
        q.preferred = None
        q._symbol = None
        q._output_unit = None
        return q

    def projection_onto(self, other: Vector[D]) -> Vector[D]:
        """
        Compute projection of this vector onto another.

        Args:
            other: Vector to project onto

        Returns:
            Projection vector (parallel to other)

        Raises:
            ValueError: If other vector is zero
        """
        if not isinstance(other, Vector):
            raise TypeError(f"Expected Vector, got {type(other)}")

        mag_other_sq = np.sum(other._coords**2)
        if mag_other_sq == 0:
            raise ValueError("Cannot project onto zero vector")

        # Projection formula: proj = (v · u / |u|²) * u
        dot_product = np.sum(self._coords * other._coords)
        scale = dot_product / mag_other_sq

        result = object.__new__(Vector)
        result._coords = scale * other._coords
        result._dim = self._dim
        result._unit = self._unit
        return result

    def to_unit(self, unit: Unit[D] | str) -> Vector[D]:
        """
        Convert to different display unit (SI values unchanged).

        Args:
            unit: Target unit for display

        Returns:
            New Vector with updated display unit
        """
        if isinstance(unit, str):
            from ..core.unit import ureg

            resolved = ureg.resolve(unit, dim=self._dim)
            if resolved is None:
                raise ValueError(f"Unknown unit '{unit}'")
            unit = resolved

        # Create new Vector with same SI values, different display unit
        result = object.__new__(Vector)
        result._coords = self._coords.copy()  # Copy to avoid aliasing
        result._dim = self._dim
        result._unit = unit
        return result

    def to_array(self) -> NDArray[np.float64]:
        """
        Get components as numpy array (in current display unit).

        Returns:
            Array of [u, v, w] components in display units
        """
        if self._unit is None:
            return self._coords.copy()
        return (self._coords - self._unit.si_offset) / self._unit.si_factor

    def __eq__(self, other: object) -> bool:
        """
        Check equality between vectors (same components and dimension).

        Args:
            other: Vector to compare with

        Returns:
            True if vectors are equal within tolerance
        """
        if not isinstance(other, Vector):
            return NotImplemented

        if self._dim != other._dim:
            return False

        # Use small tolerance for floating point comparison
        return bool(np.allclose(self._coords, other._coords, rtol=1e-10, atol=1e-10))

    def __str__(self) -> str:
        """String representation of the vector."""
        coords = self.to_array()
        unit_str = f" {self._unit.symbol}" if self._unit else ""
        return f"Vector({coords[0]:.6g}, {coords[1]:.6g}, {coords[2]:.6g}{unit_str})"

    def __repr__(self) -> str:
        """Representation of the vector."""
        return self.__str__()
