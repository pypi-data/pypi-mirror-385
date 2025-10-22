"""
CoordinateSystem class for handling orthogonal and non-orthogonal coordinate systems.

Supports:
- Standard orthogonal (x, y) with 90° separation
- Non-orthogonal systems (e.g., u, v with arbitrary angle between axes)
- Conversion between custom coordinate systems and standard x-y system
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ..core.unit import Unit


class CoordinateSystem:
    """
    Represents a 2D coordinate system with potentially non-orthogonal axes.

    For standard orthogonal systems:
        - x and y axes are 90° apart
        - Axes are labeled 'x' and 'y'

    For non-orthogonal systems:
        - Axes can be any angle apart (e.g., 75° or 105°)
        - Axes can have custom labels (e.g., 'u' and 'v')
        - Angles are measured from the positive horizontal (standard x-axis)

    Examples:
        >>> # Standard orthogonal system
        >>> standard = CoordinateSystem.standard()

        >>> # Non-orthogonal u-v system (u at 0°, v at 75°)
        >>> uv_system = CoordinateSystem(
        ...     axis1_label="u",
        ...     axis2_label="v",
        ...     axis1_angle=0,
        ...     axis2_angle=75,
        ...     angle_unit="degree"
        ... )

        >>> # Convert force from u-v to x-y
        >>> force_uv = (4000, 3000)  # (u_component, v_component)
        >>> force_xy = uv_system.to_cartesian(force_uv[0], force_uv[1])
    """

    __slots__ = ("axis1_label", "axis2_label", "axis1_angle", "axis2_angle", "_is_orthogonal")

    def __init__(self, axis1_label: str = "x", axis2_label: str = "y", axis1_angle: float = 0.0, axis2_angle: float = 90.0, angle_unit: str = "degree"):
        """
        Create a coordinate system.

        Args:
            axis1_label: Label for first axis (default "x")
            axis2_label: Label for second axis (default "y")
            axis1_angle: Angle of first axis from positive x-axis
            axis2_angle: Angle of second axis from positive x-axis
            angle_unit: Unit for angles ("degree" or "radian")
        """
        self.axis1_label = axis1_label
        self.axis2_label = axis2_label

        # Convert to radians if needed
        if angle_unit == "degree":
            self.axis1_angle = math.radians(axis1_angle)
            self.axis2_angle = math.radians(axis2_angle)
        else:
            self.axis1_angle = axis1_angle
            self.axis2_angle = axis2_angle

        # Check if orthogonal
        angle_diff = abs(self.axis2_angle - self.axis1_angle)
        self._is_orthogonal = math.isclose(angle_diff, math.pi / 2, abs_tol=1e-6)

    @classmethod
    def standard(cls) -> CoordinateSystem:
        """
        Create standard orthogonal x-y coordinate system.

        Returns:
            CoordinateSystem with x at 0° and y at 90°
        """
        return cls(axis1_label="x", axis2_label="y", axis1_angle=0.0, axis2_angle=90.0, angle_unit="degree")

    @classmethod
    def from_angle_between(cls, axis1_label: str, axis2_label: str, axis1_angle: float = 0.0, angle_between: float = 90.0, angle_unit: str = "degree") -> CoordinateSystem:
        """
        Create a coordinate system by specifying the angle between axes.

        Args:
            axis1_label: Label for first axis
            axis2_label: Label for second axis
            axis1_angle: Angle of first axis from positive x-axis
            angle_between: Angle between the two axes (measured counterclockwise from axis1 to axis2)
            angle_unit: Unit for angles ("degree" or "radian")

        Returns:
            CoordinateSystem instance

        Examples:
            >>> # u-v system with 75° between axes (u at 0°, v at 75°)
            >>> uv_system = CoordinateSystem.from_angle_between("u", "v", axis1_angle=0, angle_between=75)
        """
        if angle_unit == "degree":
            axis1_rad = math.radians(axis1_angle)
            between_rad = math.radians(angle_between)
        else:
            axis1_rad = axis1_angle
            between_rad = angle_between

        axis2_angle_rad = axis1_rad + between_rad

        return cls(axis1_label=axis1_label, axis2_label=axis2_label, axis1_angle=math.degrees(axis1_rad), axis2_angle=math.degrees(axis2_angle_rad), angle_unit="degree")

    @property
    def is_orthogonal(self) -> bool:
        """Whether this coordinate system is orthogonal (90° between axes)."""
        return self._is_orthogonal

    @property
    def angle_between(self) -> float:
        """Angle between the two axes in radians."""
        return self.axis2_angle - self.axis1_angle

    def to_cartesian(self, component1: float, component2: float) -> tuple[float, float]:
        """
        Convert components in this coordinate system to standard x-y cartesian.

        Args:
            component1: Component along first axis
            component2: Component along second axis

        Returns:
            Tuple of (x, y) components in standard cartesian system

        Examples:
            >>> # u-v system: u at 0°, v at 75°
            >>> uv = CoordinateSystem.from_angle_between("u", "v", 0, 75)
            >>> # Force with 2.07 kN along u and 2.93 kN along v
            >>> x, y = uv.to_cartesian(2.07, 2.93)
        """
        # Each component contributes to x and y based on its angle
        x = component1 * math.cos(self.axis1_angle) + component2 * math.cos(self.axis2_angle)
        y = component1 * math.sin(self.axis1_angle) + component2 * math.sin(self.axis2_angle)
        return (x, y)

    def from_cartesian(self, x: float, y: float) -> tuple[float, float]:
        """
        Convert standard x-y cartesian components to this coordinate system.

        For non-orthogonal systems, this solves the linear system:
            x = c1 * cos(θ1) + c2 * cos(θ2)
            y = c1 * sin(θ1) + c2 * sin(θ2)

        Args:
            x: X-component in standard cartesian
            y: Y-component in standard cartesian

        Returns:
            Tuple of (component1, component2) in this coordinate system

        Examples:
            >>> # u-v system: u at 0°, v at 75°
            >>> uv = CoordinateSystem.from_angle_between("u", "v", 0, 75)
            >>> # Force with x=3.5 kN, y=2.0 kN
            >>> u, v = uv.from_cartesian(3.5, 2.0)
        """
        # Set up the linear system as a matrix equation
        # [cos(θ1)  cos(θ2)] [c1]   [x]
        # [sin(θ1)  sin(θ2)] [c2] = [y]

        A = np.array([[math.cos(self.axis1_angle), math.cos(self.axis2_angle)], [math.sin(self.axis1_angle), math.sin(self.axis2_angle)]])
        b = np.array([x, y])

        # Solve for [c1, c2]
        components = np.linalg.solve(A, b)
        return (float(components[0]), float(components[1]))

    def angle_to_axis1(self, angle_from_x: float) -> float:
        """
        Convert an angle measured from positive x-axis to angle from axis1.

        Args:
            angle_from_x: Angle in radians from positive x-axis (counterclockwise)

        Returns:
            Angle in radians measured from axis1 (counterclockwise)
        """
        return angle_from_x - self.axis1_angle

    def angle_from_axis1(self, angle_from_axis1: float) -> float:
        """
        Convert an angle measured from axis1 to angle from positive x-axis.

        Args:
            angle_from_axis1: Angle in radians from axis1 (counterclockwise)

        Returns:
            Angle in radians from positive x-axis (counterclockwise)
        """
        return angle_from_axis1 + self.axis1_angle

    def __str__(self) -> str:
        """String representation."""
        axis1_deg = math.degrees(self.axis1_angle)
        axis2_deg = math.degrees(self.axis2_angle)
        angle_between_deg = math.degrees(self.angle_between)

        if self.is_orthogonal and self.axis1_label == "x" and self.axis2_label == "y":
            return "CoordinateSystem(standard x-y)"
        else:
            return f"CoordinateSystem({self.axis1_label} at {axis1_deg:.1f}°, {self.axis2_label} at {axis2_deg:.1f}°, {angle_between_deg:.1f}° between)"

    def __repr__(self) -> str:
        """Representation."""
        return self.__str__()
