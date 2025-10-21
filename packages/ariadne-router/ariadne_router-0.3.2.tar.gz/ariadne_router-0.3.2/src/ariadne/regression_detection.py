"""
Performance Regression Detection System for Ariadne.

This module implements automated performance regression detection to monitor
quantum backend performance over time and alert when significant performance
degradations are detected.
"""

import hashlib
import json
import logging
import sqlite3
import statistics
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit

logger = logging.getLogger(__name__)


class RegressionSeverity(Enum):
    """Severity levels for performance regressions."""

    MINOR = "minor"  # 10-25% degradation
    MODERATE = "moderate"  # 25-50% degradation
    MAJOR = "major"  # 50-100% degradation
    CRITICAL = "critical"  # >100% degradation


class MetricType(Enum):
    """Types of performance metrics to track."""

    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    ACCURACY = "accuracy"
    BACKEND_LATENCY = "backend_latency"


@dataclass
class PerformanceMetric:
    """Represents a single performance measurement."""

    metric_type: MetricType
    value: float
    timestamp: float
    backend: str
    circuit_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RegressionAlert:
    """Represents a detected performance regression."""

    metric_type: MetricType
    backend: str
    circuit_hash: str
    severity: RegressionSeverity
    baseline_value: float
    current_value: float
    degradation_percent: float
    detection_timestamp: float
    confidence: float
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StatisticalBaseline:
    """Statistical baseline for performance metrics."""

    mean: float
    std: float
    median: float
    percentile_95: float
    percentile_99: float
    sample_count: int
    last_updated: float


