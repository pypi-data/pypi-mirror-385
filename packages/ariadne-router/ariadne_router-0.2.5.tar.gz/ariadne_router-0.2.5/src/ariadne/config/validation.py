"""
Configuration validation system for Ariadne.

This module provides comprehensive validation for configuration objects,
with detailed error messages and suggestions for fixes.
"""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    from ariadne.core import ConfigurationError
except ImportError:
    # Fallback for when running as a script
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ariadne.core import ConfigurationError


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """A validation issue found in configuration."""

    field_path: str
    severity: ValidationSeverity
    message: str
    suggestion: str | None = None
    code: str | None = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of configuration validation."""

    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def critical_issues(self) -> list[ValidationIssue]:
        """Get critical validation issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.CRITICAL]

    @property
    def error_issues(self) -> list[ValidationIssue]:
        """Get error validation issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.ERROR]

    @property
    def warning_issues(self) -> list[ValidationIssue]:
        """Get warning validation issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.WARNING]

    @property
    def info_issues(self) -> list[ValidationIssue]:
        """Get info validation issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.INFO]

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue."""
        self.issues.append(issue)
        if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
            self.is_valid = False


class ValidationRule:
    """Base class for validation rules."""

    def __init__(self, message: str, suggestion: str | None = None, code: str | None = None) -> None:
        """
        Initialize validation rule.

        Args:
            message: Error message
            suggestion: Suggestion for fixing the issue
            code: Error code for reference
        """
        self.message = message
        self.suggestion = suggestion
        self.code = code

    def validate(self, field_path: str, value: Any, context: dict[str, Any]) -> ValidationIssue | None:
        """
        Validate a value.

        Args:
            field_path: Path to the field being validated
            value: Value to validate
            context: Additional context for validation

        Returns:
            Validation issue if validation fails, None otherwise
        """
        raise NotImplementedError


class TypeRule(ValidationRule):
    """Rule for validating value type."""

    def __init__(self, expected_type: type, message: str | None = None, **kwargs: Any) -> None:
        """
        Initialize type rule.

        Args:
            expected_type: Expected type
            message: Custom error message
            **kwargs: Additional arguments for ValidationRule
        """
        self.expected_type = expected_type

        if message is None:
            type_name = expected_type.__name__ if hasattr(expected_type, "__name__") else str(expected_type)
            message = f"Expected type {type_name}"

        super().__init__(message, **kwargs)

    def validate(self, field_path: str, value: Any, context: dict[str, Any]) -> ValidationIssue | None:
        """Validate value type."""
        if not isinstance(value, self.expected_type):
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=self.message,
                suggestion=f"Ensure {field_path} is of type {self.expected_type.__name__}",
                code=self.code or "TYPE_MISMATCH",
                context={
                    "expected_type": self.expected_type.__name__,
                    "actual_type": type(value).__name__,
                },
            )
        return None


