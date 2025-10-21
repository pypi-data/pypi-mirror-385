"""
Ariadne Advanced Benchmarking Tutorial

This example demonstrates advanced benchmarking capabilities in Ariadne.
"""

from ariadne.education import AlgorithmExplorer
from ariadne.enhanced_benchmarking import EnhancedBenchmarkSuite, compare_backends, run_comprehensive_benchmark


def demo_advanced_benchmarking():
    """Demonstrate advanced benchmarking capabilities."""
    print("=" * 60)
    print("ARIADNE ADVANCED BENCHMARKING TUTORIAL")
    print("=" * 60)

    print("\n1. ENHANCED BENCHMARK SUITE")
    print("-" * 32)

    # Create an enhanced benchmark suite
    suite = EnhancedBenchmarkSuite()

    # Run benchmarks for different algorithms
    algorithms = ['bell', 'ghz']
    qubit_counts = [2, 3, 4]

    print("Running benchmarks...")
    for alg in algorithms:
        for qubits in qubit_counts:
            print(f"\nBenchmarking {alg} with {qubits} qubits:")
            results = suite.benchmark_single_algorithm(
                algorithm_name=alg,
                qubit_count=qubits,
                shots=100
            )

            for i, result in enumerate(results):
                if result.success:
                    print(f"  Iteration {i+1}: {result.execution_time:.4f}s, {result.throughput:.2f} shots/s")
                else:
                    print(f"  Iteration {i+1}: FAILED - {result.error_message}")

    print(f"\nCollected {len(suite.results)} benchmark results")

    print("\n2. BACKEND COMPARISON")
    print("-" * 23)

    # Compare performance of different backends
    comparison = suite.benchmark_backend_comparison(
        algorithm_name='bell',
        qubit_count=3,
        backends=['auto', 'qiskit'],
        shots=100
    )

    print("Backend Performance Comparison:")
    for backend, result in comparison.items():
        if result.success:
            print(f"  {backend}: {result.execution_time:.4f}s, {result.throughput:.2f} shots/s")
        else:
            print(f"  {backend}: FAILED - {result.error_message}")

    print("\n3. SCALABILITY ANALYSIS")
    print("-" * 23)

    # Test scalability across qubit counts
    scalability_result = suite.scalability_test(
        algorithm_name='bell',
        qubit_range=(2, 4, 1),  # Start=2, Stop=4, Step=1
        shots=100
    )

    print(f"Scalability test for {scalability_result.algorithm}:")
    for i, qubits in enumerate(scalability_result.qubit_counts):
        time_val = scalability_result.execution_times[i]
        if time_val > 0:
            print(f"  {qubits} qubits: {time_val:.4f}s, {scalability_result.throughputs[i]:.2f} shots/s")
        else:
            print(f"  {qubits} qubits: FAILED")

    print("\n4. PERFORMANCE REPORT")
    print("-" * 21)

    # Generate a comprehensive performance report
    report = suite.generate_performance_report()
    print(report[:1000] + "..." if len(report) > 1000 else report)  # Truncate if too long

    print("\n5. COMPREHENSIVE BENCHMARK")
    print("-" * 26)

    # Run a more comprehensive benchmark
    comprehensive_suite = run_comprehensive_benchmark(
        algorithms=['bell'],  # Small example
        backends=['auto'],    # Use auto routing
        qubit_counts=[2, 3],  # Small range for demo
        shots=50            # Fewer shots for faster demo
    )

    print(f"Comprehensive benchmark completed with {len(comprehensive_suite.results)} results")

    print("\n6. BACKEND COMPARISON FUNCTION")
    print("-" * 32)

    # Use convenience function to compare backends
    backend_comparison = compare_backends('ghz', 3, ['auto', 'qiskit'])
    print("Backend comparison results:")
    for backend, result in backend_comparison.items():
        if result.success:
            print(f"  {backend}: {result.execution_time:.4f}s, {result.throughput:.2f} shots/s")
        else:
            print(f"  {backend}: FAILED - {result.error_message}")

    print("\n7. EXPORTING RESULTS")
    print("-" * 20)

    # Export results to JSON
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        suite.export_results(temp_path, format="json")
        print(f"Results exported to JSON: {temp_path}")

        # Read and show first part of exported results
        with open(temp_path) as f:
            import json
            results = json.load(f)
            print(f"Exported {len(results)} benchmark results")
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

    print("\n8. ADVANCED ANALYSIS")
    print("-" * 19)

    # Get algorithm explorer for additional analysis
    explorer = AlgorithmExplorer()
    available_algorithms = explorer.list_algorithms()

    print("Analyzing available algorithms:")
    for alg_name in available_algorithms[:5]:  # Limit to first 5 for demo
        try:
            info = explorer.get_algorithm_info(alg_name)
            props = info['circuit_properties']
            print(f"  {alg_name}: {props['n_qubits']} qubits, depth {props['depth']}, {props['size']} gates")
        except Exception as e:
            print(f"  {alg_name}: Error - {str(e)}")

    print("\n" + "=" * 60)
    print("ADVANCED BENCHMARKING TUTORIAL COMPLETE")
    print("Ariadne provides comprehensive tools for quantum algorithm analysis!")
    print("=" * 60)

if __name__ == "__main__":
    demo_advanced_benchmarking()
