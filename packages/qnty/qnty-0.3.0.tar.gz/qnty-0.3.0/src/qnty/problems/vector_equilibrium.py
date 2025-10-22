"""
VectorEquilibriumProblem class for solving 2D/3D statics problems algebraically.

Uses closed-form solutions (law of cosines, law of sines, Pythagorean theorem)
instead of numerical solvers for fast, exact solutions with step-by-step reporting.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from ..core.quantity import Quantity
from ..solving.trig_solver import TrigSolver
from ..spatial.force_vector import ForceVector
from ..spatial.vector import Vector
from .problem import Problem


class VectorEquilibriumProblem(Problem):
    """
    Specialized Problem for 2D/3D vector equilibrium using algebraic methods.

    Automatically applies:
    - Law of cosines: c² = a² + b² - 2ab·cos(C)
    - Law of sines: a/sin(A) = b/sin(B) = c/sin(C)
    - Pythagorean theorem: c² = a² + b² (when angle = 90°)
    - Component summation: ΣFx = 0, ΣFy = 0, ΣFz = 0

    Examples:
        >>> # Define problem with class inheritance
        >>> class CableProblem(VectorEquilibriumProblem):
        ...     F1 = ForceVector(magnitude=700, angle=60, unit="N")
        ...     F2 = ForceVector(magnitude=450, angle=105, unit="N")
        ...     FR = ForceVector.unknown("FR", is_resultant=True)
        ...
        >>> problem = CableProblem()
        >>> solution = problem.solve()

        >>> # Or programmatically
        >>> problem = VectorEquilibriumProblem("Cable Forces")
        >>> problem.add_force(ForceVector(magnitude=700, angle=60, unit="N", name="F1"))
        >>> problem.add_force(ForceVector(magnitude=450, angle=105, unit="N", name="F2"))
        >>> problem.add_force(ForceVector.unknown("FR", is_resultant=True))
        >>> solution = problem.solve()
    """

    def __init__(self, name: str | None = None, description: str = ""):
        """
        Initialize VectorEquilibriumProblem.

        Args:
            name: Problem name
            description: Problem description
        """
        super().__init__(name=name, description=description)
        self.forces: dict[str, ForceVector] = {}
        self.solution_steps: list[dict[str, Any]] = []
        self._original_variable_states: dict[str, bool] = {}  # Track which variables were originally known
        self._original_force_states: dict[str, bool] = {}  # Track original is_known state of each force
        self.solver = TrigSolver()  # Create trig solver instance

        # Extract ForceVector class attributes
        self._extract_force_vectors()

    def _extract_force_vectors(self) -> None:
        """Extract ForceVector objects defined at class level."""
        for attr_name in dir(self.__class__):
            if attr_name.startswith("_"):
                continue

            attr = getattr(self.__class__, attr_name)
            if isinstance(attr, ForceVector):
                # Clone to avoid sharing between instances
                force_copy = self._clone_force_vector(attr)
                self.forces[attr_name] = force_copy
                setattr(self, attr_name, force_copy)

    def _clone_force_vector(self, force: ForceVector) -> ForceVector:
        """Create a copy of a ForceVector."""
        if force.is_known and force.vector is not None:
            # Known force - copy with same values
            return ForceVector(
                vector=force.vector,
                name=force.name,
                description=force.description,
                is_known=True,
                is_resultant=force.is_resultant,
                coordinate_system=force.coordinate_system,
                angle_reference=force.angle_reference,
            )
        else:
            # Unknown force - may have known angle but unknown magnitude
            angle_value = None
            angle_unit = None
            if force.angle is not None and force.angle.value is not None:
                # Angle is stored internally as standard (CCW from +x)
                # Convert back to the angle_reference system for cloning
                angle_value = force.angle_reference.from_standard(force.angle.value, angle_unit="degree")
                angle_unit = "degree"

            return ForceVector.unknown(
                name=force.name,
                is_resultant=force.is_resultant,
                angle=angle_value,
                angle_unit=angle_unit,
                description=force.description,
                coordinate_system=force.coordinate_system,
                angle_reference=force.angle_reference,
            )

    def add_force(self, force: ForceVector, name: str | None = None) -> None:
        """
        Add a force to the problem.

        Args:
            force: ForceVector to add
            name: Optional name (uses force.name if not provided)
        """
        force_name = name or force.name
        self.forces[force_name] = force
        setattr(self, force_name, force)

    def get_known_variables(self) -> dict[str, Quantity]:
        """
        Get known variables for report generation.

        Returns:
            Dictionary of variable names to Quantity objects that were originally known
        """
        known_vars = {}
        for var_name, var in self.variables.items():
            if self._original_variable_states.get(var_name, False):
                known_vars[var_name] = var
        return known_vars

    def get_unknown_variables(self) -> dict[str, Quantity]:
        """
        Get unknown variables for report generation.

        Returns:
            Dictionary of variable names to Quantity objects that were originally unknown
        """
        unknown_vars = {}
        for var_name, var in self.variables.items():
            if not self._original_variable_states.get(var_name, False):
                unknown_vars[var_name] = var
        return unknown_vars

    def solve(self, max_iterations: int = 100, tolerance: float = 1e-10) -> dict[str, ForceVector]:  # type: ignore[override]
        """
        Solve the vector equilibrium problem algebraically.

        Args:
            max_iterations: Not used (for compatibility with parent class)
            tolerance: Not used (for compatibility with parent class)

        Returns:
            Dictionary mapping force names to solved ForceVector objects

        Raises:
            ValueError: If problem is under-constrained or over-constrained
        """
        self.solution_steps = []

        # Save original is_known state for each force (for report generation)
        if not self._original_force_states:  # Only save once
            for force_name, force in self.forces.items():
                # Save whether the force was known
                self._original_force_states[force_name] = force.is_known

                # Also track which individual components were known before solving
                # This handles partially known forces (e.g., known angle, unknown magnitude)
                mag_known = force.magnitude is not None and force.magnitude.value is not None
                angle_known = force.angle is not None and force.angle.value is not None
                self._original_variable_states[f"{force_name}_mag_known"] = mag_known
                self._original_variable_states[f"{force_name}_angle_known"] = angle_known

        # Analyze problem type
        known_forces = [f for f in self.forces.values() if f.is_known]
        unknown_forces = [f for f in self.forces.values() if not f.is_known]
        resultant_forces = [f for f in self.forces.values() if f.is_resultant]

        self.logger.info(f"Solving {self.name}: {len(known_forces)} known, {len(unknown_forces)} unknown")

        # Determine solution method
        if len(unknown_forces) == 0:
            # All forces known - compute resultant
            self._solve_resultant(known_forces)
        elif len(unknown_forces) == 1 and len(known_forces) >= 1:
            # One unknown - solve using equilibrium
            self._solve_single_unknown(known_forces, unknown_forces[0], resultant_forces)
        elif len(unknown_forces) == 2 and len(resultant_forces) == 1:
            # Two unknowns with known resultant
            self._solve_two_unknowns_with_resultant(known_forces, unknown_forces, resultant_forces[0])
        else:
            raise ValueError(f"Problem configuration not supported: {len(known_forces)} known, {len(unknown_forces)} unknown")

        self.is_solved = True

        # Convert forces to variables for report generation compatibility
        self._populate_variables_from_forces()

        # Populate solving history for report generation
        self._populate_solving_history()

        return self.forces

    def _populate_variables_from_forces(self) -> None:
        """
        Convert ForceVector objects to Quantity variables for report generation.

        This ensures compatibility with qnty's report generation system.
        """
        from ..core.dimension_catalog import dim

        for force_name, force in self.forces.items():
            # Determine if this was originally known or unknown
            was_originally_known = not force.is_resultant

            if force.magnitude is not None and force.magnitude.value is not None:
                # Add magnitude as a variable
                mag_var = Quantity(name=f"{force.name} Magnitude", dim=dim.force, value=force.magnitude.value, preferred=force.magnitude.preferred, _symbol=f"{force_name}_mag")
                self.variables[f"{force_name}_mag"] = mag_var

                # Store original state for report generator
                if was_originally_known:
                    self._original_variable_states[f"{force_name}_mag"] = True
                else:
                    self._original_variable_states[f"{force_name}_mag"] = False

            if force.angle is not None and force.angle.value is not None:
                # Add angle as a variable
                angle_var = Quantity(name=f"{force.name} Direction", dim=dim.D, value=force.angle.value, preferred=force.angle.preferred, _symbol=f"{force_name}_angle")
                self.variables[f"{force_name}_angle"] = angle_var

                # Store original state
                if was_originally_known:
                    self._original_variable_states[f"{force_name}_angle"] = True
                else:
                    self._original_variable_states[f"{force_name}_angle"] = False

            # Add components if available
            if force.x is not None and force.x.value is not None:
                x_var = Quantity(name=f"{force.name} X-Component", dim=dim.force, value=force.x.value, preferred=force.x.preferred, _symbol=f"{force_name}_x")
                self.variables[f"{force_name}_x"] = x_var

            if force.y is not None and force.y.value is not None:
                y_var = Quantity(name=f"{force.name} Y-Component", dim=dim.force, value=force.y.value, preferred=force.y.preferred, _symbol=f"{force_name}_y")
                self.variables[f"{force_name}_y"] = y_var

    def _populate_solving_history(self) -> None:
        """
        Convert solution_steps to solving_history format for report generation.

        This ensures the step-by-step solution shows up in generated reports.
        """
        self.solving_history = []

        for i, step in enumerate(self.solution_steps):
            # Our new format already has the correct fields
            history_entry = {
                "step": i + 1,
                "target": step.get("target", "Unknown"),
                "method": step.get("method", "algebraic"),
                "description": step.get("description", ""),
                "equation_str": step.get("equation", ""),
                "substituted": step.get("substitution", ""),
                "result_value": step.get("result_value", ""),
                "result_unit": step.get("result_unit", ""),
                "details": step.get("description", ""),
            }
            self.solving_history.append(history_entry)

    def _solve_resultant(self, known_forces: list[ForceVector]) -> None:
        """
        Compute resultant of known forces.

        Uses vector addition (component summation).
        """
        self.solution_steps.append({"method": "Vector Addition (Component Summation)", "description": "Sum all force components to find resultant"})

        # Sum components
        sum_x = 0.0
        sum_y = 0.0
        sum_z = 0.0
        ref_unit = None

        for force in known_forces:
            if force.vector is None or force.x is None or force.y is None or force.z is None:
                continue

            if force.x.value is not None:
                sum_x += force.x.value
            if force.y.value is not None:
                sum_y += force.y.value
            if force.z.value is not None:
                sum_z += force.z.value

            if ref_unit is None and force.x.preferred is not None:
                ref_unit = force.x.preferred

        # Create resultant vector
        from ..core.dimension_catalog import dim

        x_qty = Quantity(name="FR_x", dim=dim.force, value=sum_x, preferred=ref_unit)
        y_qty = Quantity(name="FR_y", dim=dim.force, value=sum_y, preferred=ref_unit)
        z_qty = Quantity(name="FR_z", dim=dim.force, value=sum_z, preferred=ref_unit)

        resultant_vector = Vector.from_quantities(x_qty, y_qty, z_qty)

        # Find or create resultant force
        resultant = None
        for force_name, force in self.forces.items():
            if force.is_resultant:
                resultant = force
                break

        if resultant is None:
            resultant = ForceVector(vector=resultant_vector, name="FR", is_resultant=True)
            self.forces["FR"] = resultant
            setattr(self, "FR", resultant)
        else:
            # Update existing resultant
            resultant._vector = resultant_vector
            resultant._compute_magnitude_and_angle()
            resultant.is_known = True

        if ref_unit is not None and resultant.magnitude is not None and resultant.angle is not None:
            mag_value = resultant.magnitude.value / ref_unit.si_factor if resultant.magnitude.value is not None else 0.0
            ang_value = resultant.angle.value * 180 / math.pi if resultant.angle.value is not None else 0.0
            self.solution_steps.append({"result": f"Resultant: {mag_value:.2f} {ref_unit.symbol} at {ang_value:.1f}°"})

    def _solve_single_unknown(self, known_forces: list[ForceVector], unknown_force: ForceVector, resultant_forces: list[ForceVector]) -> None:
        """
        Solve for single unknown force given known forces.

        Uses law of cosines and law of sines.
        """
        # Special case: Known resultant + one known force, solve for unknown force
        # Pattern: F_unknown + F_known = F_resultant (where F_resultant is also in known_forces)
        if len(resultant_forces) == 1 and len(known_forces) == 2:
            # Check if one of the known forces is the resultant
            resultant = resultant_forces[0]
            if resultant in known_forces:
                # Find the other known force (not the resultant)
                other_known = [f for f in known_forces if f != resultant][0]
                # Solve: F_unknown = F_resultant - F_other_known
                self._solve_unknown_from_resultant_and_known(unknown_force, resultant, other_known)
                return

        if len(known_forces) == 2 and len(resultant_forces) == 1:
            # Two known forces, unknown resultant
            self._solve_resultant_from_two_forces(known_forces[0], known_forces[1], unknown_force)
        elif len(known_forces) == 2 and unknown_force.is_resultant:
            # Two known forces, solve for resultant
            self._solve_resultant_from_two_forces(known_forces[0], known_forces[1], unknown_force)
        elif len(known_forces) >= 2 and not unknown_force.is_resultant:
            # Multiple known forces and unknown resultant - find equilibrium force
            # First compute resultant of known forces
            self._solve_resultant(known_forces)
            # The unknown force must balance this resultant
            resultant = self.forces.get("FR")
            if resultant and resultant.vector:
                # Unknown force is negative of resultant
                unknown_vector = -resultant.vector
                unknown_force._vector = unknown_vector
                unknown_force._compute_magnitude_and_angle()
                unknown_force.is_known = True
        else:
            # Fall back to component summation
            self._solve_by_components(known_forces, unknown_force)

    def _solve_unknown_from_resultant_and_known(self, unknown_force: ForceVector, resultant: ForceVector, known_force: ForceVector) -> None:
        """
        Solve for unknown force given known resultant and one known force.

        Uses Law of Cosines and Law of Sines to solve the triangle formed by:
        F_unknown + F_known = F_resultant

        This is the same method as solving for a resultant from two known forces,
        but we're solving for one of the sides instead of the resultant.
        """
        # Get magnitudes and angles
        if resultant.magnitude is None or resultant.magnitude.value is None:
            raise ValueError(f"Resultant {resultant.name} has no magnitude")
        if known_force.magnitude is None or known_force.magnitude.value is None:
            raise ValueError(f"Force {known_force.name} has no magnitude")
        if resultant.angle is None or resultant.angle.value is None:
            raise ValueError(f"Resultant {resultant.name} has no angle")
        if known_force.angle is None or known_force.angle.value is None:
            raise ValueError(f"Force {known_force.name} has no angle")

        F_R = resultant.magnitude.value
        F_known = known_force.magnitude.value
        theta_R = resultant.angle.value  # radians
        theta_known = known_force.angle.value  # radians

        # Compute the angle between the resultant and known force in the triangle
        # This is the interior angle at the junction point
        gamma = abs(theta_R - theta_known)
        # Ensure gamma is the angle in the triangle (between 0 and π)
        if gamma > math.pi:
            gamma = 2 * math.pi - gamma

        # Apply law of cosines: F_unknown² = F_R² + F_known² - 2·F_R·F_known·cos(γ)
        # This gives us the magnitude of the unknown force
        F_unknown_squared = F_R**2 + F_known**2 - 2 * F_R * F_known * math.cos(gamma)
        F_unknown = math.sqrt(F_unknown_squared)

        # Now find the angle of the unknown force using vector addition
        # F_unknown = F_R - F_known (vector subtraction)
        F_Rx = F_R * math.cos(theta_R)
        F_Ry = F_R * math.sin(theta_R)
        F_knownx = F_known * math.cos(theta_known)
        F_knowny = F_known * math.sin(theta_known)
        F_unknownx = F_Rx - F_knownx
        F_unknowny = F_Ry - F_knowny
        theta_unknown = math.atan2(F_unknowny, F_unknownx)

        # Get unit symbols
        force_unit = resultant.magnitude.preferred.symbol if resultant.magnitude.preferred else "N"

        # Step 1: Solve for unknown magnitude using Law of Cosines
        gamma_deg = math.degrees(gamma)
        # Use LaTeX theta command for proper rendering with force angles
        # Format subscript to handle underscores properly (e.g., F_R becomes F_{R})
        resultant_subscript = resultant.name.replace("_", "_{") + "}" if "_" in resultant.name else resultant.name
        known_subscript = known_force.name.replace("_", "_{") + "}" if "_" in known_force.name else known_force.name
        # Display as cos(θ_R - θ_known) or cos(θ_known - θ_R) depending on which is larger
        if theta_R > theta_known:
            angle_expr = f"\\theta_{{{resultant_subscript}}} - \\theta_{{{known_subscript}}}"
        else:
            angle_expr = f"\\theta_{{{known_subscript}}} - \\theta_{{{resultant_subscript}}}"

        self.solution_steps.append(
            {
                "target": f"|{unknown_force.name}|",
                "method": "Law of Cosines",
                "equation": f"{unknown_force.name}^2 = {resultant.name}^2 + {known_force.name}^2 - 2*{resultant.name}*{known_force.name}*cos({angle_expr})",
                "substitution": f"{unknown_force.name}^2 = ({F_R:.2f} {force_unit})^2 + ({F_known:.2f} {force_unit})^2 - 2 * ({F_R:.2f} {force_unit}) * ({F_known:.2f} {force_unit}) * cos({gamma_deg:.1f}°)",
                "result_value": f"{F_unknown:.2f}",
                "result_unit": force_unit,
            }
        )

        # Step 2: Solve for unknown direction using Law of Sines
        # sin(alpha) / F_known = sin(gamma) / F_unknown
        sin_alpha = F_known * math.sin(gamma) / F_unknown
        alpha = math.asin(np.clip(sin_alpha, -1.0, 1.0))

        # The angle we report depends on the geometry
        # For the textbook problem, they report θ where sin(90°+θ)/F_known = sin(gamma)/F_unknown
        theta_unknown_deg = math.degrees(theta_unknown)

        # Format the angle expression using theta notation like in Law of Cosines
        # For consistency, use theta notation for all force angles
        unknown_subscript = unknown_force.name.replace("_", "_{") + "}" if "_" in unknown_force.name else unknown_force.name
        unknown_angle = f"\\theta_{{{unknown_subscript}}}"  # Direction angle of unknown force
        # gamma is the same angle as in Law of Cosines
        if theta_R > theta_known:
            gamma_angle = f"\\theta_{{{resultant_subscript}}} - \\theta_{{{known_subscript}}}"
        else:
            gamma_angle = f"\\theta_{{{known_subscript}}} - \\theta_{{{resultant_subscript}}}"

        self.solution_steps.append(
            {
                "target": f"{unknown_angle}",
                "method": "Law of Sines",
                "equation": f"sin({unknown_angle}) / {known_force.name} = sin({gamma_angle}) / {unknown_force.name}",
                "substitution": f"sin({unknown_angle}) / {F_known:.2f} {force_unit} = sin({gamma_deg:.1f}°) / {F_unknown:.2f} {force_unit}",
                "result_value": f"{theta_unknown_deg:.2f}",
                "result_unit": "°",
            }
        )

        # Create unknown force vector
        ref_unit = resultant.magnitude.preferred
        from ..core.dimension_catalog import dim
        from ..core.unit import ureg

        mag_qty = Quantity(name=f"{unknown_force.name}_magnitude", dim=dim.force, value=F_unknown, preferred=ref_unit)
        degree_unit = ureg.resolve("degree", dim=dim.D)
        angle_qty = Quantity(name=f"{unknown_force.name}_angle", dim=dim.D, value=theta_unknown, preferred=degree_unit)

        # Use the computed components
        unknown_vector = Vector(F_unknownx, F_unknowny, 0.0, unit=ref_unit)

        # Update unknown force
        unknown_force._vector = unknown_vector
        unknown_force._magnitude = mag_qty
        unknown_force._angle = angle_qty
        unknown_force.is_known = True

    def _solve_resultant_from_two_forces(self, force1: ForceVector, force2: ForceVector, resultant: ForceVector) -> None:
        """
        Solve for resultant of two forces using law of cosines and law of sines.

        This is the classic parallelogram/triangle method.
        """
        # Get magnitudes and angles
        if force1.magnitude is None or force1.magnitude.value is None:
            raise ValueError(f"Force {force1.name} has no magnitude")
        if force2.magnitude is None or force2.magnitude.value is None:
            raise ValueError(f"Force {force2.name} has no magnitude")
        if force1.angle is None or force1.angle.value is None:
            raise ValueError(f"Force {force1.name} has no angle")
        if force2.angle is None or force2.angle.value is None:
            raise ValueError(f"Force {force2.name} has no angle")

        F1 = force1.magnitude.value
        F2 = force2.magnitude.value
        theta1 = force1.angle.value  # radians
        theta2 = force2.angle.value  # radians

        # Compute the angle between the two forces
        # Always use the positive angle between 0 and 2π
        gamma = abs(theta2 - theta1)
        # Ensure gamma is the smaller angle (between 0 and π)
        if gamma > math.pi:
            gamma = 2 * math.pi - gamma

        # Apply law of cosines: FR² = F1² + F2² - 2·F1·F2·cos(180° - γ)
        # Note: The angle in the triangle is (180° - γ) due to parallelogram law
        angle_in_triangle = math.pi - gamma
        FR_squared = F1**2 + F2**2 - 2 * F1 * F2 * math.cos(angle_in_triangle)
        FR = math.sqrt(FR_squared)

        # Compute resultant using vector addition (this gives the correct angle)
        F1x = F1 * math.cos(theta1)
        F1y = F1 * math.sin(theta1)
        F2x = F2 * math.cos(theta2)
        F2y = F2 * math.sin(theta2)
        FRx = F1x + F2x
        FRy = F1y + F2y
        theta_R = math.atan2(FRy, FRx)

        # Get unit symbols
        force_unit = force1.magnitude.preferred.symbol if force1.magnitude.preferred else "N"

        # Step 1: Solve for resultant magnitude using Law of Cosines
        # Format substitution like reference: value and unit separated, no complex nesting
        gamma_deg = math.degrees(angle_in_triangle)
        # Use LaTeX theta command for proper rendering with force angles
        # Display as cos(θ_F2 - θ_F1) or cos(θ_F1 - θ_F2) depending on which is larger
        if theta2 > theta1:
            angle_expr = f"\\theta_{{{force2.name}}} - \\theta_{{{force1.name}}}"
        else:
            angle_expr = f"\\theta_{{{force1.name}}} - \\theta_{{{force2.name}}}"

        self.solution_steps.append(
            {
                "target": f"|{resultant.name}|",
                "method": "Law of Cosines",
                "equation": f"{resultant.name}^2 = {force1.name}^2 + {force2.name}^2 - 2*{force1.name}*{force2.name}*cos(180° - ({angle_expr}))",
                "substitution": f"{resultant.name}^2 = ({F1:.2f} {force_unit})^2 + ({F2:.2f} {force_unit})^2 - 2 * ({F1:.2f} {force_unit}) * ({F2:.2f} {force_unit}) * cos({gamma_deg:.1f}°)",
                "result_value": f"{FR:.2f}",
                "result_unit": force_unit,
            }
        )

        # Step 2: Solve for resultant direction using Law of Sines
        # Calculate alpha using law of sines for display purposes
        sin_alpha = F1 * math.sin(angle_in_triangle) / FR
        alpha = math.asin(np.clip(sin_alpha, -1.0, 1.0))

        # Format resultant angle using theta notation
        resultant_subscript = resultant.name.replace("_", "_{") + "}" if "_" in resultant.name else resultant.name
        resultant_angle = f"\\theta_{{{resultant_subscript}}}"

        self.solution_steps.append(
            {
                "target": f"{resultant_angle}",
                "method": "Law of Sines",
                "equation": f"sin(alpha) / {force1.name} = sin(gamma) / {resultant.name}",
                "substitution": f"sin(alpha) / {F1:.2f} {force_unit} = sin({math.degrees(angle_in_triangle):.1f}°) / {FR:.2f} {force_unit}",
                "result_value": f"{math.degrees(theta_R):.2f}",
                "result_unit": "°",
            }
        )

        # Create resultant vector using the correct angle from atan2
        ref_unit = force1.magnitude.preferred
        from ..core.dimension_catalog import dim
        from ..core.unit import ureg

        mag_qty = Quantity(name="FR_magnitude", dim=dim.force, value=FR, preferred=ref_unit)
        degree_unit = ureg.resolve("degree", dim=dim.D)
        angle_qty = Quantity(name="FR_angle", dim=dim.D, value=theta_R, preferred=degree_unit)

        # Use the computed components
        resultant_vector = Vector(FRx, FRy, 0.0, unit=ref_unit)

        # Update resultant force
        resultant._vector = resultant_vector
        resultant._magnitude = mag_qty
        resultant._angle = angle_qty
        resultant.is_known = True

    def _solve_two_unknowns_with_resultant(
        self,
        known_forces: list[ForceVector],  # noqa: ARG002
        unknown_forces: list[ForceVector],
        resultant: ForceVector,
    ) -> None:
        """
        Solve for two unknowns given a known resultant.

        This uses the TrigSolver to solve decomposition problems where the resultant
        and component angles are known, but component magnitudes are unknown.
        """
        if resultant.is_known:
            self.solver.solve_two_unknowns_with_known_resultant(unknown_forces, resultant)
        else:
            raise ValueError("Cannot solve: two unknowns require a known resultant")

    def _solve_by_components(self, known_forces: list[ForceVector], unknown_force: ForceVector) -> None:
        """
        Solve using component summation (ΣFx = 0, ΣFy = 0).

        This assumes equilibrium: unknown force balances known forces.
        """
        self.solution_steps.append({"method": "Component Summation (Equilibrium)", "description": "ΣFx = 0, ΣFy = 0"})

        # Sum known force components
        sum_x = 0.0
        sum_y = 0.0
        sum_z = 0.0
        ref_unit = None

        for force in known_forces:
            if force.vector is None or force.x is None or force.y is None or force.z is None:
                continue

            if force.x.value is not None:
                sum_x += force.x.value
            if force.y.value is not None:
                sum_y += force.y.value
            if force.z.value is not None:
                sum_z += force.z.value

            if ref_unit is None and force.x.preferred is not None:
                ref_unit = force.x.preferred

        # Unknown force must balance the sum
        unknown_x = -sum_x
        unknown_y = -sum_y
        unknown_z = -sum_z

        self.solution_steps.append({"calculation": f"ΣFx = {sum_x:.2f} → Unknown Fx = {unknown_x:.2f}", "calculation2": f"ΣFy = {sum_y:.2f} → Unknown Fy = {unknown_y:.2f}"})

        # Create unknown vector
        from ..core.dimension_catalog import dim

        x_qty = Quantity(name=f"{unknown_force.name}_x", dim=dim.force, value=unknown_x, preferred=ref_unit)
        y_qty = Quantity(name=f"{unknown_force.name}_y", dim=dim.force, value=unknown_y, preferred=ref_unit)
        z_qty = Quantity(name=f"{unknown_force.name}_z", dim=dim.force, value=unknown_z, preferred=ref_unit)

        unknown_vector = Vector.from_quantities(x_qty, y_qty, z_qty)

        # Update unknown force
        unknown_force._vector = unknown_vector
        unknown_force._compute_magnitude_and_angle()
        unknown_force.is_known = True

    def generate_report_content(self) -> dict[str, Any]:
        """
        Generate report content for vector equilibrium problem.

        Returns:
            Dictionary with report sections
        """
        content = {"title": self.name, "description": self.description, "problem_type": "Vector Equilibrium (Statics)", "given": [], "find": [], "solution_steps": self.solution_steps, "results": []}

        # List given forces
        for name, force in self.forces.items():
            if force.is_known and not force.is_resultant and force.magnitude is not None and force.angle is not None:
                if force.magnitude.value is not None and force.angle.value is not None:
                    mag_val = force.magnitude.value / force.magnitude.preferred.si_factor if force.magnitude.preferred else force.magnitude.value
                    ang_val = force.angle.value * 180 / math.pi
                    mag_unit = force.magnitude.preferred.symbol if force.magnitude.preferred else ""

                    content["given"].append(f"{name} = {mag_val:.1f} {mag_unit} at {ang_val:.1f}°")

        # List unknowns
        for name, force in self.forces.items():
            if not force.is_known or (force.is_resultant and not self.is_solved):
                content["find"].append(f"{name}: {force.description or 'magnitude and direction'}")

        # List results
        if self.is_solved:
            for name, force in self.forces.items():
                if force.is_resultant or (not force.is_known):
                    if force.magnitude and force.angle and force.magnitude.value is not None and force.angle.value is not None:
                        mag_val = force.magnitude.value / force.magnitude.preferred.si_factor if force.magnitude.preferred else force.magnitude.value
                        ang_val = force.angle.value * 180 / math.pi
                        mag_unit = force.magnitude.preferred.symbol if force.magnitude.preferred else ""

                        content["results"].append(f"{name} = {mag_val:.1f} {mag_unit} at {ang_val:.1f}°")

        return content

    def __str__(self) -> str:
        """String representation."""
        status = "SOLVED" if self.is_solved else "UNSOLVED"
        return f"VectorEquilibriumProblem('{self.name}', forces={len(self.forces)}, {status})"
