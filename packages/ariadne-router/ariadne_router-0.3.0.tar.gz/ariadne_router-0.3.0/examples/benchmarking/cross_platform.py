#!/usr/bin/env python3
"""
Cross-Platform Benchmarking Utility

This script loops over available backends and exports benchmark results
in JSON format for citable, reproducible cross-simulator benchmarks.
"""

import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit

from ariadne import simulate


def create_benchmark_circuits():
    """Create a set of benchmark circuits for cross-platform testing."""
    circuits = {}

    # Bell State (2-qubit Clifford)
    bell = QuantumCircuit(2, 2)
    bell.h(0)
    bell.cx(0, 1)
    bell.measure_all()
    circuits['bell'] = bell

    # GHZ State (multi-qubit Clifford)
    ghz = QuantumCircuit(8, 8)
    ghz.h(0)
    for i in range(1, 8):
        ghz.cx(0, i)
    ghz.measure_all()
    circuits['ghz'] = ghz

    # QAOA Circuit (8-qubit variational)
    qaoa = QuantumCircuit(8, 8)
    # Initial state
    for i in range(8):
        qaoa.h(i)
    # QAOA layers
    for layer in range(2):
        # Problem Hamiltonian
        for i in range(7):
            qaoa.cx(i, i + 1)
            qaoa.rz(0.5, i + 1)
            qaoa.cx(i, i + 1)
        # Mixer Hamiltonian
        for i in range(8):
            qaoa.rx(0.3, i)
    qaoa.measure_all()
    circuits['qaoa'] = qaoa

    # Random Circuit (non-Clifford)
    random_circ = QuantumCircuit(6, 6)
    np.random.seed(42)  # For reproducibility
    for i in range(6):
        random_circ.h(i)
    for _ in range(10):
        control = np.random.randint(6)
        target = np.random.randint(6)
        if control != target:
            random_circ.cx(control, target)
        qubit = np.random.randint(6)
        random_circ.rz(np.random.uniform(0, 2*np.pi), qubit)
    random_circ.measure_all()
    circuits['random'] = random_circ

    return circuits


def benchmark_circuit(circuit, backend, shots=1000):
    """Benchmark a single circuit on a specific backend."""
    try:
        start_time = time.perf_counter()
        result = simulate(circuit, shots=shots, backend=backend)
        end_time = time.perf_counter()

        return {
            'success': True,
            'execution_time': end_time - start_time,
            'backend_used': result.backend_used.value,
            'shots': shots,
            'counts': dict(result.counts),
            'unique_outcomes': len(result.counts),
            'throughput': shots / (end_time - start_time)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'backend_requested': backend,
            'shots': shots
        }


def run_cross_platform_benchmark(algorithms=None, backends=None, shots=1000):
    """
    Run cross-platform benchmark across specified algorithms and backends.

    Args:
        algorithms: List of algorithm names to test (default: all)
        backends: List of backend names to test (default: auto-detected)
        shots: Number of shots per simulation

    Returns:
        Dictionary with benchmark results
    """
    if algorithms is None:
        algorithms = ['bell', 'ghz', 'qaoa', 'random']

    if backends is None:
        backends = ['auto', 'stim', 'qiskit', 'mps', 'tensor_network']

    print(f"Running cross-platform benchmark...")
    print(f"Algorithms: {algorithms}")
    print(f"Backends: {backends}")
    print(f"Shots per simulation: {shots}")
    print("=" * 50)

    # Create benchmark circuits
    circuits = create_benchmark_circuits()

    # Initialize results structure
    results = {
        'timestamp': datetime.now().isoformat(),
        'system_info': {
            'platform': time.platform(),
            'python_version': time.python_version(),
        },
        'config': {
            'algorithms': algorithms,
            'backends': backends,
            'shots': shots
        },
        'results': {}
    }

    # Run benchmarks
    for alg_name in algorithms:
        if alg_name not in circuits:
            print(f"Warning: Unknown algorithm '{alg_name}', skipping...")
            continue

        circuit = circuits[alg_name]
        print(f"\nBenchmarking {alg_name} ({circuit.num_qubits} qubits, {circuit.depth()} depth):")

        results['results'][alg_name] = {
            'circuit_info': {
                'qubits': circuit.num_qubits,
                'depth': circuit.depth(),
                'gate_counts': dict(circuit.count_ops())
            },
            'backends': {}
        }

        for backend in backends:
            print(f"  {backend:15} ... ", end="", flush=True)

            if backend == 'auto':
                # Use automatic routing
                try:
                    start_time = time.perf_counter()
                    result = simulate(circuit, shots=shots)
                    end_time = time.perf_counter()

                    backend_result = {
                        'success': True,
                        'execution_time': end_time - start_time,
                        'backend_used': result.backend_used.value,
                        'shots': shots,
                        'counts': dict(result.counts),
                        'unique_outcomes': len(result.counts),
                        'throughput': shots / (end_time - start_time),
                        'auto_routing': True
                    }
                    print(f"OK ({result.backend_used.value})")
                except Exception as e:
                    backend_result = {
                        'success': False,
                        'error': str(e),
                        'backend_requested': 'auto',
                        'shots': shots
                    }
                    print(f"FAILED ({e})")
            else:
                # Use specific backend
                backend_result = benchmark_circuit(circuit, backend, shots)
                if backend_result['success']:
                    print(f"OK")
                else:
                    print(f"FAILED")

            results['results'][alg_name]['backends'][backend] = backend_result

    return results


def export_benchmark_report(algorithms, backends, shots=1000, fmt="json"):
    """
    Return dict ready for JSON/CSV/Latex; keys: date, algorithms, hardware, results.

    Args:
        algorithms: List of algorithm names to test
        backends: List of backend names to test
        shots: Number of shots per simulation
        fmt: Output format (currently only 'json' supported)

    Returns:
        Dictionary containing benchmark report
    """
    if fmt != "json":
        raise ValueError(f"Format '{fmt}' not yet supported. Use 'json'.")

    # Run the benchmark
    results = run_cross_platform_benchmark(algorithms, backends, shots)

    # Create export-ready report
    report = {
        'date': results['timestamp'],
        'algorithms': results['config']['algorithms'],
        'hardware': results['system_info'],
        'results': results['results']
    }

    return report


def main():
    """Main function to run cross-platform benchmark and save results."""
    # Run benchmark with default settings
    results = run_cross_platform_benchmark()

    # Save results to JSON file
    output_file = f"cross_platform_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nBenchmark results saved to: {output_file}")

    # Print summary
    print("\nSummary:")
    print("=" * 30)

    for alg_name, alg_data in results['results'].items():
        print(f"\n{alg_name.upper()}:")
        successful_backends = []
        failed_backends = []

        for backend_name, backend_data in alg_data['backends'].items():
            if backend_data['success']:
                successful_backends.append(backend_name)
            else:
                failed_backends.append(backend_name)

        if successful_backends:
            print(f"  Working: {', '.join(successful_backends)}")
        if failed_backends:
            print(f"  Failed: {', '.join(failed_backends)}")


if __name__ == "__main__":
    main()