class PerformanceRegressionDetector:
    """Main class for detecting performance regressions."""

    def __init__(
        self,
        db_path: str = "ariadne_performance.db",
        baseline_window_days: int = 30,
        detection_threshold: float = 0.15,  # 15% degradation threshold
        min_samples: int = 10,
        confidence_threshold: float = 0.80,
    ):
        self.db_path = Path(db_path)
        self.baseline_window_days = baseline_window_days
        self.detection_threshold = detection_threshold
        self.min_samples = min_samples
        self.confidence_threshold = confidence_threshold

        # In-memory caches
        self.baselines: dict[str, StatisticalBaseline] = {}
        self.recent_metrics: dict[str, list[PerformanceMetric]] = {}
        self.alerts: list[RegressionAlert] = []

        # Threading
        self._lock = threading.Lock()
        self._monitoring_thread: threading.Thread | None = None
        self._running = False

        # Initialize database
        self._init_database()

        # Load existing baselines
        self._load_baselines()

        logger.info("PerformanceRegressionDetector initialized")

    def _init_database(self) -> None:
        """Initialize SQLite database for storing performance data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    backend TEXT NOT NULL,
                    circuit_hash TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS regression_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    backend TEXT NOT NULL,
                    circuit_hash TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    baseline_value REAL NOT NULL,
                    current_value REAL NOT NULL,
                    degradation_percent REAL NOT NULL,
                    detection_timestamp REAL NOT NULL,
                    confidence REAL NOT NULL,
                    description TEXT,
                    metadata TEXT,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS statistical_baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    baseline_key TEXT UNIQUE NOT NULL,
                    mean_value REAL NOT NULL,
                    std_value REAL NOT NULL,
                    median_value REAL NOT NULL,
                    percentile_95 REAL NOT NULL,
                    percentile_99 REAL NOT NULL,
                    sample_count INTEGER NOT NULL,
                    last_updated REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for performance
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_metrics_backend_type ON performance_metrics(backend, metric_type)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_circuit ON performance_metrics(circuit_hash)")

            conn.commit()

    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        backend: str,
        circuit: QuantumCircuit | None = None,
        circuit_hash: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a performance metric measurement."""
        if circuit is not None:
            circuit_hash = self._hash_circuit(circuit)
        elif circuit_hash is None:
            circuit_hash = "unknown"

        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            timestamp=time.time(),
            backend=backend,
            circuit_hash=circuit_hash,
            metadata=metadata or {},
        )

        # Store in database
        self._store_metric_db(metric)

        # Update in-memory cache
        with self._lock:
            key = self._get_baseline_key(metric_type, backend, circuit_hash)
            if key not in self.recent_metrics:
                self.recent_metrics[key] = []

            self.recent_metrics[key].append(metric)

            # Keep only recent metrics in memory (last 1000 per key)
            if len(self.recent_metrics[key]) > 1000:
                self.recent_metrics[key] = self.recent_metrics[key][-1000:]

        # Check for regression
        self._check_for_regression(metric)

        logger.debug(f"Recorded metric: {metric_type.value} = {value} for backend {backend}")

    def _store_metric_db(self, metric: PerformanceMetric) -> None:
        """Store metric in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO performance_metrics
                    (metric_type, value, timestamp, backend, circuit_hash, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric.metric_type.value,
                        metric.value,
                        metric.timestamp,
                        metric.backend,
                        metric.circuit_hash,
                        json.dumps(metric.metadata),
                    ),
                )
                conn.commit()
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                # Initialize database if tables don't exist
                self._init_database()
                # Retry the operation
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO performance_metrics
                        (metric_type, value, timestamp, backend, circuit_hash, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            metric.metric_type.value,
                            metric.value,
                            metric.timestamp,
                            metric.backend,
                            metric.circuit_hash,
                            json.dumps(metric.metadata),
                        ),
                    )
                    conn.commit()
            else:
                raise

    def _hash_circuit(self, circuit: QuantumCircuit) -> str:
        """Generate a hash for a quantum circuit based on its structure."""
        # Create a string representation of the circuit structure
        circuit_str = f"qubits:{circuit.num_qubits},clbits:{circuit.num_clbits},"

        for instruction in circuit.data:
            op = instruction.operation
            qubits = [circuit.find_bit(q).index for q in instruction.qubits]
            clbits = [circuit.find_bit(c).index for c in instruction.clbits]

            circuit_str += f"{op.name}({','.join(map(str, op.params))})->{qubits},{clbits};"

        return hashlib.md5(circuit_str.encode()).hexdigest()[:16]

    def _get_baseline_key(self, metric_type: MetricType, backend: str, circuit_hash: str) -> str:
        """Generate a unique key for baseline storage."""
        return f"{metric_type.value}:{backend}:{circuit_hash}"

    def _check_for_regression(self, metric: PerformanceMetric) -> None:
        """Check if a metric indicates a performance regression."""
        baseline_key = self._get_baseline_key(metric.metric_type, metric.backend, metric.circuit_hash)

        # Get or create baseline
        baseline_result: StatisticalBaseline | None = self._get_baseline(
            baseline_key, metric.metric_type, metric.backend, metric.circuit_hash
        )

        if baseline_result is None or baseline_result.sample_count < self.min_samples:
            # Not enough data for regression detection
            return

        # Calculate expected range based on baseline
        expected_max = baseline_result.mean + 2 * baseline_result.std

        # For execution time and latency, higher values are worse
        if metric.metric_type in [MetricType.EXECUTION_TIME, MetricType.BACKEND_LATENCY]:
            threshold_value = baseline_result.mean * (1 + self.detection_threshold)

            if metric.value > threshold_value:
                degradation_percent = ((metric.value - baseline_result.mean) / baseline_result.mean) * 100
                confidence = min(1.0, (metric.value - threshold_value) / (expected_max - threshold_value))

                if confidence >= self.confidence_threshold:
                    self._create_regression_alert(metric, baseline_result, degradation_percent, confidence)

        # For throughput and accuracy, lower values are worse
        elif metric.metric_type in [MetricType.THROUGHPUT, MetricType.ACCURACY]:
            threshold_value = baseline_result.mean * (1 - self.detection_threshold)

            if metric.value < threshold_value:
                degradation_percent = ((baseline_result.mean - metric.value) / baseline_result.mean) * 100
                expected_min = baseline_result.mean - 2 * baseline_result.std
                confidence = min(1.0, (threshold_value - metric.value) / (threshold_value - expected_min))

                if confidence >= self.confidence_threshold:
                    self._create_regression_alert(metric, baseline_result, degradation_percent, confidence)

        # For error rate, higher values are worse
        elif metric.metric_type == MetricType.ERROR_RATE:
            threshold_value = baseline_result.mean * (1 + self.detection_threshold)

            if metric.value > threshold_value:
                degradation_percent = ((metric.value - baseline_result.mean) / baseline_result.mean) * 100
                confidence = min(1.0, (metric.value - threshold_value) / (expected_max - threshold_value))

                if confidence >= self.confidence_threshold:
                    self._create_regression_alert(metric, baseline_result, degradation_percent, confidence)

    def _create_regression_alert(
        self,
        metric: PerformanceMetric,
        baseline: StatisticalBaseline,
        degradation_percent: float,
        confidence: float,
    ) -> None:
        """Create a regression alert."""
        # Determine severity
        if degradation_percent < 25:
            severity = RegressionSeverity.MINOR
        elif degradation_percent < 50:
            severity = RegressionSeverity.MODERATE
        elif degradation_percent < 100:
            severity = RegressionSeverity.MAJOR
        else:
            severity = RegressionSeverity.CRITICAL

        # Create description
        direction = (
            "increased"
            if metric.metric_type in [MetricType.EXECUTION_TIME, MetricType.BACKEND_LATENCY, MetricType.ERROR_RATE]
            else "decreased"
        )

        description = (
            f"{metric.metric_type.value} has {direction} by {degradation_percent:.1f}% "
            f"for backend {metric.backend}. Current value: {metric.value:.4f}, "
            f"baseline: {baseline.mean:.4f} (±{baseline.std:.4f})"
        )

        alert = RegressionAlert(
            metric_type=metric.metric_type,
            backend=metric.backend,
            circuit_hash=metric.circuit_hash,
            severity=severity,
            baseline_value=baseline.mean,
            current_value=metric.value,
            degradation_percent=degradation_percent,
            detection_timestamp=metric.timestamp,
            confidence=confidence,
            description=description,
            metadata={
                "baseline_std": baseline.std,
                "baseline_samples": baseline.sample_count,
                "baseline_last_updated": baseline.last_updated,
            },
        )

        # Store alert
        self._store_alert_db(alert)

        with self._lock:
            self.alerts.append(alert)

            # Keep only recent alerts in memory
            if len(self.alerts) > 1000:
                self.alerts = self.alerts[-1000:]

        logger.warning(f"Performance regression detected: {description}")

    def _store_alert_db(self, alert: RegressionAlert) -> None:
        """Store regression alert in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO regression_alerts
                (metric_type, backend, circuit_hash, severity, baseline_value,
                 current_value, degradation_percent, detection_timestamp,
                 confidence, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    alert.metric_type.value,
                    alert.backend,
                    alert.circuit_hash,
                    alert.severity.value,
                    alert.baseline_value,
                    alert.current_value,
                    alert.degradation_percent,
                    alert.detection_timestamp,
                    alert.confidence,
                    alert.description,
                    json.dumps(alert.metadata),
                ),
            )
            conn.commit()

    def _get_baseline(
        self, baseline_key: str, metric_type: MetricType, backend: str, circuit_hash: str
    ) -> StatisticalBaseline | None:
        """Get or compute baseline for a metric."""
        with self._lock:
            if baseline_key in self.baselines:
                baseline: StatisticalBaseline = self.baselines[baseline_key]

                # Check if baseline needs refresh
                if time.time() - baseline.last_updated > 86400:  # 24 hours
                    self._update_baseline(baseline_key, metric_type, backend, circuit_hash)
                    refreshed = self.baselines.get(baseline_key)
                    if refreshed is not None:
                        baseline = refreshed

                return baseline
            else:
                # Compute new baseline
                return self._compute_baseline(baseline_key, metric_type, backend, circuit_hash)

    def _compute_baseline(
        self, baseline_key: str, metric_type: MetricType, backend: str, circuit_hash: str
    ) -> StatisticalBaseline | None:
        """Compute statistical baseline from historical data."""
        # Get historical data from database
        cutoff_time = time.time() - (self.baseline_window_days * 86400)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT value FROM performance_metrics
                WHERE metric_type = ? AND backend = ? AND circuit_hash = ?
                AND timestamp >= ?
                ORDER BY timestamp ASC
            """,
                (metric_type.value, backend, circuit_hash, cutoff_time),
            )

            values = [row[0] for row in cursor.fetchall()]

        if len(values) < self.min_samples:
            return None

        # Compute statistics
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0.0
        median_val = statistics.median(values)

        # Compute percentiles
        sorted_values = sorted(values)
        p95_idx = int(0.95 * len(sorted_values))
        p99_idx = int(0.99 * len(sorted_values))

        baseline = StatisticalBaseline(
            mean=mean_val,
            std=std_val,
            median=median_val,
            percentile_95=sorted_values[p95_idx],
            percentile_99=sorted_values[p99_idx],
            sample_count=len(values),
            last_updated=time.time(),
        )

        # Cache and store baseline
        with self._lock:
            self.baselines[baseline_key] = baseline

        self._store_baseline_db(baseline_key, baseline)

        return baseline

    def _update_baseline(self, baseline_key: str, metric_type: MetricType, backend: str, circuit_hash: str) -> None:
        """Update an existing baseline with new data."""
        new_baseline = self._compute_baseline(baseline_key, metric_type, backend, circuit_hash)

        if new_baseline:
            with self._lock:
                self.baselines[baseline_key] = new_baseline

            logger.debug(f"Updated baseline for {baseline_key}")

    def _store_baseline_db(self, baseline_key: str, baseline: StatisticalBaseline) -> None:
        """Store baseline in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO statistical_baselines
                (baseline_key, mean_value, std_value, median_value,
                 percentile_95, percentile_99, sample_count, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    baseline_key,
                    baseline.mean,
                    baseline.std,
                    baseline.median,
                    baseline.percentile_95,
                    baseline.percentile_99,
                    baseline.sample_count,
                    baseline.last_updated,
                ),
            )
            conn.commit()

    def _load_baselines(self) -> None:
        """Load existing baselines from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT baseline_key, mean_value, std_value, median_value,
                           percentile_95, percentile_99, sample_count, last_updated
                    FROM statistical_baselines
                """)

                for row in cursor.fetchall():
                    baseline_key = row[0]
                    baseline = StatisticalBaseline(
                        mean=row[1],
                        std=row[2],
                        median=row[3],
                        percentile_95=row[4],
                        percentile_99=row[5],
                        sample_count=row[6],
                        last_updated=row[7],
                    )

                    self.baselines[baseline_key] = baseline

            logger.info(f"Loaded {len(self.baselines)} baselines from database")
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                logger.info("No baselines table found, skipping load")
                return
            raise

    def start_monitoring(self, check_interval: float = 300.0) -> None:
        """Start background monitoring thread."""
        if self._running:
            logger.warning("Monitoring already running")
            return

        self._running = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, args=(check_interval,), daemon=True)
        self._monitoring_thread.start()

        logger.info("Started performance regression monitoring")

    def stop_monitoring(self) -> None:
        """Stop background monitoring."""
        self._running = False

        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5.0)

        logger.info("Stopped performance regression monitoring")

    def _monitoring_loop(self, check_interval: float) -> None:
        """Background monitoring loop."""
        while self._running:
            try:
                # Update baselines periodically
                self._refresh_stale_baselines()

                # Clean up old data
                self._cleanup_old_data()

                time.sleep(check_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Back off on error

    def _refresh_stale_baselines(self) -> None:
        """Refresh baselines that are older than 24 hours."""
        current_time = time.time()
        stale_baselines = []

        with self._lock:
            for key, baseline in self.baselines.items():
                if current_time - baseline.last_updated > 86400:  # 24 hours
                    stale_baselines.append(key)

        for baseline_key in stale_baselines:
            parts = baseline_key.split(":")
            if len(parts) == 3:
                metric_type = MetricType(parts[0])
                backend = parts[1]
                circuit_hash = parts[2]

                self._update_baseline(baseline_key, metric_type, backend, circuit_hash)

    def _cleanup_old_data(self) -> None:
        """Clean up old performance data to manage database size."""
        # Keep data for 90 days
        cutoff_time = time.time() - (90 * 86400)

        with sqlite3.connect(self.db_path) as conn:
            # Clean up old metrics
            cursor = conn.execute("DELETE FROM performance_metrics WHERE timestamp < ?", (cutoff_time,))
            metrics_deleted = cursor.rowcount

            # Clean up old alerts (keep for 180 days)
            alert_cutoff = time.time() - (180 * 86400)
            cursor = conn.execute("DELETE FROM regression_alerts WHERE detection_timestamp < ?", (alert_cutoff,))
            alerts_deleted = cursor.rowcount

            conn.commit()

            if metrics_deleted > 0 or alerts_deleted > 0:
                logger.info(f"Cleaned up {metrics_deleted} old metrics and {alerts_deleted} old alerts")

    # Public API methods

    def get_recent_alerts(
        self,
        hours: int = 24,
        severity: RegressionSeverity | None = None,
        backend: str | None = None,
    ) -> list[RegressionAlert]:
        """Get recent regression alerts."""
        cutoff_time = time.time() - (hours * 3600)

        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT metric_type, backend, circuit_hash, severity, baseline_value,
                       current_value, degradation_percent, detection_timestamp,
                       confidence, description, metadata
                FROM regression_alerts
                WHERE detection_timestamp >= ?
            """
            params: list[Any] = [cutoff_time]

            if severity:
                query += " AND severity = ?"
                params.append(severity.value)

            if backend:
                query += " AND backend = ?"
                params.append(backend)

            query += " ORDER BY detection_timestamp DESC"

            cursor = conn.execute(query, params)
            alerts = []

            for row in cursor.fetchall():
                alert = RegressionAlert(
                    metric_type=MetricType(row[0]),
                    backend=row[1],
                    circuit_hash=row[2],
                    severity=RegressionSeverity(row[3]),
                    baseline_value=row[4],
                    current_value=row[5],
                    degradation_percent=row[6],
                    detection_timestamp=row[7],
                    confidence=row[8],
                    description=row[9],
                    metadata=json.loads(row[10]) if row[10] else {},
                )
                alerts.append(alert)

            return alerts

    def get_performance_summary(self, backend: str, hours: int = 24) -> dict[str, Any]:
        """Get performance summary for a backend."""
        cutoff_time = time.time() - (hours * 3600)

        with sqlite3.connect(self.db_path) as conn:
            # Get metric statistics
            cursor = conn.execute(
                """
                SELECT metric_type, AVG(value), MIN(value), MAX(value), COUNT(*)
                FROM performance_metrics
                WHERE backend = ? AND timestamp >= ?
                GROUP BY metric_type
            """,
                (backend, cutoff_time),
            )

            metrics = {}
            for row in cursor.fetchall():
                metrics[row[0]] = {
                    "average": row[1],
                    "minimum": row[2],
                    "maximum": row[3],
                    "sample_count": row[4],
                }

            # Get alert counts
            cursor = conn.execute(
                """
                SELECT severity, COUNT(*)
                FROM regression_alerts
                WHERE backend = ? AND detection_timestamp >= ?
                GROUP BY severity
            """,
                (backend, cutoff_time),
            )

            alert_counts = {}
            for row in cursor.fetchall():
                alert_counts[row[0]] = row[1]

            return {
                "backend": backend,
                "time_period_hours": hours,
                "metrics": metrics,
                "alert_counts": alert_counts,
                "total_alerts": sum(alert_counts.values()),
                "generated_at": time.time(),
            }

    def acknowledge_alert(self, alert_id: int) -> None:
        """Acknowledge a regression alert."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE regression_alerts SET acknowledged = TRUE WHERE id = ?", (alert_id,))
            conn.commit()

    def get_baseline_info(self, metric_type: MetricType, backend: str, circuit_hash: str) -> dict[str, Any] | None:
        """Get baseline information for a specific metric."""
        baseline_key = self._get_baseline_key(metric_type, backend, circuit_hash)
        baseline = self._get_baseline(baseline_key, metric_type, backend, circuit_hash)

        if baseline:
            return {
                "mean": baseline.mean,
                "std": baseline.std,
                "median": baseline.median,
                "percentile_95": baseline.percentile_95,
                "percentile_99": baseline.percentile_99,
                "sample_count": baseline.sample_count,
                "last_updated": baseline.last_updated,
                "confidence_interval_95": (
                    baseline.mean - 1.96 * baseline.std,
                    baseline.mean + 1.96 * baseline.std,
                ),
            }

        return None


# Global instance for easy access
_global_detector: PerformanceRegressionDetector | None = None


def get_regression_detector() -> PerformanceRegressionDetector:
    """Get the global regression detector instance."""
    global _global_detector
    if _global_detector is None:
        _global_detector = PerformanceRegressionDetector()
    return _global_detector


def record_performance_metric(
    metric_type: MetricType,
    value: float,
    backend: str,
    circuit: QuantumCircuit | None = None,
    circuit_hash: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Convenience function to record a performance metric."""
    detector = get_regression_detector()
    detector.record_metric(metric_type, value, backend, circuit, circuit_hash, metadata)
