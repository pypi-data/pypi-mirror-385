"""
Simulation Result Analysis and Visualization

This module provides comprehensive analysis and visualization tools for
quantum simulation results, including performance analysis, circuit
visualization, and comparative studies.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.figure import Figure


@dataclass
class VisualizationConfig:
    """Configuration for visualization generation."""

    # Output options
    save_plots: bool = True
    show_plots: bool = False
    output_dir: Path = Path("./ariadne_plots")
    file_format: str = "png"  # png, pdf, svg, html

    # Plot styling
    style: str = "seaborn"  # matplotlib style
    color_palette: str = "viridis"
    figure_size: tuple[int, int] = (12, 8)
    dpi: int = 300

    # Content options
    include_performance_analysis: bool = True
    include_comparison_plots: bool = True
    include_circuit_analysis: bool = True
    include_statistical_analysis: bool = True


class ResultAnalyzer:
    """
    Comprehensive analyzer for quantum simulation results.

    Provides statistical analysis, performance metrics, and insights
    from quantum simulation results.
    """

    def __init__(self, config: VisualizationConfig | None = None):
        """Initialize result analyzer."""
        self.config = config or VisualizationConfig()

        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Set matplotlib style with fallback
        try:
            plt.style.use(self.config.style)
        except OSError:
            # Fallback to default style if seaborn is not available
            plt.style.use("default")
        sns.set_palette(self.config.color_palette)

    def analyze_single_result(self, result: Any) -> dict[str, Any]:
        """Analyze a single simulation result."""

        analysis = {
            "timestamp": time.time(),
            "backend_used": result.backend_used,
            "execution_time": result.execution_time,
            "total_shots": sum(result.counts.values()),
            "unique_states": len(result.counts),
            "entropy": self._calculate_measurement_entropy(result.counts),
            "probability_distribution": self._get_probability_distribution(result.counts),
            "statistical_metrics": self._calculate_statistical_metrics(result.counts),
        }

        # Add quantum advantage analysis if available
        if hasattr(result, "quantum_advantage") and result.quantum_advantage:
            analysis["quantum_advantage"] = result.quantum_advantage

        # Add resource estimates if available
        if hasattr(result, "resource_estimate") and result.resource_estimate:
            analysis["resource_estimate"] = {
                "execution_time_estimate": result.resource_estimate.execution_time_estimate,
                "memory_requirement_mb": result.resource_estimate.memory_requirement_mb,
                "qubit_requirement": result.resource_estimate.qubit_requirement,
            }

        return analysis

    def analyze_batch_results(self, results: list[Any]) -> dict[str, Any]:
        """Analyze multiple simulation results."""

        if not results:
            return {}

        # Individual analyses
        individual_analyses = [self.analyze_single_result(result) for result in results]

        # Aggregate statistics
        execution_times = [a["execution_time"] for a in individual_analyses]
        backend_usage: dict[str, int] = {}
        total_shots = sum(a["total_shots"] for a in individual_analyses)

        for analysis in individual_analyses:
            backend = analysis["backend_used"]
            backend_usage[backend] = backend_usage.get(backend, 0) + 1

        batch_analysis = {
            "num_simulations": len(results),
            "total_execution_time": sum(execution_times),
            "average_execution_time": np.mean(execution_times),
            "execution_time_std": np.std(execution_times),
            "backend_usage": backend_usage,
            "total_shots": total_shots,
            "individual_analyses": individual_analyses,
        }

        # Performance trends
        if len(results) > 1:
            batch_analysis["performance_trends"] = self._analyze_performance_trends(individual_analyses)

        return batch_analysis

    def compare_backends(self, backend_results: dict[str, Any]) -> dict[str, Any]:
        """Compare results across different backends."""

        comparison: dict[str, Any] = {
            "backends_compared": list(backend_results.keys()),
            "performance_comparison": {},
            "accuracy_comparison": {},
            "efficiency_metrics": {},
        }

        # Performance comparison
        for backend, result in backend_results.items():
            analysis = self.analyze_single_result(result)

            comparison["performance_comparison"][backend] = {
                "execution_time": analysis["execution_time"],
                "shots_per_second": analysis["total_shots"] / max(analysis["execution_time"], 1e-6),
                "memory_efficiency": analysis.get("resource_estimate", {}).get("memory_requirement_mb", 0),
            }

        # Find best performing backend
        fastest_backend = min(
            comparison["performance_comparison"].keys(),
            key=lambda b: comparison["performance_comparison"][b]["execution_time"],
        )

        comparison["fastest_backend"] = fastest_backend
        comparison["speedup_ratios"] = {}

        baseline_time = comparison["performance_comparison"][fastest_backend]["execution_time"]
        for backend, metrics in comparison["performance_comparison"].items():
            comparison["speedup_ratios"][backend] = metrics["execution_time"] / baseline_time

        return comparison

    def _calculate_measurement_entropy(self, counts: dict[str, int]) -> float:
        """Calculate Shannon entropy of measurement outcomes."""
        total = sum(counts.values())
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        return entropy

    def _get_probability_distribution(self, counts: dict[str, int]) -> dict[str, float]:
        """Get normalized probability distribution."""
        total = sum(counts.values())
        return {state: count / total for state, count in counts.items()}

    def _calculate_statistical_metrics(self, counts: dict[str, int]) -> dict[str, float]:
        """Calculate statistical metrics for measurement results."""
        total_shots = sum(counts.values())
        if total_shots == 0 or len(counts) == 0:
            return {
                "mean_probability": 0.0,
                "std_probability": 0.0,
                "max_probability": 0.0,
                "min_probability": 0.0,
                "coefficient_of_variation": 0.0,
            }

        probabilities = [count / total_shots for count in counts.values()]

        return {
            "mean_probability": float(np.mean(probabilities)),
            "std_probability": float(np.std(probabilities)),
            "max_probability": float(max(probabilities)),
            "min_probability": float(min(probabilities)),
            "coefficient_of_variation": float(np.std(probabilities) / max(float(np.mean(probabilities)), 1e-10)),
        }

    def _analyze_performance_trends(self, analyses: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze performance trends across multiple simulations."""

        execution_times = [a["execution_time"] for a in analyses]
        entropies = [a["entropy"] for a in analyses]

        trends = {
            "execution_time_trend": np.polyfit(range(len(execution_times)), execution_times, 1)[0],
            "entropy_trend": np.polyfit(range(len(entropies)), entropies, 1)[0],
            "performance_stability": 1.0 / (1.0 + np.std(execution_times) / max(np.mean(execution_times), 1e-6)),
        }

        return trends


