"""
Vector diagram visualization for statics problems.

Generates properly scaled and labeled vector diagrams for force vectors,
including angles, components, and resultants. Diagrams can be saved as
images for inclusion in PDF reports.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, FancyArrowPatch

if TYPE_CHECKING:
    from ...spatial.force_vector import ForceVector


class VectorDiagram:
    """
    Generate scaled vector diagrams for statics problems.

    Creates professional-quality diagrams with:
    - Scaled vector arrows
    - Coordinate axes
    - Angle annotations
    - Force labels
    - Optional component projections
    - Grid (optional)

    Examples:
        >>> diagram = VectorDiagram(title="Cable Forces")
        >>> diagram.add_vector(F1, color='red', label='F₁')
        >>> diagram.add_vector(F2, color='blue', label='F₂')
        >>> diagram.add_resultant(FR, color='green', label='FR')
        >>> diagram.save("diagram.png")
    """

    def __init__(
        self,
        title: str = "Vector Diagram",
        figsize: tuple[float, float] = (10, 10),
        show_grid: bool = True,
        show_components: bool = False,
        origin: tuple[float, float] = (0, 0)
    ):
        """
        Initialize vector diagram.

        Args:
            title: Diagram title
            figsize: Figure size in inches (width, height)
            show_grid: Whether to show grid
            show_components: Whether to show component projections
            origin: Origin point (x, y) for vectors
        """
        self.title = title
        self.figsize = figsize
        self.show_grid = show_grid
        self.show_components = show_components
        self.origin = origin

        # Storage for vectors
        self.vectors: list[dict] = []
        self.resultant: dict | None = None

        # Auto-scale parameters (computed when drawing)
        self.max_magnitude: float = 0.0

    def add_vector(
        self,
        force: ForceVector,
        color: str = 'blue',
        label: str | None = None,
        show_angle: bool = True,
        linewidth: float = 2.5
    ) -> None:
        """
        Add a force vector to the diagram.

        Args:
            force: ForceVector to add
            color: Arrow color
            label: Label for vector (uses force.name if None)
            show_angle: Whether to show angle annotation
            linewidth: Arrow line width
        """
        if not force.is_known or force.magnitude is None or force.angle is None:
            return

        mag = force.magnitude.value if force.magnitude.value else 0.0
        angle_rad = force.angle.value if force.angle.value else 0.0

        self.vectors.append({
            'force': force,
            'magnitude': mag,
            'angle': angle_rad,
            'color': color,
            'label': label or force.name,
            'show_angle': show_angle,
            'linewidth': linewidth
        })

        # Update max magnitude for scaling
        if mag > self.max_magnitude:
            self.max_magnitude = mag

    def add_resultant(
        self,
        force: ForceVector,
        color: str = 'green',
        label: str | None = None,
        linewidth: float = 3.0
    ) -> None:
        """
        Add resultant force vector (drawn with dashed line).

        Args:
            force: Resultant ForceVector
            color: Arrow color
            label: Label for resultant
            linewidth: Arrow line width
        """
        if not force.is_known or force.magnitude is None or force.angle is None:
            return

        mag = force.magnitude.value if force.magnitude.value else 0.0
        angle_rad = force.angle.value if force.angle.value else 0.0

        self.resultant = {
            'force': force,
            'magnitude': mag,
            'angle': angle_rad,
            'color': color,
            'label': label or force.name,
            'linewidth': linewidth
        }

        # Update max magnitude for scaling
        if mag > self.max_magnitude:
            self.max_magnitude = mag

    def save(
        self,
        output_path: str | Path,
        dpi: int = 300,
        bbox_inches: str = 'tight'
    ) -> Path:
        """
        Generate and save the vector diagram.

        Args:
            output_path: Output file path (png, pdf, svg supported)
            dpi: Resolution for raster formats
            bbox_inches: Bounding box setting

        Returns:
            Path to saved file
        """
        output_path = Path(output_path)

        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)

        # Set title
        ax.set_title(self.title, fontsize=16, fontweight='bold', pad=20)

        # Calculate scale factor and determine plot bounds
        # First, find the actual extent of all vectors
        scale_factor = 1.0
        max_x, min_x, max_y, min_y = 0.0, 0.0, 0.0, 0.0

        if self.max_magnitude > 0:
            scale_factor = 8.0 / self.max_magnitude  # Scale to ~8 units

            # Calculate actual bounds needed to show all vectors
            for vec_data in self.vectors:
                mag = vec_data['magnitude']
                angle = vec_data['angle']
                scaled_mag = mag * scale_factor
                x = scaled_mag * np.cos(angle)
                y = scaled_mag * np.sin(angle)
                max_x = max(max_x, x)
                min_x = min(min_x, x)
                max_y = max(max_y, y)
                min_y = min(min_y, y)

            if self.resultant:
                mag = self.resultant['magnitude']
                angle = self.resultant['angle']
                scaled_mag = mag * scale_factor
                x = scaled_mag * np.cos(angle)
                y = scaled_mag * np.sin(angle)
                max_x = max(max_x, x)
                min_x = min(min_x, x)
                max_y = max(max_y, y)
                min_y = min(min_y, y)

        # Draw regular vectors
        for vec_data in self.vectors:
            self._draw_vector(ax, vec_data, scale_factor)

        # Draw resultant (if present)
        if self.resultant:
            self._draw_resultant(ax, self.resultant, scale_factor)

        # Set equal aspect ratio
        ax.set_aspect('equal', adjustable='box')

        # Configure grid
        if self.show_grid:
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, zorder=0)

        # Set limits with padding - ensure we show all quadrants with vectors
        # Always show at least a small margin even if vectors are in only one quadrant
        margin = 1.5
        xlim_min = min(min_x - margin, -1.0)
        xlim_max = max(max_x + margin, 1.0)
        ylim_min = min(min_y - margin, -1.0)
        ylim_max = max(max_y + margin, 1.0)

        ax.set_xlim(xlim_min, xlim_max)
        ax.set_ylim(ylim_min, ylim_max)

        # Draw coordinate axes AFTER setting limits so they span properly
        self._draw_axes(ax, xlim_min, xlim_max, ylim_min, ylim_max)

        # Get unit from first vector for axis labels
        unit_str = self._get_unit_string()

        # Transform axis ticks to show actual force magnitudes
        if unit_str and self.max_magnitude > 0:
            # Get current tick locations
            xticks = ax.get_xticks()
            yticks = ax.get_yticks()

            # Convert scaled positions back to actual force magnitudes
            unit_scale = self.max_magnitude / 8.0  # Inverse of scale_factor

            # Set tick positions explicitly, then set labels
            ax.set_xticks(xticks)
            ax.set_yticks(yticks)
            ax.set_xticklabels([f'{x * unit_scale:.0f}' for x in xticks])
            ax.set_yticklabels([f'{y * unit_scale:.0f}' for y in yticks])

            # Axis labels with units
            ax.set_xlabel(f'x-component ({unit_str})', fontsize=12, fontweight='bold')
            ax.set_ylabel(f'y-component ({unit_str})', fontsize=12, fontweight='bold')
        else:
            ax.set_xlabel('x', fontsize=12, fontweight='bold')
            ax.set_ylabel('y', fontsize=12, fontweight='bold')

        # Add legend
        ax.legend(loc='best', fontsize=11, framealpha=0.9, fancybox=True, shadow=True)

        # Save figure
        plt.savefig(output_path, dpi=dpi, bbox_inches=bbox_inches)
        plt.close(fig)

        return output_path

    def _get_unit_string(self) -> str:
        """Get unit string from first vector."""
        if self.vectors and len(self.vectors) > 0:
            force = self.vectors[0]['force']
            if force.magnitude and force.magnitude.preferred:
                return force.magnitude.preferred.symbol
        if self.resultant:
            force = self.resultant['force']
            if force.magnitude and force.magnitude.preferred:
                return force.magnitude.preferred.symbol
        return ""

    def _format_label_for_legend(self, label: str) -> str:
        """Format label for legend using LaTeX."""
        # Convert underscores to subscripts for legend
        # F_1 -> F₁, F_R -> Fᴿ
        if '_' in label:
            parts = label.split('_', 1)
            if len(parts) == 2:
                base, subscript = parts
                return f'${base}_{{{subscript}}}$'
        return label

    def _format_vector_label(self, force: ForceVector, label: str) -> str:
        """
        Format vector label with LaTeX notation and magnitude.

        Returns formatted string like: "$F_1$ = 450 N"
        """
        # Format the force name with LaTeX subscripts
        latex_label = self._format_label_for_legend(label)

        # Get magnitude and unit
        if force.magnitude and force.magnitude.value is not None:
            mag_value = force.magnitude.value
            if force.magnitude.preferred:
                mag_value = mag_value / force.magnitude.preferred.si_factor
                unit = force.magnitude.preferred.symbol
            else:
                unit = "N"

            # Format: $F_1$ = 450 N
            return f"{latex_label} = {mag_value:.0f} {unit}"
        else:
            return latex_label

    def _draw_axes(self, ax, xlim_min: float, xlim_max: float, ylim_min: float, ylim_max: float) -> None:
        """Draw coordinate axes spanning the entire plot."""
        # Origin marker
        ax.plot(0, 0, 'ko', markersize=8, zorder=5)

        # X-axis spanning entire width
        ax.annotate('', xy=(xlim_max * 0.95, 0), xytext=(xlim_min * 0.95, 0),
                    arrowprops=dict(arrowstyle='->', lw=2, color='black'), zorder=1)

        # Y-axis spanning entire height
        ax.annotate('', xy=(0, ylim_max * 0.95), xytext=(0, ylim_min * 0.95),
                    arrowprops=dict(arrowstyle='->', lw=2, color='black'), zorder=1)

    def _draw_vector(self, ax, vec_data: dict, scale_factor: float) -> None:
        """Draw a force vector."""
        mag = vec_data['magnitude']
        angle = vec_data['angle']
        color = vec_data['color']
        label = vec_data['label']
        show_angle = vec_data['show_angle']
        linewidth = vec_data['linewidth']
        force = vec_data['force']

        # Calculate scaled magnitude
        scaled_mag = mag * scale_factor

        # Calculate endpoint
        x_end = scaled_mag * math.cos(angle)
        y_end = scaled_mag * math.sin(angle)

        # Draw vector arrow with larger, more visible arrowhead
        arrow = FancyArrowPatch(
            (0, 0), (x_end, y_end),
            arrowstyle='->,head_width=0.4,head_length=0.6',
            mutation_scale=20,  # Makes arrowhead larger
            color=color,
            linewidth=linewidth,
            label=self._format_label_for_legend(label),
            zorder=3
        )
        ax.add_patch(arrow)

        # Format label with LaTeX and magnitude
        formatted_label = self._format_vector_label(force, label)

        # Add label near the tip
        label_offset = 0.5
        label_x = x_end + label_offset * math.cos(angle)
        label_y = y_end + label_offset * math.sin(angle)
        ax.text(
            label_x, label_y, formatted_label,
            fontsize=11, fontweight='bold',
            color=color,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor=color, linewidth=2, alpha=0.9)
        )

        # Show angle annotation with force name
        if show_angle:
            angle_label = f"θ_{force.name}" if hasattr(force, 'name') and force.name else None
            self._draw_angle_annotation(ax, angle, min(scaled_mag * 0.3, 2.0), color, angle_label)

        # Show components if requested
        if self.show_components:
            self._draw_components(ax, x_end, y_end, color)

    def _draw_resultant(self, ax, res_data: dict, scale_factor: float) -> None:
        """Draw resultant vector with dashed line."""
        mag = res_data['magnitude']
        angle = res_data['angle']
        color = res_data['color']
        label = res_data['label']
        linewidth = res_data['linewidth']
        force = res_data['force']

        # Calculate scaled magnitude
        scaled_mag = mag * scale_factor

        # Calculate endpoint
        x_end = scaled_mag * math.cos(angle)
        y_end = scaled_mag * math.sin(angle)

        # Draw dashed vector arrow with larger, more visible arrowhead
        arrow = FancyArrowPatch(
            (0, 0), (x_end, y_end),
            arrowstyle='->,head_width=0.5,head_length=0.7',
            mutation_scale=20,  # Makes arrowhead larger
            color=color,
            linewidth=linewidth,
            linestyle='--',
            label=self._format_label_for_legend(label),
            zorder=4
        )
        ax.add_patch(arrow)

        # Format label with LaTeX and magnitude
        formatted_label = self._format_vector_label(force, label)

        # Add label near the tip
        label_offset = 0.6
        label_x = x_end + label_offset * math.cos(angle)
        label_y = y_end + label_offset * math.sin(angle)
        ax.text(
            label_x, label_y, formatted_label,
            fontsize=12, fontweight='bold',
            color=color,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=color, linewidth=2.5, alpha=0.95)
        )

        # Always show angle for resultant with angle name
        angle_label = f"θ_{force.name}" if hasattr(force, 'name') and force.name else None
        self._draw_angle_annotation(ax, angle, min(scaled_mag * 0.25, 2.0), color, angle_label)

    def _draw_angle_annotation(self, ax, angle: float, radius: float, color: str, angle_name: str | None = None) -> None:
        """Draw angle arc and label with optional angle variable name."""
        # Convert angle to degrees
        angle_deg = math.degrees(angle)

        # Ensure angle is positive and within [0, 360)
        while angle_deg < 0:
            angle_deg += 360
        while angle_deg >= 360:
            angle_deg -= 360

        # Draw arc from x-axis to vector
        arc = Arc(
            (0, 0), 2 * radius, 2 * radius,
            angle=0, theta1=0, theta2=angle_deg,
            color=color, linewidth=1.5, linestyle=':', zorder=2
        )
        ax.add_patch(arc)

        # Calculate label position at midpoint of arc using normalized angle
        # IMPORTANT: Use angle_deg (normalized) not original angle for positioning
        if angle_deg > 120:
            # For large angles, place label closer to the vector (85% of the way)
            label_angle_deg = angle_deg * 0.85
        elif angle_deg < 30:
            # For small angles, place at midpoint but farther out
            label_angle_deg = angle_deg / 2
            radius = radius * 1.5
        else:
            # For medium angles, use midpoint
            label_angle_deg = angle_deg / 2

        # Convert to radians for positioning
        label_angle_rad = math.radians(label_angle_deg)
        label_radius = radius * 1.2
        label_x = label_radius * math.cos(label_angle_rad)
        label_y = label_radius * math.sin(label_angle_rad)

        # Create label with angle name if provided
        if angle_name:
            label_text = f"{angle_name} = {angle_deg:.1f}°"
        else:
            label_text = f"{angle_deg:.1f}°"

        ax.text(
            label_x, label_y, label_text,
            fontsize=10, color=color,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7)
        )

    def _draw_components(self, ax, x: float, y: float, color: str) -> None:
        """Draw component projections (dashed lines)."""
        # X-component (vertical dashed line from tip to x-axis)
        ax.plot([x, x], [0, y], color=color, linestyle=':', linewidth=1.5, alpha=0.6)

        # Y-component (horizontal dashed line from tip to y-axis)
        ax.plot([0, x], [y, y], color=color, linestyle=':', linewidth=1.5, alpha=0.6)

        # Labels for components
        ax.text(x, -0.3, f"{x:.1f}", fontsize=9, ha='center', color=color)
        ax.text(-0.3, y, f"{y:.1f}", fontsize=9, va='center', color=color)


def create_force_diagram(
    problem,
    output_path: str | Path,
    title: str | None = None,
    show_components: bool = False,
    **kwargs
) -> Path:
    """
    Create vector diagram from a VectorEquilibriumProblem.

    Args:
        problem: VectorEquilibriumProblem instance (must be solved)
        output_path: Output file path
        title: Diagram title (uses problem.name if None)
        show_components: Whether to show component projections
        **kwargs: Additional arguments for VectorDiagram

    Returns:
        Path to saved diagram

    Examples:
        >>> problem = Problem_2_1()
        >>> problem.solve()
        >>> create_force_diagram(problem, "diagram.png")
    """
    title = title or problem.name
    diagram = VectorDiagram(title=title, show_components=show_components, **kwargs)

    # Color palette for vectors
    colors = ['#E74C3C', '#3498DB', '#F39C12', '#9B59B6', '#1ABC9C', '#E67E22']
    color_idx = 0

    # Add known forces
    for name, force in problem.forces.items():
        if force.is_resultant:
            continue  # Handle resultants separately

        if force.is_known and force.magnitude and force.angle:
            diagram.add_vector(
                force,
                color=colors[color_idx % len(colors)],
                label=name,
                show_angle=True
            )
            color_idx += 1

    # Add resultant (if present)
    for name, force in problem.forces.items():
        if force.is_resultant and force.is_known:
            diagram.add_resultant(force, color='#27AE60', label=name)
            break

    # Save diagram
    return diagram.save(output_path)
