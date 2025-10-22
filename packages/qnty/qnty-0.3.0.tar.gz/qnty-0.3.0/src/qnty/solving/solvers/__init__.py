"""
Solver package for the Optinova engineering problem library.

This package contains different solver implementations for solving systems
of engineering equations.
"""

from ..manager import SolverManager
from .base import BaseSolver, SolveResult
from .iterative import IterativeSolver
from .simultaneous import SimultaneousEquationSolver

__all__ = ["BaseSolver", "SolveResult", "IterativeSolver", "SimultaneousEquationSolver", "SolverManager"]
