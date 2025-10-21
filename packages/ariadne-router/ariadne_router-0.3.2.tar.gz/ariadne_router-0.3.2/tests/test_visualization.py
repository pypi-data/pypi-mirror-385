"""
Comprehensive test suite for Ariadne visualization module.

Tests the ResultAnalyzer, ResultVisualizer, and visualization convenience functions
with proper mocking for external dependencies.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
from pytest import CaptureFixture

from ariadne.types import BackendType, SimulationResult
from ariadne.visualization import (
    ResultAnalyzer,
    ResultVisualizer,
    VisualizationConfig,
    analyze_batch_results,
    compare_backend_results,
    visualize_decision,
    visualize_result,
)


class TestVisualizationConfig:
    """Test VisualizationConfig dataclass functionality."""

    def test_config_default_initialization(self) -> None:
        """Test default configuration initialization."""
        config = VisualizationConfig()

        assert config.save_plots is True
        assert config.show_plots is False
        assert config.output_dir == Path("./ariadne_plots")
        assert config.file_format == "png"
        assert config.style == "seaborn"
        assert config.color_palette == "viridis"
        assert config.figure_size == (12, 8)
        assert config.dpi == 300
        assert config.include_performance_analysis is True
        assert config.include_comparison_plots is True
        assert config.include_circuit_analysis is True
        assert config.include_statistical_analysis is True

    def test_config_custom_initialization(self) -> None:
        """Test custom configuration initialization."""
        custom_dir = Path("/custom/path")
        config = VisualizationConfig(
            save_plots=False,
            show_plots=True,
            output_dir=custom_dir,
            file_format="pdf",
            style="ggplot",
            color_palette="plasma",
            figure_size=(10, 6),
            dpi=150,
            include_performance_analysis=False,
            include_comparison_plots=False,
            include_circuit_analysis=False,
            include_statistical_analysis=False,
        )

        assert config.save_plots is False
        assert config.show_plots is True
        assert config.output_dir == custom_dir
        assert config.file_format == "pdf"
        assert config.style == "ggplot"
        assert config.color_palette == "plasma"
        assert config.figure_size == (10, 6)
        assert config.dpi == 150
        assert config.include_performance_analysis is False
        assert config.include_comparison_plots is False
        assert config.include_circuit_analysis is False
        assert config.include_statistical_analysis is False


class TestResultAnalyzer:
    """Test ResultAnalyzer class functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.config = VisualizationConfig()
        self.analyzer = ResultAnalyzer(self.config)

        # Create mock simulation result
        self.mock_result = Mock(spec=SimulationResult)
        self.mock_result.backend_used = BackendType.STIM
        self.mock_result.execution_time = 0.5
        self.mock_result.counts = {"00": 500, "11": 500}

        # Add optional attributes
        self.mock_result.quantum_advantage = {
            "overall_advantage_score": 0.8,
            "has_quantum_advantage": True,
        }

        resource_mock = Mock()
        resource_mock.execution_time_estimate = 0.6
        resource_mock.memory_requirement_mb = 128.0
        resource_mock.qubit_requirement = 10
        self.mock_result.resource_estimate = resource_mock

    def test_analyzer_initialization(self) -> None:
        """Test ResultAnalyzer initialization."""
        analyzer = ResultAnalyzer()
        assert analyzer.config is not None
        assert analyzer.config.output_dir.exists()

    def test_analyze_single_result_basic(self) -> None:
        """Test basic single result analysis."""
        analysis = self.analyzer.analyze_single_result(self.mock_result)

        assert analysis["backend_used"] == BackendType.STIM
        assert analysis["execution_time"] == 0.5
        assert analysis["total_shots"] == 1000
        assert analysis["unique_states"] == 2
        assert "entropy" in analysis
        assert "probability_distribution" in analysis
        assert "statistical_metrics" in analysis

    def test_analyze_single_result_with_quantum_advantage(self) -> None:
        """Test analysis with quantum advantage data."""
        analysis = self.analyzer.analyze_single_result(self.mock_result)

        assert "quantum_advantage" in analysis
        assert analysis["quantum_advantage"]["overall_advantage_score"] == 0.8
        assert analysis["quantum_advantage"]["has_quantum_advantage"] is True

    def test_analyze_single_result_with_resource_estimate(self) -> None:
        """Test analysis with resource estimate data."""
        analysis = self.analyzer.analyze_single_result(self.mock_result)

        assert "resource_estimate" in analysis
        resource_data = analysis["resource_estimate"]
        assert resource_data["execution_time_estimate"] == 0.6
        assert resource_data["memory_requirement_mb"] == 128.0
        assert resource_data["qubit_requirement"] == 10

    def test_analyze_single_result_empty_counts(self) -> None:
        """Test analysis with empty measurement counts."""
        empty_result = Mock(spec=SimulationResult)
        empty_result.backend_used = BackendType.QISKIT
        empty_result.execution_time = 0.1
        empty_result.counts = {}

        analysis = self.analyzer.analyze_single_result(empty_result)

        assert analysis["total_shots"] == 0
        assert analysis["unique_states"] == 0
        assert analysis["entropy"] == 0.0
        assert analysis["probability_distribution"] == {}

    def test_analyze_batch_results_empty(self) -> None:
        """Test batch analysis with empty results list."""
        analysis = self.analyzer.analyze_batch_results([])
        assert analysis == {}

    def test_analyze_batch_results_multiple(self) -> None:
        """Test batch analysis with multiple results."""
        results = [self.mock_result, self.mock_result]
        analysis = self.analyzer.analyze_batch_results(results)

        assert analysis["num_simulations"] == 2
        assert analysis["total_execution_time"] == 1.0
        assert analysis["average_execution_time"] == 0.5
        assert "backend_usage" in analysis
        assert analysis["backend_usage"][BackendType.STIM] == 2

    def test_calculate_measurement_entropy(self) -> None:
        """Test entropy calculation for various distributions."""
        # Uniform distribution (max entropy)
        uniform_counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        uniform_entropy = self.analyzer._calculate_measurement_entropy(uniform_counts)
        assert abs(uniform_entropy - 2.0) < 0.01  # log2(4) = 2

        # Deterministic distribution (min entropy)
        deterministic_counts = {"00": 1000}
        deterministic_entropy = self.analyzer._calculate_measurement_entropy(deterministic_counts)
        assert deterministic_entropy == 0.0

        # Empty counts
        empty_entropy = self.analyzer._calculate_measurement_entropy({})
        assert empty_entropy == 0.0

    def test_get_probability_distribution(self) -> None:
        """Test probability distribution calculation."""
        counts = {"00": 300, "11": 700}
        distribution = self.analyzer._get_probability_distribution(counts)

        assert distribution["00"] == 0.3
        assert distribution["11"] == 0.7
        assert sum(distribution.values()) == 1.0

    def test_calculate_statistical_metrics(self) -> None:
        """Test statistical metrics calculation."""
        counts = {"00": 400, "01": 300, "10": 200, "11": 100}
        metrics = self.analyzer._calculate_statistical_metrics(counts)

        assert "mean_probability" in metrics
        assert "std_probability" in metrics
        assert "max_probability" in metrics
        assert "min_probability" in metrics
        assert "coefficient_of_variation" in metrics

        # All probabilities should sum to 1
        assert abs(metrics["mean_probability"] * 4 - 1.0) < 0.01

    def test_compare_backends(self) -> None:
        """Test backend comparison functionality."""
        backend_results = {"stim": self.mock_result, "qiskit": self.mock_result}

        comparison = self.analyzer.compare_backends(backend_results)

        assert "backends_compared" in comparison
        assert "performance_comparison" in comparison
        assert "fastest_backend" in comparison
        assert "speedup_ratios" in comparison
        assert len(comparison["backends_compared"]) == 2


