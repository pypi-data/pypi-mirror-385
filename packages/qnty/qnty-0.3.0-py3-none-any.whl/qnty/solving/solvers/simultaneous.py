from typing import Any

import numpy as np

try:
    from scipy.linalg import solve as scipy_solve  # type: ignore[import-untyped]

    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    scipy_solve = None

from qnty.solving.order import Order

from ...algebra import Equation
from ...core.quantity import FieldQuantity, Quantity
from ..utils import SolverConstants
from .base import BaseSolver, SolveResult


class SimultaneousEquationSolver(BaseSolver):
    """
    Solver for n×n simultaneous linear equation systems using matrix operations.

    This solver handles systems where equations are mutually dependent (forming cycles
    in the dependency graph), requiring simultaneous solution rather than sequential
    solution of individual equations.

    Algorithm:
    1. Validate system requirements (square, n≥2, has cycles)
    2. Extract coefficient matrix A and constant vector b from equations
    3. Check numerical stability (condition number)
    4. Solve matrix system Ax = b using robust linear algebra
    5. Update variables with solutions and verify residuals

    Supports any size square system (n equations, n unknowns) that is:
    - Linearly independent (non-singular matrix)
    - Well-conditioned (numerically stable)
    - Composed of linear equations with units preserved throughout

    Examples:
        2×2 system: x + y = 3, 2x - y = 0 → x=1, y=2
        3×3 system: Complex engineering systems with interdependent variables
    """

    # Use consolidated constants from utils module (SolverConstants)

    def can_handle(self, equations: list[Equation], unknowns: set[str], dependency_graph: Order | None = None, analysis: dict[str, Any] | None = None) -> bool:
        """
        Determine if this solver can handle the given system.

        Args:
            equations: List of equations to solve
            unknowns: Set of unknown variable symbols
            dependency_graph: Optional dependency graph (unused)
            analysis: Optional system analysis containing cycle information

        Returns:
            True if this solver can handle the system:
            - Square system (n equations = n unknowns)
            - Minimum size (n ≥ 2)
            - Contains cycles (indicating simultaneous equations needed)
        """
        # dependency_graph parameter unused but required for interface compatibility
        _ = dependency_graph

        system_size = len(equations)
        num_unknowns = len(unknowns)

        # Validate square system with minimum size
        if system_size != num_unknowns or system_size < SolverConstants.MIN_SYSTEM_SIZE:
            return False

        # Only handle systems with cycles (mutual dependencies)
        if analysis is None:
            return False
        has_cycles = analysis.get("has_cycles", False)
        return bool(has_cycles)

    def solve(
        self, equations: list[Equation], variables: dict[str, FieldQuantity], dependency_graph: Order | None = None, max_iterations: int = 100, tolerance: float = SolverConstants.DEFAULT_TOLERANCE
    ) -> SolveResult:
        """
        Solve the n×n simultaneous system using matrix operations.

        Args:
            equations: List of n linear equations to solve simultaneously
            variables: Dictionary of all variables (known and unknown)
            dependency_graph: Optional dependency graph
                (unused for simultaneous systems)
            max_iterations: Maximum iterations
                (unused for direct matrix solving)
            tolerance: Numerical tolerance for residual checking

        Returns:
            SolveResult containing the solution or error information
        """
        # Mark unused parameters to satisfy linter
        _ = dependency_graph, max_iterations

        self.steps = []

        # Step 1: Validate system requirements
        validation_result = self._validate_system(equations, variables)
        if not validation_result.success:
            return validation_result

        unknown_variable_names = list(self._get_unknown_variables(variables))
        working_variables = dict(variables)

        # Step 2: Extract and solve matrix system
        try:
            solution_vector = self._solve_matrix_system(equations, unknown_variable_names, working_variables)
            if solution_vector is None:
                return self._create_error_result(working_variables, "Failed to solve matrix system")

            # Step 3: Update variables with solutions
            self._apply_solution_to_variables(unknown_variable_names, solution_vector, working_variables)

            # Step 4: Verify solution quality
            verification_result = self._verify_solution_quality(equations, working_variables, tolerance)

            return SolveResult(
                variables=working_variables, steps=self.steps, success=verification_result.success, message=verification_result.message, method="SimultaneousEquationSolver", iterations=1
            )

        except Exception as general_error:
            return self._create_error_result(working_variables, f"Simultaneous solving failed: {general_error}")

    def _validate_system(self, equations: list[Equation], variables: dict[str, FieldQuantity]) -> SolveResult:
        """
        Validate that the system meets requirements for simultaneous solving.

        Returns:
            SolveResult with success=True if valid, or error result if invalid
        """
        unknown_variable_names = list(self._get_unknown_variables(variables))
        num_unknowns = len(unknown_variable_names)
        num_equations = len(equations)

        # Validate square system with minimum size
        if num_unknowns != num_equations or num_unknowns < SolverConstants.MIN_SYSTEM_SIZE:
            return SolveResult(
                variables=variables,
                steps=self.steps,
                success=False,
                message=f"Simultaneous solver requires n×n system (got {num_equations} equations, {num_unknowns} unknowns)",
                method="SimultaneousEquationSolver",
            )

        if self.logger:
            self.logger.debug(f"Attempting {num_unknowns}×{num_unknowns} simultaneous solution for {unknown_variable_names}")

        return SolveResult(variables=variables, steps=self.steps, success=True, message="System validation passed", method="SimultaneousEquationSolver")

    def _solve_matrix_system(self, equations: list[Equation], unknown_variables: list[str], working_variables: dict[str, FieldQuantity]) -> np.ndarray | None:
        """
        Extract coefficient matrix and solve the linear system.

        Returns:
            Solution vector if successful, None if failed
        """
        # Extract coefficient matrix A and constant vector b
        coefficient_matrix, constant_vector = self._extract_matrix_system(equations, unknown_variables, working_variables)

        if coefficient_matrix is None or constant_vector is None:
            if self.logger:
                self.logger.error("Could not extract linear coefficients from equations")
            return None

        # Check numerical stability via condition number
        condition_number = np.linalg.cond(coefficient_matrix)
        if condition_number > SolverConstants.MAX_CONDITION_NUMBER:
            if self.logger:
                # Use debug level for expected fallback scenarios (systems with conditionals)
                if np.isinf(condition_number):
                    self.logger.debug("Matrix is singular (cond=inf), falling back to iterative solver")
                else:
                    self.logger.debug(f"System is ill-conditioned (cond={condition_number:.2e}), falling back to iterative solver")
            return None

        try:
            # Choose optimal solving algorithm based on system size
            system_size = coefficient_matrix.shape[0]
            solution_vector = self._solve_optimized_system(coefficient_matrix, constant_vector, system_size)
            return solution_vector

        except np.linalg.LinAlgError as linear_algebra_error:
            if self.logger:
                self.logger.error(f"Linear algebra error: {linear_algebra_error}")
            return None

    def _solve_optimized_system(self, coefficient_matrix: np.ndarray, constant_vector: np.ndarray, system_size: int) -> np.ndarray:
        """
        Solve the matrix system using optimized algorithms based on system characteristics.

        Args:
            coefficient_matrix: The coefficient matrix A
            constant_vector: The constant vector b
            system_size: Size of the system (n for n×n)

        Returns:
            Solution vector for the system Ax = b
        """
        if system_size <= SolverConstants.LARGE_SYSTEM_THRESHOLD:
            # Use standard NumPy solver for small-medium systems
            return np.linalg.solve(coefficient_matrix, constant_vector)
        else:
            # For large systems, use more efficient algorithms
            if self.logger:
                self.logger.debug(f"Using optimized algorithms for large system (n={system_size})")

            # Check matrix density to decide between dense/sparse algorithms
            density = np.count_nonzero(coefficient_matrix) / coefficient_matrix.size

            if density < SolverConstants.SPARSE_THRESHOLD:
                # Use sparse matrix algorithms
                if self.logger:
                    self.logger.debug(f"Matrix density {density:.3f} < {SolverConstants.SPARSE_THRESHOLD}, using sparse algorithms")
                return self._solve_sparse_system(coefficient_matrix, constant_vector)
            else:
                # Use optimized dense algorithms
                if self.logger:
                    self.logger.debug(f"Matrix density {density:.3f} >= {SolverConstants.SPARSE_THRESHOLD}, using optimized dense algorithms")
                return self._solve_large_dense_system(coefficient_matrix, constant_vector)

    def _solve_sparse_system(self, coefficient_matrix: np.ndarray, constant_vector: np.ndarray) -> np.ndarray:
        """
        Solve sparse matrix system. Currently falls back to dense solver.
        """
        return np.linalg.solve(coefficient_matrix, constant_vector)

    def _solve_large_dense_system(self, coefficient_matrix: np.ndarray, constant_vector: np.ndarray) -> np.ndarray:
        """
        Solve large dense matrix system using optimized algorithms.
        """
        if HAS_SCIPY and scipy_solve is not None:
            return scipy_solve(coefficient_matrix, constant_vector, assume_a="gen")
        return np.linalg.solve(coefficient_matrix, constant_vector)

    def _apply_solution_to_variables(self, unknown_variables: list[str], solution_vector: np.ndarray, working_variables: dict[str, FieldQuantity]):
        """
        Apply solution values to variables and record solving steps.
        """
        for i, variable_name in enumerate(unknown_variables):
            solution_value = float(solution_vector[i])
            self._update_variable_with_solution(variable_name, solution_value, working_variables)

    def _verify_solution_quality(self, equations: list[Equation], working_variables: dict[str, FieldQuantity], tolerance: float) -> SolveResult:
        """
        Verify solution quality by checking equation residuals.

        Returns:
            SolveResult indicating whether solution meets quality requirements
        """
        max_residual = 0.0
        for equation in equations:
            if equation.check_residual(working_variables, tolerance):
                if self.logger:
                    self.logger.debug(f"Equation {equation.name} verified")
            else:
                residual = self._calculate_equation_residual(equation, working_variables)
                max_residual = max(max_residual, abs(residual))
                if self.logger:
                    self.logger.warning(f"Equation {equation.name} residual: {residual}")

        is_successful = max_residual < tolerance
        success_message = "Simultaneous system solved successfully" if is_successful else f"Large residuals detected (max={max_residual:.2e})"

        if self.logger and is_successful:
            num_unknowns = len([v for v in working_variables.values() if not v.is_known])
            variable_solutions = {var: f"{working_variables[var].quantity}" for var in working_variables if not working_variables[var].is_known}
            self.logger.debug(f"Solved {num_unknowns}×{num_unknowns} system: {variable_solutions}")

        return SolveResult(variables=working_variables, steps=[], success=is_successful, message=success_message, method="SimultaneousEquationSolver")

    def _extract_matrix_system(self, equations: list[Equation], unknown_variables: list[str], variables: dict[str, FieldQuantity]) -> tuple[np.ndarray | None, np.ndarray | None]:
        """
        Extract coefficient matrix A and constant vector b from the system of equations.

        Args:
            equations: List of linear equations to extract coefficients from
            unknown_variables: List of unknown variable symbols (determines column order)
            variables: Dictionary of all variables for evaluation

        Returns:
            Tuple of (coefficient_matrix, constant_vector) for system Ax = b
            Returns (None, None) if extraction fails

        Algorithm:
            For each equation, extract coefficients by numerical differentiation:
            1. Test each unknown variable with value 1, others with 0
            2. Calculate residual to determine coefficient
            3. Build coefficient matrix row by row
        """
        try:
            num_equations = len(equations)

            # Use consistent float64 precision for numerical stability
            dtype = np.float64

            coefficient_matrix = np.zeros((num_equations, num_equations), dtype=dtype)
            constant_vector = np.zeros(num_equations, dtype=dtype)

            # Process equations in batches for large systems to reduce memory pressure
            for equation_index, equation in enumerate(equations):
                coefficient_list = self._extract_linear_coefficients_vector(equation, unknown_variables, variables)
                if coefficient_list is None:
                    return None, None

                # coefficient_list contains [a1, a2, ..., an, constant]
                # where equation is a1*x1 + a2*x2 + ... + an*xn = constant
                coefficient_matrix[equation_index, :] = coefficient_list[:-1]  # Coefficients
                constant_vector[equation_index] = coefficient_list[-1]  # Constant term

            return coefficient_matrix, constant_vector

        except Exception:
            return None, None

    def _extract_linear_coefficients_vector(self, equation: Equation, unknown_variables: list[str], variables: dict[str, FieldQuantity]) -> list[float] | None:
        """
        Extract linear coefficients from equation using numerical differentiation.

        Args:
            equation: The equation to extract coefficients from
            unknown_variables: List of unknown variable symbols
            variables: Dictionary of all variables

        Returns:
            List [a1, a2, ..., an, c] for equation a1*x1 + a2*x2 + ... + an*xn = c
            Returns None if extraction fails

        Algorithm:
            Uses finite difference approximation:
            1. Set all unknowns to 0, calculate residual → gives constant term
            2. Set one unknown to 1, others to 0 → gives coefficient for that variable
            3. Repeat for all unknowns to build coefficient vector
        """
        try:
            num_unknowns = len(unknown_variables)
            coefficients = []

            # Memory optimization: Pre-allocate arrays for large systems
            residual_test_cases: list[float] = []

            # Reuse test variables dictionary to reduce object creation overhead
            test_vars = variables.copy()

            # Test case for each unknown variable (finite difference)
            for variable_index in range(num_unknowns):
                self._set_test_variables(test_vars, unknown_variables, variable_index)
                residual = self._calculate_equation_residual(equation, test_vars)
                residual_test_cases.append(residual)

            # Test case with all unknowns = 0 (baseline)
            self._set_test_variables(test_vars, unknown_variables, -1)  # -1 means set all to 0
            baseline_residual = self._calculate_equation_residual(equation, test_vars)

            # Extract coefficients: for equation sum(ai*xi) - c = 0
            # When xi=1, xj=0 (j≠i): ai - c = residual_i  →  ai = residual_i + c
            # When all xi=0: -c = baseline_residual  →  c = -baseline_residual

            constant_term = -baseline_residual
            for residual in residual_test_cases:
                coefficient = residual + constant_term
                coefficients.append(coefficient)

            coefficients.append(constant_term)  # Add constant term
            return coefficients

        except Exception:
            return None

    def _calculate_equation_residual(self, equation: Equation, test_variables: dict[str, FieldQuantity]) -> float:
        """
        Calculate equation residual (LHS - RHS) with proper unit handling.

        Args:
            equation: The equation to evaluate
            test_variables: Dictionary of variables with test values

        Returns:
            Numerical residual value (dimensionless)
            Returns infinity if evaluation fails
        """
        try:
            left_hand_side = equation.lhs.evaluate(test_variables)
            right_hand_side = equation.rhs.evaluate(test_variables)

            # Calculate residual and extract numerical value
            residual = left_hand_side - right_hand_side
            return self._extract_numerical_value(residual)

        except Exception:
            # Fallback for cases where evaluation fails
            return float("inf")

    def _update_variable_with_solution(self, variable_symbol: str, solution_value: float, variables: dict[str, FieldQuantity]):
        """
        Update a variable with its solved value and record the solving step.

        Args:
            variable_symbol: Symbol of the variable to update
            solution_value: Numerical solution value
            variables: Dictionary of variables to update
        """
        original_variable = variables[variable_symbol]
        if original_variable.quantity is None:
            raise ValueError(f"Variable {variable_symbol} has no quantity")
        # Use consolidated utility for unit resolution
        result_unit = self._resolve_preferred_unit(original_variable, variable_symbol)

        solution_quantity = Quantity.from_value(solution_value, result_unit, name="solution")

        # Create solved variable with correct constructor
        solved_variable = FieldQuantity(name=original_variable.name, dim=original_variable.dim, value=solution_value, preferred=result_unit)
        solved_variable._symbol = variable_symbol
        variables[variable_symbol] = solved_variable

        # Record solving step for tracking
        self._log_step(
            1,  # iteration number
            variable_symbol,
            "simultaneous_system",
            str(solution_quantity),
            "simultaneous",
        )

    def _set_test_variables(self, test_vars: dict[str, FieldQuantity], unknown_variables: list[str], active_index: int):
        """
        Set test variables for coefficient extraction.

        Args:
            test_vars: Dictionary of test variables to modify
            unknown_variables: List of unknown variable names
            active_index: Index of variable to set to 1.0, others set to 0.0. If -1, all set to 0.0
        """
        for unknown_index, var_name in enumerate(unknown_variables):
            test_value = 1.0 if unknown_index == active_index else 0.0
            original_var = test_vars[var_name]
            if original_var.quantity is None:
                raise ValueError(f"Variable {var_name} has no quantity")

            # Use consolidated utility for unit resolution
            preferred_unit = self._resolve_preferred_unit(original_var, var_name)

            test_var = FieldQuantity(name=f"test_{var_name}", dim=original_var.dim, value=test_value, preferred=preferred_unit)
            test_var._symbol = var_name
            test_vars[var_name] = test_var
