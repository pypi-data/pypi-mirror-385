"""
Comprehensive error handling system for Ariadne.

This module provides a structured hierarchy of exceptions for different types of errors
that can occur during quantum circuit simulation and routing.
"""

from __future__ import annotations

from typing import Any


class AriadneError(Exception):
    """Base exception for all Ariadne errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} (Details: {details_str})"
        return self.message


class BackendUnavailableError(AriadneError):
    """Raised when a backend is not available or fails to initialize."""

    def __init__(self, backend_name: str, reason: str, details: dict[str, Any] | None = None):
        self.backend_name = backend_name
        self.reason = reason
        message = f"Backend '{backend_name}' unavailable: {reason}"
        super().__init__(message, details)

    def __str__(self) -> str:
        return f"Backend '{self.backend_name}' unavailable: {self.reason}"


class CircuitTooLargeError(AriadneError):
    """Raised when a circuit exceeds the capabilities of available backends."""

    def __init__(self, num_qubits: int, depth: int, backend: str | None = None):
        self.num_qubits = num_qubits
        self.depth = depth
        self.backend = backend
        message = f"Circuit too large: {num_qubits} qubits, depth {depth}"
        if backend:
            message += f" for backend '{backend}'"
        super().__init__(message, {"num_qubits": num_qubits, "depth": depth, "backend": backend})


class ResourceExhaustionError(AriadneError):
    """Raised when system resources are exhausted during simulation."""

    def __init__(self, resource_type: str, required: float, available: float):
        self.resource_type = resource_type
        self.required = required
        self.available = available
        message = f"Insufficient {resource_type}: required {required}, available {available}"
        super().__init__(message, {"resource_type": resource_type, "required": required, "available": available})


class SimulationError(AriadneError):
    """Raised when simulation fails due to circuit or backend issues."""

    def __init__(self, message: str, circuit_info: dict[str, Any] | None = None, backend: str | None = None):
        self.circuit_info = circuit_info or {}
        self.backend = backend
        details = {"circuit_info": circuit_info, "backend": backend}
        super().__init__(message, details)


class ConfigurationError(AriadneError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, config_key: str, value: Any, reason: str):
        self.config_key = config_key
        self.value = value
        self.reason = reason
        message = f"Configuration error for '{config_key}': {reason}"
        super().__init__(message, {"config_key": config_key, "value": value, "reason": reason})


class RoutingError(AriadneError):
    """Raised when routing fails to find a suitable backend."""

    def __init__(self, circuit_info: dict[str, Any], available_backends: list[str]):
        self.circuit_info = circuit_info
        self.available_backends = available_backends
        message = f"No suitable backend found for circuit with {circuit_info.get('num_qubits', 'unknown')} qubits"
        super().__init__(message, {"circuit_info": circuit_info, "available_backends": available_backends})


class TimeoutError(AriadneError):
    """Raised when operation exceeds timeout limit."""

    def __init__(self, operation: str, timeout_seconds: float):
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        super().__init__(message, {"operation": operation, "timeout_seconds": timeout_seconds})


class DependencyError(AriadneError):
    """Raised when required dependencies are missing."""

    def __init__(self, dependency_name: str, purpose: str):
        self.dependency_name = dependency_name
        self.purpose = purpose
        message = f"Missing dependency '{dependency_name}' required for {purpose}"
        super().__init__(message, {"dependency_name": dependency_name, "purpose": purpose})


class ValidationError(AriadneError):
    """Raised when input validation fails."""

    def __init__(self, field_name: str, value: Any, constraint: str):
        self.field_name = field_name
        self.value = value
        self.constraint = constraint
        message = f"Validation failed for '{field_name}': {constraint}"
        super().__init__(message, {"field_name": field_name, "value": value, "constraint": constraint})