class TestResultVisualizer:
    """Test ResultVisualizer class functionality with proper mocking."""

    def setup_method(self) -> None:
        """Set up test fixtures with mocked dependencies."""
        self.config = VisualizationConfig()
        self.config.output_dir = Path(tempfile.mkdtemp())
        self.visualizer = ResultVisualizer(self.config)

        # Create mock result
        self.mock_result = Mock(spec=SimulationResult)
        self.mock_result.backend_used = BackendType.STIM
        self.mock_result.execution_time = 0.5
        self.mock_result.counts = {"00": 500, "11": 500}

        # Mock backend performance
        self.mock_result.backend_performance = {"gate_operations": 1000, "memory_usage": 50.5}

    @patch("ariadne.visualization.plt")
    @patch("ariadne.visualization.sns")
    def test_visualizer_initialization(self, mock_sns: MagicMock, mock_plt: MagicMock) -> None:
        """Test ResultVisualizer initialization."""
        visualizer = ResultVisualizer(self.config)
        assert visualizer.config == self.config
        assert visualizer.analyzer is not None

    @patch("ariadne.visualization.plt.subplots")
    @patch("ariadne.visualization.plt.tight_layout")
    def test_create_single_result_plots(self, mock_tight: MagicMock, mock_subplots: MagicMock) -> None:
        """Test single result plot creation."""
        # Mock for different subplot calls
        mock_fig = Mock()

        # First call: _plot_measurement_distribution uses plt.subplots(1, 2)
        mock_ax1 = Mock()
        mock_ax2 = Mock()
        axes_list = [mock_ax1, mock_ax2]

        # Second call: _plot_performance_metrics uses plt.subplots(2, 2)
        mock_ax00 = Mock()
        mock_ax01 = Mock()
        mock_ax10 = Mock()
        mock_ax11 = Mock()
        axes_2d = np.array([[mock_ax00, mock_ax01], [mock_ax10, mock_ax11]])

        # Set side effect to return different values for different calls
        mock_subplots.side_effect = [
            (mock_fig, axes_list),  # First call for measurement distribution
            (mock_fig, axes_2d),  # Second call for performance metrics
        ]

        with patch.object(self.visualizer, "_save_figure", return_value=Path("/test/path.png")) as mock_save:
            saved_files = self.visualizer.create_single_result_plots(self.mock_result)
            mock_save.assert_called()

        assert len(saved_files) > 0
        assert mock_subplots.call_count == 2

    @patch("ariadne.visualization.plt.subplots")
    @patch("ariadne.visualization.plt.tight_layout")
    def test_create_comparison_plots(self, mock_tight: MagicMock, mock_subplots: MagicMock) -> None:
        """Test comparison plot creation."""
        backend_results = {"stim": self.mock_result, "qiskit": self.mock_result}

        # Mock for different subplot calls
        mock_fig = Mock()

        # First call: _plot_backend_performance_comparison uses plt.subplots(1, 2)
        mock_ax1 = Mock()
        mock_ax2 = Mock()
        axes_list = [mock_ax1, mock_ax2]

        # Mock the bar method to return a mock object that is iterable
        mock_bar1 = Mock()
        mock_bar1.get_x.return_value = 0.0
        mock_bar1.get_width.return_value = 0.8
        mock_bar1.get_height.return_value = 0.5
        mock_ax1.bar.return_value = [mock_bar1, mock_bar1]

        # Second call: _plot_backend_accuracy_comparison uses plt.subplots() (single axis)
        mock_ax_single = Mock()

        # Set side effect to return different values for different calls
        mock_subplots.side_effect = [
            (mock_fig, axes_list),  # First call for performance comparison
            (mock_fig, mock_ax_single),  # Second call for accuracy comparison
        ]

        with patch.object(self.visualizer, "_save_figure", return_value=Path("/test/path.png")) as mock_save:
            saved_files = self.visualizer.create_comparison_plots(backend_results)
            mock_save.assert_called()

        assert len(saved_files) == 2
        assert mock_subplots.call_count == 2

    def test_calculate_distribution_similarity(self) -> None:
        """Test distribution similarity calculation."""
        counts1 = {"00": 500, "11": 500}
        counts2 = {"00": 500, "11": 500}  # Same distribution

        similarity = self.visualizer._calculate_distribution_similarity(counts1, counts2)
        assert abs(similarity - 1.0) < 0.01  # Should be very similar

        # Different distributions
        counts3 = {"00": 1000, "11": 0}
        similarity2 = self.visualizer._calculate_distribution_similarity(counts1, counts3)
        assert similarity2 < similarity  # Should be less similar

    @patch("ariadne.visualization.plt.show")
    @patch("ariadne.visualization.plt.close")
    def test_save_figure(self, mock_close: MagicMock, mock_show: MagicMock) -> None:
        """Test figure saving functionality."""
        mock_fig = Mock()

        # Test with save_plots=True, show_plots=False
        self.visualizer.config.save_plots = True
        self.visualizer.config.show_plots = False

        filepath = self.visualizer._save_figure(mock_fig, "test_figure")

        mock_fig.savefig.assert_called_once()
        mock_close.assert_called_once_with(mock_fig)
        assert filepath.name == "test_figure.png"

        # Test with show_plots=True
        self.visualizer.config.show_plots = True
        self.visualizer._save_figure(mock_fig, "test_figure2")
        mock_show.assert_called_once()


