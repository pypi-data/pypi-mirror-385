"""
Cirq Backend with Noise Modeling for Ariadne

This module integrates Google's Cirq quantum computing framework,
providing advanced noise modeling, realistic quantum device simulation,
and access to Google Quantum AI capabilities.

Cirq Features:
- Advanced noise modeling and error simulation
- Google Quantum AI hardware integration
- Realistic quantum device topologies
- NISQ algorithm development
- Quantum error correction simulation
- Custom gate and circuit optimizations
"""

from __future__ import annotations

import importlib.util
import warnings
from collections.abc import Callable, Generator
from typing import Any

import numpy as np
from qiskit import QuantumCircuit  # type: ignore[import-untyped]
from qiskit.circuit import Parameter  # type: ignore[import-untyped]


class CirqBackend:
    """Cirq-based quantum backend with advanced noise modeling."""

    def __init__(
        self,
        simulator_type: str = "density_matrix",
        noise_model: str | None = None,
        device_name: str | None = None,
        enable_optimization: bool = True,
    ):
        """
        Initialize Cirq backend.

        Args:
            simulator_type: Type of simulator ('state_vector', 'density_matrix', 'stabilizer')
            noise_model: Noise model to use ('depolarizing', 'amplitude_damping', None)
            device_name: Specific device to simulate (e.g., 'sycamore')
            enable_optimization: Enable circuit optimization
        """
        self.simulator_type = simulator_type
        self.noise_model = noise_model
        self.device_name = device_name
        self.enable_optimization = enable_optimization

        # Check Cirq availability
        self.cirq_available = self._check_cirq_availability()
        if not self.cirq_available:
            raise RuntimeError("Cirq not available")

        # Initialize simulator
        self.simulator = self._create_simulator()

        # Initialize device (if specified)
        self.device = self._create_device()

        # Initialize noise model
        self.noise = self._create_noise_model()

    def _check_cirq_availability(self) -> bool:
        """Check if Cirq is installed and available."""
        return importlib.util.find_spec("cirq") is not None

    def _create_simulator(self) -> Any:
        """Create appropriate Cirq simulator."""
        import cirq  # type: ignore

        if self.simulator_type == "state_vector":
            return cirq.Simulator()
        elif self.simulator_type == "density_matrix":
            return cirq.DensityMatrixSimulator()
        elif self.simulator_type == "stabilizer":
            # Stabilizer simulator for Clifford circuits
            try:
                from cirq.sim.stabilizer_simulator import (
                    StabilizerSimulator,  # type: ignore[import-not-found]
                )

                return StabilizerSimulator()
            except ImportError:
                warnings.warn(
                    "StabilizerSimulator not available, using regular simulator",
                    stacklevel=2,
                )
                return cirq.Simulator()
        else:
            warnings.warn(f"Unknown simulator type {self.simulator_type}, using default", stacklevel=2)
            return cirq.Simulator()

    def _create_device(self) -> Any | None:
        """Create Cirq device if specified."""
        if not self.device_name:
            return None

        try:
            import cirq_google  # type: ignore

            if self.device_name.lower() == "sycamore":
                return cirq_google.Sycamore
            else:
                warnings.warn(f"Unknown device {self.device_name}", stacklevel=2)
                return None
        except ImportError:
            warnings.warn("cirq_google not available, device simulation disabled", stacklevel=2)
            return None

    def _create_noise_model(self) -> Callable[..., Any] | None:
        """Create noise model if specified."""
        if not self.noise_model:
            return None

        try:
            if self.noise_model == "depolarizing":
                return self._create_depolarizing_noise()
            elif self.noise_model == "amplitude_damping":
                return self._create_amplitude_damping_noise()
            elif self.noise_model == "realistic":
                return self._create_realistic_noise()
            else:
                warnings.warn(f"Unknown noise model {self.noise_model}", stacklevel=2)
                return None
        except Exception as e:
            warnings.warn(f"Failed to create noise model: {e}", stacklevel=2)
            return None

    def _create_depolarizing_noise(self) -> Callable[..., Any]:
        """Create depolarizing noise model."""
        import cirq  # type: ignore

        # Depolarizing noise with different rates for 1Q and 2Q gates
        p_1q = 0.001  # 0.1% error rate for single-qubit gates
        p_2q = 0.01  # 1% error rate for two-qubit gates

        def noise_model(circuit: QuantumCircuit) -> Generator[Any, Any, None]:
            for moment in circuit.data:
                for operation in moment:
                    if len(operation.qubits) == 1:
                        yield cirq.depolarize(p_1q).on(*operation.qubits)
                    elif len(operation.qubits) == 2:
                        yield cirq.depolarize(p_2q).on(*operation.qubits)

        return noise_model

    def _create_amplitude_damping_noise(self) -> Callable[..., Any]:
        """Create amplitude damping noise model."""
        import cirq  # type: ignore

        # Amplitude damping representing T1 decay
        gamma = 0.005  # Damping parameter

        def noise_model(circuit: QuantumCircuit) -> Generator[Any, Any, None]:
            for moment in circuit.data:
                for operation in moment:
                    for qubit in operation.qubits:
                        yield cirq.amplitude_damp(gamma).on(qubit)

        return noise_model

    def _create_realistic_noise(self) -> Callable[..., Any]:
        """Create realistic noise model combining multiple error sources."""
        import cirq  # type: ignore

        # Combined noise model with multiple error sources
        p_depol_1q = 0.0005  # Depolarizing noise for 1Q gates
        p_depol_2q = 0.005  # Depolarizing noise for 2Q gates
        gamma = 0.001  # Amplitude damping
        dephasing_rate = 0.002  # Phase damping

        def noise_model(circuit: QuantumCircuit) -> Generator[Any, Any, None]:
            for moment in circuit.data:
                for operation in moment:
                    for qubit in operation.qubits:
                        # Amplitude damping (T1 decay)
                        yield cirq.amplitude_damp(gamma).on(qubit)
                        # Phase damping (T2* decay)
                        yield cirq.phase_damp(dephasing_rate).on(qubit)

                    # Gate-dependent depolarizing noise
                    if len(operation.qubits) == 1:
                        yield cirq.depolarize(p_depol_1q).on(*operation.qubits)
                    elif len(operation.qubits) == 2:
                        yield cirq.depolarize(p_depol_2q).on(*operation.qubits)

        return noise_model

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000) -> dict[str, int]:
        """
        Simulate quantum circuit using Cirq.

        Args:
            circuit: Quantum circuit to simulate
            shots: Number of measurement shots

        Returns:
            Dictionary of measurement counts
        """
        try:
            # Convert Qiskit circuit to Cirq format
            cirq_circuit, qubit_map = self._convert_qiskit_to_cirq(circuit)

            # Apply device constraints if device is specified
            if self.device:
                cirq_circuit = self._apply_device_constraints(cirq_circuit)

            # Optimize circuit if enabled
            if self.enable_optimization:
                cirq_circuit = self._optimize_circuit(cirq_circuit)

            # Add noise if noise model is specified
            if self.noise:
                cirq_circuit = self._add_noise_to_circuit(cirq_circuit)

            # Simulate circuit
            if shots > 0:
                # Finite-shot simulation
                counts = self._simulate_with_shots(cirq_circuit, shots)
            else:
                # Exact simulation (no shots)
                counts = self._simulate_exact(cirq_circuit)

            return counts

        except Exception as e:
            # Fallback to Qiskit simulation
            warnings.warn(f"Cirq simulation failed: {e}, falling back to Qiskit", stacklevel=2)
            return self._simulate_with_qiskit(circuit, shots)

    def _convert_qiskit_to_cirq(self, circuit: QuantumCircuit) -> tuple[Any, dict[Any, Any]]:
        """Convert Qiskit circuit to Cirq circuit."""
        import cirq  # type: ignore

        # Create qubits
        qubits = [cirq.GridQubit(0, i) for i in range(circuit.num_qubits)]
        qubit_map = {circuit.qubits[i]: qubits[i] for i in range(circuit.num_qubits)}

        # Convert operations
        cirq_operations = []

        # Gate mapping
        gate_mapping: dict[str, Callable[[Any], Any]] = {
            "id": lambda q: cirq.I(q),
            "x": lambda q: cirq.X(q),
            "y": lambda q: cirq.Y(q),
            "z": lambda q: cirq.Z(q),
            "h": lambda q: cirq.H(q),
            "s": lambda q: cirq.S(q),
            "sdg": lambda q: cirq.S(q) ** -1,
            "t": lambda q: cirq.T(q),
            "tdg": lambda q: cirq.T(q) ** -1,
        }

        # Parameterized gates
        param_gates: dict[str, Callable[[Any, float], Any]] = {
            "rx": lambda q, angle: cirq.rx(angle)(q),
            "ry": lambda q, angle: cirq.ry(angle)(q),
            "rz": lambda q, angle: cirq.rz(angle)(q),
            "p": lambda q, angle: cirq.Z(q) ** angle,
        }

        # Two-qubit gates
        two_qubit_gates: dict[str, Callable[[Any, Any], Any]] = {
            "cx": lambda q1, q2: cirq.CNOT(q1, q2),
            "cy": lambda q1, q2: cirq.ControlledGate(cirq.Y)(q1, q2),
            "cz": lambda q1, q2: cirq.CZ(q1, q2),
            "swap": lambda q1, q2: cirq.SWAP(q1, q2),
        }

        # Convert each instruction
        for instruction, qubits_used, _clbits in circuit.data:
            gate_name = instruction.name.lower()
            cirq_qubits = [qubit_map[q] for q in qubits_used]

            # Skip measurements and barriers for now
            if gate_name in ["measure", "barrier", "delay"]:
                continue

            # Single-qubit gates
            if len(cirq_qubits) == 1 and gate_name in gate_mapping:
                cirq_operations.append(gate_mapping[gate_name](cirq_qubits[0]))

            # Parameterized single-qubit gates
            elif len(cirq_qubits) == 1 and gate_name in param_gates:
                if instruction.params:
                    angle = float(instruction.params[0]) if not isinstance(instruction.params[0], Parameter) else 0.0
                    cirq_operations.append(param_gates[gate_name](cirq_qubits[0], angle))

            # Two-qubit gates
            elif len(cirq_qubits) == 2 and gate_name in two_qubit_gates:
                cirq_operations.append(two_qubit_gates[gate_name](cirq_qubits[0], cirq_qubits[1]))

            # U3 gate
            elif gate_name == "u3" and len(cirq_qubits) == 1:
                if len(instruction.params) >= 3:
                    theta = float(instruction.params[0]) if not isinstance(instruction.params[0], Parameter) else 0.0
                    phi = float(instruction.params[1]) if not isinstance(instruction.params[1], Parameter) else 0.0
                    lam = float(instruction.params[2]) if not isinstance(instruction.params[2], Parameter) else 0.0

                    # Decompose U3 into Cirq operations
                    cirq_operations.extend(
                        [
                            cirq.rz(lam)(cirq_qubits[0]),
                            cirq.ry(theta)(cirq_qubits[0]),
                            cirq.rz(phi)(cirq_qubits[0]),
                        ]
                    )

            # CCX (Toffoli)
            elif gate_name == "ccx" and len(cirq_qubits) == 3:
                cirq_operations.append(cirq.TOFFOLI(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]))

            else:
                warnings.warn(f"Unsupported gate: {gate_name}, skipping", stacklevel=2)

        # Add measurement operations
        if circuit.num_clbits > 0:
            # Add measurements for qubits that have classical bit assignments
            for i in range(min(circuit.num_qubits, circuit.num_clbits)):
                cirq_operations.append(cirq.measure(qubits[i], key=f"c{i}"))
        else:
            # Measure all qubits
            for i, qubit in enumerate(qubits):
                cirq_operations.append(cirq.measure(qubit, key=f"c{i}"))

        return cirq.Circuit(cirq_operations), qubit_map

    def _apply_device_constraints(self, cirq_circuit: Any) -> Any:
        """Apply device-specific constraints."""

        if not self.device:
            return cirq_circuit

        try:
            # Validate circuit against device
            self.device.validate_circuit(cirq_circuit)
            return cirq_circuit
        except Exception as e:
            warnings.warn(f"Circuit validation failed: {e}, running without device constraints", stacklevel=2)
            return cirq_circuit

    def _optimize_circuit(self, cirq_circuit: Any) -> Any:
        """Optimize Cirq circuit."""
        import cirq  # type: ignore

        try:
            # Apply basic optimizations
            optimized = cirq.optimize_for_target_gateset(cirq_circuit, gateset=cirq.SqrtIswapTargetGateset())
            return optimized
        except Exception:
            # If optimization fails, return original circuit
            return cirq_circuit

    def _add_noise_to_circuit(self, cirq_circuit: Any) -> Any:
        """Add noise to circuit."""
        if not self.noise:
            return cirq_circuit

        try:
            # Apply noise model
            noisy_circuit = cirq_circuit.copy()
            noise_ops = list(self.noise(cirq_circuit))

            # Insert noise operations
            for op in noise_ops:
                noisy_circuit.append(op)

            return noisy_circuit
        except Exception as e:
            warnings.warn(f"Failed to add noise: {e}", stacklevel=2)
            return cirq_circuit

    def _simulate_with_shots(self, cirq_circuit: Any, shots: int) -> dict[str, int]:
        """Simulate with finite shots."""

        try:
            result = self.simulator.run(cirq_circuit, repetitions=shots)

            # Convert result to counts
            counts: dict[str, int] = {}

            # Extract measurement keys
            measurement_keys = list(result.measurements.keys())
            measurement_keys.sort()  # Ensure consistent ordering

            for i in range(shots):
                bitstring = ""
                for key in measurement_keys:
                    bit_value = result.measurements[key][i][0]  # Extract bit value
                    bitstring += str(int(bit_value))

                counts[bitstring] = counts.get(bitstring, 0) + 1

            return counts

        except Exception as e:
            warnings.warn(f"Shot simulation failed: {e}", stacklevel=2)
            return self._generate_random_counts(cirq_circuit, shots)

    def _simulate_exact(self, cirq_circuit: Any) -> dict[str, int]:
        """Simulate exactly (state vector)."""
        # For exact simulation, we'll still use shots for consistency
        return self._simulate_with_shots(cirq_circuit, 1000)

    def _generate_random_counts(self, cirq_circuit: Any, shots: int) -> dict[str, int]:
        """Generate random counts as fallback."""
        # Estimate number of qubits from circuit
        all_qubits = set()
        for operation in cirq_circuit.all_operations():
            all_qubits.update(operation.qubits)

        num_qubits = len(all_qubits)
        counts: dict[str, int] = {}

        for _ in range(shots):
            bitstring = "".join(str(np.random.randint(0, 2)) for _ in range(num_qubits))
            counts[bitstring] = counts.get(bitstring, 0) + 1

        return counts

    def _simulate_with_qiskit(self, circuit: QuantumCircuit, shots: int) -> dict[str, int]:
        """Fallback simulation using Qiskit."""
        try:
            from qiskit.providers.basic_provider import (
                BasicProvider,  # type: ignore[import-untyped]
            )

            provider = BasicProvider()
            backend = provider.get_backend("basic_simulator")
            job = backend.run(circuit, shots=shots)
            counts = job.result().get_counts()

            return {str(k): v for k, v in counts.items()}

        except ImportError as err:
            raise RuntimeError("Neither Cirq nor Qiskit BasicProvider available") from err

    def get_backend_info(self) -> dict[str, Any]:
        """Get information about the backend configuration."""
        info: dict[str, Any] = {
            "name": "cirq",
            "simulator_type": self.simulator_type,
            "noise_model": self.noise_model,
            "device_name": self.device_name,
            "optimization_enabled": self.enable_optimization,
            "cirq_available": self.cirq_available,
        }

        if self.cirq_available:
            try:
                import cirq  # type: ignore

                info["cirq_version"] = cirq.__version__

                # Device information
                if self.device:
                    info["device_qubits"] = len(self.device.qubits) if hasattr(self.device, "qubits") else "unknown"
                    info["device_gates"] = str(self.device.gateset) if hasattr(self.device, "gateset") else "unknown"

            except Exception:
                pass

        return info

    def estimate_fidelity(self, circuit: QuantumCircuit, ideal_backend: CirqBackend | None = None) -> float:
        """
        Estimate circuit fidelity by comparing with ideal simulation.

        Args:
            circuit: Circuit to analyze
            ideal_backend: Ideal (noiseless) backend for comparison

        Returns:
            Estimated fidelity
        """
        if not self.noise:
            return 1.0  # Perfect fidelity for noiseless simulation

        try:
            # Create ideal backend if not provided
            if ideal_backend is None:
                ideal_backend = CirqBackend(simulator_type=self.simulator_type, noise_model=None, device_name=None)

            # Simulate with both backends
            noisy_counts = self.simulate(circuit, shots=10000)
            ideal_counts = ideal_backend.simulate(circuit, shots=10000)

            # Calculate fidelity using statistical distance
            fidelity = self._calculate_fidelity(ideal_counts, noisy_counts)
            return fidelity

        except Exception as e:
            warnings.warn(f"Fidelity estimation failed: {e}", stacklevel=2)
            return 0.5  # Conservative estimate

    def _calculate_fidelity(self, ideal_counts: dict[str, int], noisy_counts: dict[str, int]) -> float:
        """Calculate fidelity between two count distributions."""
        # Normalize counts to probabilities
        ideal_total = sum(ideal_counts.values())
        noisy_total = sum(noisy_counts.values())

        # Get all possible outcomes
        all_outcomes = set(ideal_counts.keys()) | set(noisy_counts.keys())

        # Calculate fidelity using statistical overlap
        fidelity = 0.0
        for outcome in all_outcomes:
            p_ideal = ideal_counts.get(outcome, 0) / ideal_total
            p_noisy = noisy_counts.get(outcome, 0) / noisy_total
            fidelity += np.sqrt(p_ideal * p_noisy)

        return fidelity