class ResultVisualizer:
    """
    Visualization generator for quantum simulation results.

    Creates comprehensive plots and charts for analysis and reporting.
    """

    def __init__(self, config: VisualizationConfig | None = None):
        """Initialize result visualizer."""
        self.config = config or VisualizationConfig()
        self.analyzer = ResultAnalyzer(config)

    def create_single_result_plots(self, result: Any, save_prefix: str = "single_result") -> list[Path]:
        """Create comprehensive plots for a single simulation result."""

        saved_files = []

        # Measurement distribution plot
        fig1 = self._plot_measurement_distribution(result)
        file1 = self._save_figure(fig1, f"{save_prefix}_distribution")
        saved_files.append(file1)

        # Performance metrics plot
        if hasattr(result, "backend_performance"):
            fig2 = self._plot_performance_metrics(result)
            file2 = self._save_figure(fig2, f"{save_prefix}_performance")
            saved_files.append(file2)

        # Quantum advantage analysis
        if hasattr(result, "quantum_advantage") and result.quantum_advantage:
            fig3 = self._plot_quantum_advantage(result.quantum_advantage)
            file3 = self._save_figure(fig3, f"{save_prefix}_quantum_advantage")
            saved_files.append(file3)

        return saved_files

    def create_comparison_plots(self, backend_results: dict[str, Any], save_prefix: str = "comparison") -> list[Path]:
        """Create comparison plots across multiple backends."""

        saved_files = []

        # Performance comparison
        fig1 = self._plot_backend_performance_comparison(backend_results)
        file1 = self._save_figure(fig1, f"{save_prefix}_performance")
        saved_files.append(file1)

        # Accuracy comparison (if results are from same circuit)
        fig2 = self._plot_backend_accuracy_comparison(backend_results)
        file2 = self._save_figure(fig2, f"{save_prefix}_accuracy")
        saved_files.append(file2)

        return saved_files

    def create_batch_analysis_plots(self, batch_analysis: dict[str, Any], save_prefix: str = "batch") -> list[Path]:
        """Create plots for batch simulation analysis."""

        saved_files = []

        # Performance trends
        if "performance_trends" in batch_analysis:
            fig1 = self._plot_performance_trends(batch_analysis)
            file1 = self._save_figure(fig1, f"{save_prefix}_trends")
            saved_files.append(file1)

        # Backend usage distribution
        fig2 = self._plot_backend_usage(batch_analysis["backend_usage"])
        file2 = self._save_figure(fig2, f"{save_prefix}_backend_usage")
        saved_files.append(file2)

        return saved_files

    def _plot_measurement_distribution(self, result: Any) -> Figure:
        """Plot measurement outcome distribution."""

        fig, axes = plt.subplots(1, 2, figsize=self.config.figure_size)
        ax1, ax2 = axes

        # Bar plot of counts
        states = list(result.counts.keys())
        counts = list(result.counts.values())

        ax1.bar(range(len(states)), counts)
        ax1.set_xlabel("Measurement Outcome")
        ax1.set_ylabel("Count")
        ax1.set_title("Measurement Distribution")
        ax1.set_xticks(range(len(states)))
        ax1.set_xticklabels(states, rotation=45)

        # Probability distribution
        total_shots = sum(counts)
        probabilities = [c / total_shots for c in counts]

        ax2.pie(probabilities, labels=states, autopct="%1.1f%%")
        ax2.set_title("Probability Distribution")

        plt.tight_layout()
        return fig

    def _plot_performance_metrics(self, result: Any) -> Figure:
        """Plot performance metrics."""

        fig, axes = plt.subplots(2, 2, figsize=self.config.figure_size)
        ax00, ax01, ax10, ax11 = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

        # Execution time
        ax00.bar(["Execution Time"], [result.execution_time])
        ax00.set_ylabel("Time (seconds)")
        ax00.set_title("Execution Time")

        # Backend information
        backend_info = getattr(result, "backend_performance", {})
        if backend_info:
            metrics = list(backend_info.keys())[:3]  # Show top 3 metrics
            values = [backend_info[m] for m in metrics]

            ax01.bar(metrics, values)
            ax01.set_title("Backend Performance Metrics")
            ax01.tick_params(axis="x", rotation=45)

        # Resource usage (if available)
        if hasattr(result, "resource_estimate") and result.resource_estimate:
            resource_data = {
                "Memory (MB)": result.resource_estimate.memory_requirement_mb,
                "Qubits": result.resource_estimate.qubit_requirement,
                "Gates": getattr(result.resource_estimate, "gate_count_estimate", 0),
            }

            ax10.bar(resource_data.keys(), resource_data.values())
            ax10.set_title("Resource Requirements")
            ax10.tick_params(axis="x", rotation=45)

        # Circuit analysis (if available)
        if hasattr(result, "circuit_analysis"):
            analysis = result.circuit_analysis
            key_metrics = {
                "Qubits": analysis.get("num_qubits", 0),
                "Depth": analysis.get("depth", 0),
                "Entropy": analysis.get("gate_entropy", 0),
            }

            ax11.bar(key_metrics.keys(), key_metrics.values())
            ax11.set_title("Circuit Characteristics")

        plt.tight_layout()
        return fig

    def _plot_quantum_advantage(self, qa_analysis: dict[str, Any]) -> Figure:
        """Plot quantum advantage analysis."""

        fig, axes = plt.subplots(2, 2, figsize=self.config.figure_size)

        # Overall advantage score
        score = qa_analysis.get("overall_advantage_score", 0)
        axes[0, 0].pie([score, 1 - score], labels=["Advantage", "Classical"], autopct="%1.1f%%")
        axes[0, 0].set_title(f"Quantum Advantage Score: {score:.2f}")

        # Component scores
        components = [
            "classical_intractability",
            "quantum_volume_advantage",
            "entanglement_advantage",
            "sampling_advantage",
        ]
        component_scores = []

        for comp in components:
            if comp in qa_analysis:
                comp_data = qa_analysis[comp]
                if isinstance(comp_data, dict):
                    score = comp_data.get("advantage_score", 0) or comp_data.get("intractability_score", 0)
                else:
                    score = 0
                component_scores.append(score)
            else:
                component_scores.append(0)

        axes[0, 1].bar(components, component_scores)
        axes[0, 1].set_title("Advantage Components")
        axes[0, 1].tick_params(axis="x", rotation=45)

        # Error threshold analysis
        if "error_threshold" in qa_analysis:
            et_data = qa_analysis["error_threshold"]
            error_rate = et_data.get("estimated_error_rate", 0)
            threshold = et_data.get("error_threshold", 0.1)

            axes[1, 0].bar(["Estimated", "Threshold"], [error_rate, threshold])
            axes[1, 0].set_ylabel("Error Rate")
            axes[1, 0].set_title("Error Threshold Analysis")

        # Recommendations
        recommendations = qa_analysis.get("recommendations", [])
        if recommendations:
            rec_text = "\n".join(recommendations[:3])  # Show first 3 recommendations
            axes[1, 1].text(
                0.1,
                0.5,
                rec_text,
                transform=axes[1, 1].transAxes,
                fontsize=10,
                verticalalignment="center",
                wrap=True,
            )
            axes[1, 1].set_title("Recommendations")
            axes[1, 1].axis("off")

        plt.tight_layout()
        return fig

    def _plot_backend_performance_comparison(self, backend_results: dict[str, Any]) -> Figure:
        """Plot performance comparison across backends."""

        backends = list(backend_results.keys())
        execution_times = []
        memory_usage = []

        for _backend, result in backend_results.items():
            execution_times.append(result.execution_time)
            if hasattr(result, "resource_estimate") and result.resource_estimate:
                memory_usage.append(result.resource_estimate.memory_requirement_mb)
            else:
                memory_usage.append(0)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.config.figure_size)

        # Execution time comparison
        bars1 = ax1.bar(backends, execution_times)
        ax1.set_ylabel("Execution Time (seconds)")
        ax1.set_title("Backend Performance Comparison")
        ax1.tick_params(axis="x", rotation=45)

        # Add value labels on bars
        for bar, time_val in zip(bars1, execution_times, strict=False):
            height = bar.get_height()
            # Calculate position manually to avoid Mock object arithmetic
            x_pos = bar.get_x() + bar.get_width() / 2.0
            ax1.text(x_pos, height, f"{time_val:.3f}s", ha="center", va="bottom")

        # Memory usage comparison
        if any(mem > 0 for mem in memory_usage):
            ax2.bar(backends, memory_usage)
            ax2.set_ylabel("Memory Usage (MB)")
            ax2.set_title("Memory Requirements")
            ax2.tick_params(axis="x", rotation=45)
        else:
            ax2.text(
                0.5,
                0.5,
                "Memory data not available",
                transform=ax2.transAxes,
                ha="center",
                va="center",
            )
            ax2.set_title("Memory Requirements")

        plt.tight_layout()
        return fig

    def _plot_backend_accuracy_comparison(self, backend_results: dict[str, Any]) -> Figure:
        """Plot accuracy comparison between backends."""

        fig, axes = plt.subplots(figsize=self.config.figure_size)

        # Calculate distribution similarities (simplified)
        backend_names = list(backend_results.keys())
        if len(backend_names) < 2:
            axes.text(
                0.5,
                0.5,
                "Need at least 2 backends for comparison",
                transform=axes.transAxes,
                ha="center",
                va="center",
            )
            axes.set_title("Backend Accuracy Comparison")
            return fig

        # Use first backend as reference
        reference_backend = backend_names[0]
        reference_counts = backend_results[reference_backend].counts

        similarities = []
        for backend in backend_names[1:]:
            similarity = self._calculate_distribution_similarity(reference_counts, backend_results[backend].counts)
            similarities.append(similarity)

        axes.bar(backend_names[1:], similarities)
        axes.set_ylabel("Similarity to Reference")
        axes.set_title(f"Distribution Similarity (Reference: {reference_backend})")
        axes.tick_params(axis="x", rotation=45)
        axes.set_ylim(0, 1)

        plt.tight_layout()
        return fig

    def _plot_performance_trends(self, batch_analysis: dict[str, Any]) -> Figure:
        """Plot performance trends over multiple simulations."""

        individual_analyses = batch_analysis["individual_analyses"]

        fig, axes = plt.subplots(2, 2, figsize=self.config.figure_size)

        # Execution time trend
        times = [a["execution_time"] for a in individual_analyses]
        axes[0, 0].plot(times, marker="o")
        axes[0, 0].set_xlabel("Simulation Number")
        axes[0, 0].set_ylabel("Execution Time (s)")
        axes[0, 0].set_title("Execution Time Trend")

        # Entropy trend
        entropies = [a["entropy"] for a in individual_analyses]
        axes[0, 1].plot(entropies, marker="s", color="orange")
        axes[0, 1].set_xlabel("Simulation Number")
        axes[0, 1].set_ylabel("Measurement Entropy")
        axes[0, 1].set_title("Entropy Trend")

        # Backend usage over time
        backend_sequence = [a["backend_used"] for a in individual_analyses]
        unique_backends = list(set(backend_sequence))
        backend_numbers = [unique_backends.index(b) for b in backend_sequence]

        axes[1, 0].plot(backend_numbers, marker="^", color="green")
        axes[1, 0].set_xlabel("Simulation Number")
        axes[1, 0].set_ylabel("Backend Used")
        axes[1, 0].set_title("Backend Selection Over Time")
        axes[1, 0].set_yticks(range(len(unique_backends)))
        axes[1, 0].set_yticklabels(unique_backends)

        # Performance distribution
        axes[1, 1].hist(times, bins=min(10, len(times) // 2), alpha=0.7)
        axes[1, 1].set_xlabel("Execution Time (s)")
        axes[1, 1].set_ylabel("Frequency")
        axes[1, 1].set_title("Performance Distribution")

        plt.tight_layout()
        return fig

    def _plot_backend_usage(self, backend_usage: dict[str, int]) -> Figure:
        """Plot backend usage distribution."""

        fig, ax = plt.subplots(figsize=(8, 6))

        backends = list(backend_usage.keys())
        counts = list(backend_usage.values())

        ax.pie(counts, labels=backends, autopct="%1.1f%%")
        ax.set_title("Backend Usage Distribution")

        return fig

    def _calculate_distribution_similarity(self, counts1: dict[str, int], counts2: dict[str, int]) -> float:
        """Calculate similarity between two probability distributions."""

        # Get all unique states
        all_states = set(counts1.keys()) | set(counts2.keys())

        # Normalize to probabilities
        total1 = sum(counts1.values())
        total2 = sum(counts2.values())

        prob1 = np.array([counts1.get(state, 0) / total1 for state in all_states])
        prob2 = np.array([counts2.get(state, 0) / total2 for state in all_states])

        # Calculate Bhattacharyya coefficient (similarity measure)
        similarity = float(np.sqrt(prob1 * prob2).sum())

        return similarity

    def _save_figure(self, fig: Figure, filename: str) -> Path:
        """Save figure to file."""

        filepath = self.config.output_dir / f"{filename}.{self.config.file_format}"

        fig.savefig(filepath, dpi=self.config.dpi, bbox_inches="tight")

        if self.config.show_plots:
            plt.show()
        else:
            plt.close(fig)

        return filepath


# Convenience functions
def visualize_result(result: Any, save_prefix: str = "result", config: VisualizationConfig | None = None) -> list[Path]:
    """Create visualizations for a single simulation result."""

    visualizer = ResultVisualizer(config)
    return visualizer.create_single_result_plots(result, save_prefix)


def compare_backend_results(
    backend_results: dict[str, Any],
    save_prefix: str = "comparison",
    config: VisualizationConfig | None = None,
) -> list[Path]:
    """Create comparison visualizations for multiple backend results."""

    visualizer = ResultVisualizer(config)
    return visualizer.create_comparison_plots(backend_results, save_prefix)


def analyze_batch_results(
    results: list, save_prefix: str = "batch", config: VisualizationConfig | None = None
) -> tuple[dict[str, Any], list[Path]]:
    """Analyze and visualize batch simulation results."""

    analyzer = ResultAnalyzer(config)
    visualizer = ResultVisualizer(config)

    # Perform analysis
    analysis = analyzer.analyze_batch_results(results)

    # Create visualizations
    plots = visualizer.create_batch_analysis_plots(analysis, save_prefix)

    return analysis, plots


def visualize_decision(
    circuit_name: str,
    decision_path: list[tuple[str, str]],
    final_backend: str,
    performance_gain: str,
) -> None:
    """
    Prints a clear, structured, text-based visualization of the routing decision process.

    Args:
        circuit_name: The name of the quantum circuit being routed.
        decision_path: A list of tuples [(analyzer_name, result_description)] representing the filter chain checks.
        final_backend: The name of the backend selected by the router.
        performance_gain: A string describing the estimated performance gain.
    """

    separator = "=" * 50
    check_separator = "-" * 50

    print(separator)
    print(f"ARIADNE ROUTING DECISION: {circuit_name}")
    print(separator)

    for i, (analyzer, result) in enumerate(decision_path):
        # Determine Decision based on result string content for visualization clarity
        result_upper = result.upper()
        if "ROUTE IMMEDIATELY" in result_upper:
            decision = "ROUTE IMMEDIATELY"
        elif "PASS" in result_upper:
            decision = "CONTINUE CHAIN"
        elif "FAIL" in result_upper:
            decision = "REJECT BACKEND"
        else:
            decision = "ANALYSIS COMPLETE"

        print(f"[{i + 1}] Analyzer: {analyzer}")
        print(f"    Result: {result}")
        print(f"    Decision: {decision}")
        print(check_separator)

    print(f"FINAL BACKEND: {final_backend}")
    print(f"PERFORMANCE GAIN: {performance_gain}")
    print(separator)
