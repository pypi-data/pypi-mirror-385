"""
Backend performance monitoring system for Ariadne.

This module provides comprehensive performance monitoring for quantum simulation backends,
tracking metrics, detecting regressions, and providing insights.
"""

from __future__ import annotations

import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from qiskit import QuantumCircuit

from ..core import get_logger
from ..types import BackendType


class PerformanceMetricType(Enum):
    """Types of performance metrics."""

    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    ACCURACY = "accuracy"
    STABILITY = "stability"
    RESOURCE_EFFICIENCY = "resource_efficiency"


class AlertSeverity(Enum):
    """Severity levels for performance alerts."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """A single performance metric measurement."""

    metric_type: PerformanceMetricType
    value: float
    unit: str
    timestamp: float
    backend: BackendType
    circuit_info: dict[str, Any] = field(default_factory=dict)
    additional_info: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """A performance alert."""

    severity: AlertSeverity
    metric_type: PerformanceMetricType
    backend: BackendType
    message: str
    timestamp: float
    current_value: float
    threshold_value: float
    additional_info: dict[str, Any] = field(default_factory=dict)


@dataclass
class BackendPerformanceProfile:
    """Performance profile for a backend."""

    backend: BackendType
    metrics: dict[PerformanceMetricType, list[PerformanceMetric]] = field(default_factory=dict)
    alerts: list[PerformanceAlert] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)

    def add_metric(self, metric: PerformanceMetric) -> None:
        """Add a metric to the profile."""
        if metric.metric_type not in self.metrics:
            self.metrics[metric.metric_type] = []

        self.metrics[metric.metric_type].append(metric)
        self.last_updated = metric.timestamp

        # Keep only last 1000 metrics per type
        if len(self.metrics[metric.metric_type]) > 1000:
            self.metrics[metric.metric_type] = self.metrics[metric.metric_type][-1000:]

    def get_latest_metrics(self, metric_type: PerformanceMetricType, count: int = 10) -> list[PerformanceMetric]:
        """Get latest metrics of a specific type."""
        if metric_type not in self.metrics:
            return []
        return self.metrics[metric_type][-count:]

    def get_metric_statistics(
        self, metric_type: PerformanceMetricType, time_window: float | None = None
    ) -> dict[str, float]:
        """Get statistics for a specific metric type."""
        if metric_type not in self.metrics:
            return {}

        metrics = self.metrics[metric_type]

        # Filter by time window if specified
        if time_window is not None:
            current_time = time.time()
            metrics = [m for m in metrics if current_time - m.timestamp <= time_window]

        if not metrics:
            return {}

        values = [m.value for m in metrics]

        return {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "latest": values[-1],
            "oldest": values[0],
        }


class PerformanceThreshold:
    """Threshold for performance metrics."""

    def __init__(
        self,
        metric_type: PerformanceMetricType,
        warning_threshold: float,
        error_threshold: float,
        critical_threshold: float | None = None,
        unit: str = "",
        higher_is_better: bool = False,
    ):
        """
        Initialize performance threshold.

        Args:
            metric_type: Type of metric
            warning_threshold: Threshold for warning alerts
            error_threshold: Threshold for error alerts
            critical_threshold: Threshold for critical alerts
            unit: Unit of measurement
            higher_is_better: Whether higher values are better
        """
        self.metric_type = metric_type
        self.warning_threshold = warning_threshold
        self.error_threshold = error_threshold
        self.critical_threshold = critical_threshold
        self.unit = unit
        self.higher_is_better = higher_is_better

    def check_threshold(self, value: float) -> AlertSeverity | None:
        """
        Check if value exceeds threshold.

        Args:
            value: Value to check

        Returns:
            Alert severity if threshold exceeded, None otherwise
        """
        if self.higher_is_better:
            # For metrics where higher is better (e.g., success rate)
            if value < self.error_threshold:
                return AlertSeverity.ERROR
            elif value < self.warning_threshold:
                return AlertSeverity.WARNING
        else:
            # For metrics where lower is better (e.g., execution time)
            if self.critical_threshold is not None and value > self.critical_threshold:
                return AlertSeverity.CRITICAL
            elif value > self.error_threshold:
                return AlertSeverity.ERROR
            elif value > self.warning_threshold:
                return AlertSeverity.WARNING

        return None


class PerformanceRegressionDetector:
    """Detects performance regressions in backend metrics."""

    def __init__(self, window_size: int = 100, regression_threshold: float = 0.2):
        """
        Initialize regression detector.

        Args:
            window_size: Size of the baseline window
            regression_threshold: Threshold for regression detection
        """
        self.window_size = window_size
        self.regression_threshold = regression_threshold
        self.logger = get_logger("regression_detector")

    def detect_regression(
        self, metrics: list[PerformanceMetric], recent_metrics: list[PerformanceMetric]
    ) -> dict[str, Any] | None:
        """
        Detect performance regression.

        Args:
            metrics: Baseline metrics
            recent_metrics: Recent metrics to compare

        Returns:
            Regression information or None if no regression detected
        """
        if len(metrics) < self.window_size or len(recent_metrics) < 10:
            return None

        # Calculate baseline statistics
        baseline_values = [m.value for m in metrics[-self.window_size :]]
        baseline_mean = statistics.mean(baseline_values)
        baseline_std = statistics.stdev(baseline_values) if len(baseline_values) > 1 else 0.0

        # Calculate recent statistics
        recent_values = [m.value for m in recent_metrics[-10:]]
        recent_mean = statistics.mean(recent_values)

        # Check for regression
        if baseline_std > 0:
            z_score = (recent_mean - baseline_mean) / baseline_std
            if abs(z_score) > 2.0:  # Significant change
                regression_percent = abs(recent_mean - baseline_mean) / baseline_mean

                if regression_percent > self.regression_threshold:
                    return {
                        "detected": True,
                        "baseline_mean": baseline_mean,
                        "recent_mean": recent_mean,
                        "regression_percent": regression_percent,
                        "z_score": z_score,
                        "direction": "increase" if recent_mean > baseline_mean else "decrease",
                    }

        return None


class BackendPerformanceMonitor:
    """
    Monitor performance of quantum simulation backends.

    This class collects, analyzes, and reports on backend performance metrics.
    """

    def __init__(self, alert_callback: Callable[[PerformanceAlert], None] | None = None):
        """
        Initialize the performance monitor.

        Args:
            alert_callback: Callback function for performance alerts
        """
        self.logger = get_logger("performance_monitor")
        self.alert_callback = alert_callback

        # Performance profiles for each backend
        self._profiles: dict[BackendType, BackendPerformanceProfile] = {}

        # Performance thresholds
        self._thresholds: dict[PerformanceMetricType, PerformanceThreshold] = {}

        # Regression detectors
        self._regression_detectors: dict[BackendType, dict[PerformanceMetricType, PerformanceRegressionDetector]] = {}

        # Initialize default thresholds
        self._initialize_default_thresholds()

    def _initialize_default_thresholds(self) -> None:
        """Initialize default performance thresholds."""
        # Execution time thresholds (in seconds)
        self._thresholds[PerformanceMetricType.EXECUTION_TIME] = PerformanceThreshold(
            metric_type=PerformanceMetricType.EXECUTION_TIME,
            warning_threshold=1.0,
            error_threshold=5.0,
            critical_threshold=10.0,
            unit="seconds",
            higher_is_better=False,
        )

        # Memory usage thresholds (in MB)
        self._thresholds[PerformanceMetricType.MEMORY_USAGE] = PerformanceThreshold(
            metric_type=PerformanceMetricType.MEMORY_USAGE,
            warning_threshold=1000.0,
            error_threshold=4000.0,
            critical_threshold=8000.0,
            unit="MB",
            higher_is_better=False,
        )

        # Success rate thresholds (as percentage)
        self._thresholds[PerformanceMetricType.SUCCESS_RATE] = PerformanceThreshold(
            metric_type=PerformanceMetricType.SUCCESS_RATE,
            warning_threshold=95.0,
            error_threshold=90.0,
            critical_threshold=80.0,
            unit="percent",
            higher_is_better=True,
        )

        # Throughput thresholds (shots per second)
        self._thresholds[PerformanceMetricType.THROUGHPUT] = PerformanceThreshold(
            metric_type=PerformanceMetricType.THROUGHPUT,
            warning_threshold=100.0,
            error_threshold=50.0,
            critical_threshold=10.0,
            unit="shots/sec",
            higher_is_better=True,
        )

    def record_metric(
        self,
        backend: BackendType,
        metric_type: PerformanceMetricType,
        value: float,
        unit: str = "",
        circuit_info: dict[str, Any] | None = None,
        additional_info: dict[str, Any] | None = None,
    ) -> None:
        """
        Record a performance metric.

        Args:
            backend: Backend type
            metric_type: Type of metric
            value: Metric value
            unit: Unit of measurement
            circuit_info: Information about the circuit
            additional_info: Additional information
        """
        # Create metric
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=time.time(),
            backend=backend,
            circuit_info=circuit_info or {},
            additional_info=additional_info or {},
        )

        # Get or create profile
        if backend not in self._profiles:
            self._profiles[backend] = BackendPerformanceProfile(backend=backend)
            self._regression_detectors[backend] = {}

        profile = self._profiles[backend]
        profile.add_metric(metric)

        # Check for alerts
        self._check_alerts(metric)

        # Check for regressions
        self._check_regressions(backend, metric_type)

    def _check_alerts(self, metric: PerformanceMetric) -> None:
        """Check if metric triggers any alerts."""
        if metric.metric_type not in self._thresholds:
            return

        threshold = self._thresholds[metric.metric_type]
        severity = threshold.check_threshold(metric.value)

        if severity:
            alert = PerformanceAlert(
                severity=severity,
                metric_type=metric.metric_type,
                backend=metric.backend,
                message=(
                    f"{metric.metric_type.value} {metric.value:.3f}{threshold.unit} exceeds {severity.value} threshold"
                ),
                timestamp=metric.timestamp,
                current_value=metric.value,
                threshold_value=getattr(threshold, f"{severity.value}_threshold"),
                additional_info=metric.additional_info,
            )

            # Add to profile
            self._profiles[metric.backend].alerts.append(alert)

            # Call alert callback
            if self.alert_callback:
                self.alert_callback(alert)

            # Log alert
            self.logger.warning(f"Performance alert for {metric.backend.value}: {alert.message}")

    def _check_regressions(self, backend: BackendType, metric_type: PerformanceMetricType) -> None:
        """Check for performance regressions."""
        profile = self._profiles[backend]

        # Get regression detector
        if backend not in self._regression_detectors:
            self._regression_detectors[backend] = {}

        if metric_type not in self._regression_detectors[backend]:
            self._regression_detectors[backend][metric_type] = PerformanceRegressionDetector()

        detector = self._regression_detectors[backend][metric_type]

        # Get metrics
        metrics = profile.get_latest_metrics(metric_type, count=200)
        if len(metrics) < 20:
            return

        # Split into baseline and recent
        baseline_metrics = metrics[:-20]
        recent_metrics = metrics[-20:]

        # Check for regression
        regression = detector.detect_regression(baseline_metrics, recent_metrics)

        if regression:
            self.logger.error(
                f"Performance regression detected for {backend.value} {metric_type.value}: "
                f"{regression['regression_percent']:.1%} {regression['direction']}"
            )

    def record_simulation(
        self,
        backend: BackendType,
        circuit: QuantumCircuit,
        shots: int,
        execution_time: float,
        memory_usage: float,
        success: bool,
        additional_info: dict[str, Any] | None = None,
    ) -> None:
        """
        Record simulation performance metrics.

        Args:
            backend: Backend type
            circuit: Quantum circuit
            shots: Number of shots
            execution_time: Execution time in seconds
            memory_usage: Memory usage in MB
            success: Whether simulation was successful
            additional_info: Additional information
        """
        circuit_info = {"num_qubits": circuit.num_qubits, "depth": circuit.depth(), "shots": shots}

        # Record execution time
        self.record_metric(
            backend=backend,
            metric_type=PerformanceMetricType.EXECUTION_TIME,
            value=execution_time,
            unit="seconds",
            circuit_info=circuit_info,
            additional_info=additional_info,
        )

        # Record memory usage
        self.record_metric(
            backend=backend,
            metric_type=PerformanceMetricType.MEMORY_USAGE,
            value=memory_usage,
            unit="MB",
            circuit_info=circuit_info,
            additional_info=additional_info,
        )

        # Record throughput
        throughput = shots / execution_time if execution_time > 0 else 0
        self.record_metric(
            backend=backend,
            metric_type=PerformanceMetricType.THROUGHPUT,
            value=throughput,
            unit="shots/sec",
            circuit_info=circuit_info,
            additional_info=additional_info,
        )

        # Record success/failure
        success_value = 1.0 if success else 0.0
        self.record_metric(
            backend=backend,
            metric_type=PerformanceMetricType.SUCCESS_RATE,
            value=success_value,
            unit="boolean",
            circuit_info=circuit_info,
            additional_info=additional_info,
        )

    def get_backend_profile(self, backend: BackendType) -> BackendPerformanceProfile | None:
        """
        Get performance profile for a backend.

        Args:
            backend: Backend type

        Returns:
            Performance profile or None if not available
        """
        return self._profiles.get(backend)

    def get_all_profiles(self) -> dict[BackendType, BackendPerformanceProfile]:
        """
        Get performance profiles for all backends.

        Returns:
            Dictionary of backend profiles
        """
        return self._profiles.copy()

    def get_backend_summary(self, backend: BackendType, time_window: float = 3600.0) -> dict[str, Any]:
        """
        Get performance summary for a backend.

        Args:
            backend: Backend type
            time_window: Time window in seconds

        Returns:
            Performance summary
        """
        profile = self.get_backend_profile(backend)
        if not profile:
            return {}

        summary: dict[str, Any] = {
            "backend": backend.value,
            "time_window": time_window,
            "last_updated": profile.last_updated,
            "metrics": {},
            "alerts": {
                "total": len(profile.alerts),
                "critical": len([a for a in profile.alerts if a.severity == AlertSeverity.CRITICAL]),
                "error": len([a for a in profile.alerts if a.severity == AlertSeverity.ERROR]),
                "warning": len([a for a in profile.alerts if a.severity == AlertSeverity.WARNING]),
                "info": len([a for a in profile.alerts if a.severity == AlertSeverity.INFO]),
            },
        }

        # Get statistics for each metric type
        for metric_type in PerformanceMetricType:
            stats = profile.get_metric_statistics(metric_type, time_window)
            if stats:
                summary["metrics"][metric_type.value] = stats

        return summary

    def compare_backends(
        self,
        backends: list[BackendType],
        metric_type: PerformanceMetricType,
        time_window: float = 3600.0,
    ) -> dict[str, Any]:
        """
        Compare performance of multiple backends.

        Args:
            backends: List of backends to compare
            metric_type: Metric type to compare
            time_window: Time window in seconds

        Returns:
            Comparison results
        """
        comparison: dict[str, Any] = {
            "metric_type": metric_type.value,
            "time_window": time_window,
            "backends": {},
        }

        for backend in backends:
            profile = self.get_backend_profile(backend)
            if profile:
                stats = profile.get_metric_statistics(metric_type, time_window)
                if stats:
                    comparison["backends"][backend.value] = stats

        return comparison

    def get_performance_recommendations(self, backend: BackendType) -> list[str]:
        """
        Get performance recommendations for a backend.

        Args:
            backend: Backend type

        Returns:
            List of recommendations
        """
        recommendations: list[str] = []
        profile = self.get_backend_profile(backend)

        if not profile:
            return recommendations

        # Check recent alerts
        recent_alerts = [a for a in profile.alerts if time.time() - a.timestamp < 3600]
        critical_alerts = [a for a in recent_alerts if a.severity == AlertSeverity.CRITICAL]
        error_alerts = [a for a in recent_alerts if a.severity == AlertSeverity.ERROR]

        if critical_alerts:
            recommendations.append(f"Critical performance issues detected: {len(critical_alerts)} critical alerts")

        if error_alerts:
            recommendations.append(f"Performance issues detected: {len(error_alerts)} error alerts")

        # Check execution time
        exec_time_stats = profile.get_metric_statistics(PerformanceMetricType.EXECUTION_TIME)
        if exec_time_stats and exec_time_stats.get("mean", 0) > 1.0:
            recommendations.append("Consider optimizing circuits or using a faster backend")

        # Check memory usage
        memory_stats = profile.get_metric_statistics(PerformanceMetricType.MEMORY_USAGE)
        if memory_stats and memory_stats.get("mean", 0) > 1000:
            recommendations.append("High memory usage detected, consider using memory-efficient backends")

        # Check success rate
        success_stats = profile.get_metric_statistics(PerformanceMetricType.SUCCESS_RATE)
        if success_stats and success_stats.get("mean", 1.0) < 0.95:
            recommendations.append("Low success rate detected, check backend configuration")

        return recommendations


# Global performance monitor instance
_global_performance_monitor: BackendPerformanceMonitor | None = None


def get_performance_monitor() -> BackendPerformanceMonitor:
    """Get the global performance monitor instance."""
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = BackendPerformanceMonitor()
    return _global_performance_monitor


def record_simulation_performance(
    backend: BackendType,
    circuit: QuantumCircuit,
    shots: int,
    execution_time: float,
    memory_usage: float,
    success: bool,
    additional_info: dict[str, Any] | None = None,
) -> None:
    """
    Record simulation performance using the global performance monitor.

    Args:
        backend: Backend type
        circuit: Quantum circuit
        shots: Number of shots
        execution_time: Execution time in seconds
        memory_usage: Memory usage in MB
        success: Whether simulation was successful
        additional_info: Additional information
    """
    monitor = get_performance_monitor()
    monitor.record_simulation(
        backend=backend,
        circuit=circuit,
        shots=shots,
        execution_time=execution_time,
        memory_usage=memory_usage,
        success=success,
        additional_info=additional_info,
    )
