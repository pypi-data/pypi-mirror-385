"""
Problem-validation integration for Problem class.

This module provides validation functionality through a mixin pattern,
allowing Problems to run validation checks and collect warnings.

Key features:
- Type-safe validation check management
- Robust error handling for validation failures
- Integration with Problem metaclass system
- Proper closure handling to avoid late binding issues
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, Protocol

from ..utils.shared_utilities import SafeExecutionMixin, SharedConstants

# Use shared constants
MSG_VALIDATION_CHECK_FAILED = SharedConstants.MSG_VALIDATION_CHECK_FAILED
MSG_WARNING_ATTR_UNINITIALIZED = "Problem warnings attribute is not properly initialized"
MSG_NO_CLASS_CHECKS = "No class checks found"
MSG_INVALID_CLASS_CHECKS = "Expected dict for _class_checks, got {type_name}"
MSG_MISSING_EVALUATE_METHOD = "Check object '{check_name}' missing 'evaluate' method"
MSG_CHECK_EVALUATION_FAILED = "Validation check evaluation failed"
MSG_NON_DICT_RESULT = "Validation check returned non-dict result: {result_type}"


class ValidationResult(Protocol):
    """Protocol for validation check results."""

    def evaluate(self, variables: dict[str, Any]) -> dict[str, Any] | None:
        """Evaluate the validation check."""
        ...


class ProblemAttributes(Protocol):
    """Protocol defining expected attributes for validation mixin."""

    logger: logging.Logger
    warnings: list[dict[str, Any]]
    validation_checks: list[Callable[[Any], dict[str, Any] | None]]
    variables: dict[str, Any]


class ValidationMixin(SafeExecutionMixin):
    """Mixin class providing validation functionality."""

    # These attributes will be provided by other mixins in the final Problem class
    logger: logging.Logger
    warnings: list[dict[str, Any]]
    validation_checks: list[Callable[[Any], dict[str, Any] | None]]
    variables: dict[str, Any]

    def add_validation_check(self, check_function: Callable[[Any], dict[str, Any] | None]) -> None:
        """Add a validation check function."""
        if not callable(check_function):
            raise TypeError("check_function must be callable")
        self.validation_checks.append(check_function)

    def _safe_check_attribute(self, obj: Any, attr_name: str, expected_type: type | None = None, check_callable: bool = False) -> bool:
        """
        Safely check if an object has an attribute of the expected type.

        Args:
            obj: Object to check
            attr_name: Name of the attribute to check
            expected_type: Expected type of the attribute (optional)
            check_callable: If True, check if the attribute is callable instead of type checking

        Returns:
            True if attribute exists and matches expected type, False otherwise
        """
        if not hasattr(obj, attr_name):
            return False

        if expected_type is None and not check_callable:
            return True

        try:
            attr_value = getattr(obj, attr_name)
            # Special handling for callable check
            if check_callable:
                return callable(attr_value)
            if expected_type is not None:
                return isinstance(attr_value, expected_type)
            return True
        except AttributeError:
            return False

    def _create_warning_dict(self, warning_type: str, message: str, **extra_fields) -> dict[str, Any]:
        """
        Create a standardized warning dictionary with consistent structure.

        Args:
            warning_type: Type of warning (e.g., "validation", "error")
            message: Warning message
            **extra_fields: Additional fields to include in the warning

        Returns:
            Standardized warning dictionary
        """
        warning_dict = {"type": warning_type, "message": message}
        warning_dict.update(extra_fields)
        return warning_dict

    def validate(self) -> list[dict[str, Any]]:
        """Run all validation checks and return any warnings."""
        validation_warnings: list[dict[str, Any]] = []

        for validation_check in self.validation_checks:
            if not callable(validation_check):
                self.logger.warning(f"Skipping non-callable validation check: {validation_check}")
                continue

            def execute_check() -> dict[str, Any] | None:
                result = validation_check(self)
                if result is not None and isinstance(result, dict):
                    return result
                elif result is not None:
                    self.logger.warning(MSG_NON_DICT_RESULT.format(result_type=type(result)))
                return None

            check_result = self.safe_execute_with_logging(MSG_VALIDATION_CHECK_FAILED, execute_check)

            if check_result is not None:
                validation_warnings.append(check_result)

        return validation_warnings

    def get_warnings(self) -> list[dict[str, Any]]:
        """Get all warnings from the problem."""

        # Safely get existing warnings using helper method
        def get_existing_warnings() -> list[dict[str, Any]]:
            if self._safe_check_attribute(self, "warnings", list) and self.warnings:
                return self.warnings.copy()
            else:
                self.logger.warning(MSG_WARNING_ATTR_UNINITIALIZED)
                return []

        warnings = self.safe_execute_with_logging("Getting existing warnings", get_existing_warnings, default_return=[])

        # Safely get validation warnings using helper method
        validation_warnings = self.safe_execute_with_logging("Running validation checks", self.validate, default_return=[])

        warnings.extend(validation_warnings)
        return warnings

    def _recreate_validation_checks(self) -> None:
        """Collect and integrate validation checks from class-level Check objects."""
        # Clear existing checks
        self.validation_checks = []

        # Safely get class checks using helper method
        def get_class_checks() -> dict[str, ValidationResult]:
            class_checks = getattr(self.__class__, "_class_checks", {})
            if not isinstance(class_checks, dict):
                self.logger.warning(MSG_INVALID_CLASS_CHECKS.format(type_name=type(class_checks)))
                return {}
            return class_checks

        class_checks = self.safe_execute_with_logging("Getting class checks", get_class_checks, default_return={})

        if not class_checks:
            self.logger.debug(MSG_NO_CLASS_CHECKS)
            return

        # Create validation functions from Check objects
        for check_name, check_obj in class_checks.items():
            if not self._safe_check_attribute(check_obj, "evaluate", check_callable=True):
                self.logger.warning(MSG_MISSING_EVALUATE_METHOD.format(check_name=check_name))
                continue

            validation_function = self._create_validation_function(check_obj)
            self.validation_checks.append(validation_function)

    def _create_validation_function(self, check_obj: ValidationResult) -> Callable[[Any], dict[str, Any] | None]:
        """Create a validation function from a check object, avoiding closure issues."""

        def check_function(problem_instance: Any) -> dict[str, Any] | None:
            # Safely check for variables attribute
            if not hasattr(problem_instance, "variables") or not isinstance(problem_instance.variables, dict):
                return None

            # Safely execute the check with error handling
            try:
                return check_obj.evaluate(problem_instance.variables)
            except Exception as e:
                if hasattr(problem_instance, "logger"):
                    problem_instance.logger.debug(f"{MSG_CHECK_EVALUATION_FAILED}: {e}")
                return None

        return check_function