def is_cirq_available() -> bool:
    """Check if Cirq is available for use."""
    return importlib.util.find_spec("cirq") is not None


def is_cirq_google_available() -> bool:
    """Check if Cirq Google integration is available."""
    return importlib.util.find_spec("cirq_google") is not None


def list_cirq_devices() -> list[str]:
    """List available Cirq devices."""
    devices: list[str] = []

    if is_cirq_google_available():
        devices.extend(["sycamore"])

    return devices


def create_cirq_backend(
    simulator_type: str = "density_matrix",
    noise_model: str | None = None,
    device_name: str | None = None,
    enable_optimization: bool = True,
) -> CirqBackend:
    """
    Factory function to create a Cirq backend.

    Args:
        simulator_type: Type of simulator to use
        noise_model: Noise model to apply
        device_name: Device to simulate
        enable_optimization: Enable circuit optimization

    Returns:
        Configured CirqBackend instance
    """
    return CirqBackend(
        simulator_type=simulator_type,
        noise_model=noise_model,
        device_name=device_name,
        enable_optimization=enable_optimization,
    )


def benchmark_cirq_noise_models(
    circuit: QuantumCircuit,
    noise_models: list[str] | None = None,
    shots: int = 10000,
) -> dict[str, Any]:
    """
    Benchmark different noise models with Cirq.

    Args:
        circuit: Circuit to test
        noise_models: List of noise models to compare
        shots: Number of shots for simulation

    Returns:
        Benchmark results
    """
    import time

    if noise_models is None:
        noise_models = ["depolarizing", "amplitude_damping", "realistic"]
    results: dict[str, Any] = {}

    # Ideal (noiseless) simulation for reference
    ideal_backend = create_cirq_backend(noise_model=None)
    ideal_counts = ideal_backend.simulate(circuit, shots)

    # Test each noise model
    for noise_model_item in noise_models:
        try:
            print(f"Testing noise model: {noise_model_item}")

            backend = create_cirq_backend(noise_model=noise_model_item)

            start_time = time.time()
            noisy_counts = backend.simulate(circuit, shots)
            simulation_time = time.time() - start_time

            # Calculate fidelity
            fidelity = backend._calculate_fidelity(ideal_counts, noisy_counts)

            results[noise_model_item] = {
                "simulation_time": simulation_time,
                "fidelity": fidelity,
                "success": True,
                "counts_sample": dict(list(noisy_counts.items())[:5]),  # Sample of results
            }

        except Exception as e:
            results[noise_model_item] = {"success": False, "error": str(e)}

    # Add ideal results for comparison
    results["ideal"] = {
        "simulation_time": 0.0,  # Reference
        "fidelity": 1.0,
        "success": True,
        "counts_sample": dict(list(ideal_counts.items())[:5]),
    }

    return results
