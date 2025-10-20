"""
Comprehensive logging system for Ariadne.

This module provides structured logging with different levels and formatters
for debugging and monitoring quantum circuit simulations.
"""

from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass
from typing import Any

from qiskit import QuantumCircuit


@dataclass
class LogContext:
    """Context information for log entries."""

    circuit_id: str | None = None
    backend: str | None = None
    num_qubits: int | None = None
    depth: int | None = None
    user_id: str | None = None
    session_id: str | None = None


class AriadneLogger:
    """
    Enhanced logger for Ariadne with structured logging capabilities.

    This logger provides context-aware logging with automatic inclusion
    of circuit and simulation information.
    """

    def __init__(self, name: str, level: int = logging.INFO):
        """
        Initialize the Ariadne logger.

        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(f"ariadne.{name}")
        self.logger.setLevel(level)
        self._context = LogContext()

        # Avoid duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up console and file handlers."""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Console formatter
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)

        self.logger.addHandler(console_handler)

    def set_context(self, **kwargs: Any) -> None:
        """Set logging context."""
        for key, value in kwargs.items():
            if hasattr(self._context, key):
                setattr(self._context, key, value)

    def set_circuit_context(self, circuit: QuantumCircuit, circuit_id: str | None = None) -> None:
        """Set circuit-specific context."""
        self._context.circuit_id = circuit_id or f"q{circuit.num_qubits}_d{circuit.depth()}"
        self._context.num_qubits = circuit.num_qubits
        self._context.depth = circuit.depth()

    def _format_message(self, message: str, extra: dict[str, Any] | None = None) -> str:
        """Format message with context information."""
        parts = [message]

        # Add context information
        if self._context.backend:
            parts.append(f"backend={self._context.backend}")

        if self._context.circuit_id:
            parts.append(f"circuit={self._context.circuit_id}")

        if self._context.num_qubits:
            parts.append(f"qubits={self._context.num_qubits}")

        if self._context.depth:
            parts.append(f"depth={self._context.depth}")

        # Add extra information
        if extra:
            for key, value in extra.items():
                parts.append(f"{key}={value}")

        return " | ".join(parts)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        formatted = self._format_message(message, kwargs)
        self.logger.debug(formatted)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        formatted = self._format_message(message, kwargs)
        self.logger.info(formatted)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        formatted = self._format_message(message, kwargs)
        self.logger.warning(formatted)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        formatted = self._format_message(message, kwargs)
        self.logger.error(formatted)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        formatted = self._format_message(message, kwargs)
        self.logger.critical(formatted)

    def log_routing_decision(
        self, circuit: QuantumCircuit, backend: str, confidence: float, reason: str, **kwargs: Any
    ) -> None:
        """Log routing decision."""
        self.set_circuit_context(circuit)
        self.info(
            "Routing decision made",
            backend=backend,
            confidence=f"{confidence:.3f}",
            reason=reason,
            **kwargs,
        )

    def log_simulation_start(self, circuit: QuantumCircuit, backend: str, shots: int) -> None:
        """Log simulation start."""
        self.set_circuit_context(circuit)
        self._context.backend = backend
        self.info("Simulation started", backend=backend, shots=shots)

    def log_simulation_complete(self, execution_time: float, shots: int, **kwargs: Any) -> None:
        """Log simulation completion."""
        self.info(
            "Simulation completed",
            execution_time=f"{execution_time:.4f}s",
            shots=shots,
            throughput=f"{shots / execution_time:.1f} shots/s",
            **kwargs,
        )

    def log_simulation_error(self, error: Exception, **kwargs: Any) -> None:
        """Log simulation error."""
        self.error("Simulation failed", error_type=type(error).__name__, error_message=str(error), **kwargs)

    def log_backend_unavailable(self, backend: str, reason: str) -> None:
        """Log backend unavailability."""
        self.warning("Backend unavailable", backend=backend, reason=reason)

    def log_resource_warning(self, resource_type: str, usage: float, limit: float) -> None:
        """Log resource usage warning."""
        self.warning(
            "Resource usage high",
            resource_type=resource_type,
            usage=f"{usage:.1f}",
            limit=f"{limit:.1f}",
            usage_percent=f"{(usage / limit) * 100:.1f}%",
        )


class PerformanceLogger:
    """Logger for performance metrics and timing."""

    def __init__(self, logger: AriadneLogger) -> None:
        self.logger = logger
        self._timers: dict[str, float] = {}

    def start_timer(self, name: str) -> None:
        """Start a named timer."""
        self._timers[name] = time.time()
        self.logger.debug(f"Timer started: {name}")

    def end_timer(self, name: str) -> float:
        """End a named timer and return elapsed time."""
        if name not in self._timers:
            self.logger.warning(f"Timer '{name}' was not started")
            return 0.0

        elapsed = time.time() - self._timers[name]
        del self._timers[name]

        self.logger.debug(f"Timer ended: {name}", elapsed=f"{elapsed:.4f}s")

        return elapsed

    def log_timing(self, operation: str, elapsed: float, **kwargs: Any) -> None:
        """Log timing information."""
        self.logger.info(f"Operation timing: {operation}", elapsed=f"{elapsed:.4f}s", **kwargs)

    def log_memory_usage(self, memory_mb: float, **kwargs: Any) -> None:
        """Log memory usage."""
        self.logger.debug("Memory usage", memory_mb=f"{memory_mb:.1f}", **kwargs)


# Global logger instances
_loggers: dict[str, AriadneLogger] = {}


def get_logger(name: str) -> AriadneLogger:
    """
    Get a named logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    if name not in _loggers:
        _loggers[name] = AriadneLogger(name)
    return _loggers[name]


def set_log_level(level: int) -> None:
    """Set logging level for all Ariadne loggers."""
    for logger in _loggers.values():
        logger.logger.setLevel(level)


def configure_logging(level: int = logging.INFO, format_string: str | None = None, log_file: str | None = None) -> None:
    """
    Configure global logging settings.

    Args:
        level: Logging level
        format_string: Custom format string
        log_file: Optional log file path
    """
    # Configure root logger
    root_logger = logging.getLogger("ariadne")
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


# Convenience functions
def log_info(message: str, **kwargs: Any) -> None:
    """Log info message using default logger."""
    get_logger("ariadne").info(message, **kwargs)


def log_warning(message: str, **kwargs: Any) -> None:
    """Log warning message using default logger."""
    get_logger("ariadne").warning(message, **kwargs)


def log_error(message: str, **kwargs: Any) -> None:
    """Log error message using default logger."""
    get_logger("ariadne").error(message, **kwargs)


def log_debug(message: str, **kwargs: Any) -> None:
    """Log debug message using default logger."""
    get_logger("ariadne").debug(message, **kwargs)
