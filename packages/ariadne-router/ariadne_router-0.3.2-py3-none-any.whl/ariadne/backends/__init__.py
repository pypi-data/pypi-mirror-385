"""
Backend systems for Ariadne quantum circuit simulation.

This module provides enhanced backend functionality including health checking,
pooling, fallback strategies, and performance monitoring.
"""

from .enhanced_interface import (
    BackendCapabilities,
    BackendCapability,
    EnhancedBackendInterface,
    EnhancedBackendWrapper,
    OptimizationHint,
    SimulationMetadata,
    create_enhanced_backend,
)
from .fallback import (
    BackendFallbackManager,
    FallbackReason,
    FallbackResult,
    FallbackStrategy,
    execute_with_fallback,
    get_fallback_manager,
)
from .health_checker import (
    BackendHealthChecker,
    BackendHealthMetrics,
    HealthCheckResult,
    HealthStatus,
    create_basic_health_check,
    create_circuit_based_health_check,
    get_health_checker,
    is_backend_healthy,
)
from .performance_monitor import (
    AlertSeverity,
    BackendPerformanceMonitor,
    BackendPerformanceProfile,
    PerformanceAlert,
    PerformanceMetric,
    PerformanceMetricType,
    PerformanceRegressionDetector,
    PerformanceThreshold,
    get_performance_monitor,
    record_simulation_performance,
)
from .pool import (
    BackendPool,
    BackendPoolError,
    BackendPoolExhaustedError,
    BackendPoolManager,
    PooledBackend,
    PoolStatistics,
    PoolStatus,
    create_backend_pool,
    get_pool_manager,
)

__all__ = [
    # Enhanced interface
    "BackendCapability",
    "BackendCapabilities",
    "EnhancedBackendInterface",
    "EnhancedBackendWrapper",
    "OptimizationHint",
    "SimulationMetadata",
    "create_enhanced_backend",
    # Fallback system
    "BackendFallbackManager",
    "FallbackReason",
    "FallbackResult",
    "FallbackStrategy",
    "execute_with_fallback",
    "get_fallback_manager",
    # Health checking
    "BackendHealthChecker",
    "BackendHealthMetrics",
    "HealthCheckResult",
    "HealthStatus",
    "create_basic_health_check",
    "create_circuit_based_health_check",
    "get_health_checker",
    "is_backend_healthy",
    # Performance monitoring
    "AlertSeverity",
    "BackendPerformanceMonitor",
    "BackendPerformanceProfile",
    "PerformanceAlert",
    "PerformanceMetric",
    "PerformanceMetricType",
    "PerformanceRegressionDetector",
    "PerformanceThreshold",
    "get_performance_monitor",
    "record_simulation_performance",
    # Backend pooling
    "BackendPool",
    "BackendPoolError",
    "BackendPoolExhaustedError",
    "BackendPoolManager",
    "PooledBackend",
    "PoolStatistics",
    "PoolStatus",
    "create_backend_pool",
    "get_pool_manager",
]