class TestConvenienceFunctions:
    """Test the convenience wrapper functions."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_result = Mock(spec=SimulationResult)
        self.mock_result.backend_used = BackendType.STIM
        self.mock_result.execution_time = 0.5
        self.mock_result.counts = {"00": 500, "11": 500}

    @patch("ariadne.visualization.ResultVisualizer")
    def test_visualize_result(self, mock_visualizer_class: MagicMock) -> None:
        """Test visualize_result convenience function."""
        mock_visualizer = Mock()
        mock_visualizer.create_single_result_plots.return_value = [Path("/test/path.png")]
        mock_visualizer_class.return_value = mock_visualizer

        saved_files = visualize_result(self.mock_result)

        mock_visualizer_class.assert_called_once()
        mock_visualizer.create_single_result_plots.assert_called_once_with(self.mock_result, "result")
        assert len(saved_files) == 1

    @patch("ariadne.visualization.ResultVisualizer")
    def test_compare_backend_results(self, mock_visualizer_class: MagicMock) -> None:
        """Test compare_backend_results convenience function."""
        backend_results = {"stim": self.mock_result, "qiskit": self.mock_result}

        mock_visualizer = Mock()
        mock_visualizer.create_comparison_plots.return_value = [Path("/test/path.png")]
        mock_visualizer_class.return_value = mock_visualizer

        saved_files = compare_backend_results(backend_results)

        mock_visualizer_class.assert_called_once()
        mock_visualizer.create_comparison_plots.assert_called_once_with(backend_results, "comparison")
        assert len(saved_files) == 1

    @patch("ariadne.visualization.ResultVisualizer")
    @patch("ariadne.visualization.ResultAnalyzer")
    def test_analyze_batch_results(self, mock_analyzer_class: MagicMock, mock_visualizer_class: MagicMock) -> None:
        """Test analyze_batch_results convenience function."""
        results = [self.mock_result, self.mock_result]

        mock_analyzer = Mock()
        mock_analyzer.analyze_batch_results.return_value = {"test": "analysis"}
        mock_analyzer_class.return_value = mock_analyzer

        mock_visualizer = Mock()
        mock_visualizer.create_batch_analysis_plots.return_value = [Path("/test/path.png")]
        mock_visualizer_class.return_value = mock_visualizer

        analysis, plots = analyze_batch_results(results)

        mock_analyzer_class.assert_called_once()
        mock_visualizer_class.assert_called_once()
        mock_analyzer.analyze_batch_results.assert_called_once_with(results)
        assert analysis == {"test": "analysis"}
        assert len(plots) == 1


class TestVisualizeDecision:
    """Test the visualize_decision text-based visualization function."""

    def test_visualize_decision_basic(self, capsys: CaptureFixture[str]) -> None:
        """Test basic decision visualization."""
        circuit_name = "test_circuit"
        decision_path: list[tuple[str, str]] = [
            ("CliffordAnalyzer", "Circuit is Clifford - ROUTE IMMEDIATELY to Stim"),
            ("EntanglementAnalyzer", "Low entanglement - PASS to next analyzer"),
        ]
        final_backend = "stim"
        performance_gain = "10x speedup"

        visualize_decision(circuit_name, decision_path, final_backend, performance_gain)

        captured = capsys.readouterr()
        output = captured.out

        assert "ARIADNE ROUTING DECISION: test_circuit" in output
        assert "FINAL BACKEND: stim" in output
        assert "PERFORMANCE GAIN: 10x speedup" in output
        assert "CliffordAnalyzer" in output
        assert "ROUTE IMMEDIATELY" in output

    def test_visualize_decision_empty_path(self, capsys: CaptureFixture[str]) -> None:
        """Test decision visualization with empty path."""
        circuit_name = "empty_circuit"
        decision_path: list[tuple[str, str]] = []
        final_backend = "qiskit"
        performance_gain = "No gain"

        visualize_decision(circuit_name, decision_path, final_backend, performance_gain)

        captured = capsys.readouterr()
        output = captured.out

        assert "ARIADNE ROUTING DECISION: empty_circuit" in output
        assert "FINAL BACKEND: qiskit" in output
        assert "PERFORMANCE GAIN: No gain" in output


# Run all tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
