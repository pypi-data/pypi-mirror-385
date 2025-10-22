"""
AngleReference class for specifying how angles are measured in force vectors.

Supports:
- Different reference axes (positive x-axis, positive y-axis, custom vectors)
- Measurement direction (counterclockwise or clockwise)
- Converting between different angle reference systems

Engineering statics convention:
- Counterclockwise (CCW) angles are positive
- Clockwise (CW) angles are negative
"""

from __future__ import annotations

import math
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class AngleDirection(Enum):
    """Direction for measuring angles."""

    COUNTERCLOCKWISE = "counterclockwise"
    CCW = "counterclockwise"  # Alias
    CLOCKWISE = "clockwise"
    CW = "clockwise"  # Alias


class AngleReference:
    """
    Specifies how an angle is measured for a force vector.

    By default, angles in engineering statics are measured counterclockwise
    from the positive x-axis. This class allows specifying different reference
    axes and measurement directions.

    Examples:
        >>> # Standard: CCW from positive x-axis
        >>> ref1 = AngleReference.standard()

        >>> # Clockwise from positive u-axis
        >>> ref2 = AngleReference(axis_angle=0, direction=AngleDirection.CLOCKWISE, axis_label="u")

        >>> # CCW from positive y-axis
        >>> ref3 = AngleReference.from_axis("+y")

        >>> # CW from negative x-axis
        >>> ref4 = AngleReference.from_axis("-x", direction=AngleDirection.CLOCKWISE)

        >>> # CCW from custom vector at 30°
        >>> ref5 = AngleReference(axis_angle=30, direction=AngleDirection.COUNTERCLOCKWISE)
    """

    __slots__ = ("axis_angle", "direction", "axis_label", "_description")

    def __init__(
        self,
        axis_angle: float = 0.0,
        direction: AngleDirection | str = AngleDirection.COUNTERCLOCKWISE,
        axis_label: str = "+x",
        angle_unit: str = "degree",
        description: str = "",
    ):
        """
        Create an angle reference.

        Args:
            axis_angle: Angle of reference axis from standard +x-axis (in degrees by default)
            direction: Measurement direction (COUNTERCLOCKWISE or CLOCKWISE)
            axis_label: Label for the reference axis (e.g., "+x", "+y", "u", "-x")
            angle_unit: Unit for axis_angle ("degree" or "radian")
            description: Human-readable description
        """
        # Convert angle to radians (internal representation)
        if angle_unit == "degree":
            self.axis_angle = math.radians(axis_angle)
        else:
            self.axis_angle = axis_angle

        # Convert string to enum if needed
        if isinstance(direction, str):
            direction = direction.lower()
            if direction in ("counterclockwise", "ccw"):
                self.direction = AngleDirection.COUNTERCLOCKWISE
            elif direction in ("clockwise", "cw"):
                self.direction = AngleDirection.CLOCKWISE
            else:
                raise ValueError(f"Unknown direction: {direction}. Use 'counterclockwise', 'ccw', 'clockwise', or 'cw'")
        else:
            self.direction = direction

        self.axis_label = axis_label
        self._description = description

    @classmethod
    def standard(cls) -> AngleReference:
        """
        Standard angle reference: counterclockwise from positive x-axis.

        This is the default convention in engineering statics.

        Returns:
            AngleReference for CCW from +x-axis
        """
        return cls(axis_angle=0.0, direction=AngleDirection.COUNTERCLOCKWISE, axis_label="+x", angle_unit="degree", description="counterclockwise from +x-axis")

    @classmethod
    def from_axis(cls, axis_label: str, direction: AngleDirection | str = AngleDirection.COUNTERCLOCKWISE, angle_unit: str = "degree") -> AngleReference:
        """
        Create angle reference from a standard axis label.

        Supported axis labels:
        - "+x" or "x": Positive x-axis (0°)
        - "+y" or "y": Positive y-axis (90°)
        - "-x": Negative x-axis (180°)
        - "-y": Negative y-axis (270°)
        - Custom labels like "u", "v" can be used with explicit axis_angle

        Args:
            axis_label: Axis label ("+x", "+y", "-x", "-y", or custom)
            direction: Measurement direction
            angle_unit: Unit for angles

        Returns:
            AngleReference instance

        Examples:
            >>> # CCW from +y-axis
            >>> ref1 = AngleReference.from_axis("+y")

            >>> # Clockwise from +x-axis
            >>> ref2 = AngleReference.from_axis("+x", direction="clockwise")
        """
        # Map standard axis labels to angles
        axis_angles = {
            "+x": 0.0,
            "x": 0.0,
            "+y": 90.0,
            "y": 90.0,
            "-x": 180.0,
            "-y": 270.0,
        }

        axis_angle = axis_angles.get(axis_label, 0.0)  # Default to 0 for custom labels

        direction_str = direction.value if isinstance(direction, AngleDirection) else direction
        description = f"{direction_str} from {axis_label}-axis"

        return cls(axis_angle=axis_angle, direction=direction, axis_label=axis_label, angle_unit="degree", description=description)

    @classmethod
    def from_coordinate_system(cls, coord_system, axis_index: int = 0, direction: AngleDirection | str = AngleDirection.COUNTERCLOCKWISE) -> AngleReference:
        """
        Create angle reference from a coordinate system axis.

        Args:
            coord_system: CoordinateSystem instance
            axis_index: Which axis to use as reference (0 = first axis, 1 = second axis)
            direction: Measurement direction

        Returns:
            AngleReference instance

        Examples:
            >>> from qnty.spatial.coordinate_system import CoordinateSystem
            >>> uv_system = CoordinateSystem.from_angle_between("u", "v", 0, 75)
            >>> ref = AngleReference.from_coordinate_system(uv_system, axis_index=0, direction="clockwise")
        """
        if axis_index == 0:
            axis_angle = coord_system.axis1_angle
            axis_label = coord_system.axis1_label
        elif axis_index == 1:
            axis_angle = coord_system.axis2_angle
            axis_label = coord_system.axis2_label
        else:
            raise ValueError(f"axis_index must be 0 or 1, got {axis_index}")

        direction_str = direction.value if isinstance(direction, AngleDirection) else direction
        description = f"{direction_str} from {axis_label}-axis"

        return cls(axis_angle=axis_angle, direction=direction, axis_label=axis_label, angle_unit="radian", description=description)

    def to_standard(self, angle: float, angle_unit: str = "radian") -> float:
        """
        Convert an angle in this reference system to standard (CCW from +x-axis).

        Args:
            angle: Angle value in this reference system
            angle_unit: Unit of input angle ("degree" or "radian")

        Returns:
            Angle in radians, measured CCW from +x-axis (standard convention)

        Examples:
            >>> # 30° clockwise from +x is -30° CCW from +x = 330° CCW from +x
            >>> ref = AngleReference.from_axis("+x", direction="clockwise")
            >>> standard_angle = ref.to_standard(30, angle_unit="degree")
            >>> # standard_angle ≈ 5.759 radians (330°)
        """
        # Convert to radians if needed
        if angle_unit == "degree":
            angle_rad = math.radians(angle)
        else:
            angle_rad = angle

        # Apply direction (clockwise inverts the angle)
        if self.direction == AngleDirection.CLOCKWISE:
            angle_rad = -angle_rad

        # Add reference axis offset
        standard_angle = self.axis_angle + angle_rad

        # Normalize to [0, 2π)
        standard_angle = standard_angle % (2 * math.pi)

        return standard_angle

    def from_standard(self, standard_angle: float, angle_unit: str = "radian") -> float:
        """
        Convert a standard angle (CCW from +x-axis) to this reference system.

        Args:
            standard_angle: Angle in radians, measured CCW from +x-axis
            angle_unit: Desired output unit ("degree" or "radian")

        Returns:
            Angle in this reference system

        Examples:
            >>> # 330° CCW from +x is 30° CW from +x
            >>> ref = AngleReference.from_axis("+x", direction="clockwise")
            >>> ref_angle = ref.from_standard(math.radians(330), angle_unit="degree")
            >>> # ref_angle ≈ 30.0
        """
        # Subtract reference axis offset
        relative_angle = standard_angle - self.axis_angle

        # Apply direction (clockwise inverts the angle)
        if self.direction == AngleDirection.CLOCKWISE:
            relative_angle = -relative_angle

        # Normalize to [0, 2π)
        relative_angle = relative_angle % (2 * math.pi)

        # Convert to desired unit
        if angle_unit == "degree":
            return math.degrees(relative_angle)
        else:
            return relative_angle

    @property
    def description(self) -> str:
        """Human-readable description of this angle reference."""
        if self._description:
            return self._description

        direction_str = "counterclockwise" if self.direction == AngleDirection.COUNTERCLOCKWISE else "clockwise"
        return f"{direction_str} from {self.axis_label}"

    def __str__(self) -> str:
        """String representation."""
        return f"AngleReference({self.description})"

    def __repr__(self) -> str:
        """Representation."""
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        """Compare two AngleReferences for equality."""
        if not isinstance(other, AngleReference):
            return NotImplemented

        # Two angle references are equal if they produce the same conversion
        # for any given angle
        return math.isclose(self.axis_angle, other.axis_angle, abs_tol=1e-9) and self.direction == other.direction
