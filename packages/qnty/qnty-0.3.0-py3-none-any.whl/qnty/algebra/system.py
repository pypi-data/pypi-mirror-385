from .equation import Equation


class EquationSystem:
    """
    System of equations that can be solved together.
    Optimized with __slots__ for memory efficiency.
    """

    __slots__ = ("equations",)

    def __init__(self, equations: list[Equation] | None = None):
        self.equations = equations or []

    def add_equation(self, equation: Equation):
        """Add an equation to the system."""
        self.equations.append(equation)

    def __str__(self) -> str:
        return f"EquationSystem({len(self.equations)} equations)"

    def __repr__(self) -> str:
        return f"EquationSystem(equations={self.equations!r})"
