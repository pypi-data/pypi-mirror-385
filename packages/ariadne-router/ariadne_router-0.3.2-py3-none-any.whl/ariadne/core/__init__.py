"""Core Ariadne functionality for error handling, caching, resource management, and logging."""

from .cache import (
    CacheEntry,
    CircuitAnalysisCache,
    cached_analyze,
    get_global_cache,
    set_global_cache,
)
from .error_handling import (
    AriadneError,
    BackendUnavailableError,
    CircuitTooLargeError,
    ConfigurationError,
    DependencyError,
    ResourceExhaustionError,
    RoutingError,
    SimulationError,
    TimeoutError,
    ValidationError,
)
from .logging import (
    AriadneLogger,
    PerformanceLogger,
    configure_logging,
    get_logger,
    log_debug,
    log_error,
    log_info,
    log_warning,
    set_log_level,
)
from .resource_manager import (
    ResourceManager,
    ResourceRequirements,
    SystemResources,
    check_circuit_feasibility,
    get_resource_manager,
)

__all__ = [
    # Error handling
    "AriadneError",
    "BackendUnavailableError",
    "CircuitTooLargeError",
    "ResourceExhaustionError",
    "SimulationError",
    "ConfigurationError",
    "RoutingError",
    "TimeoutError",
    "DependencyError",
    "ValidationError",
    # Caching
    "CircuitAnalysisCache",
    "CacheEntry",
    "cached_analyze",
    "get_global_cache",
    "set_global_cache",
    # Resource management
    "ResourceManager",
    "SystemResources",
    "ResourceRequirements",
    "get_resource_manager",
    "check_circuit_feasibility",
    # Logging
    "AriadneLogger",
    "PerformanceLogger",
    "get_logger",
    "configure_logging",
    "set_log_level",
    "log_info",
    "log_warning",
    "log_error",
    "log_debug",
]