class RangeRule(ValidationRule):
    """Rule for validating numeric ranges."""

    def __init__(
        self,
        min_value: float | None = None,
        max_value: float | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize range rule.

        Args:
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            **kwargs: Additional arguments for ValidationRule
        """
        self.min_value = min_value
        self.max_value = max_value

        if min_value is not None and max_value is not None:
            message = f"Value must be between {min_value} and {max_value}"
        elif min_value is not None:
            message = f"Value must be at least {min_value}"
        elif max_value is not None:
            message = f"Value must be at most {max_value}"
        else:
            message = "Invalid range rule"

        super().__init__(message, **kwargs)

    def validate(self, field_path: str, value: Any, context: dict[str, Any]) -> ValidationIssue | None:
        """Validate numeric range."""
        if not isinstance(value, int | float):
            return None  # Type validation should catch this

        if self.min_value is not None and value < self.min_value:
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=f"Value {value} is below minimum {self.min_value}",
                suggestion=f"Ensure {field_path} is at least {self.min_value}",
                code=self.code or "VALUE_TOO_SMALL",
                context={"min_value": self.min_value, "actual_value": value},
            )

        if self.max_value is not None and value > self.max_value:
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=f"Value {value} is above maximum {self.max_value}",
                suggestion=f"Ensure {field_path} is at most {self.max_value}",
                code=self.code or "VALUE_TOO_LARGE",
                context={"max_value": self.max_value, "actual_value": value},
            )

        return None


class ChoiceRule(ValidationRule):
    """Rule for validating choices from a set of options."""

    def __init__(self, choices: list[Any], case_sensitive: bool = True, **kwargs: Any) -> None:
        """
        Initialize choice rule.

        Args:
            choices: List of valid choices
            case_sensitive: Whether comparison is case sensitive
            **kwargs: Additional arguments for ValidationRule
        """
        self.choices = choices
        self.case_sensitive = case_sensitive

        message = f"Value must be one of: {', '.join(str(c) for c in choices)}"
        super().__init__(message, **kwargs)

    def validate(self, field_path: str, value: Any, context: dict[str, Any]) -> ValidationIssue | None:
        """Validate choice."""
        if self.case_sensitive:
            is_valid = value in self.choices
            valid_choices = self.choices
        else:
            value_str = str(value).lower()
            valid_choices = [str(c).lower() for c in self.choices]
            is_valid = value_str in valid_choices

        if not is_valid:
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=f"Value '{value}' is not a valid choice",
                suggestion=f"Choose from: {', '.join(str(c) for c in self.choices)}",
                code=self.code or "INVALID_CHOICE",
                context={"valid_choices": valid_choices, "actual_value": value},
            )

        return None


class RegexRule(ValidationRule):
    """Rule for validating string patterns with regular expressions."""

    def __init__(self, pattern: str, **kwargs: Any) -> None:
        """
        Initialize regex rule.

        Args:
            pattern: Regular expression pattern
            **kwargs: Additional arguments for ValidationRule
        """
        self.pattern = re.compile(pattern)
        self.pattern_str = pattern

        message = f"Value must match pattern: {pattern}"
        super().__init__(message, **kwargs)

    def validate(self, field_path: str, value: Any, context: dict[str, Any]) -> ValidationIssue | None:
        """Validate regex pattern."""
        if not isinstance(value, str):
            return None  # Type validation should catch this

        if not self.pattern.match(value):
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=f"Value '{value}' does not match required pattern",
                suggestion=f"Ensure {field_path} matches pattern: {self.pattern_str}",
                code=self.code or "PATTERN_MISMATCH",
                context={"pattern": self.pattern_str, "actual_value": value},
            )

        return None


class PathRule(ValidationRule):
    """Rule for validating file system paths."""

    def __init__(
        self,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_dir: bool = False,
        is_readable: bool = False,
        is_writable: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialize path rule.

        Args:
            must_exist: Path must exist
            must_be_file: Path must be a file
            must_be_dir: Path must be a directory
            is_readable: Path must be readable
            is_writable: Path must be writable
            **kwargs: Additional arguments for ValidationRule
        """
        self.must_exist = must_exist
        self.must_be_file = must_be_file
        self.must_be_dir = must_be_dir
        self.is_readable = is_readable
        self.is_writable = is_writable

        message = "Invalid path"
        super().__init__(message, **kwargs)

    def validate(self, field_path: str, value: Any, context: dict[str, Any]) -> ValidationIssue | None:
        """Validate file system path."""
        if not isinstance(value, str):
            return None  # Type validation should catch this

        path = value

        # Check if path exists
        if self.must_exist and not os.path.exists(path):
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=f"Path does not exist: {path}",
                suggestion=f"Ensure the path {path} exists or create it",
                code=self.code or "PATH_NOT_EXIST",
                context={"path": path},
            )

        # Skip further checks if path doesn't exist
        if not os.path.exists(path):
            return None

        # Check if path is a file
        if self.must_be_file and not os.path.isfile(path):
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=f"Path is not a file: {path}",
                suggestion=f"Ensure {path} is a file",
                code=self.code or "PATH_NOT_FILE",
                context={"path": path},
            )

        # Check if path is a directory
        if self.must_be_dir and not os.path.isdir(path):
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=f"Path is not a directory: {path}",
                suggestion=f"Ensure {path} is a directory",
                code=self.code or "PATH_NOT_DIR",
                context={"path": path},
            )

        # Check if path is readable
        if self.is_readable and not os.access(path, os.R_OK):
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=f"Path is not readable: {path}",
                suggestion=f"Check permissions for {path}",
                code=self.code or "PATH_NOT_READABLE",
                context={"path": path},
            )

        # Check if path is writable
        if self.is_writable and not os.access(path, os.W_OK):
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=f"Path is not writable: {path}",
                suggestion=f"Check permissions for {path}",
                code=self.code or "PATH_NOT_WRITABLE",
                context={"path": path},
            )

        return None


class CustomRule(ValidationRule):
    """Rule for custom validation logic."""

    def __init__(self, validator: Callable[[Any, dict[str, Any]], str | None], **kwargs: Any) -> None:
        """
        Initialize custom rule.

        Args:
            validator: Custom validation function that returns an error message or None
            **kwargs: Additional arguments for ValidationRule
        """
        self.validator = validator
        super().__init__("Custom validation failed", **kwargs)

    def validate(self, field_path: str, value: Any, context: dict[str, Any]) -> ValidationIssue | None:
        """Validate with custom logic."""
        error_message = self.validator(value, context)

        if error_message:
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=error_message,
                suggestion=self.suggestion,
                code=self.code or "CUSTOM_VALIDATION_FAILED",
                context={"value": value},
            )

        return None


