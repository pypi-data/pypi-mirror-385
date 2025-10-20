"""
Dynamic Backend Capacity Calibration System

This module provides real-time calibration of backend capacities based on
actual performance measurements. It enables adaptive optimization of the
quantum router's backend selection algorithm.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean

import numpy as np
from qiskit import QuantumCircuit

# --- Calibration Constants ---
# General System Parameters
RECALIBRATION_FREQUENCY = 10
MIN_MEASUREMENTS_FOR_CALIBRATION = 3
MIN_CONFIDENCE_THRESHOLD = 0.3
CIRCUIT_HASH_LENGTH = 16
CALIBRATION_VERSION = "1.0"

# Confidence Calculation Parameters
FULL_CONFIDENCE_MEASUREMENT_COUNT = 20.0
CONFIDENCE_COUNT_WEIGHT = 0.7
CONFIDENCE_SUCCESS_RATE_WEIGHT = 0.3

# Capacity Calculation Parameters (Clifford Circuits)
CLIFFORD_DEFAULT_CAPACITY = 8.0
CLIFFORD_BASELINE_TIME_S = 0.1  # Target time for a standard Clifford circuit
CLIFFORD_MIN_CAPACITY = 1.0
CLIFFORD_SCALING_FACTOR = 10.0
CLIFFORD_MAX_CAPACITY = 20.0

# Capacity Calculation Parameters (General Circuits)
GENERAL_DEFAULT_CAPACITY = 10.0
GENERAL_BASELINE_TIME_S = 0.2  # Target time for a standard general circuit
GENERAL_MIN_CAPACITY = 1.0
GENERAL_SCALING_FACTOR = 12.0
GENERAL_MAX_CAPACITY = 25.0

# Memory Efficiency Parameters
MEMORY_DEFAULT_EFFICIENCY = 0.8
MEMORY_AMPLITUDE_BYTES = 8  # 8 bytes per complex amplitude (64-bit float real + 64-bit float imaginary)
BYTES_TO_MB_DIVISOR = 1024 * 1024
MEMORY_MIN_USAGE_THRESHOLD = 1.0
MEMORY_MAX_EFFICIENCY = 1.0

# Platform Boost Parameters
PLATFORM_BOOST_MIN = 1.0
PLATFORM_BOOST_SCALING_FACTOR = 2.0
PLATFORM_BOOST_MAX = 2.5


@dataclass
class PerformanceMeasurement:
    """Single performance measurement for a backend."""

    backend_name: str
    circuit_qubits: int
    circuit_depth: int
    is_clifford: bool
    execution_time: float
    memory_usage_mb: float
    success: bool
    timestamp: float
    shots: int
    circuit_hash: str


@dataclass
class BackendProfile:
    """Performance profile for a specific backend."""

    backend_name: str
    measurements: list[PerformanceMeasurement]
    calibrated_capacities: dict[str, float]
    last_updated: float
    confidence_score: float


@dataclass
class CalibrationData:
    """Complete calibration dataset."""

    version: str
    created_timestamp: float
    last_updated: float
    backend_profiles: dict[str, BackendProfile]
    calibrated_capacities: dict[str, dict[str, float]]
    measurement_count: int


class BackendCalibrator:
    """
    Dynamic calibration system for quantum backend performance.

    Continuously learns optimal backend selection based on real performance
    measurements and adapts routing decisions accordingly.
    """

    def __init__(self, calibration_file: Path | None = None) -> None:
        """Initialize calibrator with optional persistent storage."""
        self.calibration_file = calibration_file or Path("ariadne_calibration.json")
        self.measurements: list[PerformanceMeasurement] = []
        self.backend_profiles: dict[str, BackendProfile] = {}
        self.calibration_data: CalibrationData | None = None

        # Load existing calibration data
        self.load_calibration()

    def record_measurement(
        self,
        backend_name: str,
        circuit: QuantumCircuit,
        execution_time: float,
        memory_usage_mb: float = 0.0,
        success: bool = True,
        shots: int = 1000,
    ) -> None:
        """Record a performance measurement for a backend."""

        # Create circuit hash for deduplication
        circuit_hash = self._hash_circuit(circuit)

        # Analyze circuit properties
        from ariadne.route.analyze import analyze_circuit

        analysis = analyze_circuit(circuit)

        measurement = PerformanceMeasurement(
            backend_name=backend_name,
            circuit_qubits=circuit.num_qubits,
            circuit_depth=circuit.depth(),
            is_clifford=bool(analysis["is_clifford"]),
            execution_time=execution_time,
            memory_usage_mb=memory_usage_mb,
            success=success,
            timestamp=time.time(),
            shots=shots,
            circuit_hash=circuit_hash,
        )

        self.measurements.append(measurement)

        # Update backend profile
        if backend_name not in self.backend_profiles:
            self.backend_profiles[backend_name] = BackendProfile(
                backend_name=backend_name,
                measurements=[],
                calibrated_capacities={},
                last_updated=time.time(),
                confidence_score=0.0,
            )

        self.backend_profiles[backend_name].measurements.append(measurement)
        self.backend_profiles[backend_name].last_updated = time.time()

        # Trigger recalibration if enough new data
        if (
            len(self.measurements) % RECALIBRATION_FREQUENCY == 0
        ):  # Recalibrate every RECALIBRATION_FREQUENCY measurements
            self.recalibrate_all()

    def recalibrate_all(self) -> None:
        """Recalibrate all backend capacities based on measurements."""

        for _backend_name, profile in self.backend_profiles.items():
            if len(profile.measurements) < MIN_MEASUREMENTS_FOR_CALIBRATION:
                continue  # Need minimum measurements for calibration

            # Calculate performance metrics
            clifford_capacity = self._calculate_clifford_capacity(profile.measurements)
            general_capacity = self._calculate_general_capacity(profile.measurements)
            memory_efficiency = self._calculate_memory_efficiency(profile.measurements)
            apple_silicon_boost = self._calculate_platform_boost(profile.measurements)

            # Update calibrated capacities
            profile.calibrated_capacities = {
                "clifford_capacity": clifford_capacity,
                "general_capacity": general_capacity,
                "memory_efficiency": memory_efficiency,
                "apple_silicon_boost": apple_silicon_boost,
            }

            # Calculate confidence based on measurement count and variance
            profile.confidence_score = self._calculate_confidence(profile.measurements)

        # Save calibration data
        self.save_calibration()

    def _calculate_clifford_capacity(self, measurements: list[PerformanceMeasurement]) -> float:
        """Calculate calibrated Clifford circuit capacity."""
        clifford_times = [
            m.execution_time for m in measurements if m.is_clifford and m.success and m.execution_time > 0
        ]

        if not clifford_times:
            return CLIFFORD_DEFAULT_CAPACITY  # Default capacity

        # Higher capacity = lower execution time (better performance)
        avg_time = float(np.mean(clifford_times))
        baseline_time = CLIFFORD_BASELINE_TIME_S  # Baseline time for Clifford circuits

        # Scale capacity: faster execution = higher capacity
        raw_capacity = baseline_time / avg_time * CLIFFORD_SCALING_FACTOR
        capacity = max(CLIFFORD_MIN_CAPACITY, raw_capacity)
        return min(CLIFFORD_MAX_CAPACITY, capacity)  # Cap at reasonable maximum

    def _calculate_general_capacity(self, measurements: list[PerformanceMeasurement]) -> float:
        """Calculate calibrated general circuit capacity."""
        general_times = [
            m.execution_time for m in measurements if not m.is_clifford and m.success and m.execution_time > 0
        ]

        if not general_times:
            return GENERAL_DEFAULT_CAPACITY  # Default capacity

        avg_time = float(np.mean(general_times))
        baseline_time = GENERAL_BASELINE_TIME_S  # Baseline time for general circuits

        raw_capacity = baseline_time / avg_time * GENERAL_SCALING_FACTOR
        capacity = max(GENERAL_MIN_CAPACITY, raw_capacity)
        return min(GENERAL_MAX_CAPACITY, capacity)

    def _calculate_memory_efficiency(self, measurements: list[PerformanceMeasurement]) -> float:
        """Calculate memory efficiency score."""
        memory_usages = [m.memory_usage_mb for m in measurements if m.memory_usage_mb > 0 and m.success]

        if not memory_usages:
            return MEMORY_DEFAULT_EFFICIENCY  # Default efficiency

        # Qubit scaling analysis
        qubit_counts = [m.circuit_qubits for m in measurements if m.memory_usage_mb > 0 and m.success]

        if (
            len(memory_usages) < MIN_MEASUREMENTS_FOR_CALIBRATION - 1
        ):  # Requires at least 2 measurements for scaling analysis
            return MEMORY_DEFAULT_EFFICIENCY

        # Fit memory scaling: memory ~ 2^qubits
        try:
            # Calculate memory per exponential qubit
            efficiency_scores = []
            for mem, qubits in zip(memory_usages, qubit_counts, strict=False):
                if qubits > 0:
                    expected_mem = (
                        MEMORY_AMPLITUDE_BYTES * (2**qubits) / BYTES_TO_MB_DIVISOR
                    )  # Bytes per amplitude / MB conversion
                    efficiency = expected_mem / max(mem, MEMORY_MIN_USAGE_THRESHOLD)
                    efficiency_scores.append(min(MEMORY_MAX_EFFICIENCY, efficiency))

            if efficiency_scores:
                return fmean(efficiency_scores)
        except Exception:
            pass

        return MEMORY_DEFAULT_EFFICIENCY

    def _calculate_platform_boost(self, measurements: list[PerformanceMeasurement]) -> float:
        """Calculate platform-specific performance boost."""
        # This would compare performance across different platforms
        # For now, return a conservative estimate based on timing variance

        times = [m.execution_time for m in measurements if m.success and m.execution_time > 0]

        if len(times) < MIN_MEASUREMENTS_FOR_CALIBRATION:
            return PLATFORM_BOOST_MIN  # No boost if insufficient data

        # Lower variance suggests more consistent (optimized) performance
        time_std = float(np.std(times))
        time_mean = float(np.mean(times))

        if time_mean > 0:
            cv = time_std / time_mean  # Coefficient of variation
            # Lower CV = more consistent = better optimization
            candidate: float = PLATFORM_BOOST_SCALING_FACTOR - cv
            if candidate < PLATFORM_BOOST_MIN:
                candidate = PLATFORM_BOOST_MIN

            boost = candidate if candidate <= PLATFORM_BOOST_MAX else PLATFORM_BOOST_MAX
            return boost

        return PLATFORM_BOOST_MIN

    def _calculate_confidence(self, measurements: list[PerformanceMeasurement]) -> float:
        """Calculate confidence score for calibration."""
        count = len(measurements)
        success_rate = sum(1 for m in measurements if m.success) / max(count, 1)

        # Confidence increases with more measurements and higher success rate
        count_confidence = min(
            MEMORY_MAX_EFFICIENCY, count / FULL_CONFIDENCE_MEASUREMENT_COUNT
        )  # Full confidence at FULL_CONFIDENCE_MEASUREMENT_COUNT+ measurements

        return count_confidence * CONFIDENCE_COUNT_WEIGHT + success_rate * CONFIDENCE_SUCCESS_RATE_WEIGHT

    def _hash_circuit(self, circuit: QuantumCircuit) -> str:
        """Generate hash for circuit to enable deduplication."""
        import hashlib

        # Create a simple representation of the circuit
        circuit_str = ""
        for instruction, qubits, _clbits in circuit.data:
            qubit_indices = [circuit.find_bit(q).index for q in qubits]
            circuit_str += f"{instruction.name}-{qubit_indices};"

        return hashlib.md5(circuit_str.encode()).hexdigest()[:CIRCUIT_HASH_LENGTH]

    def get_calibrated_capacities(self, backend_name: str) -> dict[str, float] | None:
        """Get calibrated capacities for a specific backend."""
        if backend_name in self.backend_profiles:
            profile = self.backend_profiles[backend_name]
            if profile.confidence_score > MIN_CONFIDENCE_THRESHOLD:  # Minimum confidence threshold
                return profile.calibrated_capacities.copy()

        return None

    def save_calibration(self) -> None:
        """Save calibration data to persistent storage."""
        try:
            # Prepare calibration data
            calibrated_capacities = {}
            for name, profile in self.backend_profiles.items():
                if profile.confidence_score > MIN_CONFIDENCE_THRESHOLD:
                    calibrated_capacities[name] = profile.calibrated_capacities

            calibration_data = CalibrationData(
                version=CALIBRATION_VERSION,
                created_timestamp=getattr(self.calibration_data, "created_timestamp", time.time()),
                last_updated=time.time(),
                backend_profiles=self.backend_profiles,
                calibrated_capacities=calibrated_capacities,
                measurement_count=len(self.measurements),
            )

            self.calibration_data = calibration_data

            # Convert to JSON-serializable format
            data_dict = {
                "version": calibration_data.version,
                "created_timestamp": calibration_data.created_timestamp,
                "last_updated": calibration_data.last_updated,
                "calibrated_capacities": calibration_data.calibrated_capacities,
                "measurement_count": calibration_data.measurement_count,
                "backend_profiles": {
                    name: {
                        "backend_name": profile.backend_name,
                        "calibrated_capacities": profile.calibrated_capacities,
                        "last_updated": profile.last_updated,
                        "confidence_score": profile.confidence_score,
                        "measurement_count": len(profile.measurements),
                    }
                    for name, profile in calibration_data.backend_profiles.items()
                },
            }

            # Save to file
            with open(self.calibration_file, "w") as f:
                json.dump(data_dict, f, indent=2)

        except Exception as e:
            print(f"Warning: Failed to save calibration data: {e}")

    def load_calibration(self) -> None:
        """Load calibration data from persistent storage."""
        try:
            if not self.calibration_file.exists():
                return

            with open(self.calibration_file) as f:
                data_dict = json.load(f)

            # Reconstruct calibration data (simplified version)
            self.calibration_data = CalibrationData(
                version=data_dict.get("version", "1.0"),
                created_timestamp=data_dict.get("created_timestamp", time.time()),
                last_updated=data_dict.get("last_updated", time.time()),
                backend_profiles={},  # Simplified - don't load full measurements
                calibrated_capacities=data_dict.get("calibrated_capacities", {}),
                measurement_count=data_dict.get("measurement_count", 0),
            )

        except Exception as e:
            print(f"Warning: Failed to load calibration data: {e}")
            self.calibration_data = None


# Global calibrator instance
_global_calibrator: BackendCalibrator | None = None


def get_calibrator() -> BackendCalibrator:
    """Get the global calibrator instance."""
    global _global_calibrator
    if _global_calibrator is None:
        _global_calibrator = BackendCalibrator()
    return _global_calibrator


def load_calibration() -> CalibrationData | None:
    """Load calibration data for router initialization."""
    calibrator = get_calibrator()
    return calibrator.calibration_data


def record_backend_performance(
    backend_name: str,
    circuit: QuantumCircuit,
    execution_time: float,
    memory_usage_mb: float = 0.0,
    success: bool = True,
    shots: int = 1000,
) -> None:
    """Record backend performance measurement."""
    calibrator = get_calibrator()
    calibrator.record_measurement(
        backend_name=backend_name,
        circuit=circuit,
        execution_time=execution_time,
        memory_usage_mb=memory_usage_mb,
        success=success,
        shots=shots,
    )
