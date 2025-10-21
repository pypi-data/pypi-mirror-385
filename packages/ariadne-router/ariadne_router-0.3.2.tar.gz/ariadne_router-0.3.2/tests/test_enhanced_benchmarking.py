"""
Test module for enhanced benchmarking functionality.
"""

from ariadne.enhanced_benchmarking import (
    CrossValidationSuite,
    EnhancedBenchmarkSuite,
    compare_backends,
    quick_performance_test,
    run_comprehensive_benchmark,
)


def test_enhanced_benchmark_suite():
    """Test the enhanced benchmark suite functionality."""
    suite = EnhancedBenchmarkSuite()

    # Test single algorithm benchmarking
    results = suite.benchmark_single_algorithm(algorithm_name="bell", qubit_count=2, shots=100, iterations=2)

    assert len(results) == 2  # 2 iterations
    for result in results:
        assert result.algorithm == "bell"
        assert result.success  # Should succeed for Bell state
        assert result.qubits == 2
        assert result.shots == 100
        assert result.execution_time >= 0
        assert result.throughput >= 0

    # Test backend comparison
    comparison = suite.benchmark_backend_comparison(
        algorithm_name="bell", qubit_count=2, backends=["auto", "qiskit"], shots=100
    )

    assert len(comparison) == 2  # 2 backends
    for _backend, result in comparison.items():
        assert result.algorithm == "bell"
        assert result.qubits == 2
        assert result.shots == 100
        # Results may or may not be successful depending on backend availability

    # Test generating report
    report = suite.generate_performance_report()
    assert isinstance(report, str)
    assert "Ariadne Benchmark Report" in report


def test_scalability_test():
    """Test the scalability testing functionality."""
    suite = EnhancedBenchmarkSuite()

    # Test scalability (limited range to avoid long tests)
    scalability_result = suite.scalability_test(
        algorithm_name="bell",
        qubit_range=(2, 3, 1),  # Small range for quick test
        shots=100,
    )

    assert scalability_result.algorithm == "bell"
    assert scalability_result.qubit_counts == [2, 3]
    assert len(scalability_result.execution_times) == 2
    assert len(scalability_result.throughputs) == 2
    assert len(scalability_result.success_rates) == 2


def test_cross_validation_suite():
    """Test the cross-validation functionality."""
    from ariadne.algorithms import get_algorithm
    from ariadne.algorithms.base import AlgorithmParameters

    # Create a simple circuit
    alg_class = get_algorithm("bell")
    circuit = alg_class(AlgorithmParameters(n_qubits=2)).create_circuit()

    validator = CrossValidationSuite()

    # Test cross-validation
    validation_result = validator.validate_backend_consistency(
        circuit=circuit, backends=["auto", "qiskit"], shots=100, tolerance=0.1
    )

    assert "consistent" in validation_result
    assert "results" in validation_result
    assert isinstance(validation_result["results"], dict)


def test_convenience_functions():
    """Test the convenience functions."""
    # Test quick performance test
    suite = quick_performance_test()
    assert len(suite.results) > 0

    # Test backend comparison
    results = compare_backends("bell", 2, ["auto", "qiskit"])
    assert isinstance(results, dict)
    assert len(results) == 2  # 2 backends


def test_comprehensive_benchmark():
    """Test the comprehensive benchmark function."""
    # Run a small comprehensive benchmark
    suite = run_comprehensive_benchmark(
        algorithms=["bell"],  # Just one algorithm to keep test quick
        backends=["auto"],  # Just auto to keep it simple
        qubit_counts=[2, 3],  # Small range
        shots=100,
    )

    # Should have at least some results
    assert len(suite.results) >= 2  # 2 qubit counts


if __name__ == "__main__":
    # Run the tests
    test_enhanced_benchmark_suite()
    print("✓ EnhancedBenchmarkSuite test passed")

    test_scalability_test()
    print("✓ Scalability test passed")

    test_cross_validation_suite()
    print("✓ CrossValidationSuite test passed")

    test_convenience_functions()
    print("✓ Convenience functions test passed")

    test_comprehensive_benchmark()
    print("✓ Comprehensive benchmark test passed")

    print("\nAll enhanced benchmarking tests passed!")