class FieldSchema:
    """Schema definition for a configuration field."""

    def __init__(
        self,
        description: str = "",
        default: Any = None,
        required: bool = True,
        rules: list[ValidationRule] | None = None,
        examples: list[Any] | None = None,
    ) -> None:
        """
        Initialize field schema.

        Args:
            description: Field description
            default: Default value
            required: Whether field is required
            rules: Validation rules
            examples: Example values
        """
        self.description = description
        self.default = default
        self.required = required
        self.rules = rules or []
        self.examples = examples or []

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule."""
        self.rules.append(rule)

    def validate(self, field_path: str, value: Any, context: dict[str, Any]) -> ValidationResult:
        """
        Validate a value against this schema.

        Args:
            field_path: Path to the field
            value: Value to validate
            context: Additional context for validation

        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True)

        # Check if required field is missing
        if value is None and self.required:
            result.add_issue(
                ValidationIssue(
                    field_path=field_path,
                    severity=ValidationSeverity.ERROR,
                    message="Required field is missing",
                    suggestion=f"Provide a value for {field_path}",
                    code="REQUIRED_FIELD_MISSING",
                    context={"field_path": field_path},
                )
            )
            return result

        # Skip validation if value is None and not required
        if value is None:
            return result

        # Apply validation rules
        for rule in self.rules:
            issue = rule.validate(field_path, value, context)
            if issue:
                result.add_issue(issue)

        return result


class ConfigurationSchema:
    """Schema definition for configuration objects."""

    def __init__(self, description: str = "") -> None:
        """
        Initialize configuration schema.

        Args:
            description: Schema description
        """
        self.description = description
        self.fields: dict[str, FieldSchema] = {}

    def add_field(self, name: str, schema: FieldSchema) -> None:
        """Add a field to the schema."""
        self.fields[name] = schema

    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """
        Validate a configuration against this schema.

        Args:
            config: Configuration to validate

        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True)

        # Validate each field
        for field_name, field_schema in self.fields.items():
            field_path = field_name
            field_value = config.get(field_name)

            # Create field context
            field_context = {"field_name": field_name, "config": config}

            # Validate field
            field_result = field_schema.validate(field_path, field_value, field_context)

            # Add issues to result
            for issue in field_result.issues:
                result.add_issue(issue)

        return result


class ConfigurationValidator:
    """Validator for configuration objects."""

    def __init__(self) -> None:
        """Initialize configuration validator."""
        self.schemas: dict[str, ConfigurationSchema] = {}
        self.global_rules: list[ValidationRule] = []

    def register_schema(self, name: str, schema: ConfigurationSchema) -> None:
        """Register a configuration schema."""
        self.schemas[name] = schema

    def add_global_rule(self, rule: ValidationRule) -> None:
        """Add a global validation rule applied to all configurations."""
        self.global_rules.append(rule)

    def validate(self, config: dict[str, Any], schema_name: str) -> ValidationResult:
        """
        Validate a configuration against a schema.

        Args:
            config: Configuration to validate
            schema_name: Name of schema to use

        Returns:
            Validation result
        """
        if schema_name not in self.schemas:
            raise ConfigurationError(
                "schema",
                schema_name,
                f"Unknown schema '{schema_name}'",
            )

        schema = self.schemas[schema_name]
        result = schema.validate(config)

        # Apply global rules
        for rule in self.global_rules:
            issue = rule.validate("config", config, {"schema": schema_name})
            if issue:
                result.add_issue(issue)

        return result

    def get_schema(self, name: str) -> ConfigurationSchema | None:
        """Get a configuration schema by name."""
        return self.schemas.get(name)

    def list_schemas(self) -> list[str]:
        """List all registered schema names."""
        return list(self.schemas.keys())


# Global validator instance
_global_validator: ConfigurationValidator | None = None


def get_validator() -> ConfigurationValidator:
    """Get the global configuration validator."""
    global _global_validator
    if _global_validator is None:
        _global_validator = ConfigurationValidator()
    return _global_validator


def validate_config(config: dict[str, Any], schema_name: str) -> ValidationResult:
    """
    Validate a configuration using the global validator.

    Args:
        config: Configuration to validate
        schema_name: Name of schema to use

    Returns:
        Validation result
    """
    validator = get_validator()
    return validator.validate(config, schema_name)


def register_schema(name: str, schema: ConfigurationSchema) -> None:
    """
    Register a configuration schema using the global validator.

    Args:
        name: Schema name
        schema: Configuration schema
    """
    validator = get_validator()
    validator.register_schema(name, schema)
